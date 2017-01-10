## database
import psycopg2

## system libraries
import io
import pickle
import datetime, time
import logging
import json

## numerical libraries
import numpy as np
import matplotlib
matplotlib.use('Agg')
import pylab as pl
import matplotlib.gridspec as gridspec

## web libraries
import tornado
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





class listInductionsHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    def get(self):

        sampleid = int( self.get_argument('smp', -1) )

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:

            miolo = '<div class="page-header">' + \
                    '<table class="table table-striped">' + \
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

            miolo += '</tbody></table></div>'

            miolo += '<div class="page-header">' + \
                    '<table class="table table-striped">' + \
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

            miolo += '</tbody></table></div>'
            self.render('pages/index.html', title="List of inductions", miolo = miolo,
                        top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to list_inductions from outside IP list: ' + str(self.request.remote_ip) )

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
