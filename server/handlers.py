import psycopg2
import faroreDB

import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httpserver
import logging
import json
import urlparse
import time
import threading
import functools
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('pages/index.html')
        print self.request.remote_ip
        return



class inputMetadataHandler(tornado.web.RequestHandler):
    def get(self):
        
        if self.request.remote_ip[:-2] == '132.239.77.':
            self.render('pages/input_metadata.html')
        
        return



class listInductionsHandler(tornado.web.RequestHandler):
    
    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return
    
    def get(self):
        
        print self.request.remote_ip
        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:
            
            self.write( file("pages/top.html").read() )
            
            # Retrieving data from inductions
            db = self.db
            listInds = self.db.getInductionsMetadata( limit=50 )
            
            for ind in listInds:
                self.write("----------------")
                self.write("<p>Induction code: " + str(ind[0]) + "</p>")
                self.write("<p>Sample: " + str(ind[5]) + " - Enose: hal" + str(ind[8])+"k </p>")

                date = str(ind[1])[:9]
                t0   = str(ind[1])[10:]
                tc   = str(ind[2])[10:]
                
                self.write("<p>Date: " + date + "  - t0: " + t0 + " - tc: " + tc  + "</p>")
                self.write("<p>Click to see more details...</p>")
                
            self.write( file("pages/bottom.html").read() )
            
        return





class viewInductionHandler(tornado.web.RequestHandler):
    
    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    
    def get(self):
        
        print self.request.remote_ip
        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:
            
            self.write( file("pages/top.html").read() )
            
            # Retrieving data from inductions
            db = self.db
            listInds = self.db.getSamples( 2, "2016-12-25 00:00:00", "2016-12-25 01:00:00" )
            
            self.write( len(listInds) )
                
            self.write( file("pages/bottom.html").read() )
            
        return




    
class actionMetadataHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    
    def post(self):
        
        if self.request.remote_ip[:-2] == self.IPs[0]:
            self.render('pages/metadata_action.html')
            
            date = self.get_argument('date', '')
            t0 = self.get_argument('t0', '')
            tc = self.get_argument('tc', '')
            delta0 = self.get_argument('delta0', '')
            deltac = self.get_argument('deltac', '')
            sample = self.get_argument('sample', '')
            weather = self.get_argument('weather', '')
            enose =  self.get_argument('enose', '')
            
            if len(enose) > 1:
                enose = enose[3]
            
            self.db.insertInduction(date, t0, tc, delta0, deltac, sample, weather, enose)
            
            return
