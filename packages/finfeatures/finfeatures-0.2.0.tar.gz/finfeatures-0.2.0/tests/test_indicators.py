import pandas as pd
import pytest
import finfeatures as ff

def test_simple_moving_average():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    df = pd.DataFrame(data)
    df = ff.simple_moving_average(df, column='Close', window=3)
    assert 'Close_SMA_3' in df.columns

def test_exponential_moving_average():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    df = pd.DataFrame(data)
    df = ff.exponential_moving_average(df, column='Close', window=3)
    assert 'Close_EMA_3' in df.columns

def test_relative_strength_index():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    df = pd.DataFrame(data)
    df = ff.relative_strength_index(df, column='Close')
    assert 'Close_RSI_14' in df.columns

def test_macd():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    df = pd.DataFrame(data)
    df = ff.macd(df, column='Close')
    assert 'Close_MACD' in df.columns
    assert 'Close_MACD_Signal' in df.columns
    assert 'Close_MACD_Histogram' in df.columns

def test_bollinger_bands():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    df = pd.DataFrame(data)
    df = ff.bollinger_bands(df, column='Close')
    assert 'Close_BB_Middle' in df.columns
    assert 'Close_BB_Upper' in df.columns
    assert 'Close_BB_Lower' in df.columns
    assert 'Close_BB_Width' in df.columns
    assert 'Close_BB_Position' in df.columns

def test_average_true_range():
    data = {
        'High': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 
        'Low': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
        'Close': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5]
    }
    df = pd.DataFrame(data)
    df = ff.average_true_range(df, high_col='High', low_col='Low', close_col='Close')
    assert 'ATR_14' in df.columns

def test_stochastic_oscillator():
    data = {
        'High': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 
        'Low': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
        'Close': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5]
    }
    df = pd.DataFrame(data)
    df = ff.stochastic_oscillator(df, high_col='High', low_col='Low', close_col='Close')
    assert 'Stoch_K_14' in df.columns
    assert 'Stoch_D_14_3' in df.columns

def test_premium_feature_set():
    data = {
        'High': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 
        'Low': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
        'Close': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5]
    }
    df = pd.DataFrame(data)
    df = ff.premium_feature_set(df, close_col='Close', high_col='High', low_col='Low')
    
    # Test basic indicators from basic_feature_set
    assert 'Close_SMA_20' in df.columns
    assert 'Close_EMA_20' in df.columns
    assert 'Close_RSI_14' in df.columns
    assert 'Close_MACD' in df.columns
    assert 'Close_MACD_Signal' in df.columns
    assert 'Close_BB_Upper' in df.columns
    assert 'Close_BB_Lower' in df.columns
    
    # Test premium indicators
    assert 'ATR_14' in df.columns
    assert 'Stoch_K_14' in df.columns
    assert 'Stoch_D_14_3' in df.columns
    assert 'Williams_R_14' in df.columns
    assert 'CCI_20' in df.columns

# Additional comprehensive tests
def test_williams_r():
    data = {
        'High': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 
        'Low': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
        'Close': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5]
    }
    df = pd.DataFrame(data)
    df = ff.williams_r(df, high_col='High', low_col='Low', close_col='Close')
    assert 'Williams_R_14' in df.columns

def test_commodity_channel_index():
    data = {
        'High': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 
        'Low': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
        'Close': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5]
    }
    df = pd.DataFrame(data)
    df = ff.commodity_channel_index(df, high_col='High', low_col='Low', close_col='Close')
    assert 'CCI_20' in df.columns

def test_multi_timeframe_sma():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}
    df = pd.DataFrame(data)
    df = ff.multi_timeframe_sma(df, column='Close', windows=[3, 5, 10])
    assert 'Close_SMA_3' in df.columns
    assert 'Close_SMA_5' in df.columns
    assert 'Close_SMA_10' in df.columns

def test_generate_sma_signals():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}
    df = pd.DataFrame(data)
    df = ff.generate_sma_signals(df, column='Close', fast_window=3, slow_window=5)
    assert 'Close_SMA_3' in df.columns
    assert 'Close_SMA_5' in df.columns
    assert 'Close_SMA_Signal' in df.columns

def test_basic_feature_set():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]}
    df = pd.DataFrame(data)
    df = ff.basic_feature_set(df, column='Close')
    assert 'Close_SMA_20' in df.columns
    assert 'Close_EMA_20' in df.columns
    assert 'Close_RSI_14' in df.columns
    assert 'Close_MACD' in df.columns
    assert 'Close_MACD_Signal' in df.columns
    assert 'Close_BB_Upper' in df.columns
    assert 'Close_BB_Lower' in df.columns

# Error handling tests
def test_invalid_column():
    data = {'Close': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    
    with pytest.raises(ValueError, match="Column 'Invalid' not found in DataFrame"):
        ff.simple_moving_average(df, column='Invalid', window=3)

def test_empty_dataframe():
    df = pd.DataFrame()
    
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        ff.simple_moving_average(df, column='Close', window=3)

def test_invalid_window():
    data = {'Close': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    
    with pytest.raises(ValueError, match="Window must be an integer >= 1"):
        ff.simple_moving_average(df, column='Close', window=0)

def test_macd_invalid_periods():
    data = {'Close': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    
    with pytest.raises(ValueError, match="Fast period must be less than slow period"):
        ff.macd(df, column='Close', fast=26, slow=12)

# Test inplace functionality
def test_inplace_functionality():
    data = {'Close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    df = pd.DataFrame(data)
    original_id = id(df)
    
    # Test inplace=True
    result = ff.simple_moving_average(df, column='Close', window=3, inplace=True)
    assert id(result) == original_id
    assert 'Close_SMA_3' in df.columns
    
    # Test inplace=False (default)
    df2 = pd.DataFrame(data)
    result2 = ff.simple_moving_average(df2, column='Close', window=5)
    assert id(result2) != id(df2)
    assert 'Close_SMA_5' not in df2.columns
    assert 'Close_SMA_5' in result2.columns
