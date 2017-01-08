## database
import psycopg2

## system libraries
import io
import pickle
import datetime, time
import logging
import json

## gpg library
import gnupg

## numerical libraries
import numpy as np
import matplotlib
matplotlib.use('Agg')
import pylab as pl
import matplotlib.gridspec as gridspec

## web libraries
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httpserver
import urlparse
import threading
import functools
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient

## custom libraries
import faroreDB





class viewInductionHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return


    def genImage(self, data, dtI = 0, dtF = 0):

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
        sensorPanel.set_ylim(miny*0.9, maxy*1.1)

        ## Drawing line when induction happened
        if dtI != 0 and dtF != 0:
            tI = matplotlib.dates.date2num( dtI )
            tF = matplotlib.dates.date2num( dtF )

            sensorPanel.plot( [tI, tI], [miny*0.5 , maxy*2], '--', color=(1.0,0.,0.0), lw=3., alpha=0.3, zorder=-1 )
            sensorPanel.plot( [tF, tF], [miny*0.5 , maxy*2], '--', color=(1.0,0.,0.0), lw=3., alpha=0.3, zorder=-1 )


        sensorPanel.set_ylabel("Sensor resistance")
        sensorPanel.set_xlabel('Time (h)')
        sensorPanel.set_xlim( time.min() - 0.01, time.max() + 0.01)
        sensorPanel.grid(True)

        ## Temperature and humidity
        tempPanel = pl.subplot(gs[1,0])
        tempPanel.plot(time, data[:,2], '-')
        tempPanel.set_ylabel("Temperature")
        tempPanel.set_xlabel('Time (h)')
        tempPanel.set_xlim( time.min() - 0.01, time.max() + 0.01)

        humdPanel = pl.subplot(gs[1,1])
        humdPanel.plot(time, data[:,3], '-')
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

            ## Subsampling
            samples = samples[:: samples.shape[0]/2000, :]

            ## Converting time to number and sorting by time
            samples[:,1] = matplotlib.dates.date2num( samples[:,1] )
            samples = samples[ samples[:,1].argsort() ]


            ## generating the plot
            image = self.genImage( samples, dtI, dtF )

            ## Printing to output...
            self.set_header('Content-type', 'image/png')
            self.set_header('Content-length', len(image))
            self.write(image)

        return




class showTimeSeriesHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    def get(self):
        self.post()
        return

    def post(self):

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:


            datei = self.get_argument('datei', " ")
            timei = self.get_argument('timei', " ")
            datef = self.get_argument('datef', " ")
            timef = self.get_argument('timef', " ")
            enose = self.get_argument('enose', " ")

            miolo = file('pages/showTimeSeriesForm.html').read()
            miolo = miolo.replace("{{ enose }}", enose)
            miolo = miolo.replace("{{ datei }}", datei)
            miolo = miolo.replace("{{ timei }}", timei)
            miolo = miolo.replace("{{ datef }}", datef)
            miolo = miolo.replace("{{ timef }}", timef)

            if datei != " ":

                miolo += "<img src=\"./view?" \
                        + "datei=" + datei + "&datef=" + datef + \
                        "&timei=" + timei + "&timef=" + timef + "&enose=" + enose + "\" " \
                        + " style=\"width: 80%;\"/>"

            self.render('pages/index.html', title="Displaying induction", miolo = miolo,
                        top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())

        return





class serveFileHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs, homedir):
        self.db = database
        self.IPs = IPs
        self.homedir = homedir
        return


    def get(self):

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:

            ## Getting input variables
            datei = self.get_argument('datei', '')
            timei = self.get_argument('timei', '')
            datef = self.get_argument('datef', '')
            timef = self.get_argument('timef', '')
            enose = int( self.get_argument('enose', '') )
            keyID = self.get_argument('k', '')

            logging.warning('Data retrieval by ' + keyID +
                            ' (IP:' + str(self.request.remote_ip) +
                            ' ) from enose ' +  str(enose) )

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

            ## Subsampling
            samples = samples[:: samples.shape[0]/2000, :]

            ## Converting time to number and sorting by time
            samples[:,1] = matplotlib.dates.date2num( samples[:,1] )
            samples = samples[ samples[:,1].argsort() ]

            ## encrypting for the client
            msg  = json.dumps( samples.tolist() )
            gpg  = gnupg.GPG( homedir = self.homedir )
            emsg = gpg.encrypt(msg, keyID)

            ## Serving the resulting numpy array
            self.write( str(emsg) )


        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to metadata_action from outside IP list: ' + str(self.request.remote_ip) )


        return
