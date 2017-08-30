import pandas as pd 

def get_SMA(df, period = 1 ):
   return  pd.rolling_mean(df,period)

