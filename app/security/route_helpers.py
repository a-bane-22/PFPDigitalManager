from app import db
from app.models import (Security, SecurityDailyAdjusted)
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import plotly.graph_objs as go
import os
from datetime import date

color_list = ['black', 'blue', 'cyan', 'green', 'red']


def line_generator(line_number=0):
    color_index = line_number % len(color_list)
    return go.scatter.Line(color=color_list[color_index], dash='solid', width=3)


def marker_generator(marker_number=0, size=10):
    color_index = marker_number % len(color_list)
    return go.scatter.Marker(color=color_list[color_index],
                             size=size,
                             symbol='star')


def legend_title_generator(title):
    return go.scatter.Legendgrouptitle(text=title)


# Pre:  symbol is a string representing a security
# Post: RV is a pandas dataFrame object containing adjusted close price data
#        for the last 100 days
def get_daily_price_data(symbol):
    ts = TimeSeries(key=os.environ['ALPHAVANTAGE_API_KEY'])
    data, meta_data = ts.get_daily_adjusted(symbol=symbol,
                                            outputsize='compact')
    date_price_pair = [(key, data[key]['5. adjusted close']) for key
                       in data.keys()]
    num_points = len(date_price_pair)
    data_points = dict([(i, date_price_pair[i]) for i in range(num_points)])
    return pd.DataFrame(data_points)


# Pre:  price_data is an iterable of DailyAdjustedPrice object
#       price_type is one of 'open', 'close', 'adjusted_close',
#        'high', or 'low'
# Post: RV = date_list, value_list where date_list contains strings
#            representing dates and value_list contains floats corresponding
#            to the daily price as determined by price_type
def get_daily_adjusted_price_data_by_type(price_data, price_type):
    date_list = [price.date for price in price_data]
    value_list = []
    if price_type == 'open':
        value_list = [price.open for price in price_data]
    elif price_type == 'close':
        value_list = [price.close for price in price_data]
    elif price_type == 'adjusted_close':
        value_list = [price.adjusted_close for price in price_data]
    elif price_type == 'high':
        value_list = [price.high for price in price_data]
    elif price_type == 'low':
        value_list = [price.low for price in price_data]
    elif price_type == 'volume':
        value_list = [price.volume for price in price_data]
    return date_list, value_list


# Pre:  symbol is a string representing a security
#       num_points is a positive integer representing the # of data points
#       period is a positive integer representing the # of intervals to
#        include in the average calculation
#       interval is a string representing the time between each price point
#        in the average calculation
#       series_type is a string representing the price value to use in the
#        average calculation
# Post: RV is a pandas DataFrame object containing WMA data for the security
#        generated using the period, interval, and series type provided.
def get_wma_data(symbol, num_points=100, period=20, interval='daily',
                 series_type='close'):
    ti = TechIndicators(key=os.environ['ALPHAVANTAGE_API_KEY'])
    data, meta_data = ti.get_wma(symbol=symbol, interval=interval,
                                 time_period=period, series_type=series_type)
    date_value_pairs = [(key, float(data[key]['WMA'])) for key in data.keys()]
    if len(date_value_pairs) < num_points:
        num_points = len(date_value_pairs)
    data_points = dict([(i, date_value_pairs[i]) for i in range(num_points)])
    return pd.DataFrame(data_points)


def get_crossover_trades(df_0, df_1):
    crossover_points = []
    data = {'0': df_0.loc[0], '1': df_0.loc[1], '2': df_1.loc[1]}
    df_2 = pd.DataFrame(data)
    prev_val_0 = df_2.loc[0][1]
    prev_val_1 = df_2.loc[0][2]
    for index in df_2.index:
        curr_val_0 = df_2.loc[index][1]
        curr_val_1 = df_2.loc[index][2]
        if prev_val_0 < prev_val_1 and curr_val_0 > curr_val_1:
            crossover_points.append(('BUY', df_2.loc[index][0]))
        elif prev_val_0 > prev_val_1 and curr_val_0 < curr_val_1:
            crossover_points.append(('SELL', df_2.loc[index][0]))
        prev_val_0 = curr_val_0
        prev_val_1 = curr_val_1
    return crossover_points


# Pre:  values is a list of 3-tuples (val_1, val_2, date) where val_1 and
#        val_2 are floats and date is a string
# Post: RV is a list of 2-tuples (val_1, date) such that the previous val_1
#        was greater than or equal to val_2 and is now lesser or val_1 was
#        lesser than or equal to val_2 and is now greater
def get_crossover_points(df_0, df_1):
    x_vals = []
    y_vals = []
    data = {'0': df_0.loc[0], '1': df_0.loc[1], '2': df_1.loc[1]}
    df_2 = pd.DataFrame(data)
    prev_val_0 = df_2.loc[0][1]
    prev_val_1 = df_2.loc[0][2]
    for index in df_2.index:
        curr_val_0 = df_2.loc[index][1]
        curr_val_1 = df_2.loc[index][2]
        if ((prev_val_0 < prev_val_1 and curr_val_0 > curr_val_1) or
                (prev_val_0 > prev_val_1 and curr_val_0 < curr_val_1)):
            x_vals.append(df_2.loc[index][0])
            y_vals.append(curr_val_0)
        prev_val_0 = curr_val_0
        prev_val_1 = curr_val_1
    return x_vals, y_vals


def generate_daily_close_wma_crossover_chart(symbol, num_points=100, period_0=20, period_1=100,
                                             series_type='close'):
    file_name = f'{symbol}_{period_0}_{period_1}_daily_close_wma_crossover_{date.today()}.png'
    file_path = os.path.join('technical_indicators/wma_crossover/' + file_name)
    df_0 = get_wma_data(symbol=symbol, num_points=num_points,
                        period=period_0, interval='daily',
                        series_type=series_type)
    df_1 = get_wma_data(symbol=symbol, num_points=num_points,
                        period=period_1, interval='daily',
                        series_type=series_type)
    df_price = get_daily_price_data(symbol=symbol)
    cross_x_vals, cross_y_vals = get_crossover_points(df_0=df_0, df_1=df_1)
    line_specification_0 = line_generator(line_number=0)
    line_specification_1 = line_generator(line_number=1)
    line_specification_price = line_generator(line_number=2)
    marker_crossover = marker_generator(marker_number=3, size=10)
    title_0 = f"{period_0}-Day Close WMA"
    title_1 = f"{period_1}-Day Close WMA"
    title_2 = "Daily Close Price"
    title_3 = "Crossover Marker"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_0.loc[0],
                             y=df_0.loc[1],
                             line=line_specification_0,
                             mode='lines',
                             name=title_0))
    fig.add_trace(go.Scatter(x=df_1.loc[0],
                             y=df_1.loc[1],
                             line=line_specification_1,
                             mode='lines',
                             name=title_1))
    fig.add_trace(go.Scatter(x=df_price.loc[0],
                             y=df_price.loc[1],
                             line=line_specification_price,
                             mode='lines',
                             name=title_2))
    fig.add_trace(go.Scatter(x=cross_x_vals,
                             y=cross_y_vals,
                             marker=marker_crossover,
                             mode='markers',
                             name=title_3))
    fig.write_image(file_path)
    return file_path


def process_daily_close_wma_crossover_data(securities, period_0, period_1):
    crossovers = []
    for security in securities:
        df_0 = get_wma_data(symbol=security.symbol,
                            num_points=100,
                            period=period_0,
                            interval='daily',
                            series_type='close')
        df_1 = get_wma_data(symbol=security.symbol,
                            num_points=100,
                            period=period_1,
                            interval='daily',
                            series_type='close')
        crossover_trades = get_crossover_trades(df_0=df_0, df_1=df_1)
        for trade in crossover_trades:
            crossovers.append((security.symbol, trade))
    return crossovers


def store_daily_adjusted_price_data(security_id):
    security = Security.query.get(int(security_id))
    ts = TimeSeries(key=os.environ['ALPHAVANTAGE_API_KEY'])
    data, meta_data = ts.get_daily_adjusted(symbol=security.symbol,
                                            outputsize='compact')
    snapshots = [SecurityDailyAdjusted(symbol=security.symbol,
                                       date=date.fromisoformat(key),
                                       open=float(data[key]['1. open']),
                                       close=float(data[key]['4. close']),
                                       adjusted_close=float(data[key]['5. adjusted close']),
                                       high=float(data[key]['2. high']),
                                       low=float(data[key]['3. low']),
                                       volume=int(data[key]['6. volume']),
                                       dividend_amount=float(data[key]['7. dividend amount']),
                                       split_coefficient=float(data[key]['8. split coefficient']),
                                       security_id=security.id) for key in data.keys()]
    db.session.add_all(instances=snapshots)
    db.session.commit()
