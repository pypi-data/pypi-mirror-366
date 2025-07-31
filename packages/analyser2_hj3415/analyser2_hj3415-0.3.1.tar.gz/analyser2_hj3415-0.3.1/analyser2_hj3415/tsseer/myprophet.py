from typing import Any, Literal

import json
from prophet import Prophet
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .utils import get_raw_data, judge_trend

from redis_hj3415.wrapper import redis_cached, redis_async_cached
from redis_hj3415.common.connection import get_redis_client_async
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'INFO')


def prepare_data(df: pd.DataFrame) -> dict[str, pd.DataFrame | StandardScaler]:
    # ── (1) 기본 정리 ────────────────────────────────────
    df.columns = df.columns.get_level_values(0)
    df.index   = df.index.tz_localize(None)
    df = df[['Close', 'Volume']].dropna().reset_index()
    df.columns = ['ds', 'y', 'volume']          # Prophet 규격

    # ── (2) 스케일러 두 개 생성 ─────────────────────────
    volume_scaler = StandardScaler()
    y_scaler      = StandardScaler()

    df['volume_scaled'] = volume_scaler.fit_transform(df[['volume']])
    df['y_scaled']      = y_scaler.fit_transform(df[['y']])

    return {
        'prepared_df'   : df,              # y/raw, y_scaled, volume_scaled 모두 보존
        'volume_scaler' : volume_scaler,
        'y_scaler'      : y_scaler,
    }


def run_forecast(df_scaler_dict: dict[str, object], periods: int = 180) -> pd.DataFrame:
    """Prophet 학습 & periods 일 예측 → 역-스케일링해서 반환"""

    # ── 0. 필요한 객체 꺼내기 ───────────────────────────
    df:            pd.DataFrame   = df_scaler_dict['prepared_df'].copy()
    vol_scaler:    StandardScaler = df_scaler_dict['volume_scaler']
    y_scaler:      StandardScaler = df_scaler_dict['y_scaler']

    # ── 1. Prophet 학습용 DF 생성 (y_scaled만 사용) ────
    prophet_df = (
        df[['ds', 'y_scaled', 'volume_scaled']]
        .rename(columns={'y_scaled': 'y'})
    )

    model = Prophet()
    model.add_regressor('volume_scaled')
    model.fit(prophet_df)

    # ── 2. 미래 데이터프레임 생성 ───────────────────────
    future = model.make_future_dataframe(periods=periods)

    mean_vol = df['volume'].mean()
    future['volume_scaled'] = vol_scaler.transform([[mean_vol]] * len(future))

    # ── 3. 예측 + y 역-스케일링 ─────────────────────────
    pred_df = model.predict(future)

    cols_to_inverse = ['yhat', 'yhat_lower', 'yhat_upper']
    pred_df[cols_to_inverse] = y_scaler.inverse_transform(pred_df[cols_to_inverse])

    # (선택) 학습 구간의 실측 y도 복원해 두면 병합/시각화에 편리
    df['y'] = y_scaler.inverse_transform(df[['y_scaled']])
    # pred_df 와 df 를 나중에 merge 하면 실측·예측을 한 눈에 볼 수 있음

    return pred_df


def latest_anomaly_score(
    df: pd.DataFrame,
    *,
    y_col: str = 'actual',
    lo_col: str = 'lower',
    up_col: str = 'upper',
    ndigits: int = 4,
    eps: float = 1e-9
) -> float | None:
    """
    최근 값이 예측 구간을 얼마나 벗어났는지 비율로 반환.
    - upper 초과 → 양수
    - lower 초과 → 음수
    - 구간 안 → 0
    - 계산 불가 → None
    """
    valid = df.dropna(subset=[y_col, lo_col, up_col])
    if valid.empty:
        return None

    y, lo, up = valid.iloc[-1][[y_col, lo_col, up_col]]

    width = max(up - lo, eps)

    if y > up:
        score = (y - up) / width  # 양수
    elif y < lo:
        score = -(lo - y) / width  # 음수
    else:
        score = 0.0

    return round(score, ndigits)


@redis_cached(prefix='prophet')
def prophet_forecast(ticker: str, refresh: bool = False, cache_only: bool = False) -> dict[str, Any]:
    """
    Prophet 모델로 **단일 종목**의 과거·미래 시계열을 예측하고,
    결과를 JSON 직렬화에 친화적인 ``dict`` 형태로 반환한다.
    캐싱은 `@redis_cached` 데코레이터가 담당한다.

    -------
    동작 흐름
    -------
    1. **캐시 조회** – `prophet:{ticker}` 키 (소문자)
       * hit → 즉시 반환
       * miss → 단계 2 진행
    2. **예측 파이프라인**
       ① 원시 데이터 로드 → ② 스케일링·전처리 →
       ③ Prophet 학습·예측 → ④ 추세·Anomaly 계산
    3. **캐시 저장** – 기본 TTL 12 h (`REDIS_EXPIRE_TIME_H`)

    ----------
    Parameters
    ----------
    ticker : str
        종목 티커. 예) ``"005930.KS"``
    refresh : bool, default ``False``
        • ``True``  → 캐시를 무시하고 새로 계산 후 갱신
        • ``False`` → 캐시가 있으면 사용
    cache_only : bool, default ``False``
        • ``True``  → 캐시가 없으면 모델을 실행하지 않고 ``None`` 반환
        • ``False`` → 캐시 miss 시 모델 실행

    -------
    Returns
    -------
    dict[str, Any] | None
        ===========  ==========================================================
        키            설명
        -----------  ----------------------------------------------------------
        ds           ``List[str]``  예측·실측 날짜 (YYYY-MM-DD)
        actual       ``List[float | None]``  실제 값
        forecast     ``List[float | None]``  예측 평균값 (yhat)
        lower        ``List[float | None]``  95 % 하단 구간
        upper        ``List[float | None]``  95 % 상단 구간
        trend        ``"상승" | "하락" | "횡보" | "미정"``  최신 추세 판단
        anomaly_score   ``float``  최신 구간 이상 점수 (± 값, 0 : 정상)
        ===========  ==========================================================
        *``cache_only=True`` + miss* 인 경우 ``None`` 반환.

    -------
    Examples
    -------
    >>> # 캐시 우선, 없으면 계산
    >>> prophet_forecast("005930.KS")
    {...}

    >>> # 강제 재계산
    >>> prophet_forecast("005930.KS", refresh=True)

    >>> # 캐시만 조회, 없으면 None
    >>> prophet_forecast("005930.KS", cache_only=True)

    Notes
    -----
    • `judge_trend()` : 예측값 기울기로 상승/하락/횡보 판정
    • `latest_anomaly_score()` : 최신 지점이 예측 구간 밖이면 ± 스코어
    • 반환 리스트 원소 수는 **실측 + 예측 구간** 전체 길이와 동일하다.
    """
    df = get_raw_data(ticker)
    df_scaler_dict = prepare_data(df)
    past_and_forecast = run_forecast(df_scaler_dict)

    prepared_df: pd.DataFrame = df_scaler_dict['prepared_df']
    merged = (
        prepared_df[['ds', 'y']]
        .merge(
            past_and_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
            on='ds', how='outer'
        )
        .sort_values('ds')
    )

    # ------------- (2) 추세 평가 -------------
    fcst_vals = merged.loc[merged['yhat'].notna(), 'yhat'].values
    trend = judge_trend(fcst_vals)  # "상승" | "하락" | "횡보" | 미정

    # 3-1) anomaly score 계산
    anomaly = latest_anomaly_score(merged, y_col='y', lo_col='yhat_lower', up_col='yhat_upper')

    return {
        'ds'      : merged['ds'].dt.strftime('%Y-%m-%d').tolist(),
        'actual'  : merged['y'].where(merged['y'].notna()).tolist(),
        'forecast': merged['yhat'].round(2).tolist(),
        'lower'   : merged['yhat_lower'].round(2).tolist(),
        'upper'   : merged['yhat_upper'].round(2).tolist(),
        'trend': trend,
        "anomaly_score": anomaly
    }


@redis_async_cached(prefix="prophet_trend")
async def filter_prophet_by_trend_and_anomaly(tickers: list[str], trend: Literal["상승", "하락"],
                                              refresh: bool = False, cache_only: bool = False) -> list[dict]:
    r = get_redis_client_async()

    keys   = [f"prophet:{t.lower()}" for t in tickers]
    values = await r.mget(keys)

    rows: list[dict] = []
    for ticker, raw in zip(tickers, values):
        payload: dict | None = json.loads(raw) if raw else None
        if payload is None:
            continue
        if trend != payload['trend']:
            continue
        anomaly_score = payload.get('anomaly_score')
        if anomaly_score is None:
            continue
        if trend == '상승' and anomaly_score <= -0.01:
            rows.append(
                {'ticker': ticker, 'trend': payload['trend'], 'anomaly_score': anomaly_score}
            )
        elif trend == '하락' and anomaly_score >= 0.01:
            rows.append(
                {'ticker': ticker, 'trend': payload['trend'], 'anomaly_score': anomaly_score}
            )
    # ── 핵심: 절대값 기준 내림차순 정렬 ──────────────────
    rows.sort(key=lambda item: abs(item["anomaly_score"]), reverse=True)
    return rows

