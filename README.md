# EletrcicityPricesForecasting

Task: Electricity prices forecasting, using belgium day-ahead market as an example. Hourly data is observed and prices are predicted one-day ahead and one-week ahead.

Feature Engineering: There are two ways of feature engineering. The first one is multi-step forecasting that consecutive data points in chronological order are used. The other is one-step forecasting that the task is tranformed to predict one target value instead.

![One-step Forecasting](https://github.com/Zhihao9/EletrcicityPricesForecasting/blob/main/OneStep-day.ipynb)

![Multi-step Forecasting](https://github.com/Zhihao9/EletrcicityPricesForecasting/blob/main/FEmultistep.png)

Models:

multi-step models:
- ARIMA and SARIMA
- RNNs
- LSTM

One-step models:
- Random Forest
- XGBoost
- FeedForward Neural Networks
- LinXGBoost

