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

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    
    ## THE CLIENT connected
    def open(self):
        print self.state
        logging.info("New client connected into DataIntegration from " +str(self.request.remote_ip) )
        
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
                self.write_message("Waiting")
                
            elif message == "sent":
                self.write_message("Processing")

        else:
            self.write_message("Wait for your turn. Current status: "
                               + str(dataIntegrationHandler.state) )

        
        return
        
    ## Client disconnected
    def on_close(self):
        
        logging.info("Connected to DataIntegration closed from " +str(self.request.remote_ip) )
        if dataIntegrationHandler.currentClient == self:
            dataIntegrationHandler.currentClient = 0
        
        return
