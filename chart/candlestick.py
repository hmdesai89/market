from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY, date2num , num2date
from matplotlib.finance import candlestick_ohlc
#from db.populate_db import DBClient as client
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np

class MyPlot():
    
    def __init__(self):
        self.plot=None
        self.fig, self.ax = plt.subplots()


    def show_plot(self):
        plt.show()
        
     
    def pandas_candlestick_ohlc(self,dat, stick = "day", otherseries = None):
        """
        :param dat: pandas DataFrame object with datetime64 index, and float columns "Open", "High", "Low", and "Close", likely created via DataReader from "yahoo"
        :param stick: A string or number indicating the period of time covered by a single candlestick. Valid string inputs include "day", "week", "month", and "year", ("day" default), and any numeric input indicates the number of trading days included in a period
        :param otherseries: An iterable that will be coerced into a list, containing the columns of dat that hold other series to be plotted as lines
     
        This will show a Japanese candlestick plot for stock data stored in dat, also plotting other series if passed.
        """
        mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
        alldays = DayLocator()              # minor ticks on the days
        dayFormatter = DateFormatter('%d')      # e.g., 12
     
        # Create a new DataFrame which includes OHLC data for each period specified by stick input
        transdat = dat.loc[:,["open", "high", "low", "close"]]
        if (type(stick) == str):
            if stick == "day":
                plotdat = transdat
                stick = 1 # Used for plotting
            elif stick in ["week", "month", "year"]:
                if stick == "week":
                    transdat["week"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[1]) # Identify weeks
                elif stick == "month":
                    transdat["month"] = pd.to_datetime(transdat.index).map(lambda x: x.month) # Identify months
                transdat["year"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[0]) # Identify years
                grouped = transdat.groupby(list(set(["year",stick]))) # Group by year and other appropriate variable
                plotdat = pd.DataFrame({"Open": [], "High": [], "Low": [], "Close": []}) # Create empty data frame containing what will be plotted
                for name, group in grouped:
                    plotdat = plotdat.append(pd.DataFrame({"Open": group.iloc[0,0],
                                                "High": max(group.High),
                                                "Low": min(group.Low),
                                                "Close": group.iloc[-1,3]},
                                               index = [group.index[0]]))
                if stick == "week": stick = 5
                elif stick == "month": stick = 30
                elif stick == "year": stick = 365
     
        elif (type(stick) == int and stick >= 1):
            transdat["stick"] = [np.floor(i / stick) for i in range(len(transdat.index))]
            grouped = transdat.groupby("stick")
            plotdat = pd.DataFrame({"Open": [], "High": [], "Low": [], "Close": []}) # Create empty data frame containing what will be plotted
            for name, group in grouped:
                plotdat = plotdat.append(pd.DataFrame({"Open": group.iloc[0,0],
                                            "High": max(group.High),
                                            "Low": min(group.Low),
                                            "Close": group.iloc[-1,3]},
                                           index = [group.index[0]]))
     
        else:
            raise ValueError('Valid inputs to argument "stick" include the strings "day", "week", "month", "year", or a positive integer')
     
     
        # Set plot parameters, including the self.axis object ax used for plotting
        self.fig.subplots_adjust(bottom=0.2)
        if plotdat.index[-1] - plotdat.index[0] < pd.Timedelta('730 days'):
            weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
            self.ax.xaxis.set_major_locator(mondays)
            self.ax.xaxis.set_minor_locator(alldays)
        else:
            weekFormatter = DateFormatter('%b %d, %Y')
        self.ax.xaxis.set_major_formatter(weekFormatter)
     
        self.ax.grid(True)
     
        # Create the candelstick chart
    
        candlestick_ohlc(self.ax, list(zip(list(date2num(dat.index.tolist())), dat["open"].tolist(), dat["high"].tolist(),
                          dat["low"].tolist(), dat["close"].tolist())),
                          colorup = "black", colordown = "red", width = stick * .4)
     
        # Plot other series (such as moving averages) as lines
        if otherseries != None:
            if type(otherseries) != list:
                otherseries = [otherseries]
            dat.loc[:,otherseries].plot(ax = self.ax, lw = 1.3, grid = True)
     
        # self.ax.xaxis_date()
        self.ax.autoscale_view()
        self.fig.autofmt_xdate() 
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
     
        #plt.show()

    def add_ichimoku(self, dat):
            dat.loc[:,['chikou_span']].plot(ax = self.ax, lw = 1.3, grid = True)
    
    
    def weekday_ohlc(self, ohlc_data, fmt='%b %d', freq=7, **kwargs):
        """ Wrapper function for matplotlib.finance.candlestick_ohlc
            that artificially spaces data to avoid gaps from weekends """
    
        # Convert data to numpy array
        ax = self.ax
        ohlc_data_arr = np.array(ohlc_data)
        ohlc_data_arr2 = np.hstack(
            [np.arange(ohlc_data_arr[:,0].size)[:,np.newaxis], ohlc_data_arr[:,1:]])
        ndays = ohlc_data_arr2[:,0]  # array([0, 1, 2, ... n-2, n-1, n])
    
        # Convert matplotlib date numbers to strings based on `fmt`
        dates = ndays
        print dates
        date_strings = []
        for date in dates:
            date_strings.append(date.strftime(fmt))
    
        # Plot candlestick chart
        candlestick_ohlc(ax, ohlc_data_arr2, **kwargs)
    
        # Format x axis
        ax.set_xticks(ndays[::freq])
        ax.set_xticklabels(date_strings[::freq], rotation=45, ha='right')
        ax.set_xlim(ndays.min(), ndays.max())
     
    
if __name__ == '__main__' :
    cli = client('BOM_500325')
    #cli.create_database()
    #cli.write_database( {'open': q.open_, 'high': q.high,
    #                     'low': q.low, 'close': q.close,
    #                     'volume': q.volume}, q.date)
    #To Do create a api for time query
    data = cli.read_database('select * from BOM_500325 where time >= \'2017-03-27\' and time < \'2017-03-27\'')['BOM_500325']
    #print(data.loc['2017-03-27':'2017-03-30'])
    pandas_candlestick_ohlc(data)
  

