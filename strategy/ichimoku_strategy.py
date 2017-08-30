import pandas as pd
import pdb
import math
from matplotlib.dates import date2num , num2date


def ichimoku_df(df, period = 1, last_index = []):


    transdat = df.loc[:,["open", "high", "low", "close"]]
    transdat["minute"] = [math.ceil(x/period) for x in transdat.index.minute]
    transdat["hour"] = [x for x in transdat.index.hour]
    transdat["date"] = [x for x in transdat.index.date]
    grouped = transdat.groupby(["date","hour", "minute"])
    plotdat = pd.DataFrame({"open": [], "high": [], "low": [], "close": []})
    for name,group in grouped:
        plotdat = plotdat.append(pd.DataFrame({"open": group.iloc[0,0],
                                               "high": max(group.high),
                                                "low": min(group.low),
                                                "close": group.iloc[-1,3]},
                                               index = [group.index[0]]))

    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    period9_high = pd.rolling_max(plotdat['high'], window=9)
    period9_low = pd.rolling_min(plotdat['low'], window=9)
    tenkan_sen = (period9_high + period9_low) / 2
    plotdat['tenkan_sen'] = tenkan_sen
 
    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = pd.rolling_max(plotdat['high'], window=26)
    period26_low = pd.rolling_min(plotdat['low'], window=26)
    kijun_sen = (period26_high + period26_low) / 2
    plotdat['kijun_sen'] = kijun_sen
    
    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
    plotdat['senkou_span_a'] = senkou_span_a
    
    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = pd.rolling_max(plotdat['high'], window=52)
    period52_low = pd.rolling_min(plotdat['low'], window=52)
    senkou_span_b = ((period52_high + period52_low) / 2).shift(26)
    plotdat['senkou_span_b'] = senkou_span_b

    # The most current closing price plotted 22 time periods behind (optional)
    chikou_span = plotdat['close'].shift(-26) # 22 according to investopedia
    plotdat['chikou_span'] = chikou_span


    if isinstance(last_index, list):
        return plotdat
    else :
        return plotdat[last_index:]


def ichimoku_analysis(df, st,prev = ['',0,'']):
    chikou_signal = 'HOLD'
    avg_signal = 'HOLD'
    cloud_signal = 'HOLD'
    state = ''
    signal = prev[:3]
    df['ang_kijun'] = df.kijun_sen.diff(5)
    df['chikou_signal'] = (df.chikou_span - df.close).shift(26)

    # print df.loc[:,['ang_kijun','kijun_sen']]
    profit = 0
    bp = 0
    sp = 0
    if prev[0] == "BUY":
        bp = prev[1]
        state = 'BOUGHT'
    elif prev[0] == "SELL":
        sp = prev[1]
   
    date = prev[2]

    for index,data in df.iterrows():
        if data['chikou_signal'] > 0:
	    chikou_signal = 'BUY'
	else :
	    chikou_signal = 'SELL'
	if (max(data['senkou_span_a'],data['senkou_span_b']) <  data['close']) :
	    cloud_signal = 'BUY'
	else :
	    cloud_signal = 'SELL'

	if data['tenkan_sen'] > data['kijun_sen'] :
	    avg_signal = 'BUY'
	else :
	    avg_signal = 'SELL'

        if state == "BOUGHT" and min(data['senkou_span_a'],data['senkou_span_b']) > data['close'] :
            ultimate_sell = True
        else :
            ultimate_sell = False

	if ( chikou_signal == 'BUY' and cloud_signal == 'BUY' and
	     (data['ang_kijun']/data['close']) > 0.003
              and state == '' ): # Removed avg signal in buying 
            bp =  data['close']
	    state = 'BOUGHT'
            date = index
            signal = ["BUY", bp, date]
            print "----BUY "+st.name
            print signal
            st.signal = signal

        
 
	elif ( (state == 'BOUGHT' and  avg_signal == 'SELL' and
	       chikou_signal == 'SELL' and (abs( data['ang_kijun'])/data['close']) > 0.005)
               or ultimate_sell) : 
               #or (state == 'BOUGHT' and cloud_signal == 'SELL' )):
            sp =  data['close']
	    state = ''
            profit += (sp-bp)
            date = index
            signal = ["SELL", sp, date]
            print "---Selling "+st.name
            print signal
            st.signal = signal
            print "Transaction ---->"
            print sp-bp
            st.profit += (sp -bp)
            st.transection += 1

	

    #print '-------------Brace yourself Profit-------------'
    #print profit
    return signal
