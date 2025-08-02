# finfeatures/__init__.py
"""
FinFeatures: Advanced Financial Feature Engineering Library
"""

from .indicators import (
    simple_moving_average,
    exponential_moving_average,
    relative_strength_index,
    macd,
    bollinger_bands,
    average_true_range,
    stochastic_oscillator,
    williams_r,
    commodity_channel_index,
    multi_timeframe_sma,
    generate_sma_signals,
    basic_feature_set,
    premium_feature_set
)

from .transformers import (
    rolling_volatility,
    percent_change,
    rolling_correlation,
    rolling_beta,
    z_score,
    rolling_skewness,
    rolling_kurtosis,
    price_normalization
)

from .utils import (
    validate_inputs,
    validate_window,
    validate_multiple_columns,
    FinFeaturesConfig
)

__version__ = "0.2.0"
__author__ = "Advait Dharmadhikari"
__email__ = "advaituni@gmail.com"

# This is crucial for type checkers
__all__ = [
    # Technical Indicators
    'simple_moving_average',
    'exponential_moving_average',
    'relative_strength_index',
    'macd',
    'bollinger_bands',
    'average_true_range',
    'stochastic_oscillator',
    'williams_r',
    'commodity_channel_index',
    'multi_timeframe_sma',
    'generate_sma_signals',
    'basic_feature_set',
    'premium_feature_set',
    
    # Transformers
    'rolling_volatility',
    'percent_change',
    'rolling_correlation',
    'rolling_beta',
    'z_score',
    'rolling_skewness',
    'rolling_kurtosis',
    'price_normalization',
    
    # Utilities
    'validate_inputs',
    'validate_window',
    'validate_multiple_columns',
    'FinFeaturesConfig'
]
