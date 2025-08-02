# FinFeatures

[![PyPI version](https://badge.fury.io/py/finfeatures.svg)](https://badge.fury.io/py/finfeatures)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)]()

**Advanced Financial Feature Engineering Library for Quantitative Finance and Algorithmic Trading**

FinFeatures is a comprehensive Python library designed for financial technical analysis and feature engineering. It provides a wide range of technical indicators, statistical transformations, and utility functions optimized for quantitative finance applications.

## 🚀 Key Features

### Technical Indicators
- **Moving Averages**: Simple (SMA) and Exponential (EMA) Moving Averages
- **Momentum Indicators**: RSI, MACD with Signal and Histogram
- **Volatility Indicators**: Bollinger Bands, Average True Range (ATR)
- **Oscillators**: Stochastic Oscillator, Williams %R
- **Other Indicators**: Commodity Channel Index (CCI)

### Statistical Transformations
- **Volatility Analysis**: Rolling volatility with annualization options
- **Returns Calculation**: Simple and logarithmic returns
- **Statistical Measures**: Rolling correlation, beta, z-scores, skewness, kurtosis
- **Normalization**: MinMax, Z-score, and Robust scaling methods

### Advanced Features
- **Signal Generation**: Automated buy/sell signal generation
- **Multi-timeframe Analysis**: Batch processing for multiple timeframes
- **Memory Efficient**: Optional in-place operations
- **Type Safety**: Full type hints and validation
- **Robust Error Handling**: Comprehensive input validation

## 📦 Installation

### From PyPI (Recommended)



## 📊 Available Functions

### Technical Indicators

| Function | Description | Key Parameters |
|----------|-------------|----------------|
| `simple_moving_average()` | Simple Moving Average | `window`, `min_periods` |
| `exponential_moving_average()` | Exponential Moving Average | `window` |
| `relative_strength_index()` | RSI with Wilder's smoothing | `window` (default: 14) |
| `macd()` | MACD with signal and histogram | `fast`, `slow`, `signal` |
| `bollinger_bands()` | Bollinger Bands with position | `window`, `num_std` |
| `average_true_range()` | Average True Range | `window` (default: 14) |
| `stochastic_oscillator()` | Stochastic %K and %D | `k_window`, `d_window` |
| `williams_r()` | Williams %R | `window` (default: 14) |
| `commodity_channel_index()` | Commodity Channel Index | `window` (default: 20) |

### Statistical Transformations

| Function | Description | Key Parameters |
|----------|-------------|----------------|
| `rolling_volatility()` | Rolling volatility calculation | `window`, `annualize` |
| `percent_change()` | Simple/log returns | `periods`, `method` |
| `rolling_correlation()` | Rolling correlation | `column1`, `column2`, `window` |
| `rolling_beta()` | Rolling beta calculation | `asset_col`, `market_col`, `window` |
| `z_score()` | Rolling z-score | `window` |
| `rolling_skewness()` | Rolling skewness | `window` |
| `rolling_kurtosis()` | Rolling kurtosis | `window` |
| `price_normalization()` | Various normalization methods | `method`, `window` |

### Convenience Functions

| Function | Description |
|----------|-------------|
| `basic_feature_set()` | Apply basic technical indicators |
| `premium_feature_set()` | Apply comprehensive indicator set |
| `multi_timeframe_sma()` | SMA for multiple timeframes |
| `generate_sma_signals()` | Generate trading signals |

## 🔧 Configuration

### Default Parameters


### Custom Indicator Pipeline
# Trend indicators
df = ff.multi_timeframe_sma(df, price_col, windows=)
df = ff.exponential_moving_average(df, price_col, window=12)
df = ff.exponential_moving_average(df, price_col, window=26)

# Momentum indicators
df = ff.relative_strength_index(df, price_col, window=14)
df = ff.macd(df, price_col)

# Volatility indicators
df = ff.bollinger_bands(df, price_col, window=20)
df = ff.rolling_volatility(df, price_col, window=20)

# Generate signals
df = ff.generate_sma_signals(df, price_col, fast_window=10, slow_window=30)

return df


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

## 🐛 Bug Reports

If you encounter any bugs, please file an issue on [GitHub Issues](https://github.com/advaitdharmadhikari/finfeatures/issues) with:
- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment details

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [pandas](https://pandas.pydata.org/) and [numpy](https://numpy.org/)
- Inspired by various financial analysis libraries
- Thanks to the quantitative finance community

## 📚 Additional Resources

- [Technical Analysis Explained](https://www.investopedia.com/technical-analysis-4689657)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Quantitative Finance with Python](https://www.quantstart.com/)

**Happy Trading! 📈**

*Made with ❤️ by [Advait Dharmadhikari](https://github.com/advaitdharmadhikari)*
