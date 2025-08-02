import pandas as pd
import numpy as np
from typing import Optional, List
from .utils import validate_inputs, validate_window, validate_multiple_columns, FinFeaturesConfig

def simple_moving_average(df: pd.DataFrame, column: str, window: Optional[int] = None, min_periods: Optional[int] = None, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate Simple Moving Average for a given column.
    """
    if window is None:
        window = FinFeaturesConfig.DEFAULT_MA_WINDOW
    
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column, min_length=1)
    validate_window(window, 1)
    
    df[f'{column}_SMA_{window}'] = df[column].rolling(
        window=window, 
        min_periods=min_periods
    ).mean()
    
    return df

def exponential_moving_average(df: pd.DataFrame, column: str, window: Optional[int] = None, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate Exponential Moving Average for a given column.
    """
    if window is None:
        window = FinFeaturesConfig.DEFAULT_MA_WINDOW
    
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    validate_window(window, 1)
    
    df[f'{column}_EMA_{window}'] = df[column].ewm(span=window, adjust=False).mean()
    
    return df

def relative_strength_index(df: pd.DataFrame, column: str, window: Optional[int] = None, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate Relative Strength Index (RSI) for a given column.
    """
    if window is None:
        window = FinFeaturesConfig.DEFAULT_RSI_WINDOW
    
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    validate_window(window, 2)
    
    delta = df[column].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Use Wilder's smoothing (more traditional for RSI)
    alpha = 1.0 / window
    rs = gain.ewm(alpha=alpha, adjust=False).mean() / loss.ewm(alpha=alpha, adjust=False).mean()
    
    df[f'{column}_RSI_{window}'] = 100 - (100 / (1 + rs))
    
    return df

def macd(df: pd.DataFrame, column: str, fast: Optional[int] = None, slow: Optional[int] = None, signal: Optional[int] = None, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence) for a given column.
    """
    if fast is None:
        fast = FinFeaturesConfig.DEFAULT_MACD_FAST
    if slow is None:
        slow = FinFeaturesConfig.DEFAULT_MACD_SLOW
    if signal is None:
        signal = FinFeaturesConfig.DEFAULT_MACD_SIGNAL
    
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    validate_window(fast, 1)
    validate_window(slow, 1)
    validate_window(signal, 1)
    
    if fast >= slow:
        raise ValueError("Fast period must be less than slow period")
    
    ema_fast = df[column].ewm(span=fast, adjust=False).mean()
    ema_slow = df[column].ewm(span=slow, adjust=False).mean()
    
    df[f'{column}_MACD'] = ema_fast - ema_slow
    df[f'{column}_MACD_Signal'] = df[f'{column}_MACD'].ewm(span=signal, adjust=False).mean()
    df[f'{column}_MACD_Histogram'] = df[f'{column}_MACD'] - df[f'{column}_MACD_Signal']
    
    return df

def bollinger_bands(df: pd.DataFrame, column: str, window: Optional[int] = None, num_std: Optional[int] = None, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate Bollinger Bands for a given column.
    """
    if window is None:
        window = FinFeaturesConfig.DEFAULT_MA_WINDOW
    if num_std is None:
        num_std = FinFeaturesConfig.DEFAULT_BB_STD
    
    if not inplace:
        df = df.copy()
    
    validate_inputs(df, column)
    validate_window(window, 2)
    
    rolling_mean = df[column].rolling(window).mean()
    rolling_std = df[column].rolling(window).std()
    
    df[f'{column}_BB_Middle'] = rolling_mean
    df[f'{column}_BB_Upper'] = rolling_mean + (rolling_std * num_std)
    df[f'{column}_BB_Lower'] = rolling_mean - (rolling_std * num_std)
    df[f'{column}_BB_Width'] = df[f'{column}_BB_Upper'] - df[f'{column}_BB_Lower']
    df[f'{column}_BB_Position'] = (df[column] - df[f'{column}_BB_Lower']) / df[f'{column}_BB_Width']
    
    return df

def average_true_range(df: pd.DataFrame, high_col: str, low_col: str, close_col: str, window: Optional[int] = None, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate Average True Range (ATR) for given OHLC columns.
    """
    if window is None:
        window = FinFeaturesConfig.DEFAULT_ATR_WINDOW
    
    if not inplace:
        df = df.copy()
    
    validate_multiple_columns(df, [high_col, low_col, close_col])
    validate_window(window, 1)
    
    high_low = df[high_col] - df[low_col]
    high_close = (df[high_col] - df[close_col].shift()).abs()
    low_close = (df[low_col] - df[close_col].shift()).abs()
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df[f'ATR_{window}'] = tr.rolling(window=window).mean()
    
    return df

def stochastic_oscillator(df: pd.DataFrame, high_col: str, low_col: str, close_col: str, k_window: Optional[int] = None, d_window: int = 3, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate Stochastic Oscillator for given OHLC columns.
    """
    if k_window is None:
        k_window = FinFeaturesConfig.DEFAULT_STOCH_WINDOW
    
    if not inplace:
        df = df.copy()
    
    validate_multiple_columns(df, [high_col, low_col, close_col])
    validate_window(k_window, 1)
    validate_window(d_window, 1)
    
    lowest_low = df[low_col].rolling(window=k_window).min()
    highest_high = df[high_col].rolling(window=k_window).max()
    
    df[f'Stoch_K_{k_window}'] = 100 * ((df[close_col] - lowest_low) / (highest_high - lowest_low))
    df[f'Stoch_D_{k_window}_{d_window}'] = df[f'Stoch_K_{k_window}'].rolling(window=d_window).mean()
    
    return df

def williams_r(df: pd.DataFrame, high_col: str, low_col: str, close_col: str, window: int = 14, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate Williams %R for given OHLC columns.
    """
    if not inplace:
        df = df.copy()
    
    validate_multiple_columns(df, [high_col, low_col, close_col])
    validate_window(window, 1)
    
    highest_high = df[high_col].rolling(window=window).max()
    lowest_low = df[low_col].rolling(window=window).min()
    
    df[f'Williams_R_{window}'] = -100 * ((highest_high - df[close_col]) / (highest_high - lowest_low))
    
    return df

def commodity_channel_index(df: pd.DataFrame, high_col: str, low_col: str, close_col: str, window: int = 20, constant: float = 0.015, inplace: bool = False) -> pd.DataFrame:
    """
    Calculate Commodity Channel Index (CCI) for given OHLC columns.
    """
    if not inplace:
        df = df.copy()
    
    validate_multiple_columns(df, [high_col, low_col, close_col])
    validate_window(window, 1)
    
    tp = (df[high_col] + df[low_col] + df[close_col]) / 3
    sma_tp = tp.rolling(window=window).mean()
    mad = tp.rolling(window=window).apply(lambda x: np.abs(x - x.mean()).mean())
    
    df[f'CCI_{window}'] = (tp - sma_tp) / (constant * mad)
    
    return df

def multi_timeframe_sma(df: pd.DataFrame, column: str, windows: List[int], inplace: bool = False) -> pd.DataFrame:
    """
    Calculate SMA for multiple timeframes at once.
    """
    if not inplace:
        df = df.copy()
    
    for window in windows:
        df = simple_moving_average(df, column, window, inplace=True)
    
    return df

def generate_sma_signals(df: pd.DataFrame, column: str, fast_window: int, slow_window: int, inplace: bool = False) -> pd.DataFrame:
    """
    Generate trading signals based on SMA crossovers.
    """
    if not inplace:
        df = df.copy()
    
    if fast_window >= slow_window:
        raise ValueError("Fast window must be less than slow window")
    
    df = simple_moving_average(df, column, fast_window, inplace=True)
    df = simple_moving_average(df, column, slow_window, inplace=True)
    
    fast_col = f'{column}_SMA_{fast_window}'
    slow_col = f'{column}_SMA_{slow_window}'
    
    df[f'{column}_SMA_Signal'] = 0
    df.loc[df[fast_col] > df[slow_col], f'{column}_SMA_Signal'] = 1
    df.loc[df[fast_col] < df[slow_col], f'{column}_SMA_Signal'] = -1
    
    return df

def basic_feature_set(df: pd.DataFrame, column: str = 'Close', inplace: bool = False) -> pd.DataFrame:
    """
    Apply a basic set of technical indicators to the DataFrame.
    """
    if not inplace:
        df = df.copy()
    
    df = simple_moving_average(df, column, window=20, inplace=True)
    df = exponential_moving_average(df, column, window=20, inplace=True)
    df = relative_strength_index(df, column, inplace=True)
    df = macd(df, column, inplace=True)
    df = bollinger_bands(df, column, inplace=True)
    
    return df

def premium_feature_set(df: pd.DataFrame, close_col: str = 'Close', high_col: str = 'High', low_col: str = 'Low', inplace: bool = False) -> pd.DataFrame:
    """
    Apply a comprehensive set of technical indicators to the DataFrame.
    """
    if not inplace:
        df = df.copy()
    
    df = basic_feature_set(df, column=close_col, inplace=True)
    df = average_true_range(df, high_col=high_col, low_col=low_col, close_col=close_col, inplace=True)
    df = stochastic_oscillator(df, high_col=high_col, low_col=low_col, close_col=close_col, inplace=True)
    df = williams_r(df, high_col=high_col, low_col=low_col, close_col=close_col, inplace=True)
    df = commodity_channel_index(df, high_col=high_col, low_col=low_col, close_col=close_col, inplace=True)
    
    return df
