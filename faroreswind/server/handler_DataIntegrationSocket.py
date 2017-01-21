# standard libraries
import sys, os, time, io
import datetime
import logging
import numpy as np

# postgre database
import psycopg2

# to create threads
import multiprocessing as mp


# For the web service
import tornado
import tornado.ioloop
import tornado.web as web
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httpserver
import numpy as np
import tornado.websocket
import json
import urlparse
import time
import threading
import functools
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient

# Our own library
import faroreDB



class dataIntegrationHandler(tornado.websocket.WebSocketHandler):

    state = 0
    currentClient = 0

    ###
    # Dictionary of the state
    #
    # 0 -> doing nothin'
    # 1 -> started talking to another process
    # 2 -> processing file
    # 3 -> finishing another process
    #
    ###

    def initialize(self, database, IPs, tmpFolder):
        self.db = database
        self.IPs = IPs
        self.tmpFolder = tmpFolder
        return


    ## THE CLIENT connected
    def open(self):
        print self.state
        logging.info("DataIntgr. New client connected into DataIntegration from " +str(self.request.remote_ip) )

        if self.state == 0:
            self.write_message("Free")
            dataIntegrationHandler.state = 1
            dataIntegrationHandler.currentClient = self

        else:
            self.write_message("Busy")

        return

    ## The client sent the message
    def on_message(self, message):

        if dataIntegrationHandler.currentClient == self:

            if message == "sending":
                logging.info("DataIntgr. Client exporting and sending data (from " +str(self.request.remote_ip)+ ")" )
                self.write_message("Waiting")


            elif 'My name:' in message:
                self.enose_id =  int(message.split(':')[1])
                logging.info("DataIntgr. Client identified as hal" +str(self.enose_id)+ "k (from " +str(self.request.remote_ip)+ ")" )


            elif message == "sent":
                print self.enose_id
                logging.info("DataIntgr. Client sent data (from " +str(self.request.remote_ip)+ ")" )

                for file in os.listdir(self.tmpFolder):
                    if file.startswith("NewData_"+str(self.enose_id)):

                        ## Removing extension
                        filename = file[:-4]
                        logging.info("DataIntgr. Processing file " +filename+ " (from " +str(self.request.remote_ip)+ ")" )
                        self.write_message("Processing")


                        ## Converting into CSV file
                        ym = filename.split('_')[2]
                        dia = filename.split('_')[3]
                        os.system("python "+self.tmpFolder+"npy2csv_convert.py "+self.tmpFolder+filename
                                    +".npy "+dia+" "+ym+" "+str(self.enose_id))

                        ## Importing into the DATABASE
                        self.db.copy("measurement",self.tmpFolder+filename+".csv")

                        logging.info("DataIntgr. New data processed and stored (from " +str(self.request.remote_ip)+ ")" )

                        ## Cleaning files
                        os.system("mv "+self.tmpFolder+filename+ ".npy "+self.tmpFolder+filename.split('New')[1]+".npy")
                        os.system("zip "+self.tmpFolder+filename.split('New')[1]+".zip "+self.tmpFolder+filename.split('New')[1]+".npy")
                        os.system("rm -f "+self.tmpFolder+filename+ ".csv")


                ## Finishing the process
                logging.info("DataIntgr. Done with newly data from " +str(self.request.remote_ip) )
                dataIntegrationHandler.state = 0

        else:
            self.write_message("Wait for your turn. Current status: "
                                    + str(dataIntegrationHandler.state) )
            print "Client disconnected."

        return


    ## Client disconnected
    def on_close(self):

        logging.info("Connected to DataIntegration closed from " +str(self.request.remote_ip) )
        if dataIntegrationHandler.currentClient == self:
            dataIntegrationHandler.currentClient = 0
        return
