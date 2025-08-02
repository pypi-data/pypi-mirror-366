from typing import Dict, Union, Callable
from functools import reduce
import itertools
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
import finlab.ml.feature as feature
import finlab.ml.label as label
from finlab.dataframe import FinlabDataFrame

logger = logging.getLogger(__name__)

try:
    from sklearn.decomposition import PCA
    from sklearn.metrics import ndcg_score
except ImportError:
    logger.warning("sklearn is not installed, calc_centrality will not be available")
    PCA = None
    ndcg_score = None



def is_boolean_series(series: pd.Series) -> bool:
    """
    Check if a pandas Series contains boolean values, handling NaN values.
    
    In older pandas versions, boolean Series with NaN values get converted to float dtype.
    This function detects such cases by checking if the non-NaN values are boolean.
    
    Args:
        series (pd.Series): The Series to check
        
    Returns:
        bool: True if the Series contains boolean values (including NaN), False otherwise
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Pure boolean
        >>> s1 = pd.Series([True, False, True])
        >>> is_boolean_series(s1)  # True
        >>> 
        >>> # Boolean with NaN (becomes float in old pandas)
        >>> s2 = pd.Series([True, False, np.nan])
        >>> is_boolean_series(s2)  # True
        >>> 
        >>> # Non-boolean
        >>> s3 = pd.Series([1, 2, 3])
        >>> is_boolean_series(s3)  # False
    """
    # Check if it's already boolean dtype
    if series.dtype == bool:
        return True
    
    # Check if it's float dtype (which could be boolean with NaN)
    else:
        # Get non-NaN values
        non_nan_values = series.dropna()
        if len(non_nan_values) == 0:
            # All NaN - could be boolean
            return True
        
        # Check if non-NaN values are boolean
        return non_nan_values.isin([True, False, 0, 1]).all()
    
    return False

def corr(df):
    ret = df.corr().iloc[0, 1]
    return ret

def ndcg_k(k):
    def ndcg(df):
        s1 = (np.reshape(df.iloc[:,0].rank().values, (-1, len(df))))
        s2 = (np.reshape(df.iloc[:,1].rank().values, (-1, len(df))))
        if ndcg_score is None:
            raise ImportError("sklearn is not installed, ndcg_score will not be available")
        return ndcg_score(s1, s2, k=k)
    return ndcg

ndcg20 = ndcg_k(20)
ndcg50 = ndcg_k(50)

def precision_at_rank(k):

    def ret(df):

        y_true = df.iloc[:, 0]
        y_score = df.iloc[:, 1]
        assert (k >= 0) & (k <= 1)
        # Get the indices of the top k scores
        selected = y_score.rank(pct=True) > k
        return y_true.rank(pct=True)[selected.values].mean()
        
    return ret


def calc_metric(factor, adj_close, days=[10, 20, 60, 120], func=corr):

    """計算因子

    Args:
        factor (pd.DataFrame): 因子
        adj_close (pd.DataFrame): 股價
        days (list, optional): 預測天數. Defaults to [10, 20, 60, 120].
        func (function, optional): 計算函數. Defaults to corr.

    Returns:
        pd.DataFrame: 因子計算結果

    Example:
        >>> factor = data.indicator('RSI')
        >>> adj_close = data.get('etl:adj_close')
        >>> calc_metric(factor, adj_close)

        | date       | factor_10 | factor_20 | factor_60 | factor_120 |
        |------------|-----------|-----------|-----------|------------|
        | 2010-01-01 | 0.1       | 0.2       | 0.3       | 0.4        |
        | 2010-01-02 | 0.1       | 0.2       | 0.3       | 0.4        |
        | 2010-01-03 | 0.1       | 0.2       | 0.3       | 0.4        |
        | 2010-01-04 | 0.1       | 0.2       | 0.3       | 0.4        |
        | 2010-01-05 | 0.1       | 0.2       | 0.3       | 0.4        |
    """

    if isinstance(factor, pd.DataFrame):
        factor = {'factor': factor}

    for fname, f in factor.items():
        factor[fname] = FinlabDataFrame(f).index_str_to_date()

    ics = {}

    total = len(days) * len(factor)
    with tqdm(total=total, desc="Processing") as pbar:
        for d in days:
            ret = adj_close.shift(-d-1) / adj_close.shift(-1) - 1

            for fname, f in factor.items():
                inter_col = f.columns.intersection(adj_close.columns)
                inter_index = f.index.intersection(adj_close.index)

                # Use reindex to avoid type issues with loc
                f_subset = f.reindex(index=inter_index, columns=inter_col)
                ret_subset = ret.reindex(index=inter_index, columns=inter_col)
                
                funstack = f_subset.unstack()
                ret_unstack = ret_subset.unstack()


                ics[f"{fname}_{d}"] = pd.DataFrame({
                    'ret': ret_unstack.values,
                    'f': funstack.values,
                }, index=funstack.index).dropna().groupby(level='date').apply(func)
                pbar.update(1)

    return pd.concat(ics, axis=1)


def ic(factor, adj_close, days=[10, 20, 60, 120]):
    """計算因子的IC

    Args:
        factor (pd.DataFrame): 因子
        adj_close (pd.DataFrame): 股價
        days (list, optional): 預測天數. Defaults to [10, 20, 60, 120].


    Returns:
        pd.DataFrame: 因子計算結果

    Example:
        >>> factor = data.indicator('RSI')
        >>> adj_close = data.get('etl:adj_close')
        >>> calc_metric(factor, adj_close)

        | date       | factor_10 | factor_20 | factor_60 | factor_120 |
        |------------|-----------|-----------|-----------|------------|
        | 2010-01-01 | 0.1       | 0.2       | 0.3       | 0.4        |
        | 2010-01-02 | 0.1       | 0.2       | 0.3       | 0.4        |
        | 2010-01-03 | 0.1       | 0.2       | 0.3       | 0.4        |
        | 2010-01-04 | 0.1       | 0.2       | 0.3       | 0.4        |
        | 2010-01-05 | 0.1       | 0.2       | 0.3       | 0.4        |
    """
    return calc_metric(factor, adj_close, days=days, func=corr)


def generate_features_and_labels(
    dfs: Dict[str, Union[pd.DataFrame, Callable]], 
    resample: str
) -> tuple[pd.DataFrame, pd.Series]:
    """
    生成因子特徵和標籤，這是因子分析的核心步驟。

    此函式封裝了因子分析中特徵和標籤生成的標準流程：
    1. 使用 `finlab.ml.feature.combine` 將因子字典轉換為特徵 DataFrame
    2. 使用 `finlab.ml.label.excess_over_mean` 生成超額報酬標籤

    Args:
        dfs (Dict[str, Union[pd.DataFrame, Callable]]):
            因子字典，包含因子名稱和對應的因子數據或計算函式。
            
            - Key (str): 因子名稱，將成為輸出 DataFrame 的欄位名
            - Value (Union[pd.DataFrame, Callable]): 因子數據或計算函式
                - pd.DataFrame: 直接提供的因子數據
                - Callable: 計算因子的函式，將被調用以獲取因子數據
            
            此為 `finlab.ml.feature.combine` 的標準輸入格式。
        resample (str):
            重採樣頻率，用於特徵和標籤的生成。
            
            例如: 'M' (月度), 'Q' (季度), 'Y' (年度)

    Returns:
        tuple[pd.DataFrame, pd.Series]: 
            - pd.DataFrame: 特徵 DataFrame，索引為日期，欄位為因子名稱
            - pd.Series: 標籤 Series，索引為日期，值為超額報酬

    Raises:
        ValueError: 如果輸入的因子字典為空或無效。

    Example:
        >>> from finlab import data
        >>> from finlab.tools.factor_analysis import generate_features_and_labels
        >>> 
        >>> price = data.get('etl:adj_close')
        >>> marketcap = data.get('etl:market_value')
        >>> revenue = data.get('monthly_revenue:當月營收')
        >>> 
        >>> features, labels = generate_features_and_labels({
        ...     'marketcap': marketcap.rank(pct=True, axis=1) < 0.3,
        ...     'revenue': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
        ...     'momentum': price / price.shift(20) - 1 > 0
        ... }, resample=revenue.index)
        >>> 
        >>> print(f"Features shape: {features.shape}")
        >>> print(f"Labels shape: {labels.shape}")
        Features shape: (120, 3)
        Labels shape: (120,)
    """
    # 生成特徵和標籤
    features = feature.combine(dfs, resample=resample)
    labels: pd.Series = label.excess_over_mean(index=features.index, resample=resample)
    
    return features, labels


def calc_factor_return(
    features: pd.DataFrame,
    labels: pd.Series
) -> pd.DataFrame:
    """
    計算基於特徵和標籤的等權重投資組合週期表現。

    此函式是因子績效計算的核心引擎，接受預先準備好的特徵和標籤，
    然後計算每個因子的投資組合報酬。

    函式會自動處理以下流程：
    1. 驗證所有特徵都是布林值
    2. 對每個因子計算等權重投資組合的週期報酬
    3. 自動裁剪掉第一個非空行之前的數據

    Args:
        features (pd.DataFrame):
            特徵 DataFrame，索引為日期，欄位為因子名稱，值應為布林值。
        labels (pd.Series):
            標籤 Series，索引為日期，值為超額報酬。

    Returns:
        pd.DataFrame: 一個索引為日期、欄位為各因子名稱的 DataFrame，其值為每個週期的等權重投組表現。
                     輸出會自動從第一個非空行開始，確保數據完整性。

    Raises:
        ValueError: 如果特徵不是布林值。

    Example:
        >>> from finlab import data
        >>> from finlab.tools.factor_analysis import calc_factor_return, generate_features_and_labels
        >>> 
        >>> price = data.get('etl:adj_close')
        >>> marketcap = data.get('etl:market_value')
        >>> revenue = data.get('monthly_revenue:當月營收')
        >>> 
        >>> # 先生成特徵和標籤
        >>> features, labels = generate_features_and_labels({
        ...     'marketcap': marketcap.rank(pct=True, axis=1) < 0.3,
        ...     'revenue': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
        ...     'momentum': price / price.shift(20) - 1 > 0
        ... }, resample=revenue.index)
        >>> 
        >>> # 計算因子報酬
        >>> factor_return = calc_factor_return(features, labels)
        >>> 
        >>> # 輸出範例
        >>> print(factor_return.head())
        | datetime            |   marketcap |     revenue |    momentum |
        |:--------------------|------------:|------------:|------------:|
        | 2013-04-30 00:00:00 |  0.018      | -0.005      |  0.009      |
        | 2013-05-31 00:00:00 |  0.004      | -0.003      | -0.001      |
        | 2013-06-30 00:00:00 | -0.013      | -0.006      |  0.023      |
        | 2013-07-31 00:00:00 |  0.007      | -0.007      |  0.001      |
        | 2013-08-31 00:00:00 |  0.014      | -0.003      | -0.005      |
    """

    # check if all feathres is boolean
    for f in features.columns:
        if not is_boolean_series(features[f]):
            raise ValueError(f"Feature {f} is not a boolean")

    def _factor_return(f: pd.Series) -> pd.Series:
        """計算單一因子的投資組合報酬"""
        return labels.mask(f != True).groupby(level=0).mean()
    
    # 對每個因子計算報酬
    factor_return = features.apply(_factor_return)

    # 裁剪時間：從第一個非空行開始
    first_nonan = factor_return.notna().all(axis=1).pipe(lambda s: s[s]).index[0]
    
    return factor_return.loc[first_nonan:]


def _calc_centrality_for_window(window_data: pd.DataFrame, n_components: int) -> pd.Series:
    """
    使用 PCA 計算單一數據窗口內各資產的集中度(Centrality)。
    這是 asset_concentration 的核心輔助函式。

    集中度 C(i) 的計算公式是一個加權平均值，其物理意義為「一個資產在所有主成分中的加權平均相對影響力」。
    公式參照學術文獻，結構如下:
        C_i = sum_{j=1 to N} (AR_j * RelativeInfluence_ij) / sum_{j=1 to N} AR_j

    其中:
    - C_i: 資產 i 的集中度分數。
    - N: 主成分數量 (n_components)。
    - AR_j: 第 j 個主成分的吸收率 (Absorption Ratio)，代表該主成分解釋的變異數佔總變異數的比例。
    - RelativeInfluence_ij: 資產 i 在第 j 個主成分中的「相對影響力」。
      其計算方式為: |w_ij| / (sum_{k=1 to M} |w_kj|)
      - w_ij: 資產 i 在第 j 個主成分的特徵向量(eigenvector)中的權重。
      - M: 資產總數。
      這個正規化步驟計算了資產 i 的權重在該主成分所有資產權重總和中的佔比。

    Args:
        window_data (pd.DataFrame): 一個時間窗口內的因子投組日報酬數據。行為日期，列為因子名稱。
        n_components (int): 用於計算的 PCA 主成分數量。

    Returns:
        pd.Series: 包含該窗口內每個因子(資產)集中度分數的 Series。

    Example:
        A Series where index is the factor name and values are centrality scores.

        盈利      0.1
        營收      0.2
        市值      0.3
    """
    if window_data.empty or window_data.shape[1] < n_components:
        return pd.Series(dtype=np.float64)

    clean_data = window_data.dropna()
    
    if len(clean_data) <= n_components or clean_data.shape[1] < n_components:
        return pd.Series(np.nan, index=window_data.columns)

    try:
        # --- 核心計算 ---
        # 步驟 1: 擬合 PCA 模型
        if PCA is None:
            raise ImportError("sklearn is not installed, calc_centrality will not be available")
        
        pca = PCA(n_components=min(n_components, clean_data.shape[1]))
        pca.fit(clean_data)
        
        # 步驟 2: 計算吸收率 (Absorption Ratio, AR_j)
        cov_matrix = clean_data.cov()
        total_variance = np.sum(np.diag(cov_matrix))
        if total_variance == 0:
            return pd.Series(np.nan, index=window_data.columns)

        absorption_ratio = pca.explained_variance_ / total_variance # AR_j

        # 步驟 3: 計算歸一化的特徵向量權重 (w_ij)
        eigenvectors = pca.components_ # 原始特徵向量 (EV_ij)
        abs_eigenvectors = np.abs(eigenvectors)

        sum_of_abs_eigenvectors = np.sum(abs_eigenvectors, axis=1, keepdims=True)
        sum_of_abs_eigenvectors[sum_of_abs_eigenvectors == 0] = 1.0
        # 歸一化權重 w_ij
        normalized_abs_ev = abs_eigenvectors / sum_of_abs_eigenvectors

        # 步驟 4: 根據公式計算中心性
        # 分子: sum(AR_j * w_ij)
        numerator = (absorption_ratio[:, np.newaxis] * normalized_abs_ev).sum(axis=0)
        
        # 分母: sum(AR_j)
        denominator = np.sum(absorption_ratio)
        
        with np.errstate(divide='ignore', invalid='ignore'):
            centrality_values = numerator / denominator
        
        result = pd.Series(centrality_values, index=clean_data.columns)
        result.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        return result.reindex(window_data.columns)
        
    except Exception as e:
        logger.warning(f"Centrality (集中度) calculation failed for a window: {e}")
        return pd.Series(np.nan, index=window_data.columns)


def calc_centrality(
    return_df: pd.DataFrame,
    window_periods: int,
    n_components: int = 1
) -> pd.DataFrame:
    """
    對指定的時間序列數據計算滾動資產集中度。

    此函式為通用函式，可應用於任何以時間為索引、資產為欄位的 DataFrame(例如因子報酬)。
    它現在是頻率無關的，滾動窗口由整數 `window_periods` 指定。

    Args:
        return_df (pd.DataFrame): 
            一個時間序列 DataFrame，索引為日期，欄位為資產(例如因子名稱)。
            雖然參數名稱為 `return_df`，但此函式設計上可接受任何資產的時間序列數據，例如因子波動率，但就是不能解釋資產集中度了。
        window_periods (int): 
            滾動窗口的長度，以數據點的「數量」計。例如，如果 `return_df` 是月資料，
            `window_periods=3` 就代表使用 3 個月的滾動窗口。
        n_components (int): 
            用於計算的 PCA 主成分數量。

    Returns:
        pd.DataFrame: 包含滾動集中度分數的 DataFrame。

    Example:
        | date        | FactorA      | FactorB      |
        |-------------|--------------|--------------|
        | 2025-01-01  | 0.1          | 0.2          |
        | 2025-01-02  | 0.1          | 0.2          |
        | 2025-01-03  | 0.1          | 0.2          |
        | 2025-01-04  | 0.1          | 0.2          |
        | 2025-01-05  | 0.1          | 0.2          |
    """
    logger.info(f"Calculating rolling centrality with window of {window_periods} periods...")
    
    if return_df.empty or return_df.shape[0] < window_periods:
        logger.warning("Input DataFrame is empty or has fewer rows than the window period. Returning empty DataFrame.")
        return pd.DataFrame(columns=return_df.columns)

    # min_periods 設為窗口的80%，或至少是 n_components + 1，確保有足夠的資料點來計算主成分。
    min_p = max(n_components + 1, int(window_periods * 0.8))
    rolling_obj = return_df.rolling(
        window=window_periods, 
        min_periods=min_p
    )
    
    centrality_results = []
    
    for i, window_data in enumerate(tqdm(rolling_obj, total=len(return_df) - min_p + 1, desc="Rolling Centrality")):
        # 如果滾動窗口的資料點數小於 min_periods，則跳過。
        if window_data.shape[0] < min_p:
            continue
            
        centrality_series = _calc_centrality_for_window(window_data, n_components)
        centrality_series.name = window_data.index[-1] # 使用滾動窗口的最後一個日期作為索引
        centrality_results.append(centrality_series)

    if not centrality_results:
        logger.warning("No centrality results were calculated. The resulting DataFrame will be empty.")
        return pd.DataFrame(columns=return_df.columns, index=pd.to_datetime([]))
    
    centrality_df = pd.concat(centrality_results, axis=1).T
    centrality_df.index.name = 'date'
    logger.info("Rolling centrality calculation complete.")
    return centrality_df


def calc_shapley_values(
    features: pd.DataFrame,
    labels: pd.Series
) -> pd.DataFrame:
    """
    計算因子的 Shapley 值，用於評估每個因子對投資組合表現的邊際貢獻。

    Shapley 值是一種合作博弈論中的概念，用於公平分配聯盟的總收益給各個參與者。
    在因子分析中，我們將每個因子視為一個"參與者"，投資組合的報酬視為"聯盟的總收益"。
    
    計算過程：
    1. 對所有可能的因子組合（從單一因子到全部因子）
    2. 計算每個組合的投資組合報酬
    3. 根據 Shapley 值公式計算每個因子的邊際貢獻

    Args:
        features (pd.DataFrame):
            特徵 DataFrame，索引為日期，欄位為因子名稱，值應為布林值。
            每個因子代表一個投資策略（True 表示選中該股票）。
        labels (pd.Series):
            標籤 Series，索引為日期，值為超額報酬。
            應為 MultiIndex，包含 'datetime' 和 'stock_id' 層級。

    Returns:
        pd.DataFrame: 
            包含每個因子 Shapley 值的 DataFrame。
            索引為日期，欄位為因子名稱，值為該因子的 Shapley 值。

    Raises:
        ValueError: 
            - 如果 features 為空或沒有欄位
            - 如果 labels 的索引不是 MultiIndex
            - 如果 features 不是布林值
            - 如果 features 和 labels 的時間索引不匹配

    Example:
        >>> from finlab import data
        >>> from finlab.tools.factor_analysis import calc_shapley_values, generate_features_and_labels
        >>> 
        >>> price = data.get('etl:adj_close')
        >>> marketcap = data.get('etl:market_value')
        >>> revenue = data.get('monthly_revenue:當月營收')
        >>> 
        >>> # 生成特徵和標籤
        >>> features, labels = generate_features_and_labels({
        ...     'marketcap': marketcap.rank(pct=True, axis=1) < 0.3,
        ...     'revenue': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
        ...     'momentum': price / price.shift(20) - 1 > 0
        ... }, resample=revenue.index)
        >>> 
        >>> # 計算 Shapley 值
        >>> shapley_df = calc_shapley_values(features, labels)
        >>> 
        >>> print(shapley_df.head())
        | datetime            |   marketcap |     revenue |    momentum |
        |:--------------------|------------:|------------:|------------:|
        | 2013-04-30 00:00:00 |  0.012      | -0.003      |  0.006      |
        | 2013-05-31 00:00:00 |  0.002      | -0.001      | -0.001      |
        | 2013-06-30 00:00:00 | -0.008      | -0.004      |  0.015      |
        | 2013-07-31 00:00:00 |  0.004      | -0.004      |  0.001      |
        | 2013-08-31 00:00:00 |  0.009      | -0.002      | -0.003      |

    Note:
        - Shapley 值的計算複雜度為 O(2^n)，其中 n 為因子數量
        - 對於大量因子，計算時間可能較長
        - 建議因子數量不超過 10 個以確保合理的計算時間
    """
    # 輸入驗證
    if features.empty or features.shape[1] == 0:
        raise ValueError("Features DataFrame is empty or has no columns")
    
    if not isinstance(labels.index, pd.MultiIndex):
        raise ValueError("Labels must have MultiIndex with 'datetime' and 'stock_id' levels")
    
    # 檢查 features 是否為布林值
    for col in features.columns:
        if not is_boolean_series(features[col]):
            raise ValueError(f"Feature column '{col}' is not boolean")
    
    # 檢查時間索引匹配
    feature_dates = features.index
    label_dates = labels.index.get_level_values('datetime').unique()
    
    if not feature_dates.equals(label_dates):
        logger.warning("Feature and label date indices do not match exactly")
    
    shapley_values: Dict[str, pd.Series] = {}
    
    total_combinations = sum(len(list(itertools.combinations(features.columns, i))) 
                           for i in range(1, len(features.columns) + 1))
    
    with tqdm(total=total_combinations, desc="Calculating Shapley values") as pbar:
        for i in range(1, len(features.columns) + 1):
            for combo in itertools.combinations(features.columns, i):
                # 使用 reduce 來對所有選中的因子進行 AND 運算
                if i == 1:
                    selected_stocks = features[combo[0]]
                else:
                    selected_stocks = reduce(lambda x, y: x & y, [features[col] for col in combo])
                
                # 獲取日期索引
                dt = labels.index.get_level_values('datetime')
                
                # 計算該組合的投資組合報酬
                v = labels.mask(selected_stocks != True).groupby(dt).mean().fillna(0)
                
                # 將報酬平均分配給該組合中的每個因子
                for col in combo:
                    # 確保時間索引匹配
                    if col in shapley_values:
                        shapley_values[col] += v / len(combo)
                    else:
                        shapley_values[col] = v / len(combo)
                
                pbar.update(1)
    
    return pd.DataFrame(shapley_values)



def calc_ic(features, labels, rank=False):
    """
    計算特徵與標籤之間的相關係數（IC），可選擇是否對特徵進行排名。

    Args:
        features (pd.DataFrame): 特徵資料，索引為MultiIndex（日期, 股票代碼），欄位為因子名稱。
        labels (pd.Series): 標籤資料，索引為MultiIndex（日期, 股票代碼）。
        rank (bool, optional): 是否對特徵進行排名。預設為False。

    Returns:
        pd.DataFrame: 每個日期、每個因子的IC值。
    """
    if rank:
        return features.groupby(level=0).apply(lambda x: x.rank(pct=True).corrwith(labels))

    ret = features.groupby(level=0).apply(lambda x: x.corrwith(labels))
    first_nonan = ret.notna().all(axis=1).pipe(lambda s: s[s]).index[0]
    return ret.loc[first_nonan:]

def calc_regression_stats(
    df: pd.DataFrame,
    p_value_threshold: float = 0.05,
    r_squared_threshold: float = 0.1
) -> pd.DataFrame:
    """
    對 DataFrame 中的每個時間序列進行線性回歸，並回傳原始統計數據。

    此函式使用純 pandas 操作進行向量化計算，不依賴 scipy。

    Args:
        df (pd.DataFrame):
            時間序列 DataFrame，索引為 DatetimeIndex，欄位為不同的指標序列。
        p_value_threshold (float, optional):
            p 值閾值，用於判斷趨勢的統計顯著性。預設為 0.05。
        r_squared_threshold (float, optional):
            R² 閾值，用於判斷趨勢的解釋力。預設為 0.1。

    Returns:
        pd.DataFrame: 線性回歸的統計結果，包含以下欄位：
            - slope: 線性回歸斜率
            - p_value: 斜率的 p 值
            - r_squared: 決定係數 (R²)
            - tail_estimate: 時間序列尾部的估計值
            - trend: 趨勢分類 ("up", "down", "flat")

    Example:
        >>> # 假設 ic_df 是一個包含 IC 時間序列的 DataFrame
        >>> # ic_df = calc_ic(features, labels)
        >>>
        >>> # 1. 計算回歸統計數據
        >>> trend_stats = calc_regression_stats(ic_df)
        >>> print(trend_stats)
        
        >>> # 2. 基於回傳結果進行客製化分析
        >>> # 範例：找出統計顯著 (p-value < 0.05) 且趨勢向上 (slope > 0) 的因子
        >>> significant_up_trend = trend_stats[
        ...     (trend_stats['p_value'] < 0.05) & (trend_stats['slope'] > 0)
        ... ]
        >>> print(significant_up_trend)
        
        >>> # 3. 查看趨勢分類結果
        >>> up_trends = trend_stats[trend_stats['trend'] == 'up']
        >>> down_trends = trend_stats[trend_stats['trend'] == 'down']
        >>> flat_trends = trend_stats[trend_stats['trend'] == 'flat']
    """
    
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be DatetimeIndex for trend analysis")
    
    min_periods = 6
    
    # 過濾有效欄位並準備數據
    # 過濾掉數據點不足的欄位（按列計算非NaN值的數量）
    valid_columns = []
    for col in df.columns:
        non_nan_count = df[col].notna().sum()
        if non_nan_count >= min_periods:
            valid_columns.append(col)
    
    if not valid_columns:
        return pd.DataFrame(columns=['slope', 'p_value', 'r_squared', 'tail_estimate', 'trend'])
    
    df_clean = df[valid_columns].copy()
    
    # 時間序列（相對於第一個觀測點的天數）
    x = (df_clean.index - df_clean.index[0]).days.values.reshape(-1, 1)
    
    # 向量化計算所有統計量
    def calc_stats(series):
        """計算單一序列的線性回歸統計量"""
        y = series.dropna().values
        if len(y) < min_periods:
            return pd.Series([np.nan] * 5, index=['slope', 'intercept', 'r_squared', 'p_value', 'tail_estimate'])
        
        # 對應的時間點
        x_clean = x[:len(y)]
        
        # 線性回歸
        X = np.column_stack([x_clean, np.ones_like(x_clean)])
        try:
            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
            slope, intercept = coeffs[0], coeffs[1]
        except:
            return pd.Series([np.nan] * 5, index=['slope', 'intercept', 'r_squared', 'p_value', 'tail_estimate'])
        
        # 預測值和 R²
        y_pred = slope * x_clean.flatten() + intercept
        r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
        
        # 簡化的 p-value (基於 t-statistic)
        if len(y) > 2:
            mse = np.sum((y - y_pred) ** 2) / (len(y) - 2)
            se_slope = np.sqrt(mse / np.sum((x_clean.flatten() - np.mean(x_clean)) ** 2))
            t_stat = slope / se_slope if se_slope > 0 else 0
            p_value = 2 * (1 - abs(t_stat) / (abs(t_stat) + 1)) if t_stat != 0 else 1
        else:
            p_value = 1.0
        
        # 尾部估計值
        tail_estimate = slope * x[-1] + intercept
        
        return pd.Series([slope, intercept, r_squared, p_value, tail_estimate], 
                        index=['slope', 'intercept', 'r_squared', 'p_value', 'tail_estimate'])
    
    # 應用到所有欄位
    stats_df = df_clean.apply(calc_stats).T
    
    # 添加趨勢分類
    stats_df['trend'] = 'flat'
    significant_mask = (stats_df['p_value'] < p_value_threshold) & (stats_df['r_squared'] > r_squared_threshold)
    stats_df.loc[significant_mask & (stats_df['slope'] > 0), 'trend'] = 'up'
    stats_df.loc[significant_mask & (stats_df['slope'] <= 0), 'trend'] = 'down'
    
    return stats_df