# standard libraries
import sys, os, time, io
import datetime

# enose library
import ElectronicNose as EN

# signal processing and math
import signal
import numpy as np

# to create threads
import multiprocessing as mp

# For plot
import matplotlib as mpl
mpl.use('Agg')
import pylab as pl
import matplotlib.gridspec as gridspec

# For the web service
import tornado.ioloop
import tornado.web
import logging

hn = logging.NullHandler()
hn.setLevel(logging.DEBUG)
logging.getLogger("tornado.access").addHandler(hn)
logging.getLogger("tornado.access").propagate = False

def collector(enose):

    count = 0

    while stopSwitch.value != 0:

        if stopSwitch.value == 3:
            file_name = time.strftime("%Y-%m_%d_%H:%M:%S")
            ##TO DO checar se arquivo foi salvo e exportado
            np.save( file_name+'.npy', enose.memory )
            os.system("scp "+file_name+".npy jaquejbrito@itristan.ucsd.edu:/home/SENSORS_data/toexport/")
            enose.forget()

        ## Getting new sample
        enose.sniff()

        count +=1
        if count == 20:
            # updating shared array
            np.save( 'recent.npy', enose.memory[-5000:] )
            count = 0


        key = True
        while key:
            time.sleep(0.01)
            key = not ( 100 - ( ( time.time() % 1 )*1000 % 100 ) < 50 )


    np.save('Data.npy', enose.memory)

    return




def genImage():

    # Collecting latest data
    recent = np.load('recent.npy')
    # Converting time from seconds to hours
    time = recent[:,0] / 3600.

    pl.figure( figsize=(8,5) )

    gs = gridspec.GridSpec(2, 2, height_ratios=[1.5,1], width_ratios = [1,1] )

    ## Starting with the sensors

    sensorPanel = pl.subplot(gs[0,:])
    for j in range(1,9):
        sensorPanel.plot(time, recent[:,j])

    sensorPanel.set_ylabel("Sensor resistance")
    sensorPanel.set_xlabel('Time (h)')
    sensorPanel.set_xlim( time.min() - 0.01, time.max() + 0.01)
    sensorPanel.grid(True)

    ## Temperature and humidity
    tempPanel = pl.subplot(gs[1,0])
    tempPanel.plot(time, recent[:,9])
    tempPanel.set_ylabel("Temperature")
    tempPanel.set_xlabel('Time (h)')
    tempPanel.set_xlim( time.min() - 0.01, time.max() + 0.01)

    humdPanel = pl.subplot(gs[1,1])
    humdPanel.plot(time, recent[:,10])
    humdPanel.set_ylabel("Humidity")
    humdPanel.set_xlabel('Time (h)')
    humdPanel.set_xlim( time.min() - 0.01, time.max() + 0.01)



    memdata = io.BytesIO()

    pl.tight_layout()
    pl.savefig(memdata, format='png', dpi=150)
    image = memdata.getvalue()
    pl.close()
    return image

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("<html><head>")
        self.write('<meta http-equiv="refresh" content="5">')
        self.write("<title>Sensor</title></head>")
        self.write("<body>")
        self.write("<h1>Sensor hal"+str(sensorname.value)+"k</h1>")
        self.write('<img src="recent.png" style="width: 900px;" />')
        self.write("</body></html>")

class ImageHandler(tornado.web.RequestHandler):
    def get(self):
        image = genImage()
        self.set_header('Content-type', 'image/png')
        self.set_header('Content-length', len(image))
        self.write(image)


def webservice():

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/recent.png", ImageHandler),
    ])

    application.listen(8888)
    tornado.ioloop.PeriodicCallback(try_exit, 100).start()
    tornado.ioloop.IOLoop.instance().start()

    return





def try_exit():
    if  stopSwitch.value == 0:
        tornado.ioloop.IOLoop.instance().stop()
    return


def signal_handler(signal, frame):
    print "\nStopping..."
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Defining the name
sensorname = mp.Value('i')
sensorname.value = int(sys.argv[-1])

print "Creating the ENose object..."
enose = EN.ElectronicNose()

print "Preparing environment..."

stopSwitch = mp.Value('i')
stopSwitch.value = 1

sniffer = mp.Process(target=collector, args=(enose,))
sniffer.start()

print( "Starting web service (use port 8888)" )
is_closing = False
webserv = mp.Process(target=webservice, args=())
webserv.start()


print "Starting data collection (CTRL+C to stop)"
print "\n"



while True:

    command = raw_input("\nCommand: [")

    if command == "":
        ctime = datetime.datetime.now()
        print "Current time stamp: ", ctime

    elif command == "plot" or command == "p":
        stopSwitch.value = 2
        pl.close()

    elif command == "export" or command == "e":
        stopSwitch.value = 3

    elif command == "stop" or command == "s":
        stopSwitch.value = 0
        sniffer.join()
        os.system(" rm -f recent.npy plot_recent.png ")
        break



print "\nThe end, my friend."
