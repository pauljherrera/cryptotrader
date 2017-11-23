# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 11:40:11 2017

@author: paulj
"""

import pandas as pd

def resample_ohlcv(df, rule='1H'):
    """
    Resamples a OHLCV DataFrame.
    Returns a OHLCV DataFrame.
    Differs from pandas.resample().ohlc() because it considers all the columns
    of the DataFrame, not just the close.
    """
    resampled_df = pd.DataFrame()
    resampled_df['open'] = df['open'].resample(rule).first()
    resampled_df['high'] = df['high'].resample(rule).max()
    resampled_df['low'] = df['low'].resample(rule).min()
    resampled_df['close'] = df['close'].resample(rule).last()
    resampled_df['volume'] = df['volume'].resample(rule).sum()
    
    return resampled_df


    