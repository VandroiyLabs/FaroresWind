# FaroresWind client


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