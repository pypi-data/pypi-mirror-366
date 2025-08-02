import pandas as pd
from typing import Optional, List

class FinFeaturesConfig:
    """Configuration class for default parameters"""
    DEFAULT_RSI_WINDOW = 14
    DEFAULT_MA_WINDOW = 20
    DEFAULT_MACD_FAST = 12
    DEFAULT_MACD_SLOW = 26
    DEFAULT_MACD_SIGNAL = 9
    DEFAULT_BB_STD = 2
    DEFAULT_ATR_WINDOW = 14
    DEFAULT_STOCH_WINDOW = 14

def validate_inputs(df: pd.DataFrame, column: str, min_length: Optional[int] = None):
    """
    Validate DataFrame and column inputs.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to validate
    column : str
        Column name to check
    min_length : int, optional
        Minimum required DataFrame length
        
    Raises
    ------
    ValueError
        If validation fails
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")
    if df.empty:
        raise ValueError("DataFrame cannot be empty.")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    if df[column].isna().all():
        raise ValueError(f"Column '{column}' contains only NaN values.")
    if min_length and len(df) < min_length:
        raise ValueError(f"DataFrame must have at least {min_length} rows.")

def validate_window(window: int, min_window: int = 1):
    """
    Validate window parameter for technical indicators.
    
    Parameters
    ----------
    window : int
        Window size to validate
    min_window : int, default 1
        Minimum allowed window size
        
    Raises
    ------
    ValueError
        If window is invalid
    """
    if not isinstance(window, int) or window < min_window:
        raise ValueError(f"Window must be an integer >= {min_window}")

def validate_multiple_columns(df: pd.DataFrame, columns: List[str]):
    """
    Validate multiple columns exist in DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    columns : list
        List of column names to validate
        
    Raises
    ------
    ValueError
        If any column is missing
    """
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
