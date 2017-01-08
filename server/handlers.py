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




class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('pages/index.html', title="Farore's wind", miolo = "",
                    top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())
        return



class inputMetadataHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.IPs = IPs
        return

    def get(self):

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:
            miolo = file('pages/input_metadata.html').read()
            self.render('pages/index.html', title="Farore's wind", miolo = miolo,
                        top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to input_metadata from outside IP list: ' + str(self.request.remote_ip) )

        return



class inputEnoseConfigHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.IPs = IPs
        return

    def get(self):

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:
            miolo = file('pages/input_enose_config.html').read()
            self.render('pages/index.html', title="Farore's wind", miolo = miolo,
                        top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to input_metadata from outside IP list: ' + str(self.request.remote_ip) )

        return


class listInductionsHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    def get(self):

        sampleid = int( self.get_argument('smp', -1) )

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:

            miolo = '<div class="page-header">' + \
                    '<div class="row"><div class="col-md-6"><table class="table table-striped">' + \
                    '<thead><tr><th width=100px>Sample id</th><th>Number</th><th>Avg duration</th></tr></thead>'+ \
                    '<tbody>\n'

            listSamples = self.db.getInductionList( )

            total = 0
            smp_count = 0
            for sample in listSamples:
                anchor = "<a href='/list_inductions?smp="+str(smp_count)+"'>"
                smp_count += 1
                miolo += "<tr><td>"+anchor+sample[0]+"</a></td><td>"+str(sample[1])+"</td><td>"+str(sample[2])+"</td></tr>"
                total += sample[1]

            miolo += "<tr><td><a href='/list_inductions'>Total</a></td><td>"+str(total)+"</td><td>&nbsp;</td></tr>"

            miolo += '</tbody></table></div></div></div>'

            miolo += '<div class="page-header">' + \
                    '<div class="row"><div class="col-md-6"><table class="table table-striped">' + \
                    '<thead><tr><th width=100px>Id</th><th>Sample name/description</th><th>Enose</th><th>Date</th><th>t0</th><th>tc</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th></tr></thead>'+ \
                    '<tbody>\n'


            ## Selecting which sample
            if sampleid > len( listSamples ): sampleid = -1
            if sampleid >= 0:
                sample = listSamples[sampleid][0]
            else:
                sample = ''

            ## Retrieving data from inductions
            db = self.db
            listInds = self.db.getInductionsMetadata( sample = sample, limit = 50 )

            for ind in listInds:
                miolo += "<tr><td>" + str(ind[0]) + "</td>\n"
                miolo += "<td>" + str(ind[5]) + "</td><td>hal" + str(ind[8])+"k</td>\n"

                date = str(ind[1])[:10]
                t0   = str(ind[1])[10:]
                tc   = str(ind[2])[10:]

                miolo += "<td>" + date + "</td><td>" + t0 + "</td><td>" + tc  + "</td>\n"

                link = "<form action=\"./showInduction\" id=\"form" + str(ind[0]) + "\" method=\"post\">\n" \
                        + "<input type=\"hidden\" name=\"enose\" value=\""+str(ind[8])+"\" />\n" \
                        + "<input type=\"hidden\" name=\"datei\" value=\""+date+"\" />\n" \
                        + "<input type=\"hidden\" name=\"timei\" value=\""+t0+"\" />\n" \
                        + "<input type=\"hidden\" name=\"datef\" value=\""+date+"\" />\n" \
                        + "<input type=\"hidden\" name=\"timef\" value=\""+tc+"\" />\n" \
                        + "<p><a href=\"javascript:{}\" onclick=\"document.getElementById('form" + str(ind[0]) \
                        + "').submit(); return false;\">See induction</a></p>\n" \
                        + "</form>\n"

                miolo += "<td>"+link+"</td>"

                miolo += "<td><a href=\"/updateInductionIndex?id=" + str(ind[0]) + "\">"
                miolo+= "Update indexing...</a></td>"
                
                miolo += '</tr>\n\n'

            miolo += '</tbody></table></div></div></div>'
            self.render('pages/index.html', title="List of inductions", miolo = miolo,
                        top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to list_inductions from outside IP list: ' + str(self.request.remote_ip) )

        return




class listEnoseConfHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    def get(self):

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:

            miolo = '<div class="page-header">' + \
                    '<div class="row"><div class="col-md-6"><table class="table table-striped">' + \
                    '<thead><tr><th width=500px colspan=2>enose ID</th><th width=150px colspan=3>Location</th><th width=150px colspan=3>Date</th><th width=50px></th><th width=50px></th></tr></thead>'+ \
                    '<tbody>\n'

            # Retrieving data from inductions
            db = self.db
            listConfs = self.db.getEnoseConfs( )

            for conf in listConfs:
                miolo += "<tr><td colspan=2>hal" + str(conf[-1]) + "k</td>\n"
                miolo += "<td colspan=3>" + str(conf[-2]) + "</td>\n"
                miolo += "<td colspan=5>" + str(conf[1]) + "</td>"

                miolo += "</tr><tr>"
                for j in range(10):
                    miolo += "<td>" + str(conf[2+j]) + "</td>"

                miolo += "</tr>"

            miolo += '</tbody></table></div></div></div>'
            self.render('pages/index.html', title="Current list of ENoses", miolo = miolo,
                        top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to list_inductions from outside IP list: ' + str(self.request.remote_ip) )

        return





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




class showInductionHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    def post(self):

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:

            datei = self.get_argument('datei', '')
            timei = self.get_argument('timei', '')
            datef = self.get_argument('datef', '')
            timef = self.get_argument('timef', '')
            enose = self.get_argument('enose', '')

            miolo = "<img src=\"./view?" \
                        + "datei=" + datei + "&datef=" + datef + \
                        "&timei=" + timei + "&timef=" + timef + "&enose=" + enose + "\" " \
                        + " style=\"width: 80%;\"/>"

            self.render('pages/index.html', title="Displaying induction", miolo = miolo,
                        top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())

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

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to metadata_action from outside IP list: ' + str(self.request.remote_ip) )

        return


class actionEnoseConfigHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return


    def post(self):

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:
            self.render('pages/metadata_action.html')

            date = self.get_argument('date', '')


            S = []
            for j in range(1,11):
                S.append( self.get_argument('S'+str(j), '') )

            T = []
            for j in range(1,9):
                T.append( self.get_argument('T'+str(j), '') )

            location = self.get_argument('location', '')
            enose =  self.get_argument('enose', '')

            if len(enose) > 1:
                enose = enose[3]

            self.db.insertEnoseConf(enose, date, S, T, location)

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to metadata_action from outside IP list: ' + str(self.request.remote_ip) )

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





class  updateInductionIndexHandler(tornado.web.RequestHandler):
    
    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return
    
    
    def get(self):

        if self.request.remote_ip[:-2] == self.IPs[0]:
                        
            id = int( self.get_argument('id', '') )
            logging.info('Updating indexing of ind_id in measurements by IP:' + str(self.request.remote_ip) +
                         ' ) from ind_id ' +  str(id) )

            
            metadata = self.db.getInductionsMetadata(ind_id = id)[0]
            
            # pre-buffer
            timebuffer = datetime.timedelta(minutes=metadata[3])
            # Initial time to retrieve
            dtI_b = metadata[1] - timebuffer
            # post-buffer
            timebuffer = datetime.timedelta(minutes=metadata[4])
            # Final time to retrieve
            dtF_b = metadata[2] + timebuffer
            
            
            ## Retrieving data from inductions
            self.db.updateInductionIndexingMeasurement( id, int(metadata[-1]), str(dtI_b), str(dtF_b) )
            
            
            logging.info('Updated indexing of ind_id in measurements by IP:' + str(self.request.remote_ip) +
                            ' ) from ind_id ' +  str(id) )

            self.write('<script>location = "/list_inductions"</script>')
            

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to metadata_action from outside IP list: ' + str(self.request.remote_ip) )

        return
