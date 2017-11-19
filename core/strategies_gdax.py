import numpy as np
import pandas as pd
import datetime as dt
from urllib import request
import threading
import json
import sys
import os
import requests
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber


class Strategy(Subscriber):
#needs coments
    def __init__(self, *args, **kwargs):
        self.product = kwargs['pairs']
        self.period = kwargs['ATR-Period']
        self.bars = kwargs['Bars']
        self.check = True
        self.temp_df = pd.DataFrame(columns=['time','price','size'])
        self.temp_df['time'] = pd.to_datetime(self.temp_df['time'], format="%Y-%m-%dT%H:%M:%S.%fZ")
        self.temp_df = self.temp_df.set_index('time', drop=True, inplace = True)
        self.main_df = self.df_load(60, self.product)
        self.main_df.drop(self.main_df.tail(1).index,inplace=True)
        self.timer = dt.datetime.now()
        self.main_atr = self.ATR(self.main_df)

        for i in self.bars:
            print(self.main_atr.resample(str(i)+'min').asfreq())



    def df_load(self, granularity, product):

        timeframe = {'granularity': granularity}
        req = requests.get("https://api.gdax.com//products/{}/candles".format(product),params=timeframe)
        data = json.loads(req.text)
        headers = ["time", "low", "high", "open", "close", "volume"]
        hist_df = pd.DataFrame(data, columns=headers)
        hist_df['time'] = pd.to_datetime(hist_df['time'],unit = 's')
        hist_df[['low','high','open','close']] = hist_df[['low','high','open','close']].apply(pd.to_numeric)
        hist_df.set_index('time', drop=True, inplace=True)
        hist_df = hist_df[['open','high','low','close','volume']]

        return hist_df

    def ATR(self, df):
        df['TR1'] = abs (df['high'] - df['low'])
        df['TR2'] = abs (df['high'] - df['close'].shift())
        df['TR3'] = abs (df['low'] - df['close'].shift())
        df['TrueRange'] = df[['TR1','TR2','TR3']].max(axis=1)
        df['ATR'] = df.TrueRange.rolling(self.period).mean().ffill()
        del [df['TR1'],df['TR2'],df['TR3']]
        return df

    def check_time(self, clock):
        if (self.check):
             self.check = False
             self.time = clock

    def update(self, message):
        #print(message)
        self.live(message)

    def live(self, message):
        #creates a new data frame and concatenates it to our main one
        time = dt.datetime.strptime(message['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.check_time(time)

        if (time.minute == self.time.minute):
            live_data = [time, message['price'] , message['size']]
            columns_n = ['time', 'price', 'size']
            live_df = pd.DataFrame([live_data], columns=columns_n)
            live_df.set_index('time', drop=True, inplace=True)
            self.temp_df = pd.concat([live_df,self.temp_df])
            self.temp_df[['price', 'size']] = self.temp_df[['price','size']].apply(pd.to_numeric)
        else:
            print(self.temp_df)
            self.time = time
            vol_s = self.temp_df['size']
            vol_s = vol_s.resample('1T').sum()
            self.new_df = self.temp_df['price'].resample('1T').ohlc()
            self.new_df['volume'] = vol_s
            self.main_df = pd.concat([self.new_df, self.main_df])
            df_atr = self.ATR(self.main_df)

            for i in self.bars:
                print(df_atr.resample(str(i)+'min').asfreq())
            self.temp_df = self.temp_df[0:0]

#i will add this soon
"""class MACrossover(Strategy):
    def __init__(self, timeframe, long_period, short_period, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.timeframe = str(timeframe) + 'S'
        self.long_period = long_period
        self.short_period = short_period

    def calculate(self, message):
        "
        Sends a dictionary as trading signal.
        "

        # Main logic.
        # Entry signals.
        if (self.accountState == 'CLOSE') and (message['side'] == 'BUY'):
            self.ask = self.data[self.data.Type == 'BUY'].resample(self.timeframe).last().ffill()
            long_ma = self.ask.Price.rolling(self.long_period).mean()
            short_ma = self.ask.Price.rolling(self.short_period).mean()
            print('Long MA: {} - Short MA: {}'.format(long_ma[-1], short_ma[-1]))
            if (short_ma[-1] > long_ma[-1]):
                print('Buy signal')
                self.accountState = 'BUY'
                signal = {'type' : message['type'],
                          'price' : message['price']}
                self.pub.dispatch('signals', signal)

        # Exit signals.
        elif (self.accountState == 'BUY') and (message['type'] == 'SELL'):
            self.bid = self.data[self.data.Type == 'SELL'].resample(self.timeframe).last().ffill()
            long_ma = self.bid.Price.rolling(self.long_period).mean()
            short_ma = self.bid.Price.rolling(self.short_period).mean()
            print('Long MA: {} - Short MA: {}'.format(long_ma[-1], short_ma[-1]))
            if (short_ma[-1] < long_ma[-1]):
                print('Close signal')
                self.accountState = 'CLOSE'
                signal = {'type' : message['type'],
                          'price' : message['price']}
                self.pub.dispatch('signals', signal)
"""
