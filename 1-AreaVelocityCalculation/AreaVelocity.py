import math
import pandas as pd
# Tesler script to calculate the area of a partially full pipe, multiply by velocity to produce a flow
def prepare_data(data, data_name: str):
    """ datetime type """
    data["time"] = pd.to_datetime(data.time)

    """ sort values """
    data.sort_values(by=['time'], inplace=True)

    """ set index """
    data.set_index("time", inplace=True)

    """ drop duplicate time"""
    data = data[~data.index.duplicated(keep='first')]

    """ resample """
    data = data.resample('5T').pad()

    """ reset index """
    data.reset_index("time", inplace=True)

    """ rename column names """
    data.columns = ['time', data_name]

    # data[data_name][data[data_name]==0] = np.nan
    return data


def merge_data(channel1, channel2):
    data = pd.merge_ordered(channel1, channel2, on=['time'], how='outer')
    data.drop_duplicates(subset="time", inplace=True)
    return data


diameter=900.0 # (diameter of pipe in mm)
diameterM=diameter/1000.0 # calculate diameter in m
radius=diameter/2.0 # calculate radius in mm
radiusM=radius/1000.0 # calculate radius in m
area=math.pi*(diameterM)**2/4 # calculate area of full pipe in square meters

dateData=[]
flows=[]

dp = pd.read_csv("Level.csv")
dp = prepare_data(dp,"depth")

vel = pd.read_csv("Velocity.csv")
vel = prepare_data(vel,"velocity")

def calcFlow(depth, velocity):
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
        return flow        

df = merge_data(dp, vel)
print(df)

df['flow'] = df.apply(lambda row: calcFlow(row.depth,row.velocity), axis = 1)
df= df[['time','flow']]
df.columns = ['time', 'value']
df.set_index("time", inplace=True)
print(df)
output_file_name="Calculated Flow"
df.to_csv(output_file_name + ".csv")