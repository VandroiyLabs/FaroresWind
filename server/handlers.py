import psycopg2
import faroreDB

import io
import datetime

import numpy as np
import matplotlib
matplotlib.use('Agg')
import pylab as pl
import matplotlib.gridspec as gridspec

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
    
    
    def genImage(self, data):
        
        # Converting time from seconds to hours
        time = data[:,1]
        
        pl.figure( figsize=(8,5) )
        
        gs = gridspec.GridSpec(2, 2, height_ratios=[1.5,1], width_ratios = [1,1] )
        
        ## Starting with the sensorS
        sensorPanel = pl.subplot(gs[0,:])
        for j in range(4,12):
            sensorPanel.plot(time, data[:,j], '-')

        sensorPanel.set_ylabel("Sensor resistance")
        sensorPanel.set_xlabel('Time (h)')
        sensorPanel.set_xlim( time.min() - 0.01, time.max() + 0.01)
        sensorPanel.grid(True)
                    
        ## Temperature and humidity
        tempPanel = pl.subplot(gs[1,0])
        tempPanel.plot(time, data[:,2])
        tempPanel.set_ylabel("Temperature")
        tempPanel.set_xlabel('Time (h)')
        tempPanel.set_xlim( time.min() - 0.01, time.max() + 0.01)
        
        humdPanel = pl.subplot(gs[1,1])
        humdPanel.plot(time, data[:,3])
        humdPanel.set_ylabel("Humidity")
        humdPanel.set_xlabel('Time (h)')
        humdPanel.set_xlim( time.min() - 0.01, time.max() + 0.01)
        
        pl.tight_layout()
        
        memdata = io.BytesIO()
        pl.savefig(memdata, format='png')
        pl.close()
        
        image = memdata.getvalue()
        return image

    
    
    def get(self):
        
        print self.request.remote_ip
        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:

            ## Getting input variables
            datei = self.get_argument('datei', '')
            timei = self.get_argument('timei', '')
            datef = self.get_argument('datef', '')
            timef = self.get_argument('timef', '')
            enose = int( self.get_argument('enose', '') )

            print datei, timei, datef, timef
            
            ## Retrieving data from inductions
            samples = np.asarray(self.db.getSamples( enose,
                                                     datei + " " + timei,
                                                     datef + " " + timef ))
            
            ## Subsampling
            samples = samples[:: samples.shape[0]/1000, :]
            
            ## converting time to number
            samples[:,1] = matplotlib.dates.date2num( samples[:,1] )
            
            ## generating the plot
            image = self.genImage( samples )
            
            ## Printing to output...
            self.set_header('Content-type', 'image/png')
            self.set_header('Content-length', len(image))
            self.write(image)
            
        return




class showInductionHandler(tornado.web.RequestHandler):
    
    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return
    
    def post(self):
        
        print self.request.remote_ip
        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:
            
            datei = self.get_argument('datei', '')
            timei = self.get_argument('timei', '')
            datef = self.get_argument('datef', '')
            timef = self.get_argument('timef', '')
            enose = int( self.get_argument('enose', '') )
            
            
            self.write( file("pages/top.html").read() )
            
            self.write( "<img src=\"./view?" \
                        + "datei=2016-12-27&datef=2016-12-27&timei=14:00:00&timef=16:00:00" \
                        + "&enose=2\" />"
            )
            
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
