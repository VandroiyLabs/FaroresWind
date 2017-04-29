## database
import psycopg2

## system libraries
import io, os
import datetime, time
import logging

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

rootdir = os.path.dirname(__file__)




class listEnoseConfHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    def get(self):

        if self.request.remote_ip[:11] in self.IPs :

            miolo = '<div class="page-header">' + \
                    '<table class="table table-striped">' + \
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

            miolo += '</tbody></table></div>'
            self.render(rootdir+'/pagess/index.html', title="Current list of ENoses", miolo = miolo,
                        top=file(rootdir+"/pagess/top.html").read(), bottom=file(rootdir+"/pagess/bottom.html").read())

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to list_inductions from outside IP list: ' + str(self.request.remote_ip) )

        return




class inputEnoseConfigHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.IPs = IPs
        return

    def get(self):

        if self.request.remote_ip[:-2] == self.IPs[0] or self.request.remote_ip[:7] == self.IPs[1]:
            miolo = file(rootdir+'/pagess/input_enose_config.html').read()
            self.render(rootdir+'/pagess/index.html', title="Farore's wind", miolo = miolo,
                        top=file(rootdir+"/pagess/top.html").read(), bottom=file(rootdir+"/pagess/bottom.html").read())

        ## If in this else, someone tried to access this
        else:
            logging.warning('Access to input_metadata from outside IP list: ' + str(self.request.remote_ip) )

        return






class actionEnoseConfigHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):
        self.db = database
        self.IPs = IPs
        return

    def post(self):

        if self.request.remote_ip[:11] in self.IPs :
            self.render(rootdir+'/pagess/metadata_action.html')

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
