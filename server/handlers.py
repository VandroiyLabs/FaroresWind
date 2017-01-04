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
                self.write("----------------\n")
                self.write("<p>Induction code: " + str(ind[0]) + "</p>\n")
                self.write("<p>Sample: " + str(ind[5]) + " - Enose: hal" + str(ind[8])+"k </p>\n")

                date = str(ind[1])[:10]
                t0   = str(ind[1])[10:]
                tc   = str(ind[2])[10:]
                
                self.write("<p>Date: " + date + "  - t0: " + t0 + " - tc: " + tc  + "</p>\n")                
                
                link = "<form action=\"./showInduction\" id=\"form" + str(ind[0]) + "\" method=\"post\">\n" \
                       + "<input type=\"hidden\" name=\"enose\" value=\""+str(ind[8])+"\" />\n" \
                       + "<input type=\"hidden\" name=\"datei\" value=\""+date+"\" />\n" \
                       + "<input type=\"hidden\" name=\"timei\" value=\""+t0+"\" />\n" \
                       + "<input type=\"hidden\" name=\"datef\" value=\""+date+"\" />\n" \
                       + "<input type=\"hidden\" name=\"timef\" value=\""+tc+"\" />\n" \
                       + "<p><a href=\"javascript:{}\" onclick=\"document.getElementById('form" + str(ind[0]) \
                       + "').submit(); return false;\">See induction</a></p>\n" \
                       + "</form>\n"

                self.write(link)
                self.write("\n\n")
                
            self.write( file("pages/bottom.html").read() )
            
        return





class viewInductionHandler(tornado.web.RequestHandler):
    
    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return
    
    
    def genImage(self, data, dtI, dtF):
        
        # Converting time from seconds to hours
        time = data[:,1]
        
        pl.figure( figsize=(8,5) )
        
        gs = gridspec.GridSpec(2, 2, height_ratios=[1.5,1], width_ratios = [1,1] )
        
        ## Starting with the sensorS
        sensorPanel = pl.subplot(gs[0,:])
        maxy = 0
        miny = 1e100
        for j in range(4,12):
            sensorPanel.plot(time, data[:,j], '-')

        maxy = np.max( np.max( data[:,4:12] ) )
        miny = np.min( np.min( data[:,4:12] ) )
        
        ## Drawing line when induction happened
        tI = matplotlib.dates.date2num( dtI )
        tF = matplotlib.dates.date2num( dtF )
        
        sensorPanel.plot( [tI, tI], [miny*0.5 , maxy*2], '--', color=(1.0,0.,0.0), lw=3., alpha=0.3, zorder=-1 )
        sensorPanel.plot( [tF, tF], [miny*0.5 , maxy*2], '--', color=(1.0,0.,0.0), lw=3., alpha=0.3, zorder=-1 )
        sensorPanel.set_ylim(miny*0.9, maxy*1.1)
        
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
        pl.savefig(memdata, format='png', dpi=400)
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


            ## Additional buffer for plot
            timebuffer = datetime.timedelta(seconds=1000)
            dtI = datetime.datetime.strptime( datei + " " + timei.split(".")[0], "%Y-%m-%d %H:%M:%S" )
            dtI_b = dtI - timebuffer
            dtF = datetime.datetime.strptime( datef + " " + timef.split(".")[0], "%Y-%m-%d %H:%M:%S" )
            dtF_b = dtF + timebuffer
            
            
            ## Retrieving data from inductions
            samples = np.asarray(
                self.db.getSamples( enose, str(dtI_b), str(dtF_b) )
            )
            
            print samples.shape
            
            ## Subsampling
            samples = samples[:: samples.shape[0]/1000, :]
            
            ## converting time to number
            samples[:,1] = matplotlib.dates.date2num( samples[:,1] )
            
            ## generating the plot
            image = self.genImage( samples, dtI, dtF )
            
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
            enose = self.get_argument('enose', '')
            
            
            self.write( file("pages/top.html").read() )
            
            self.write( "<img src=\"./view?" \
                        + "datei=" + datei + "&datef=" + datef + \
                        "&timei=" + timei + "&timef=" + timef + "&enose=" + enose + "\" " \
                        + " style=\"width: 80%;\"/>"
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
