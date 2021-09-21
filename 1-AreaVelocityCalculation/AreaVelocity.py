import csv
import sys
import math

# Tesler script to calculate the area of a partially full pipe, multiply by velocity to produce a flow

diameter=900.0 # (diameter of pipe in mm)

dateData=[]
depths=[]
velocities=[]
flows=[]

with open("Level.csv") as csvfile:
    reader=csv.reader(csvfile,delimiter=',')
    next(reader)
    for row in reader:
       dateData.append(str(row[0]))
       depths.append(float(row[1]))

with open("Velocity.csv") as csvfile:
    reader2=csv.reader(csvfile,delimiter=',')
    next(reader2)
    for row in reader2:
        velocities.append(float(row[1]))

if len(depths)!=len(velocities):
      sys.exit()

diameterM=diameter/1000.0 # calculate diameter in m
radius=diameter/2.0 # calculate radius in mm
radiusM=radius/1000.0 # calculate radius in m

area=math.pi*(diameterM)**2/4 # calculate area of full pipe in square meters

for index,depth in enumerate(depths):
        velocity=velocities[index]
        p=abs(radius-depth) # length from centre of pipe to water surface
        thetaO=math.acos(p/radius) # angle between centre of pipe and where water touches side of pipe
        alphaA=thetaO*2.0 # twice the subtended angle thetaO
        areaSector=alphaA/2.0*(radiusM)**2.0 # area of the sector
        areaMon=p/1000.0*(radiusM)*math.sin(thetaO) # area of the partial sector
        depthPercent=depth/diameter # calculate depth as a ratio of full pipe depth
        if depthPercent<=0.5:
                areaC=areaSector-areaMon # calculate area of pipe flow when pipe is less than or equal to half full
        else:
                areaC=area-(areaSector-areaMon) # calculate area of pipe flow when pipe is greater than half full

        flow=areaC*(velocity/3.281)*1000.0 # calculate flow in l/s
        flows.append(flow)

f=open("Calculated Flow.csv","a+",newline='\n') 
f.write("time,value\n")

for n in range(0,len(dateData)):
        outString=dateData[n]+","+str(flows[n])+"\n"
        f.write(outString)
        print(outString)
f.close()