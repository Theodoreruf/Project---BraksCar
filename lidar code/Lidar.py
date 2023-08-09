import os
import time
from rplidar import RPLidar

from math import *
import numpy


lidar = RPLidar('/dev/ttyUSB0')

lidar.stop()
lidar.stop_motor()
time.sleep(10)

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)

lidar.start_motor()
time.sleep(5)

mat=numpy.zeros(36)
lines = []
for h in range(0,360):
    lines.append(' "\n' )
    
w=open('donnee_Lidar.txt','w')
   
for i, scan in enumerate(lidar.iter_scans()):
    
    for j in range(0,len(scan)):
        if scan[j][0]<10:
           continue
        angle = abs(scan[j][1])
        distance = scan[j][2]
        s=str(int(distance))
        s=s+'\n'
        lines[int(angle)]= s
        
    w.truncate(0)
    w.writelines(lines)
    
    if i>=100:
        break
        
lidar.stop()
lidar.stop_motor()
lidar.disconnect()