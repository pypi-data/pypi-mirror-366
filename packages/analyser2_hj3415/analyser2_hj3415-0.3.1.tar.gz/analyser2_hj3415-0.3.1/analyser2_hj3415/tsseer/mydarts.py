from typing import Literal, Any
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from sklearn.preprocessing import StandardScaler
from darts.dataprocessing.transformers import MissingValuesFiller
import pandas as pd
import json

from .utils import get_raw_data, timeseries_to_dataframe, judge_trend
from redis_hj3415.common.connection import get_redis_client_async
from redis_hj3415.wrapper import redis_cached, redis_async_cached
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'INFO')


def prepare_data(df: pd.DataFrame) -> dict[str, TimeSeries | Scaler]:
    """
    주가-데이터 `DataFrame`을 **Darts** 시계열 객체로 전처리-패키징하는 함수
    -----------------------------------------------------------------------

    이 함수는 종가·거래량이 포함된 원본 `DataFrame`을 받아 다음 과정을 수행합니다.

    1. **컬럼 정리**
       - 다중 컬럼(OHLCV 등)이 있을 때 첫 번째 레벨만 유지합니다.
       - `Close`, `Volume` 두 컬럼만 남기고 결측 행을 제거합니다.

    2. **인덱스 정리**
       - 타임존 정보를 제거(`tz_localize(None)`)한 뒤,
         `DatetimeIndex`의 이름을 `"time"`으로 지정합니다.
       - 영업일 빈도(`'B'`)를 기준으로 빠진 날짜는 `fill_missing_dates=True` 옵션으로 자동 보간합니다.

    3. **`TimeSeries` 변환**
       - `target_series` : 종가(`Close`)를 단일 변수로 갖는 시계열
       - `volume_series` : 거래량(`Volume`)을 단일 변수로 갖는 시계열

    4. **결측값 보간**
       - 휴장일 등으로 인해 생긴 `NaN`은 **직전 값**으로 채웁니다.
         (`MissingValuesFiller().transform`)

    5. **스케일링 (0 ~ 1)**
       - `StandardScaler`를 래핑한 Darts `Scaler`를 사용해
         `target_series`와 `volume_series` 각각을 개별로 정규화합니다.
       - 변환 결과는 `target_scaled`, `volume_scaled`에 저장되며
         나중에 역-스케일링을 위해 `target_scaler`, `volume_scaler`도 함께 반환합니다.

    6. **디버그 로그**
       - 스케일된 시계열을 `mylogger.debug()`로 출력하여
         정상 변환 여부를 확인할 수 있습니다.

    반환값
    -------
    dict[str, TimeSeries | Scaler]
        - `'target_series'` : 원본 종가 시계열
        - `'volume_series'` : 원본 거래량 시계열
        - `'target_scaled'` : 정규화된 종가 시계열
        - `'volume_scaled'` : 정규화된 거래량 시계열
        - `'target_scaler'` : 종가 역-스케일링용 `Scaler` 객체
        - `'volume_scaler'` : 거래량 역-스케일링용 `Scaler` 객체
    """
    df.columns = df.columns.get_level_values(0)
    df.columns.name = None
    df = df[['Close', 'Volume']].dropna()
    df.index = df.index.tz_localize(None)  # 타임존 제거
    df.index.name = "time"  # darts는 index가 datetime이어야 함

    target_series = TimeSeries.from_dataframe(df, value_cols='Close', fill_missing_dates=True, freq='B')
    volume_series = TimeSeries.from_dataframe(df, value_cols='Volume', fill_missing_dates=True, freq='B')

    # 휴장일등으로 nan값을 가지는 데이터를 직전값으로 채운다.
    target_series = MissingValuesFiller().transform(target_series)
    volume_series = MissingValuesFiller().transform(volume_series)

    # 스케일링 (0~1)
    target_scaler = Scaler(StandardScaler())
    volume_scaler = Scaler(StandardScaler())

    target_scaled = target_scaler.fit_transform(target_series)
    volume_scaled = volume_scaler.fit_transform(volume_series)

    mylogger.debug(f"target_scaled : {target_scaled}")
    mylogger.debug(f"volume_scaled : {volume_scaled}")

    return {
        'target_series': target_series,
        'volume_series': volume_series,
        'target_scaled': target_scaled,
        'volume_scaled': volume_scaled,
        'target_scaler': target_scaler,
        'volume_scaler': volume_scaler,
    }


def prepare_train_val_series(target_type: Literal['raw', 'scaled'], series_scaler: dict[str, TimeSeries | Scaler]) -> dict[str, TimeSeries | Scaler]:
    """
    Darts 시계열을 **학습·검증 세트**로 9 : 1 분할하는 도우미 함수
    -----------------------------------------------------------------

    Parameters
    ----------
    target_type : {'raw', 'scaled'}
        - `'raw'`   : 원본 종가(`target_series`)를 학습·검증에 사용
        - `'scaled'`: 정규화된 종가(`target_scaled`)를 사용
        *(두 경우 모두 거래량은 스케일된 값 `volume_scaled`를 covariate로 사용합니다.)*

    series_scaler : dict[str, TimeSeries | Scaler]
        `prepare_darts_data()`가 반환한 딕셔너리.
        내부에서 다음 키를 참조합니다.

        * `'target_series'`  : 원본 종가 시계열
        * `'target_scaled'`  : 스케일된 종가 시계열
        * `'volume_scaled'`  : 스케일된 거래량 시계열

    Returns
    -------
    dict[str, TimeSeries | Scaler]
        * `'target_train'` : (90 %) 학습용 종가 시계열
        * `'volume_train'` : (90 %) 학습용 거래량 covariate
        * `'target_val'`   : (10 %) 검증용 종가 시계열
        * `'volume_val'`   : (10 %) 검증용 거래량 covariate

    Notes
    -----
    * 각 시계열은 `TimeSeries.split_before(0.9)`를 사용해 **시간 순서**를 유지한 채 9 : 1로 분할합니다.
    * 스케일 여부는 `target_type`으로 제어하되, **거래량 covariate**는 항상 스케일된 데이터를 사용합니다.
    * 분할 결과의 길이와 일부 내용을 `mylogger.debug()`로 남겨
      데이터 누락·분할 오류를 쉽게 확인할 수 있습니다.

    Raises
    ------
    ValueError
        `target_type`이 `'raw'  / 'scaled'` 외의 값일 경우 예외를 발생시킵니다.
    """
    target_series = series_scaler.get('target_series')
    target_scaled = series_scaler.get('target_scaled')
    volume_scaled = series_scaler.get('volume_scaled')
    if target_type == 'raw':
        target_train, target_val = target_series.split_before(0.9)
        volume_train, volume_val = volume_scaled.split_before(0.9)
    elif target_type == 'scaled':
        target_train, target_val = target_scaled.split_before(0.9)
        volume_train, volume_val = volume_scaled.split_before(0.9)
    else:
        raise ValueError(f"'{target_type}' 오류")

    mylogger.debug(f"target_train / target_val: {len(target_train)} / {len(target_val)}")
    mylogger.debug(f"target_train: {target_train}")
    mylogger.debug(f"target_val: {target_val}")
    mylogger.debug(f"volume_train / volume_val: {len(volume_train)} / {len(volume_val)}")
    mylogger.debug(f"volume_train: {volume_train}")
    mylogger.debug(f"volume_val: {volume_val}")

    return {
        'target_train': target_train,
        'volume_train': volume_train,
        'target_val': target_val,
        'volume_val': volume_val,
    }


def latest_vs_first_bounds(
    df: pd.DataFrame,
    *,
    y_col: str = "actual",
    lo_col: str = "lower",
    up_col: str = "upper",
    ndigits: int = 4,
    eps: float = 1e-9,
) -> float | None:
    """
    - 반환 값 해석
        0      → 구간 안
        >0     → upper 초과 (양수, 비율만큼 커짐)
        <0     → lower 초과 (음수, 절댓값이 비율)
        None   → 계산 불가
    """
    # ① 필요한 값 추출
    y_series  = df[y_col].dropna()
    lo_series = df[lo_col].dropna()
    up_series = df[up_col].dropna()

    if y_series.empty or lo_series.empty or up_series.empty:
        return None

    y  = y_series.iloc[-1]   # 가장 최근 actual
    lo = lo_series.iloc[0]   # 예측 구간 첫 하단
    up = up_series.iloc[0]   # 예측 구간 첫 상단

    # ② 정규화 점수 (부호 포함)
    width = max(up - lo, eps)
    if y > up:
        score = (y - up) / width        # 양수
    elif y < lo:
        score = -(lo - y) / width       # 음수
    else:
        score = 0.0

    return round(score, ndigits)


@redis_cached(prefix='nbeats')
def nbeats_forecast(ticker: str, refresh: bool = False, cache_only: bool = True) -> dict | None:
    """
    N-Beats 모델로 지정 종목의 시계열을 예측하고, 결과를 직렬화-친화적인
    ``dict`` 형식으로 반환한다.
    캐시는 함수 첫 번째 인자인 ``ticker``(소문자) 를 키로 사용하며,
    `@redis_cached` 데코레이터 덕분에 다음 흐름으로 동작한다.

    1. **캐시 조회**
       - ``refresh=False``(기본)일 때 Redis에 ``nbeats:{ticker}`` 키가
         존재하면 즉시 반환한다.
    2. **모델 실행**
       - 캐시가 없거나 ``refresh=True``이면
         (1) 원시 데이터 로드 → (2) 전처리/스케일링 →
         (3) N-Beats 학습·예측 → (4) 추세·이상치 계산을 수행한다.
    3. **캐시 저장**
       - 실행 결과를 JSON 직렬화해 TTL(기본 12 h)로 Redis에
         ``SETEX`` 한다.
    4. **cache_only 모드**
       - ``cache_only=True``이면 캐시 미스 시 모델을 돌리지 않고
         ``None`` 을 바로 반환한다.

    Parameters
    ----------
    ticker : str
        종목 티커. e.g. ``"005930.KS"``
        (캐시 키: ``nbeats:005930.ks``)
    refresh : bool, default ``False``
        ``True``  → 캐시를 무시하고 새로 계산 후 캐시 갱신
        ``False`` → 캐시가 있으면 사용
    cache_only : bool, default ``True``
        ``True``  → 캐시가 없으면 계산하지 않고 ``None`` 반환
        ``False`` → 캐시가 없으면 계산 후 저장

    Returns
    -------
    dict | None
        ========  ===================================================================
        Key       설명
        --------  -------------------------------------------------------------------
        ds        ``List[str]``  — 날짜(YYYY-MM-DD)
        actual    ``List[float|None]`` — 실제 값
        forecast  ``List[float|None]`` — 예측 평균
        lower     ``List[float|None]`` — 95 % 하단
        upper     ``List[float|None]`` — 95 % 상단
        trend     ``"상승" | "하락" | "횡보" | "미정"` — 최신 추세 판단
        anomaly_score  ``float`` — 마지막 구간의 이상 점수
        ========  ===================================================================
        캐시만 조회했고 미스가 발생한 경우( ``cache_only=True`` )에는 ``None``.

    Examples
    --------
    >>> nbeats_forecast("005930.KS", cache_only=False)
    {'ds': [...], 'actual': [...], 'forecast': [...], ...}

    >>> # 캐시 값만 필요할 때
    >>> nbeats_forecast("005930.KS")          # hit → dict
    >>> nbeats_forecast("005930.KS", refresh=True)  # 강제 재계산

    Notes
    -----
    - 모델 학습·예측은 CPU/GPU 자원이 크게 들 수 있으므로,
      가능한 한 ``cache_only=True`` 를 활용해 캐시 히트를 우선 탐색한다.
    """
    # ─────────────────────────────
    # 1) 예측 수행 (기존 코드 그대로)
    # ─────────────────────────────
    df = get_raw_data(ticker)
    series_scaler = prepare_data(df)
    train_val_dict = prepare_train_val_series('scaled', series_scaler)

    from analyser2_hj3415.tsseer.models.nbeats import train_and_forecast
    ts_dict = train_and_forecast(series_scaler, train_val_dict)

    if ts_dict is None:
        return None

    actual_ts = ts_dict['actual_ts']
    fcst_mean_ts = ts_dict['fcst_mean_ts']
    lower_ts = ts_dict['lower_ts']
    upper_ts = ts_dict['upper_ts']

    # ─────────────────────────────
    # 2) TimeSeries → DataFrame
    # ─────────────────────────────
    def _to_df(ts, name):
        df = ts.to_dataframe(copy=False)
        df.columns = [name]
        return df

    actual_df = _to_df(actual_ts, 'actual')
    fcst_df   = _to_df(fcst_mean_ts, 'forecast')
    lower_df  = _to_df(lower_ts, 'lower')
    upper_df  = _to_df(upper_ts, 'upper')

    merged = (
        actual_df
        .join([fcst_df, lower_df, upper_df], how="outer")
        .sort_index()
        .round(2)
        .where(lambda x: ~x.isna())  # NaN → None 직렬화 대비
    )

    # ─────────────────────────────
    # 3) 추세 판단 ⬅️ 여기만 새로 추가
    # ─────────────────────────────
    import numpy as np
    fcst_values = np.array([v for v in merged['forecast'].tolist() if v is not None])
    trend = judge_trend(fcst_values)  # 상승·하락·횡보 미정

    # 3-1) anomaly score 계산
    anomaly = latest_vs_first_bounds(merged, y_col='actual', lo_col='lower', up_col='upper')

    # ─────────────────────────────
    # 4) 직렬화-friendly dict 반환
    # ─────────────────────────────
    return {
        "ds": merged.index.strftime("%Y-%m-%d").tolist(),
        "actual": merged["actual"].tolist(),
        "forecast": merged["forecast"].tolist(),
        "lower": merged["lower"].tolist(),
        "upper": merged["upper"].tolist(),
        "trend": trend,
        "anomaly_score": anomaly
    }


@redis_async_cached(prefix="nbeats_trend")
async def filter_nbeats_by_trend_and_anomaly(tickers: list[str], trend: Literal["상승", "하락"],
                                              refresh: bool = False, cache_only: bool = False) -> list[dict]:
    """
    Redis에 저장된 NBEATS 결과(추세 · 이상치)를 조회해 조건에 맞는 종목만 선별하고,
    이상치의 **절대값(|anomaly_score|)**이 큰 순으로 정렬해 반환합니다.

    이 함수는 `@redis_async_cached(prefix="nbeats_trend")` 데코레이터로 캐싱됩니다.
    - 캐시 키: 데코레이터의 key_factory 기본 규칙(함수명/인자 기반) + prefix "nbeats_trend"
    - 호출 시 `refresh=True`로 전달하면 캐시를 무시하고 재계산 후 캐시를 갱신합니다.
    - `cache_only=True`이면 캐시 미스 시 원본 실행을 생략하고 데코레이터의 `default_if_miss`를 반환합니다.
    - `cache_ttl=<int|timedelta>`로 이 호출에 한해 TTL을 덮어쓸 수 있습니다(데코레이터의 `ttl_kwarg` 기본값).

    동작
    ----
    1) 각 `ticker`에 대해 Redis 키 `"nbeats:{ticker.lower()}"`를 조회(mget)하여 JSON payload를 파싱합니다.
    2) 요청한 `trend`(상승/하락)과 payload의 `trend`가 일치하는 항목만 남깁니다.
    3) `anomaly_score`가 존재하는 항목만 고려합니다.
    4) 선택 기준(임계값):
       - trend가 "상승"인 경우: `anomaly_score <= -0.01`
       - trend가 "하락"인 경우: `anomaly_score >= 0.01`
    5) 최종 리스트를 `abs(anomaly_score)` 기준 **내림차순**으로 정렬해 반환합니다.

    Parameters
    ----------
    tickers : list[str]
        조회할 종목 코드 목록. Redis 키는 `nbeats:{ticker.lower()}` 형식으로 접근합니다.
    trend : Literal["상승", "하락"]
        필터링 기준이 되는 추세.
    refresh : bool, default False
        캐시 무시 후 재계산을 강제합니다. (데코레이터가 해석하는 특수 인자)
    cache_only : bool, default False
        캐시 미스 시 원본 실행 없이 `default_if_miss`를 반환합니다. (데코레이터 특수 인자)

    Returns
    -------
    list[dict]
        조건에 부합하는 항목의 리스트.
        각 항목은 `{"ticker": str, "trend": str, "anomaly_score": float}` 형태이며,
        리스트는 `|anomaly_score|`가 큰 순으로 정렬되어 있습니다.

    Notes
    -----
    - Redis 값은 JSON 문자열이어야 하며, 파싱 실패/필드 누락 시 해당 종목은 건너뜁니다.
    - 내부적으로 `mget`을 사용하여 네트워크 왕복을 최소화합니다.
    - 캐싱 TTL, 지터(jitter) 등은 데코레이터 인자로 제어합니다(`ttl`, `jitter`, `cache_ttl` 등).

    Examples
    --------
    >>> await filter_nbeats_by_trend_and_anomaly(["005930", "000660"], "상승")
    [
        {"ticker": "000660", "trend": "상승", "anomaly_score": -0.08},
        {"ticker": "005930", "trend": "상승", "anomaly_score": -0.02},
    ]

    >>> await filter_nbeats_by_trend_and_anomaly(["035420"], "하락", refresh=True, cache_ttl=600)
    [{"ticker": "035420", "trend": "하락", "anomaly_score": 0.05}]
    """

    r = get_redis_client_async()

    keys   = [f"nbeats:{t.lower()}" for t in tickers]
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




BulkRow = tuple[str, dict[str, Any] | None]

async def bulk_get_nbeats_cache(tickers: list[str]) -> list[BulkRow]:
    """
    주어진 종목 리스트(tickers)에 대해 Redis에서 nbeats 캐시를 일괄 조회합니다.

    각 종목코드는 "nbeats:{ticker}" 형식의 Redis 키로 변환되어 조회되며,
    Redis에 해당 키가 없으면 결과는 None으로 처리됩니다.

    Parameters:
        tickers (list[str]): 조회할 종목코드 리스트 (예: ["005930", "000660", ...])

    Returns:
        list[BulkRow]: 각 종목에 대한 (ticker, 캐시 데이터) 튜플 리스트.
                       - 캐시 데이터는 JSON 파싱된 dict 또는 None.
                       - 예: [("005930", {...}), ("000660", None), ...]

    Example:
        >>> bulk_get_nbeats_cache(["005930", "000660"])
        [('005930', {'trend': '상승', ...}), ('000660', None)]
    """
    r = get_redis_client_async()

    keys   = [f"nbeats:{t.lower()}" for t in tickers]
    values = await r.mget(keys)

    rows: list[BulkRow] = []
    for tck, raw in zip(tickers, values):
        payload: dict | None = json.loads(raw) if raw else None
        rows.append((tck, payload))
    return rows























# 신뢰구간을 나타낼수 없어서 mydarts의 prophet을 사용하지않고 직접 prophet을 설치해서 사용한다.
# 즉 이 함수를 사용하지 않는다.
def run_prophet_forecast(ticker: str):
    df = get_raw_data(ticker)
    series_scaler_dict = prepare_data(df)
    train_val_dict = prepare_train_val_series('raw', series_scaler_dict)

    from analyser2_hj3415.tsseer.models.prophet import train_and_forecast
    forecast_series = train_and_forecast(train_val_dict)

    return timeseries_to_dataframe(forecast_series)

