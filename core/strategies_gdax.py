import pandas as pd
import datetime as dt
import sys
import os
import gdax

from apscheduler.schedulers.background import BackgroundScheduler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Subscriber
from core.libraries.gdax_data_downloader import get_historic_rates
from core.libraries.resampler import resample_ohlcv
pd.set_option('expand_frame_repr', False)

class Strategy(Subscriber):
    """
    Abstract class for new strategies.
    Subscribes to a data channel, parses the data and makes a call
    each tick (on_tick), each minute (on_minute_bar) and
    each customized interval (on_bar).
    """
    def __init__(self, trader=None, *args, **kwargs):
        self.product = kwargs['pairs']
        self.period = kwargs['ATR-Period']
        self.vstop_timeframe = kwargs['vstop timeframe']
        self.multiplier = kwargs['vstop multiplier']
        self.data_days = kwargs['data days']

        self.client = gdax.PublicClient()
        self.trader = trader

        self.counter = 0
        self.check = True
        self.temp_df = pd.DataFrame(columns=['time','price','size'])
        self.temp_df['time'] = pd.to_datetime(self.temp_df['time'], format="%Y-%m-%dT%H:%M:%S.%fZ")
        self.temp_df = self.temp_df.set_index('time', drop=True, inplace = True)

        self.main_df = self.df_load(60, self.product)
        self.main_df.drop(self.main_df.head(1).index,inplace=True)
        self.timer = dt.datetime.now()
        self.main_atr = self.ATR(self.main_df)
        self.check_v = True
        self.vstop = {}
        self.v_stop_init()

        # Initializing daemon for getting account balance
        scheduler = BackgroundScheduler()
        scheduler.add_job(self._scheduled_task, trigger='cron',
                          minute='*/{}'.format(self.vstop_timeframe))

        scheduler.start()

    def _scheduled_task(self):
        self.v_stop_calculate()
        self.on_bar()

    def df_load(self, granularity, product):
        today = dt.date.today()
        start_date_str = (today - dt.timedelta(days=self.data_days)).isoformat()
        end_date_str = (today + dt.timedelta(days=1)).isoformat()
        print('\nGetting historical data')
        hist_df = get_historic_rates(self.client, product='BTC-USD',
                         start_date=start_date_str, end_date=end_date_str,
                         granularity=granularity, beautify=False)
        hist_df['time'] = pd.to_datetime(hist_df['time'], unit='s')
        hist_df.set_index('time', inplace=True)
        hist_df.sort_index(inplace=True)
        hist_df = hist_df.groupby(hist_df.index).first()

        return hist_df

    def ATR(self, df):
        df['TR1'] = abs (df['high'] - df['low'])
        df['TR2'] = abs (df['high'] - df['close'].shift())
        df['TR3'] = abs (df['low'] - df['close'].shift())
        df['TrueRange'] = df[['TR1','TR2','TR3']].max(axis=1)
        df['ATR'] = df.TrueRange.rolling(self.period).mean().ffill()
        del [df['TR1'],df['TR2'],df['TR3']]
        return df

    def atr_value(self, df):
        return df['ATR'].head(1) if df['ATR'].last_valid_index() == None else df['ATR'].loc[df['ATR'].last_valid_index()]

    def v_stop_init(self):
        atr_s = self.get_timeframe(self.vstop_timeframe)

        self.vstop['Multiplier'] = self.multiplier
        self.vstop['Trend'] = self.get_trend(atr_s, 15)
        self.vstop['ATR'] =  atr_s['ATR'][-1]
        self.vstop['min_price'] = atr_s['close'][-1]
        self.vstop['max_price'] = atr_s['close'][-1]
        self.vstop['vstop'] = self.vstop['max_price'] - self.multiplier * self.vstop['ATR']

    def get_trend(self, data, period):
        #period is the init row and -1 the last
        prices = data['close']
        return "down" if prices[-1] <= prices[-period] else "up"


    def v_stop_calculate(self):
        self.atr_s = self.get_timeframe(self.vstop_timeframe)

        price = float(self.main_df['close'].tail(1))
        self.vstop['max_price'] = max(self.vstop['max_price'], price)
        self.vstop['min_price'] = min(self.vstop['min_price'], price)
        self.vstop['ATR'] = self.atr_value(self.atr_s)

        if self.vstop['Trend'] == "up":
            stop =  self.vstop['max_price'] - self.multiplier * self.vstop['ATR']
            self.vstop['vstop'] = max(self.vstop['vstop'], stop)
        else:
            stop = self.vstop['min_price'] + self.multiplier * self.vstop['ATR']
            self.vstop['vstop'] = min(self.vstop['vstop'], stop)

        trend = "up" if price >= self.vstop['vstop'] else "down"
        change = (trend != self.vstop['Trend'])

        self.vstop['Trend'] = trend
        if change:
            self.vstop['max_price'] = price
            self.vstop['min_price'] = price

            if trend == 'up':
                self.vstop['vstop'] = self.vstop['max_price'] - self.multiplier * self.vstop['ATR']
            else:
                self.vstop['vstop'] = self.vstop['min_price'] + self.multiplier * self.vstop['ATR']


    def check_time(self, clock):
        if (self.check):
             self.check = False
             self.time = clock

    def update(self, message):
        self.live(message)
        self.counter += 1
        self.on_tick()

    def live(self, message):
        #creates a new data frame and concatenates it to our main one
        time = dt.datetime.strptime(message['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.check_time(time)

        if (time.minute == self.time.minute):
            live_data = [time, message['price'] , message['size']]
            columns_n = ['time', 'price', 'size']
            live_df = pd.DataFrame([live_data], columns=columns_n)
            live_df.set_index('time', drop=True, inplace=True)
            self.temp_df = pd.concat([self.temp_df, live_df])
            self.temp_df[['price', 'size']] = self.temp_df[['price','size']].apply(pd.to_numeric)
        else:
            self.time = time
            vol_s = self.temp_df['size']
            vol_s = vol_s.resample('1T').sum()
            self.new_df = self.temp_df['price'].resample('1T').ohlc()
            self.new_df['volume'] = vol_s
            self.main_df = pd.concat([self.main_df, self.new_df])
            self.on_minute_bar()

    def get_timeframe(self, timeframe):
        resampled_df = resample_ohlcv(self.main_df, rule='{}T'.format(timeframe))
        atr_df = self.ATR(resampled_df)

        return atr_df

    def on_tick(self):
        pass

    def on_minute_bar(self):
        print('\nNew minute bar')

    def on_bar(self):
        print('\nNew bar')
