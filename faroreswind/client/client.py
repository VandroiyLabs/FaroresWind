## System libraries
import json

## numerical libraries
import numpy as np

## plot
import matplotlib
#matplotlib.use('Agg')
import pylab as pl

## gpg library
import gnupg

## URL library
import urllib2


class client:


    def __init__(self, config='client_config'):
        
        self.parseConfig( config )
        
        return
    

    def parseConfig(self, config):
        
        # Opening the configuration file 
        self.config = json.loads( open(config, 'r').read() )
        
        return
    
    
    

    def retrieveData(self, datei, timei, datef, timef, enose):
        
        url = self.config['host'] + "/serveTimeSeries?"
        url += "datei=" + datei + "&timei=" + timei
        url += "&datef=" + datef + "&timef=" + timef
        url += "&enose=" + str(enose) + "&k=" + self.config['gpg_keyid']
        print url

        msg = urllib2.urlopen(url).read()
        gpg = gnupg.GPG(verbose = True, homedir=self.config['gpg_homedir'])
        jsonDump = json.loads( str( gpg.decrypt(msg, passphrase=self.config['gpg_passphrase']) ) )
        
        return np.array(jsonDump)
