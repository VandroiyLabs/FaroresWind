# standard libraries
import sys, os, time, io
import datetime

# postgre database
import psycopg2

# signal processing and math
import signal
import numpy as np

# to create threads
import multiprocessing as mp

# For plot
import matplotlib as mpl
mpl.use('Agg')
import pylab as pl

# For the web service
import tornado.ioloop
import tornado.web as web
import logging


# Our own library
import faroreDB
from handlers import *
from DataIntegrationSocket import *







class FaroreServer:

    def __init__(self, conffile = 'config'):

        ## Setting up the logging
        logging.basicConfig(filename='farore_server.log',
                            level=logging.DEBUG,
                            format='%(name)s @ %(levelname)s # %(asctime)s -- %(message)s')


        ## Getting configurations
        self.readConfigFile(conffile)

        ## Starting the database
        self.db = faroreDB.db(self.db_username,
                              self.db_password, self.db_database)

        args = { 'database' : self.db, 'IPs' : self.IPs }

        ## Starting tornado
        handlers = [
            (r'/', MainHandler),
            (r'/DataIntegration', dataIntegrationHandler, args),
            (r'/input_metadata', inputMetadataHandler, args),
            (r'/input_enoseConf', inputEnoseConfigHandler, args),
            (r'/metadata_action', actionMetadataHandler, args),
            (r'/enoseConf_action', actionEnoseConfigHandler, args),
            (r'/list_inductions', listInductionsHandler, args),
            (r'/list_enoseConf', listEnoseConfHandler, args),
            (r'/view', viewInductionHandler, args),
            (r'/showTimeSeries', showTimeSeriesHandler, args),
            (r'/showInduction', showInductionHandler, args),

        ]

        settings = dict(
            static_path = os.path.join(os.path.dirname(__file__), "pages")
            )

        application = web.Application(handlers, **settings)
        application.listen(8799)
        tornado.ioloop.IOLoop.instance().start()

        return



    def readConfigFile(self, configFile):

        config = open(configFile, 'r')

        self.db_username = config.readline().split("\n")[0]
        self.db_password = config.readline().split("\n")[0]
        self.db_database = config.readline().split("\n")[0]

        self.IPs = config.readline().split("\n")[0].split(",")

        config.close()

        return




if __name__ == "__main__":
    server = FaroreServer()
