import ElectronicNose as EN
import signal
import sys, os, time
import datetime
import multiprocessing as mp
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import pylab as pl

def collector(enose):
    
    while stopSwitch.value != 0:

        ## Getting new sample
        enose.sniff()

        if stopSwitch.value == 2:
            # updating shared array
            np.save( 'recent.npy', enose.memory[-2000:] )
            stopSwitch.value = 1

        
        key = True
        while key:
            time.sleep(0.01)
            key = not ( 100 - ( ( time.time() % 1 )*1000 % 100 ) < 50 )


    np.save('Data.npy', enose.memory)
    
    return



def signal_handler(signal, frame):
    print "\nStopping..."
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print "Creating the ENose object..."
enose = EN.ElectronicNose()

print "Preparing environment..."

stopSwitch = mp.Value('i')
stopSwitch.value = 1

sniffer = mp.Process(target=collector, args=(enose,))
sniffer.start()

print "Starting data collection (CTRL+C to stop)"
print "\n"


while True:
    
    command = raw_input("\nCommand: [")

    if command == "":
        ctime = datetime.datetime.now()
        print "Current time stamp: ", ctime

    elif command == "plot" or command == "p":
        stopSwitch.value = 2
        time.sleep(2.)
        sofar = np.load('recent.npy')
        timeaxis = sofar[:,0]/3600.
        pl.figure( figsize=(8,4) )
        for j in range(1,9):
            pl.plot(timeaxis, sofar[:,j])
        pl.savefig("plot_recent.png",dpi=100)
        pl.close()
        
    elif command == "stop" or command == "s":
        stopSwitch.value = 0
        sniffer.join()
        os.system(" rm -f recent.npy plot_recent.png ")
        break
    
    

print "\nThe end, my friend."
