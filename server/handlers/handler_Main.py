## database
import psycopg2

## system libraries
import io
import datetime, time
import logging


## web libraries
from tornado.ioloop import IOLoop
from tornado.web import asynchronous, RequestHandler, Application
from tornado.httpclient import AsyncHTTPClient




class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('pages/index.html', title="Farore's wind", miolo = "",
                    top=file("pages/top.html").read(), bottom=file("pages/bottom.html").read())
        return
