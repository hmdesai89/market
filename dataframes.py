from db.populate_db import DBClient as client
from google_intraday import GoogleIntradayQuote
import google_intraday as gi
import json
import copy
import sys
from strategy.ichimoku_strategy import ichimoku_analysis, ichimoku_df
import time
import pandas as pd
from influxdb import InfluxDBClient


class Stock():
    def __init__(self, company, BSE_CODE, NSE_CODE):
        self.name = company
	self.BSE_CODE = BSE_CODE
	self.NSE_CODE = NSE_CODE
        self.db = "BOM_"+BSE_CODE
        self.signal = []

        self.cli = client(self.db)
        self.cli.create_database()

        self.df = None
        self.transection = 0
        self.profit = 0

    def populate_database(self, interval = 120, delta = 30, exchange = 'BOM', minute=True ):
        q = GoogleIntradayQuote(self.BSE_CODE,intnterval,delta,exchange, True)
        if q.date == []:
            raise Exception("No company in this ticker")
        cli.write_database( {'open': q.open_, 'high': q.high,
                             'low': q.low, 'close': q.close,
                             'volume': q.volume}, q.date)

    def read_database(self, time = '1d', limit = '1000'):

        query = "select * from "+self.db
        if time:
            query += " where time > now() - "+time+" limit "+limit
        data = self.cli.read_database(query+" ;")
        if data != {}:
	    if  type(self.df) is type (data[self.db]) :
                self.df = self.df.append(data[self.db])
            else :
                self.df = data[self.db]

            return data[self.db]

        return data


    def populate_df(self,interval = 120, delta = '30m',exchange = 'BOM'):
        q = GoogleIntradayQuote(self.BSE_CODE,interval,delta,exchange, True)
        data = {"open" : q.open_, "high": q.high,
	        "low": q.low, "close": q.close , "volume": q.volume}
        index = pd.DatetimeIndex(pd.to_datetime(q.date,unit='s'))
	data = pd.DataFrame(data=data,index=index)

        if  type(self.df) is type(data) :
            self.df =  self.df.append(data)
        else :
            self.df = data


class Signals():
    def __init__(self, db = 'signal', host='localhost',port=8086,user='root',password='root'):
        self.db = db
        self.cli = InfluxDBClient(host, port, user, password, db)
        self.cli.create_database(db)

    def write_signal(self, name, signal):
        di  =  [
	       { 
	          "measurement" : name,
		  "time": signal[2],
	          "fields" : {
                               "price" : float(signal[1]),
                               "signal" : signal[0]
			     }
		}]
        self.cli.write_points(di)
        
    def get_last(self,msr) :
        return self.cli.query("select * from \""+msr+"\" GROUP BY * ORDER BY DESC LIMIT 1")




if __name__ == "__main__":
    st  = Stock("test123", "533107", "")
    st.read_database(time = '5d', limit = '5000')
    st.populate_df()
    print st.df
    print "---------------------------------------------"
    print st.df[:4]
    print "--------------------------------------"
    print st.df[-4:]
