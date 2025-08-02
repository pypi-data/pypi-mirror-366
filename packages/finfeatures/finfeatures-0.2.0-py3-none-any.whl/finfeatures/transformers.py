import pandas as pd
import numpy as np
from typing import Optional
from .utils import validate_inputs, validate_window

def rolling_volatility(df: pd.DataFrame, column: str, window: int, annualize: bool = False, trading_days: int = 252, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate rolling volatility for a given column.
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    validate_window(window, 2)
    
    returns = df[column].pct_change()
    volatility = returns.rolling(window=window).std()
    
    if annualize:
        volatility = volatility * np.sqrt(trading_days)
        col_name = f'{column}_AnnualizedVol_{window}'
    else:
        col_name = f'{column}_RollingVol_{window}'
    
    df[col_name] = volatility
    
    return df

def percent_change(df: pd.DataFrame, column: str, periods: int = 1, method: str = 'simple', inplace: bool = False) -> pd.DataFrame:
    """
    Calculate percentage change for a given column.
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    
    if method not in ['simple', 'log']:
        raise ValueError("Method must be either 'simple' or 'log'")
    
    if method == 'simple':
        df[f'{column}_PctChange_{periods}'] = df[column].pct_change(periods=periods)
    elif method == 'log':
        df[f'{column}_LogReturn_{periods}'] = np.log(df[column] / df[column].shift(periods))
    
    return df

def rolling_correlation(df: pd.DataFrame, column1: str, column2: str, window: int, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate rolling correlation between two columns.
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column1)
    validate_inputs(df, column2)
    validate_window(window, 2)
    
    df[f'{column1}_{column2}_Corr_{window}'] = df[column1].rolling(window=window).corr(df[column2])
    
    return df

def rolling_beta(df: pd.DataFrame, asset_col: str, market_col: str, window: int, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate rolling beta between an asset and market.
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, asset_col)
    validate_inputs(df, market_col)
    validate_window(window, 2)
    
    asset_returns = df[asset_col].pct_change()
    market_returns = df[market_col].pct_change()
    
    covariance = asset_returns.rolling(window=window).cov(market_returns)
    market_variance = market_returns.rolling(window=window).var()
    
    df[f'{asset_col}_Beta_{window}'] = covariance / market_variance
    
    return df

def z_score(df: pd.DataFrame, column: str, window: int, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate rolling z-score for a given column.
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    validate_window(window, 2)
    
    rolling_mean = df[column].rolling(window=window).mean()
    rolling_std = df[column].rolling(window=window).std()
    
    df[f'{column}_ZScore_{window}'] = (df[column] - rolling_mean) / rolling_std
    
    return df

def rolling_skewness(df: pd.DataFrame, column: str, window: int, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate rolling skewness for a given column.
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    validate_window(window, 3)
    
    df[f'{column}_Skewness_{window}'] = df[column].rolling(window=window).skew()
    
    return df

def rolling_kurtosis(df: pd.DataFrame, column: str, window: int, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate rolling kurtosis for a given column.
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    validate_window(window, 4)
    
    df[f'{column}_Kurtosis_{window}'] = df[column].rolling(window=window).kurt()
    
    return df

def price_normalization(df: pd.DataFrame, column: str, method: str = 'minmax', window: Optional[int] = None, inplace: bool = False) -> pd.DataFrame:
    """
    Normalize price data using various methods.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing financial data
    column : str
        Column name to normalize
    method : str, default 'minmax'
        Normalization method ('minmax', 'zscore', 'robust')
    window : int, optional
        Rolling window for normalization (if None, use entire series)
    inplace : bool, default False
        If True, modify the original DataFrame
        
    Returns
    -------
    pd.DataFrame
        DataFrame with added normalized column
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    
    if method not in ['minmax', 'zscore', 'robust']:
        raise ValueError("Method must be 'minmax', 'zscore', or 'robust'")
    
    if window is not None:
        validate_window(window, 2)
    
    if method == 'minmax':
        if window:
            rolling_min = df[column].rolling(window=window).min()
            rolling_max = df[column].rolling(window=window).max()
            df[f'{column}_MinMaxNorm_{window}'] = (df[column] - rolling_min) / (rolling_max - rolling_min)
        else:
            min_val = float(df[column].min())
            max_val = float(df[column].max())
            df[f'{column}_MinMaxNorm'] = (df[column] - min_val) / (max_val - min_val)
    
    elif method == 'zscore':
        if window:
            rolling_mean = df[column].rolling(window=window).mean()
            rolling_std = df[column].rolling(window=window).std()
            df[f'{column}_ZScoreNorm_{window}'] = (df[column] - rolling_mean) / rolling_std
        else:
            mean_val = float(df[column].mean())
            std_val = float(df[column].std())
            df[f'{column}_ZScoreNorm'] = (df[column] - mean_val) / std_val
    
    elif method == 'robust':
        if window:
            rolling_median = df[column].rolling(window=window).median()
            rolling_mad = df[column].rolling(window=window).apply(lambda x: np.median(np.abs(x - np.median(x))))
            df[f'{column}_RobustNorm_{window}'] = (df[column] - rolling_median) / rolling_mad
        else:
            median_val = float(df[column].median())
            mad_val = float(np.median(np.abs(df[column] - median_val)))
            # Handle case where MAD is zero (all values are the same)
            if mad_val == 0:
                df[f'{column}_RobustNorm'] = 0.0
            else:
                df[f'{column}_RobustNorm'] = (df[column] - median_val) / mad_val
    
    return df
    """
    Normalize price data using various methods.
    """
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    
    if method not in ['minmax', 'zscore', 'robust']:
        raise ValueError("Method must be 'minmax', 'zscore', or 'robust'")
    
    if window is not None:
        validate_window(window, 2)
    
    if method == 'minmax':
        if window:
            rolling_min = df[column].rolling(window=window).min()
            rolling_max = df[column].rolling(window=window).max()
            df[f'{column}_MinMaxNorm_{window}'] = (df[column] - rolling_min) / (rolling_max - rolling_min)
        else:
            df[f'{column}_MinMaxNorm'] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
    
    elif method == 'zscore':
        if window:
            rolling_mean = df[column].rolling(window=window).mean()
            rolling_std = df[column].rolling(window=window).std()
            df[f'{column}_ZScoreNorm_{window}'] = (df[column] - rolling_mean) / rolling_std
        else:
            df[f'{column}_ZScoreNorm'] = (df[column] - df[column].mean()) / df[column].std()
    
    elif method == 'robust':
        if window:
            rolling_median = df[column].rolling(window=window).median()
            rolling_mad = df[column].rolling(window=window).apply(lambda x: np.median(np.abs(x - np.median(x))))
            df[f'{column}_RobustNorm_{window}'] = (df[column] - rolling_median) / rolling_mad
        else:
            median = df[column].median()
            mad = np.median(np.abs(df[column] - median))
            df[f'{column}_RobustNorm'] = (df[column] - median) / mad
    
    return df
