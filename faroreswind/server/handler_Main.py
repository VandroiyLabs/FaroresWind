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

class MainHandler(tornado.web.RequestHandler):
    def get(self):

        self.render('pages/index.html', title="Farore's wind", miolo = "",
                    top=file(rootdir+"/pages/top.html").read(), bottom=file(rootdir+"/pages/bottom.html").read())
        return
