import argparse
import pandas as pd

from logging import log as LOG
from influxdb import DataFrameClient
from influxdb import InfluxDBClient


class DBClient() :
    def __init__(self,dbname,host='localhost',port=8086,user='root',password='root'):
        self.db = dbname
        self.client = DataFrameClient(host, port, user, password, dbname)

    def create_database(self):
        #LOG.info('Creating db - '+ self.db)
	self.client.create_database(self.db)

    def delete_database(self):
        #LOG.info('Deleting db - '+ self.db)
	self.client.drop_database(self.db)

    def write_database(self, data, timelist ):
        index = pd.DatetimeIndex(pd.to_datetime(timelist,unit='s')) 
        df = pd.DataFrame(data=data,
                      index=index)
        print self.db
        self.client.write_points(df, self.db)

    def read_database(self, query):
        p = self.client.query(query)
	return p

        

if __name__ == '__main__':
    #args = parse_args()
    #main(host=args.host, port=args.port)
    client = DBClient('BOM_51128812')
    #client.create_database()
    # client.write_database( {'colA': [1,2], 'colB': [3,4]}, [1349720105,1349720106])
    client.read_database('select * from BOM_51128812')
    #client.delete_database()
