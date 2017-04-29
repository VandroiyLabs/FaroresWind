## database
import psycopg2

## system libraries
import io, os
import datetime, time
import logging

## web libraries
import tornado
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient

rootdir = os.path.dirname(__file__)




class loggingHandler(tornado.web.RequestHandler):

    def initialize(self, database, IPs):

        self.db = database
        self.IPs = IPs
        self.filename = 'farore_server.log'

        return


    def get(self):

        if self.request.remote_ip[:11] in self.IPs :

            logfile    = open(self.filename).read()
            logEntries = logfile.split('\n')

            miolo = '<div class="page-header">' + \
                    '<table class="table table-striped">' + \
                    '<thead><tr><th width=100px>logger</th><th>Level</th><th>date</th><th>Message</th></tr></thead>'+ \
                    '<tbody>\n'


            for entry in logEntries[-1:-200:-1]:

                if len( entry.split('--') ) == 2:
                    [metadata, message] = entry.split('--')

                    ## Removing access to css and js stuff
                    simpleAccessCheck = "304 GET /static/css/bootstrap.css" in message or \
                       "304 GET /static/js/bootstrap.min.js" in message or \
                       "304 GET /static/css/custom.css" in message

                    if not simpleAccessCheck:

                        ## Simple parser
                        mtdt_spl = metadata.split(' ')
                        loggerID = mtdt_spl[0]
                        logLevel = mtdt_spl[2]
                        logDate  = mtdt_spl[4]
                        logTime  = mtdt_spl[5]

                        ## Styling warning and errors
                        STYLE=""
                        if logLevel == "WARNING": STYLE = "style=\"color: #FA2; font-weight: bold;\""
                        if logLevel == "ERROR": STYLE = "style=\"color: #F00; font-weight: bold;\""

                        miolo += "<tr " + STYLE + "><td>"+loggerID+"</td><td>"+logLevel+"</td><td>"+logDate+" "+logTime[:8]+"</td><td>"+message+"</td></tr>\n"

                else:
                    print( entry )

            miolo += '</tbody></table></div>'

            self.render(rootdir+'/pages/index.html', title="Server logs", miolo = miolo,
                        top=file(rootdir+"/pages/top.html").read(), bottom=file(rootdir+"/pages/bottom.html").read())

        else:
            logging.warning('Access to server logs from OUTSITE IP: ' + str(self.request.remote_ip) )


        return
