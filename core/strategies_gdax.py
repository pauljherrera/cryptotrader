import numpy as np
import pandas as pd
import datetime as dt
from urllib import request
import threading
import json
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber

#subscriber?
class Strategy():

    def __init__(self,product):
        #needs arguments and define design pattern
        self.req = requests.get("https://api.gdax.com//products/{}/candles".format(product))
        self.data = json.loads(self.req.text)
        self.headers = ["time", "low", "high", "open", "close", "volume"]
        self.hist_df = pd.DataFrame(self.data, columns=self.headers)
        self.hist_df['time'] = pd.to_datetime(self.hist_df['time'],unit = 's')
        self.hist_df[['low','high','open','close']] = self.hist_df[['low','high','open','close']].apply(pd.to_numeric)
        self.hist_df.set_index('time', drop=True, inplace=True)
        self.ohlc_df=self.hist_df.resample('10T').asfreq()[1:]

    def show_df(self):
        return self.ohlc_df[::-1]


if __name__=="__main__":
    st=Strategy("ETH-USD")

    print(st.show_df())
