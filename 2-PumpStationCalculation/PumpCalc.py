import csv
from datetime import datetime
from datetime import timedelta

# Tesler script to calculate the inflow to a pump station based on two pump on/off signals

# constant wet well volume of 2.798L
wwVolume=2.798

pumpOn=0
pumpOff=1

previousP1Status=-1
previousP2Status=-1

currentP1Status=-1
currentP2Status=-1

wroteInflow=0
timingFlag=0

p1Dates=[]
p2Dates=[]

inflowDates=[]
inflows=[]

p1DateStr=[]
p2DateStr=[]
p1Status=[]
p2Status=[]

# Read pump status from channels
with open("P1.csv") as csvfile:
        reader=csv.reader(csvfile,delimiter=',')
        next(reader)
        for row in reader:
             p1DateStr.append(str(row[0]).replace("T"," "))
             p1Status.append(float(row[1]))

with open("P2.csv") as csvfile:
        reader2=csv.reader(csvfile,delimiter=',')
        next(reader2)
        for row in reader2:
             p2DateStr.append(str(row[0]).replace("T"," "))
             p2Status.append(float(row[1]))

for dateStr in p1DateStr:
        p1Dates.append(datetime.strptime(dateStr,'%Y-%m-%d %H:%M:%S'))

for dateStr in p2DateStr:
        p2Dates.append(datetime.strptime(dateStr,'%Y-%m-%d %H:%M:%S'))

# Find the earliest date/time
if min(p1Dates)<=min(p2Dates):
        minDateTime=min(p1Dates)
else:
        minDateTime=min(p2Dates)

print(minDateTime)

# Find the latest date/time
if max(p1Dates)>max(p2Dates):
        maxDateTime=max(p1Dates)
else:
        maxDateTime=max(p2Dates)

print(maxDateTime)

checkDateTime=minDateTime

while checkDateTime<=maxDateTime:
        for n in range (0,len(p1DateStr)):
                if checkDateTime.strftime('%Y-%m-%d %H:%M:%S')==p1DateStr[n]:
                        if currentP1Status==-1:
                                currentP1Status=p1Status[n]
                                currentP1StatusDateTime=checkDateTime
                        else:
                                previousP1Status=currentP1Status
                                previousP1StatusDateTime=currentP1StatusDateTime
                                currentP1Status=p1Status[n]
                                currentP1StatusDateTime=checkDateTime
                        wroteInflow=0
                        print("P1 status change:",checkDateTime,currentP1Status)
                        print(previousP1Status,previousP2Status,currentP1Status,currentP2Status)

        for n in range(0,len(p2DateStr)):
                if checkDateTime.strftime('%Y-%m-%d %H:%M:%S')==p2DateStr[n]:
                        if currentP2Status==-1:
                                currentP2Status=p2Status[n]
                                currentP2StatusDateTime=checkDateTime
                        else:
                                previousP2Status=currentP2Status
                                previousP2StatusDateTime=currentP2StatusDateTime
                                currentP2Status=p2Status[n]
                                currentP2StatusDateTime=checkDateTime
                        wroteInflow=0
                        print("P2 status change:",checkDateTime,currentP2Status)
                        print(previousP1Status,previousP2Status,currentP1Status,currentP2Status)

        if currentP1Status==pumpOff and currentP2Status==pumpOff:
                if (previousP1Status==pumpOn or previousP2Status==pumpOn) and timingFlag==0:
                        timerStart=checkDateTime
                        timingFlag=1
                        print("Started Timing a fill cycle at:",timerStart)

        if previousP1Status==pumpOff and currentP1Status==pumpOn and currentP2Status==pumpOff and wroteInflow==0:
                print("Valid fill cycle found, ended by P1 On",checkDateTime)
                inflowDates.append(checkDateTime.strftime('%Y-%m-%d %H:%M:%S'))
                timingFlag=0
                timeToFill=(currentP1StatusDateTime-timerStart).total_seconds()
                print("Time to Fill (seconds):",timeToFill)
                inflow=wwVolume*1000.0/timeToFill
                print("Calculated Inflow (l/s):",inflow)
                inflows.append(inflow)
                wroteInflow=1

        if previousP2Status==pumpOff and currentP2Status==pumpOn and currentP1Status==pumpOff and wroteInflow==0:
                print("Valid fill cycle found, ended by P2 On",checkDateTime)
                inflowDates.append(checkDateTime.strftime('%Y-%m-%d %H:%M:%S'))
                timingFlag=0
                timeToFill=(currentP2StatusDateTime-timerStart).total_seconds()
                print("Time to Fill (seconds):",timeToFill)
                inflow=wwVolume*1000.0/timeToFill
                print("Calculated Inflow (l/s):",inflow)
                wroteInflow=1
                inflows.append(inflow)

        checkDateTime=checkDateTime+timedelta(seconds=1)

f=open("Calculated Inflow.csv","a+",newline='\n') 
f.write("time,value\n")

for index,dateStr in enumerate(inflowDates):
        outputStr=dateStr+","+str(inflows[index])+"\n"
        f.write(outputStr)
        print(outputStr)
f.close()
