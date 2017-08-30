from db.populate_db import DBClient as client
from google_intraday import GoogleIntradayQuote
import google_intraday as gi
import json
import copy
import sys
from strategy.ichimoku_strategy import ichimoku_analysis, ichimoku_df 
import time
from dataframes import Stock
from dataframes import Signals
import pandas as pd

COMPANY_LIST='interest.txt'

def return_json(f):
    with open(f) as json_data:
        return json.load(json_data)

def validate_company(code, exchange):
    code = gi.find_company(code,exchange) 
    if code == 200 :
        return True
    elif code == 400:
        return False


def main():
    print "Initiateing database !!!" 
    jd = return_json(COMPANY_LIST)
    for k in jd:
        if not gi.populate_db(jd[k][0], 'BOM'):
	    print (jd[k], ' not in BOM exchange')
	    jd[k][0] = ''
	    continue
	#if jd[k][1] == '':
	    #if not gi.populate_db(jd[k][1],'NSE'):
	#    print (jd[k], ' not in NSE exchange')
            #    jd[k][1] = ''
    print '-----------------------------------------'
    print jd
    #f = open('new_list','w')
    #f.write(jd)
    #f.close()

def populate_signal():
    cli = client('signal')
      
    cli.read_database("select * from signal")


def continuous():
    jd = return_json("interest.txt")
    sig = Signals('ichimoku_signal')
    signal = {}
    stocks = []
    #for k in jd:
    #    print "Populating "+k
    #    gi.populate_db(jd[k][0], 'BOM', True)
    for k in jd:
        print "populating "+ k
        st = Stock(k,jd[k][0],jd[k][1])
        st.read_database(time = '5d', limit = '5000')
        stocks.append(st)


    print "DB walk completed !!"
    while(True):
        for st in stocks:
            if st.name in signal :
                print "--"
                print st.name
                st.populate_df()
                temp = get_analysis(st.df[-380: ], signal[st.name], st, signal[st.name][3])
                temp.append(st.df.tail(1).index [0])
                print st.df.head(1).index [0]
                print temp
                signal[st.name]= temp
		sig.write_signal(st.name, temp)
            else :
                temp = get_analysis(st.df, ['',0,''], st)
                temp.append(st.df.tail(1).index [0])
                signal[st.name] = temp
                sig.write_signal(st.name, temp)

	time.sleep(600)
     

def sim():
    sig = Signals('ichimoku_signal_sim')
    jd = return_json("interest.txt")
    signal = {}
    stocks = []
    #for k in jd:
    #    print "Populating "+k
    #    gi.populate_db(jd[k][0], 'BOM', True)
    for k in jd:
        print "populating "+ k
        st = Stock(k,jd[k][0],jd[k][1])
        st.read_database(time = '7d', limit = '4000')
        stocks.append(st)
   
 
    
    ##DB is populated
    n = 0
    while(n < len(st.df) ):
        for st in stocks:
            if st.name in signal :
                if n+600 > len(st.df):
                    temp = get_analysis(st.df[n - 320: ], signal[st.name], st, signal[st.name][3])
                    temp.append(st.df.tail(1).index [0])
                else :
                    temp = get_analysis(st.df[n - 320: n+600], signal[st.name], st, signal[st.name][3])
                    temp.append(st.df[n:n+600].tail(1).index [0])
                signal[st.name]= temp
		sig.write_signal(st.name, temp)
            else :
                temp = get_analysis(st.df[n:n+600], ['',0,''], st)
                temp.append(st.df[n:n+600].tail(1).index [0])
                signal[st.name] = temp
                sig.write_signal(st.name, temp)



        n += 600


    print "-----Final--------"
    for st in stocks :
        print st.name
        print  st.profit
        print  st.transection


def get_analysis(df, prev, st, last_index = []):
    ichimoku = ichimoku_df(df, period = 6, last_index = last_index)
    return ichimoku_analysis(ichimoku, st,prev)
    

def get_analysis_signal(analysis_name, signal = ""):
    print "Filter Singal :"+ signal
    sig=Signals(analysis_name+"_signal")
    jd = return_json("interest.txt")
    for k in jd :
        
        op = sig.get_last(k)
        s = list(op)[0][0]
        if s != None and  "signal" in s:
            if signal == "":
	        print "Company name : "+k
                print ("Signal : {0}".format(s['signal']))
                print ("Price : {0}".format(s['price']))
                print ("Time : {0}".format(s["time"]))
	    elif signal == "BUY" and s["signal"] == "BUY":
                print "Company name : "+k
	        print ("Signal : {0}".format(s['signal']))
                print ("Price : {0}".format(s['price']))
                print ("Time : {0}".format(s["time"]))
            elif signal == "SELL" and s["signal"] == "SELL":
                print "Company name : "+k
                print ("Signal : {0}".format(s['signal']))
                print ("Price : {0}".format(s['price']))
                print ("Time : {0}".format(s["time"]))
 
 

        print "-------------"

if __name__ =='__main__':
    if sys.argv[1] == 'c':
        continuous() 

    elif sys.argv[1] == 'p':
        main()

    elif sys.argv[1] == 's':
        sim()

    elif sys.argv[1] == 'last':
        if len(sys.argv) > 2 :
            get_analysis_signal("ichimoku", sys.argv[2])
        else:
            get_analysis_signal("ichimoku")


    else:
       sig = Signals('test_signal_1')
       sig.write_signal('chal',['BUY', 205.30000000000001, '2017-05-12 07:12:00+0000'])
       sig.write_signal('chal',['SELL', 210.00, '2017-05-12 09:12:00+0000'])
       sig.write_signal('chal',['BUY', 207.30000000000001, '2017-05-13 07:12:00+0000'])
       sig.write_signal('chal',['SELL', 209.00, '2017-05-14 09:12:00+0000'])



