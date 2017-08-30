from db.populate_db import DBClient as client
from chart.candlestick import MyPlot as MP
import strategy.simple_strategies as st
import matplotlib.pyplot as plt
import pandas as pd
from strategy.ichimoku_strategy import ichimoku_df
from strategy.ichimoku_strategy import ichimoku_analysis


if __name__== '__main__':
    cli = client('BOM_532922')
    #cli.create_database()
    #cli.write_database( {'open': q.open_, 'high': q.high,
    #                     'low': q.low, 'close': q.close,
    #                     'volume': q.volume}, q.date)
    #To Do create a api for time query
    #data = cli.read_database('select * from BOM_533278 where time >= \'2017-03-27\' and time < \'2017-03-28\'')['BOM_500325']
    #data['new']= st.get_SMA(data, 10)['high']
    #print  data #pd.concat([data, sma], axis=1)
    #pl = MP()
    #pl.pandas_candlestick_ohlc(data ,otherseries = 'new')
    print "First Candle stick completed"
    #pl.show_plot()
    data = cli.read_database('select * from BOM_532922')['BOM_532922']
    print "Second db read"
    #data['SMA']= st.get_SMA(data, 10)['close']
    print "Going to create second candle stick"
    #pl.pandas_candlestick_ohlc(data)# ,otherseries ='SMA')
    #pl.weekday_ohlc(data)
    print "creating plot"
    ichimoku = ichimoku_df(data, period = 10)
    #print data
    ichimoku_analysis(ichimoku) 
    #pl.add_ichimoku(data)
    #pl.show_plot()


