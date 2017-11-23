# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 11:44:53 2017

@author: Paúl Herrera
"""

import pandas as pd
import datetime as dt
import gdax
import sys
import os
from tqdm import tqdm
from time import sleep
from requests.adapters import SSLError


def append_data(client, df, product, columns, start_timestamp, 
                end_timestamp, granularity=1):
    newData = client.get_product_historic_rates(product, 
                     dt.datetime.fromtimestamp(start_timestamp).isoformat(),
                     dt.datetime.fromtimestamp(end_timestamp).isoformat(),
                     granularity=granularity)
#    print(newData)
    data = pd.concat([df, pd.DataFrame(newData, columns=columns)])
    
    return data


def beautify_data(data):
    # Reorder dataframe.
    data['time'] = data.time.apply(dt.datetime.fromtimestamp)
    data['date'] = data.time.apply(lambda x: dt.date(x.year, x.month, x.day))
    data['time'] = data.time.apply(lambda x: dt.time(x.hour, x.minute, x.second))
    # data['volume'] = data.volume.round(4)
    data = data[['date', 'time', 'open', 'high', 'low', 'close', 'volume']] 
    
    # Using data points where the price has changed.
    # data = data.where(data.close != data.close.shift()).dropna().sort_index()
    data = data.sort_values(['date', 'time'])

    return data

def get_historic_rates(client, product, start_date, end_date, 
                       granularity=1, beautify=True):
    """
    Gets the historical data of a product making the necessary
    calls to the GDAX API and returns a pandas DataFrame with
    the data.
    """
    startDate = dt.datetime.strptime(start_date, "%Y-%m-%d")
    startDateTimestamp = startDate.timestamp()
    endDate = dt.datetime.strptime(end_date, "%Y-%m-%d")
    endDateTimestamp = endDate.timestamp()
    
    # List of time divisions for retrieving data.
    timeRange = range(int(startDateTimestamp), int(endDateTimestamp), 
                      200 * granularity)
    timeRange = list(timeRange) + [endDateTimestamp]
    
    # New DataFrame.
    columns = ['time', 'low', 'high', 'open', 'close', 'volume']
    data = pd.DataFrame(columns=columns)
    
    # Populating dataframe.
    for i in tqdm(range(len(timeRange) - 1)):
        try:
            data = append_data(client, data, product, columns, 
                               timeRange[i], timeRange[i+1],
                               granularity)
        except ValueError:
            sleep(3)
            data = append_data(client, data, product, columns, 
                               timeRange[i], timeRange[i+1], 
                               granularity)
        except SSLError:
            sleep(15)
            data = append_data(client, data, product, columns, 
                               timeRange[i], timeRange[i+1], 
                               granularity)
        except:
            print("An error ocurred. The complete set of data couldn't be downloaded.")
            if beautify:
                return beautify_data(data.drop_duplicates())
            else:
                return data.drop_duplicates()
    
    if beautify:
        return beautify_data(data.drop_duplicates())
    else:
        return data.drop_duplicates()


def get_arg(index, default):
    try:
        return sys.argv[index]
    except IndexError:
        return default
    
    
    

if __name__ == "__main__":
    """
    First available dates:
    - 'BTC-USD': 2015-01-14.
    - 'ETH-USD': 2016-08-01.
    - 'LTC-USD': 2016-09-01
    """
    # Variables.
    client = gdax.PublicClient()
    product = get_arg(1, 'BTC-USD')
    start_date = get_arg(2, '2015-02-01')
    end_date = get_arg(3, '2017-08-26')
    granularity = int(get_arg(4, 900)) 
    
    # Downloading data.
    print('Downloading data for {}'.format(product))
    data = get_historic_rates(client, product, start_date, end_date, granularity)
    file_name = '{}_{}_{}_{}sec.csv'.format(product, start_date, end_date, 
                                            int(granularity))
    file_dir = os.getcwd()
    data.to_csv(os.path.join(file_dir, file_name), index=False)
    print('{} data file generated.'.format(file_name))
