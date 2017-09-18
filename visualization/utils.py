import bokeh
from bokeh.plotting import figure, show, output_file, save, ColumnDataSource
from bokeh.layouts import gridplot
from bokeh.embed import components
from bokeh.palettes import Spectral4
from bokeh.models import HoverTool, NumeralTickFormatter
from math import pi
import pandas as pd
import numpy as np
import quandl
quandl.ApiConfig.api_key = "yg94pP6kwTx8vKNJYaDc"
# Create your views here.


def volume_helper(ticker, hover, tools, source, p1):
    """ Creates a volume graph below the chose graph based on stock data with joined interactive x-axis.
    :param ticker:
    :param hover:
    :param tools:
    :param source:
    :param p1:
    :return:
    """
    if p1:
        p = figure(plot_width=1000, plot_height=200, x_axis_type='datetime', x_range=p1.x_range,
                   active_scroll='wheel_zoom', active_drag='pan', tools=[hover, tools], title='Volume for {}'.format(ticker))
    else:
        p = figure(plot_width=1000, plot_height=200, x_axis_type='datetime', active_scroll='wheel_zoom',
                   active_drag='pan', tools=[hover, tools], title='Volume for {}'.format(ticker))
    p.grid.grid_line_alpha = 0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Volume'
    p.line('x', 'Volume', color='#A6CEE3', source=source)
    p.yaxis.formatter = NumeralTickFormatter(format="00")
    p.legend.location = 'top_left'
    return p


def single_stock(ticker):
    """Creates an interactive graph based on a ticker with it's Adjusted High, Open, Low, Close
    :param ticker: str
    :return: Bokeh Plot
    """
    # choices is OHLC Adj O/C or Vol
    api_req = quandl.get('WIKI/{}'.format(ticker))
    df = api_req
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    source = ColumnDataSource(data=dict(
        x=df['Date'],
        y=df['Adj. High'],
        y1=df['Adj. Open'],
        y2=df['Adj. Low'],
        y3=df['Adj. Close'],
        Volume=df['Volume'],
    ))
    tools = 'pan,wheel_zoom,box_zoom,reset,save'
    hover = HoverTool(tooltips=[
        ("Date", "@x{%F}"),
        ("Adj. High", "@y"),
        ("Adj. Open", "@y1"),
        ("Adj. Low", "@y2"),
        ("Adj. Close", "@y3"),
        ("Volume", "@Volume{0.00 a}"),
    ], formatters={
        'x': 'datetime',
        },
        mode='mouse'
    )
    p = figure(plot_width=1000, plot_height=400, x_axis_type='datetime', tools=[hover, tools],
               title='{}'.format(ticker), active_scroll='wheel_zoom', active_drag='pan', toolbar_location='above')
    p.grid.grid_line_alpha = 0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.legend.location = 'top_right'
    p.line('x', 'y', legend='Adjusted High', color=Spectral4[0], alpha=0.5, source=source)
    p.line('x', 'y1', legend='Adjusted Open', color=Spectral4[1], alpha=0.5, source=source)
    p.line('x', 'y2', legend='Adjusted Low', color=Spectral4[2], alpha=0.5, source=source)
    p.line('x', 'y3', legend='Adjusted Close', color=Spectral4[3], alpha=0.5, source=source)
    p2 = volume_helper(ticker, hover, tools, source, p)
    p.legend.click_policy = "hide"
    return gridplot([p, p2], ncols=1, merge_tools=True, match_aspect=True)


def make_candlestick(ticker):
    """ Creates a candlestick graph based on a stock ticker
    :param ticker: str
    :return: Bokeh Plot
    """
    api_req = quandl.get('WIKI/{}'.format(ticker))
    df = api_req
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    inc = df['Adj. Close'] > df['Adj. Open']
    dec = df['Adj. Open'] > df['Adj. Close']
    source = ColumnDataSource(data=dict(
        x=df['Date'],
        y=df['Adj. High'],
        y1=df['Adj. Open'],
        y2=df['Adj. Low'],
        y3=df['Adj. Close'],
        Volume=df['Volume'],
    ))
    tools = 'pan,wheel_zoom,box_zoom,reset,save'
    hover = HoverTool(tooltips=[
        ("Date", "@x{%F}"),
        ("Adj. High", "@y"),
        ("Adj. Open", "@y1"),
        ("Adj. Low", "@y2"),
        ("Adj. Close", "@y3"),
        ("Volume", "@Volume{0.00 a}"),
    ], formatters={
        'x': 'datetime',
    },
        mode='vline'
    )
    w = 12 * 60 * 60 * 1000
    p = figure(plot_width=1000, plot_height=400, x_axis_type="datetime", tools=[hover, tools],
               active_scroll='wheel_zoom', active_drag='pan', title="{} Candlestick Graph".format(ticker))

    p.xaxis.major_label_orientation = pi/4
    p.grid.grid_line_alpha = 0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.segment(df.Date, df['Adj. High'], df.Date, df['Adj. Low'], color='black', source=source, line_width=0.5)
    p.vbar(df.Date[inc], w, df['Adj. Open'][inc], df['Adj. Close'][inc], fill_color="#D5E1DD", line_color="black",
           line_width=0.5)
    p.vbar(df.Date[dec], w, df['Adj. Open'][dec], df['Adj. Close'][dec], fill_color="#F2583E", line_color="black",
           line_width=0.5)
    p2 = volume_helper(ticker, hover, tools, source, p)
    return gridplot([p, p2], ncols=1)


def month_average(ticker):
    """Creates a One-Month Average graph
    :param ticker: str
    :return: Bokeh Plot
    """
    api_req = quandl.get('WIKI/{}'.format(ticker))
    df = api_req
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    stock = np.array(df['Adj. Close'])  # eventually make drop down menu for any
    stock_dates = np.array(df['Date'], dtype=np.datetime64)
    window_size = 30
    window = np.ones(window_size)/float(window_size)
    stock_avg = np.convolve(stock, window, 'same')
    source = ColumnDataSource(data=dict(
        x=stock_dates,
        y=stock,
        h=stock_avg,
        Volume=df['Volume'],
    ))
    tools = 'pan,wheel_zoom,box_zoom,reset,save'
    hover = HoverTool(tooltips=[
        ("Date", "@x{%F}"),
        ("Price", "@y"),
        ("Volume", "@Volume{0.00 a}")
    ], formatters={
        'x': 'datetime',
    },
        mode='mouse'
    )
    p = figure(plot_width=1000, plot_height=400, x_axis_type='datetime', tools=[hover, tools],
               active_scroll='wheel_zoom', active_drag='pan', title='One Month Avg for {}'.format(ticker))
    p.grid.grid_line_alpha = 0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.ygrid.band_fill_color = 'olive'
    p.ygrid.band_fill_alpha = 0.1
    p.circle('x', 'y', size=4, legend='close', color='darkgrey', alpha=0.4, source=source)
    p.line('x', 'h', legend='avg', color='navy', source=source)
    p.legend.location = 'top_left'
    p2 = volume_helper(ticker, hover, tools, source, p)
    return gridplot([p, p2], ncols=1, merge_tools=True, match_aspect=True)
