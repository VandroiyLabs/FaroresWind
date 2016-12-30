import serial
import numpy as np
import json
from datetime import datetime



class ElectronicNose:


    def __init__(self, devAdd='/dev/ttyUSB0', baudrate=115200/3, \
                 tmax = 1000, outputFile = '', numSensors = 8):

        ## Creating the serial object
        self.Sensor = serial.Serial(devAdd, baudrate)
        self.memory = np.empty((0, numSensors + 2 + 1))
        
        ## File to store samples
        if outputFile != '':
            self.outfile = open(outputFile, 'a')
        else:
            self.outfile = []
        
        
        ## Writing the parameters
        Vparam = '54'
        if False: self.Sensor.write('P000' + 8*Vparam )
        
        return


    def save(self, filename):
        np.save(filename, self.memory)
        return

    def closeConnection(self):
        self.Sensor.close()
        return

    def refresh(self, nmax):

        self.t[:self.tMax - nmax] = self.t[nmax:]
        self.S[:self.tMax - nmax,:] = self.S[nmax:,:]

        return


    def sniff(self, nsamples=5):
        
        # Flushing to ensure time precision
        self.Sensor.flush()
        
        # Possibly getting partial line -- this will be discarded
        self.Sensor.readline()
        
        avg = np.zeros( (1,11) )
        for j in range(nsamples):
            avg[0,1:] += self.convert( self.Sensor.readline().split('\rV')[1].split('\n')[0][8:39] )
        
        avg = avg/float(nsamples)
        
        now = datetime.now()
        avg[0,0] = now.hour*3600 + now.minute*60 + now.second + now.microsecond/1.e6
        self.memory = np.concatenate( (self.memory, np.reshape(avg, (1,11))  ), axis=0 )
        
        return

    
    def convert(self, string):
        s = np.zeros(10)
        # Converting 8 sensors
        for j in range(8):
            s[j] = int( string[j*3:j*3+3] , 16 )
        
        # Converting temperature and humidity
        s[8] = int( string[24:28] , 16)
        s[9] = int( string[28:31] , 16)
        
        return s



if __name__ == "__main__":

    # Instantiating the class
    EN = ElectronicNose()

    # Acquiring some data
    EN.sniff(1000)

    # Closing connection
    EN.closeConnection()
