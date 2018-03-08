# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Avanti Financial Services
"""
from sys import argv

import pandas as pd

from core.strategies_gdax import Strategy
from backtest_core.portfolio import Portfolio


class BacktesterCustomStrategy(Strategy):

    def vstop_strat(self, portfolio, product='BTC-USD'):
        cols = ['open', 'high', 'low', 'close',
                'volume', 'TrueRange', 'ATR']

        self.back_df = pd.DataFrame(columns=cols)
        super().v_stop_calculate(self.main_df)

        self.main_df.dropna(how='any', inplace=True)
        dataf = self.main_df
        position = None

        for item in dataf.itertuples():
            back_df = self.dataframe_handler(item)
            super().v_stop_calculate(back_df)

            open, high, low, close = item[1], item[2], item[3], item[4]
            volume, true_range, avg_tr = item[5], item[6], item[7]

            time = item[0]
            print(back_df)

            size = (portfolio.capital/close) * 0.02
            if position is None:
                if (high+low)/2 > close:
                    last_size = size
                    portfolio.place_order(time, price=close,
                                          side='BUY', size=size, product=product)
                    print("\nBUY ORDER. Price:{}\nProduct:{}\nSize:{}".\
                          format(close, product, size))
                    position = 'buy'

            elif position == 'buy':
                if (high+low+open)/3 < close:
                    position = None
                    portfolio.place_order(time,price=close,
                                          side='SELL', size=last_size, product='BTC-USD')
                    print("\nSELL ORDER. Price:{}\nProduct:{}\nSize:{}". \
                          format(close, product, last_size))

        info_df = portfolio.show_orders()
        print(info_df)

    def dataframe_handler(self, data):
        print(data)
        new_data = pd.DataFrame([data])
        new_data['time'] = pd.to_datetime(new_data['Index'],
                                           format="%Y-%m-%dT%H:%M:%S.%fZ")
        new_data = new_data.set_index('time', drop=True)
        print(new_data)
        self.back_df.append(new_data)
        return self.back_df

if __name__ == "__main__":
    # User Variables.
    try:
        new_download = argv[1]
    except IndexError:
        new_download = False;

    product = "BTC-USD"
    ATR_period = 14
    timeframe = 5
    VStop_multiplier = 3

    # Date ranges format: 'YYYY-MM-DD' or None in both cases if using data_days
    start = '2018-01-05'
    end = '2018-02-05'

    # Setting strategy parameters.
    parameters = {
        'pairs': product,
        'ATR-Period': ATR_period,
        'vstop timeframe': timeframe,
        'vstop multiplier': VStop_multiplier,
        'data days': 0,
        'start': start,
        'end': end,
        'granularity': 5}

    bt_strategy = BacktesterCustomStrategy(backtest=True, **parameters)
    dataframe = bt_strategy.main_df
    if new_download:
        # Getting the dataframe of the desired timeframe
        dataframe.to_csv("core/historic_ohlcv.csv")
    else:
        dataframe = pd.read_csv("core/historic_ohlcv.csv")

    port = Portfolio(capital=80000, c_capital=0.5)
    bt_strategy.vstop_strat(portfolio=port)

    # Shows data of every wallet
    # print(trader.list_accounts())

    # Start connection.
    # connectThread.start()
