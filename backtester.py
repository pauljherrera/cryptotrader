# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Avanti Financial Services
"""
from sys import argv

import pandas as pd

from core.strategies_gdax import Strategy


class Backtester():

    def __init__(self, data):
        """
        :param data: dataframe object that contains
        open high low close volume TrueRange AvgTR
        """
        self.dataframe = data

    def calculator(self):
        dataf = self.dataframe
        for item in dataf.itertuples():
            open, high, low, close = item[1], item[2], item[3], item[4]
            volume, true_range, avg_tr = item[5], item[6], item[7]

            if (high+low) / 2 > close:
                print("buy!")
            else:
                print("sell!")


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
    end = '2018-02-15'

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

    if new_download:
        strategy = Strategy(**parameters)
        # Getting the dataframe of the desired timeframe
        dataframe = strategy.main_df
        dataframe.to_csv("historic_ohlcv.csv")
    else:
        dataframe = pd.read_csv("historic_ohlcv.csv")

    backtester = Backtester(dataframe)
    backtester.calculator()

    # Shows data of every wallet
    # print(trader.list_accounts())

    # Start connection.
    # connectThread.start()
