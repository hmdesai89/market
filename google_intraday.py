# Copyright (c) 2014, Mark Chenoweth
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted 
# provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following 
#     disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS 
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import urllib,time,datetime
from db.populate_db import DBClient as client

class CompanyException(Exception):
    pass


class Quote(object):
    
    DATE_FMT = '%Y-%m-%d'
    TIME_FMT = '%H:%M:%S'
    
    def __init__(self):
      self.symbol = ''
      self.date,self.open_,self.high,self.low,self.close,self.volume = ([] for _ in range(6))

    def append(self,dt,open_,high,low,close,volume):
      self.date.append(int(dt))
      self.open_.append(float(open_))
      self.high.append(float(high))
      self.low.append(float(low))
      self.close.append(float(close))
      self.volume.append(int(volume))
        
    def to_csv(self):
      return ''.join(["{0},{0},{1},{2:.2f},{3:.2f},{4:.2f},{5:.2f},{6}\n".format(self.symbol,
                self.date[bar],
                self.open_[bar],self.high[bar],self.low[bar],self.close[bar],self.volume[bar]) 
                for bar in xrange(len(self.close))])
      
    def write_csv(self,filename):
      with open(filename,'w') as f:
        f.write(self.to_csv())
          
    def read_csv(self,filename):
      self.symbol = ''
      self.date,self.time,self.open_,self.high,self.low,self.close,self.volume = ([] for _ in range(7))
      for line in open(filename,'r'):
        symbol,ds,ts,open_,high,low,close,volume = line.rstrip().split(',')
        self.symbol = symbol
        dt = datetime.datetime.strptime(ds+' '+ts,self.DATE_FMT+' '+self.TIME_FMT)
        self.append(dt,open_,high,low,close,volume)
      return True

    def __repr__(self):
      return self.to_csv()

class GoogleIntradayQuote(Quote):
    ''' Intraday quotes from Google. Specify interval seconds and number of days '''
    def __init__(self,symbol,interval_seconds=300,num_days=5,exchange='BOM', mins = False):
      super(GoogleIntradayQuote,self).__init__()
      self.symbol = symbol.upper()
      url_string = "http://www.google.com/finance/getprices?q={0}".format(self.symbol)
      if mins:
          url_string += "&i={0}&p={1}m&f=d,o,h,l,c,v&i={2}".format(interval_seconds,num_days,exchange)
      else :
          url_string += "&i={0}&p={1}d&f=d,o,h,l,c,v&i={2}".format(interval_seconds,num_days,exchange)
      done = True
      while (done):
        try:
          resp = urllib.urlopen(url_string)
          done = False
        except:
          print 'TIME OUT !!!!!'

      if (resp.getcode() == 400):
        ip = raw_input("Press Enter Y after duping google..."+code)
        if ip == 'y' :
          url_string = "http://www.google.com/finance/getprices?q={0}".format(self.symbol)
          url_string += "&i={0}&p={1}d&f=d,o,h,l,c,v&i={2}".format(interval_seconds,num_days,exchange)
          resp = urllib.urlopen(url_string)
      elif (resp.getcode() == 302):
        print 'Fishy !!!!!'
        return
      #print resp.read()
      csv = resp.readlines()
      for bar in xrange(7,len(csv)):
        if csv[bar].count(',')!=5: continue
        offset,close,high,low,open_,volume = csv[bar].split(',')
        if offset[0]=='a':
          day = float(offset[1:])
          offset = 0
        else:
          offset = float(offset)
        open_,high,low,close = [float(x) for x in [open_,high,low,close]]
        dt = (day+(interval_seconds*offset))
        self.append(dt,open_,high,low,close,volume)
     
def find_company(symbol,exchange):
    ''' Intraday quotes from Google. Specify interval seconds and number of days '''
    symbol = symbol.upper()
    url_string = "http://www.google.com/finance/info?q={0}&e={1}".format(symbol,exchange)
    done = True
    while (done):
        try:
            resp = urllib.urlopen(url_string)
	    done = False
        except:
	    print 'TIME OUT happnend'
    return resp.getcode()


def populate_db(code,exchange):
    cli = client(exchange+'_'+str(code))
    q = GoogleIntradayQuote(str(code),120,100,exchange)
    if q.date == []:
        return False
    cli.create_database()
    cli.write_database( {'open': q.open_, 'high': q.high,
                         'low': q.low, 'close': q.close,
                         'volume': q.volume}, q.date)
    return True
 
     
if __name__ == '__main__':
    # populate_db(511766, 'BOM')
    q = GoogleIntradayQuote('532922',120,100,'BOM')
    if q.date == []:
        raise CompanyException("No company in this ticker")
    cli = client('BOM_532922')
    # cli.create_database()
    cli.write_database( {'open': q.open_, 'high': q.high,
                         'low': q.low, 'close': q.close,
                         'volume': q.volume}, q.date)
    data = cli.read_database('select * from BOM_532922')
    print data['BOM_532922']
    # cli.delete_database() 
    #print q                                          # print it out
    #print q.date
