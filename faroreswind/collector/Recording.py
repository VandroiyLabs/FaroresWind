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
from websocket import create_connection




## Mutliprocessing Shared variables

# Stop switch
stopSwitch = mp.Value('i')
stopSwitch.value = 1

# Exporting flag
doExport = mp.Value('i')
doExport.value = 0

# Variable for the name of the nome
sensorname = mp.Value('i')



def exporter(host):

    ## Counts how many times the server was busy,
    ## then quits...
    busyCount = 0
    maxBusyCount = 3

    ## Automatic updating system
    lastUpdateTimeStamp = datetime.datetime.now()    # first sets as starting point
    updateInterval      = datetime.timedelta(minutes = 30)


    while True:

        currTime = datetime.datetime.now()
        time4Update = currTime - lastUpdateTimeStamp > updateInterval

        if doExport.value == 1 or time4Update:

            ## In case only time4Update was true
            doExport.value = 1

            print "\n\nConnecting to server..."

            try:
                ## Connecting to the socket
                ws = create_connection("ws://" + host + ":8799/DataIntegration")

                response = ws.recv()

                ## Checking server status
                if response == "Busy":
                    print "Server is busy."
                    busyCount += 1

                    # max trials achieved, quitting trying to contat the server...
                    if busyCount == maxBusyCount:
                        print "Server not responsive!! (maxBusyCount achieved)"
                        doExport.value = 0
                        busyCount = 0


                ## Server is ready to receive the data
                elif response == "Free":
                    print "Server ready to process data."

                    ## Resetting the counter for busy responses
                    busyCount = 0

                    ## Identifying itself for the server, and sending a warning
                    ws.send( "My name: " + str(sensorname.value) )
                    ws.send( "sending" )
                    print ws.recv()

                    ## Exporting the Data
                    # Sends a message to Enose to export the data
                    stopSwitch.value = 3
                    # Waiting until ENOSE exported the data
                    while doExport.value == 1:
                        time.sleep(2.)

                    ## Receing confirmation that the server received the last message
                    ws.send("sent")
                    print ws.recv()

                    ## Closing the connection
                    ws.close()

                    ## Updating the record for the last updating time stamp
                    lastUpdateTimeStamp = datetime.datetime.now()    # first sets as starting point

                    doExport.value = 0

                else:
                    print "Server is crazy."

            except:
                print "Server not responsive!!"
                doExport.value = 0


        time.sleep(5.)

    return








def collector(enose, user, host, folder):

    ## Interval between measurements
    intrval = 0.050

    ## Counting for automatic plotting
    count = 0

    while stopSwitch.value != 0:

        ## Getting new sample
        pre = time.time()
        enose.sniff(nsamples=3)
        e = time.time() - pre < 0.005
        if e < 0.004: time.sleep(0.004 - e)

        ## Updating the local visualization tool
        count +=1
        if count == 20:
            # updating shared array
            np.save( 'recent.npy', enose.memory[-5000:] )
            count = 0


        ## Checking if data should be exported
        if stopSwitch.value == 3:

            file_name = 'NewData_' + str(sensorname.value) + '_' \
                        + time.strftime("%Y-%m_%d_%H-%M-%S")

            ##TO DO checar se arquivo foi salvo e exportado
            np.save( file_name+'.npy', enose.memory )
            outscp = os.system("scp " + file_name + ".npy "
                               + user + "@" + host + ":" + folder)

            if outscp == 0:
                os.system("rm -f "+file_name+".npy")
                enose.forget()

            stopSwitch.value = 1
            doExport.value = -1


        ## Clock
        key = True
        while key:
            dif = intrval - ( time.time() % 1 )  % intrval
            key = not ( dif  < 0.005 )
            time.sleep( dif*0.6 )


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


def webservice(port):

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/recent.png", ImageHandler),
    ])

    application.listen(port)
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






def daemon( enoseID ):

    hn = logging.NullHandler()
    hn.setLevel(logging.DEBUG)
    logging.getLogger("tornado.access").addHandler(hn)
    logging.getLogger("tornado.access").propagate = False


    signal.signal(signal.SIGINT, signal_handler)

    # Defining the name
    sensorname.value = int(enoseID)

    print "Creating the ENose object..."
    enose = EN.ElectronicNose()

    print "Preparing environment..."


    ## Reading configuration file
    configfile = file('Cconfig','r')
    user   = configfile.readline().split('\n')[0]
    port   = int(configfile.readline().split('\n')[0])
    host   = configfile.readline().split('\n')[0]
    folder = configfile.readline().split('\n')[0]
    configfile.close()
    

    ## Parallel processes

    sniffer = mp.Process(target=collector, args=(enose, user, host, folder))
    sniffer.start()

    exporter_th = mp.Process(target=exporter, args=(host,))
    exporter_th.start()


    print( "Starting web service (use port " + str(port) + ")" )
    is_closing = False
    webserv = mp.Process(target=webservice, args=(port,))
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
            doExport.value = 1
            while doExport.value != 0:
                time.sleep(0.1)

        elif command == "stop" or command == "s":
            stopSwitch.value = 0
            sniffer.join()
            os.system(" rm -f recent.npy plot_recent.png ")
            break



    print "\nThe end, my friend."
    return
