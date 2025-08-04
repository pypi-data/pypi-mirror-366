# STA410 Stock Prediction System  
  
<div>  
  
<a href="https://pepy.tech/projects/stock-prediction-sta410"><img src="https://static.pepy.tech/badge/stock-prediction-sta410" alt="PyPI Downloads"></a>
<a href="https://pepy.tech/projects/stock-prediction-sta410"><img src="https://static.pepy.tech/badge/stock-prediction-sta410/week" alt="PyPI Downloads"></a>
[![PyPI version](https://badge.fury.io/py/stock-prediction-sta410.svg)](https://pypi.org/project/stock-prediction-sta410/) 
![](https://img.shields.io/github/issues/Jamie1377/STA410.svg) 
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Jamie1377/STA410)

</div>  
   
## Overview  
  
This is a comprehensive Python package for stock price prediction that combines statistical time series analysis with advanced machine learning techniques. The system integrates traditional forecasting methods with gradient boosting models and Hidden Markov Models to provide accurate stock price predictions.  
  
### Key Features  
  
- **Hybrid Modeling Approach**: Combines ARIMA, exponential smoothing, gradient boosting, and custom models  
- **Extensive Feature Engineering**: Automatically calculates technical indicators and market features  
- **Multiple Prediction Horizons**: Supports forecasting at various time intervals  
- **Comprehensive Evaluation**: Includes metrics and visualization tools for model assessment  
- **Easy Integration**: Simple API for incorporating into existing workflows  
  
## Installation  
  
```bash  
pip install stock-prediction-sta410
```
For optimal performance, use **NumPy** version **1.26.4**:
```bash
pip install numpy==1.26.4
```
## Quick Start

```bash
from stock_prediction.core.predictor import StockPredictor  
from datetime import date  
  
# Basic usage with default settings  
StockPredictor.full_workflow(  
    "2024-01-01",  
    date.today(),  
    companies=["AAPL", "MSFT"],  
    model="arimaxgb",  
)
```

## Core Components
### StockPredictor
The main interface for interacting with the system. It handles data loading, feature engineering, model training, and forecasting.

### Modeling Approaches
- ARIMAXGBoost: A hybrid model combining ARIMA time series analysis with gradient boosting
- Hidden Markov Models: Captures underlying market regimes and state transitions
- Custom Gradient Descent: Specialized implementation with momentum and adaptive learning

### Feature Engineering
The system automatically calculates numerous technical indicators:

- Moving averages (50, 200, 7, 21-day)
- Momentum indicators (RSI, MACD, Williams %R)
- Volatility measures (Bollinger Bands, ATR)
- Volume indicators and external economic data

### Custom Gradient Descent Implementation


The package features a custom `GradientDescentRegressor` that outperforms scikit-learn's standard `SGDRegressor` in several important ways:


[(Here is the link to the complete notebook of the comparison.)](https://github.com/Jamie1377/STA410/blob/main/stock_prediction/docs/SGD_Comparison_Viz.ipynb)


#### Performance Advantages

<!-- <img src="stock_prediction/docs/SGD_Comparison/SGD_Comparison_Test_1.png"   width=50% height=100%><img src="stock_prediction/docs/SGD_Comparison/SGD_Comparison_Test_2.png" width=50% height=100%><figcaption><strong>Testing Performance:</strong> Our custom implementation consistently achieves lower MSE across time horizons after few iterations</figcaption>

<br>

<img src="stock_prediction/docs/SGD_Comparison/SGD_Comparison_Train_1.png" width=50% height=60%><img src="stock_prediction/docs/SGD_Comparison/SGD_Comparison_Train_2.png" width=50% height=60%><figcaption><strong>Training Convergence:</strong> Faster and more stable optimization compared to sklearn's SGDRegressor</figcaption> -->


<img src="stock_prediction/docs/SGD_Comparison/SGD_Comparison_Train_vs_Test.png" width=50% height=100%><img src="stock_prediction/docs/SGD_Comparison/SGD_Comparison_Losses_by_Category.png" width=50% height=100%>
<figcaption>
<strong>SGD Comparison:</strong> Epoch-wise MSE for training and test sets, and breakdown by loss category. Our custom implementation consistently achieves lower MSE and improved stability compared to sklearn's SGDRegressor.
</figcaption>



As demonstrated in our benchmark tests:

- **Superior Convergence**: Our implementation achieves lower MSE in both training and testing datasets
- **Faster Optimization**: Reaches optimal performance in fewer iterations
- **Better Generalization**: Maintains consistent performance on unseen data

#### Key Technical Innovations

1. **Advanced Initialization**: Uses **QR decomposition** to determine optimal starting coefficients, dramatically improving convergence speed compared to random or zero initialization

2. **Momentum Optimization**: Implements configurable momentum with RMSProp option to escape local minima and smooth gradient updates

3. **Hybrid Regularization**: Combines L1 and L2 penalties with independent control, providing better model generalization for financial time series

4. **Domain-Specific Loss Functions**: Incorporates directional accuracy into optimization objectives, recognizing that predicting price movement direction is often more important than exact values in financial markets

Our implementation is particularly effective for financial time series data, where traditional ML approaches often struggle with the non-stationary nature of the data.

## Advanced Usage
For more detailed examples, see the example usage script.

```bash
from stock_prediction.core.predictor import StockPredictor  
  
# Create a predictor instance  
predictor = StockPredictor(  
    "AAPL",  
    start_date="2023-01-01",  
    end_date="2024-01-01",  
    interval="1d"  
)  
  
# Load and prepare data  
predictor.load_data()  
  
# Prepare models 
predictor.prepare_models()  
  
# Generate forecasts  
forecast = predictor.one_step_forward_forecast(  
    horizon=5,  
    model="arimaxgb",  
    refit=True  
)  
  
# Print forecast results
print(forecast)
```

## Architecture
The system is built with a modular architecture:
```bash
stock_prediction/  
├── core/  
│   ├── predictor.py     # Main StockPredictor class  
│   ├── models.py        # Implementation of prediction models  
│   └── hmm_model.py     # Hidden Markov Model implementation  
├── utils/  
│   ├── preprocessing.py # Data preprocessing utilities  
│   └── evaluation.py    # Model evaluation functions  
└── docs/  
    └── example_usage.py # Usage examples  
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request or fork.

## Authors
Yue Yu (Undergraduate student at the University of Toronto)
## License
This project is licensed under the MIT License - see the LICENSE file for details.

### Disclaimer
This project is solely for educational purposes only. This repo may not be as capable of capturing the live market as hedge fund. Use the model at your own discretion and **risk**, and always consult with financial professionals before making any investment decisions.

Wiki pages you might want to explore:  
- [Overview (Jamie1377/STA410)](/wiki/Jamie1377/STA410#1)  
- [Core Components (Jamie1377/STA410)](/wiki/Jamie1377/STA410#2)
