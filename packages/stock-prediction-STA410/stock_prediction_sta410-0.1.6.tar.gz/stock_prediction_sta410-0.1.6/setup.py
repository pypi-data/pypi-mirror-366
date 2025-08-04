from setuptools import setup, find_packages

setup(
    name="stock_prediction_STA410",
    version="0.1.6",
    
    packages=find_packages(
        exclude=[
            "stock_prediction.aptos",
            "stock_prediction.aptos.*",
            "stock_prediction.logs",
            "stock_prediction.logs.*",
            "transaction_logs",
            "transaction_logs.*",
            ".aptos",
            ".aptos.*",
            "model_cache",
            "model_cache.*",
            "stock_prediction.core.autotrade",
            "stock_prediction.docs.API_KEYs",
        ]
    ),
    install_requires=[
        "numpy==1.26.4",
        "pandas",
        "yfinance",
        "scikit-learn==1.6.1",
        "statsmodels",
        "xgboost",
        "lightgbm",
        "catboost",
        "matplotlib",
        "seaborn",
        "pandas-market-calendars",
        "pandas_market_calendars",
        "mplcursors",
        "scikit-optimize",
        "hmmlearn",
        "pmdarima",
        "statsforecast",
        "pygam",
        "schedule",
        "alpaca_trade_api",
        "alpaca",
        "pyticksymbols",
    ],
    # packages=find_packages(exclude=['model_cache', 'tests']),
    exclude_package_data={"": ["*.pkl", "*.joblib"]},
)
