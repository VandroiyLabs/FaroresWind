import pylab as pl
import numpy as np

X = np.load("Data_1alcohol_weak.npy")
print X.shape

for j in range(8):
    pl.plot( X[:,0], X[:,j+1] )
pl.savefig('Plot.png', dpi=250)
