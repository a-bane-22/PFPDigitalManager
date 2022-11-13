from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import plotly.graph_objs as go
import os

color_list = ['black', 'blue', 'cyan', 'green', 'red']


def line_generator(line_number=0):
    color_index = line_number % len(color_list)
    return go.scatter.Line(color=color_list[color_index], dash='solid', width=3)


# Pre:  symbol is a string representing a security
# Post: RV is a pandas dataFrame object containing price data for the security
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


def generate_wma_crossover_chart(symbol, num_points=100, period_0=20, period_1=100,
                                 interval='daily', series_type='close'):
    file_name = os.path.join('technical_indicators/wma_crossover/' +
                             '{}_wma_crossover.png'.format(symbol))
    df_0 = get_wma_data(symbol=symbol, num_points=num_points,
                        period=period_0, interval=interval,
                        series_type=series_type)
    df_1 = get_wma_data(symbol=symbol, num_points=num_points,
                        period=period_1, interval=interval,
                        series_type=series_type)
    df_price = get_daily_price_data(symbol=symbol)
    line_specification_0 = line_generator(line_number=0)
    line_specification_1 = line_generator(line_number=1)
    line_specification_price = line_generator(line_number=2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_0.loc[0],
                             y=df_0.loc[1],
                             line=line_specification_0,
                             mode='lines'))
    fig.add_trace(go.Scatter(x=df_1.loc[0],
                             y=df_1.loc[1],
                             line=line_specification_1,
                             mode='lines'))
    fig.add_trace(go.Scatter(x=df_price.loc[0],
                             y=df_price.loc[1],
                             line=line_specification_price,
                             mode='lines'))
    fig.write_image(file_name)
    return file_name
