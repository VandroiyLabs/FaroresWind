# FaroresWind.Client

This client retrieves data back from the server, either by directly or through SSH.



### Configuration

You will need to create a configuration file (standard name is client_config). This is a json file with some information that will be used by the script client.py. Here is one example:

```
{
  "host" : "http://myserver",
  "gpg_keyid" : "KEYID",
  "gpg_homedir" : "KEY_HOME",
  "gpg_passphrase" : "KEY_PASSPHRASE"
}
```

When the client approaches the server for data, it will encrypt the data using GPG and a public key from the client. KEYID is the identification of client's key, key_home is where your private key is store (default ```~/.gnupg/```) and KEY_PASSPHRASE is the passphrase of your key. We advise you to create a key specifically for this client, and avoid using a key that you use for other applications (such as to encrypt e-mails).

To create your key, you can use ```gpg --gen-key```. Then, add your public to the server's GPG.


### Simple example

```
import client
import numpy as np
import pylab as pl

c = client.client()

x = c.retrieveData('2017-01-07','11:0:0','2017-01-07','13:0:0',3)

pl.plot(x[:,1],x[:,2])
pl.show()
```
