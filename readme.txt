To create a new strategy, follow these steps.

  1- In the file core/strategies.py create a new class that inherits the Strategy class.
  2- Override the calculate(self, message) method with the desired logic. message is a dictionary with the last JSON data point sent by the exchange. That dictionary looks like:

    {'market_history_id': 135320300899, 'exchange': 'PLNX', 'marketid': 0, 'label': 'USDT/BTC', 'tradeid': '9712278', 'time': '2017-10-25T17:14:53', 'price': 5543.54999999, 'quantity': 0.01791076, 'total': 99.2891935978, 'timestamp': '2017-10-25T17:15:02Z', 'time_local': '2017-10-25 17:14:53', 'type': 'BUY', 'exchId': 0, 'channel': 'TRADE-PLNX--USDT--BTC'}

  3- To place a trade, publish a signal. In order to publishing a signal, call the method self.pub.dispatch('signals', signal) where signal is a dictionary like this one {'type': <'BUY'/'SELL'>, 'price': '5900.5'}


The children classes of Strategy will have access to the following attributes:
  - self.data: a pandas DataFrame with the tick by tick data.
  - self.historical_data: a pandas DataFrame with the data resampled according to a timeframe established in ./live_trader.py
 

In order to start trading follow these steps:
  1- In the file ./live_trader.py, replace the API Key and Secret.
  2- Also input the desired timeframe in the line 17.
  3- Instantiate your strategy in the line 47. Pass **data as a parameter. It will look like this:
    strategy = strategies.MyStrategy(**data)
  4- Run the live_trader.py file from the command line. 



