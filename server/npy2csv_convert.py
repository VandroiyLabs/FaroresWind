import numpy as np
import sys

filename  = sys.argv[1]
day0      = int( sys.argv[2] )
yearmonth = sys.argv[3]
enose     = sys.argv[4]

jump = 1

data = np.load(filename)

data = data[::jump,:]

hasTH = False
if data.shape[1] == 11: hasTH = True

data4conv = np.zeros( (data.shape[0], data.shape[1]+1) )
data4conv[:, 1:] = data

time = data[:,0]/3600.
DaySwitchPos = np.where( np.diff(time) < -1.0 )[0] + 1

data4conv[:,0] = day0 - DaySwitchPos.shape[0]

for switch in range( DaySwitchPos.shape[0] ):
    print DaySwitchPos[switch]
    data4conv[ DaySwitchPos[switch]: , 0 ] += 1


outfile = file(filename[:-4]+'.csv','w')

for line in data4conv[:]:
    
    hora = str(int(line[1]/3600.)).zfill(2) +":"+ str(int(line[1]/60.) % 60).zfill(2) +":"+ str(int(line[1] % 60)).zfill(2)
    hora += "."+ str( int( (line[1] %1)*1000000. )).zfill(6)
    
    linha = enose + ","+yearmonth +"-" + str(int(line[0])) + " "+ hora
    
    # If files are old, columns may be missing...
    if hasTH:
        linha += "," + str(line[10]) + "," + str(line[11])
    else:
        linha += ",0.0,0.0"
    
    for j in range(2,10):
        linha += "," + str(line[j])
    linha += ",NULL"
    
    outfile.write(linha + "\n")
    
    
outfile.close()
