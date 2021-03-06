## standard libraries
import sys, os, time, io
import datetime

## postgre database
import psycopg2
import gnupg

## signal processing and math
import signal
import numpy as np

## to create threads
import multiprocessing as mp

## For the web service
import tornado.ioloop
import tornado.web as web
import logging

## Import internal modules
import faroreDB
from handler_Main import *
from handler_Inductions import *
from handler_Metadata import *
from handler_DataServing import *
from handler_DataIntegrationSocket import *
from handler_logging import *



class FaroreServer:

    def __init__(self, conffile = 'config'):
        """ This starts the server.
        """

        ## Setting up the logging
        logging.basicConfig(filename='farore_server.log',
                            level=logging.DEBUG,
                            format='%(name)s @ %(levelname)s # %(asctime)s -- %(message)s')

        logging.getLogger('gnupg').disabled = True

        ## Getting configurations
        self.readConfigFile(conffile)

        ## Starting the database
        self.db = faroreDB.db(self.db_username,
                                self.db_password, self.db_database)

        args = { 'database' : self.db, 'IPs' : self.IPs }
        argsD = { 'database' : self.db, 'IPs' : self.IPs, 'tmpFolder' : self.tmpFolder }
        args2 = { 'database' : self.db, 'IPs' : self.IPs, 'homedir' : self.homedir }

        ## Starting tornado
        handlers = [
            (r'/', MainHandler),
            (r'/logging', loggingHandler, args),
            (r'/serveTimeSeries', serveFileHandler, args2),
            (r'/DataIntegration', dataIntegrationHandler, argsD),
            (r'/input_metadata', inputMetadataHandler, args),
            (r'/input_enoseConf', inputEnoseConfigHandler, args),
            (r'/metadata_action', actionMetadataHandler, args),
            (r'/enoseConf_action',actionEnoseConfigHandler, args),
            (r'/list_inductions', listInductionsHandler, args),
            (r'/updateInductionIndex', updateInductionIndexHandler, args),
            (r'/list_enoseConf', listEnoseConfHandler, args),
            (r'/view', viewInductionHandler, args),
            (r'/showTimeSeries', showTimeSeriesHandler, args),
            (r'/showInduction', showInductionHandler, args),

        ]

        settings = dict(
            static_path = os.path.join(os.path.dirname(__file__), "pages")
            )

        application = web.Application(handlers, **settings)
        application.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()

        return



    def readConfigFile(self, configFile):
        """ This method reads the configuration file, and gets the metadata to access 
        the database, list of IPs allowed to connect to the server, and the directory 
        where the GPG keys are stored.
        """

        config = open(configFile, 'r')

        self.port = int( config.readline().split("\n")[0] )

        self.db_username = config.readline().split("\n")[0]
        self.db_password = config.readline().split("\n")[0]
        self.db_database = config.readline().split("\n")[0]

        self.IPs = config.readline().split("\n")[0].split(",")

        self.tmpFolder = config.readline().split("\n")[0]

        self.homedir = config.readline().split("\n")[0]

        config.close()

        return




if __name__ == "__main__":
    server = FaroreServer()
