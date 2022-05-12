from datetime import date, datetime
import pandas as pd
import numpy as np

# Tesler script to calculate the potential evaportranspiration (PET)


# set location and atmospheric constants for this example
avgElev=710
latDeg=49.502402
albedo=0.2
solar=0.082
boltzman=4.903*10**-9
latentHeatVap=2.45

# read input channels
dfMeanTemp = pd.read_csv('Hourly meanTemp.csv')
dfMeanTemp['time'] = pd.to_datetime(dfMeanTemp['time'])
dfMeanTemp.set_index("time", inplace=True)

dfMaxTemp = pd.read_csv('Hourly maxTemp.csv')
dfMaxTemp['time'] = pd.to_datetime(dfMaxTemp['time'])
dfMaxTemp.set_index("time", inplace=True)

dfMinTemp = pd.read_csv('Hourly minTemp.csv')
dfMinTemp['time'] = pd.to_datetime(dfMinTemp['time'])
dfMinTemp.set_index("time", inplace=True)

dfRelHumidity = pd.read_csv('Hourly relHumidity.csv')
dfRelHumidity['time'] = pd.to_datetime(dfRelHumidity['time'])
dfRelHumidity.set_index("time", inplace=True)

dfInsolIncident = pd.read_csv('Hourly isoIncident.csv')
dfInsolIncident['time'] = pd.to_datetime(dfInsolIncident['time'])
dfInsolIncident.set_index("time", inplace=True)

dfWindSpeed = pd.read_csv('Hourly windSpeed10.csv')
dfWindSpeed['time'] = pd.to_datetime(dfWindSpeed['time'])
dfWindSpeed.set_index("time", inplace=True)

# combine into one dataframe
etData = pd.concat([dfMeanTemp,dfMaxTemp,dfMinTemp,dfRelHumidity,dfInsolIncident,dfWindSpeed], axis=1, join='inner')
etData.columns = ['Timestamp','smMeanTemp','smMaxTemp','smMinTemp','smRelHum','smInsInc','smWindSpeed']

# Calculate parameters
latRad = np.pi/180*latDeg
atmPress = 101.3*((293-0.0065*avgElev)/293)**(5.26)
psycho = 0.00163/latentHeatVap*atmPress
# Calculate Min temp
etData['meanTemp'] = (etData['smMaxTemp'] + etData['smMinTemp'])/2
# Calculate wind speed
etData['windSpeed'] = etData['smWindSpeed']*(4.87/np.log(67.8*10-5.42))
# Calculate slope of vapor pressure curve
etData['slpVaporCurve'] = 4098*(0.6108*np.exp((17.27*etData['meanTemp'])/(237.3+etData['meanTemp']))/(etData['meanTemp']+237.3)**2)
# Calculate delta term
etData['deltaTerm'] = etData['slpVaporCurve']/(etData['slpVaporCurve']+psycho*(1+0.34*etData['windSpeed']))
# Calculate psi term
etData['psiTerm'] = psycho/(etData['slpVaporCurve']+psycho*(1+0.34*etData['windSpeed']))
# Calculate temp term
etData['tempTerm'] = (900/(etData['meanTemp']+273))*etData['windSpeed']
# Calculate max sat vapor pressure
etData['maxSatVapPress'] = 0.6108*np.exp(17.27*etData['smMaxTemp']/(etData['smMaxTemp']+237.3))
# Calculate min sat vapor pressure
etData['minSatVapPress'] = 0.6108*np.exp(17.27*etData['smMinTemp']/(etData['smMinTemp']+237.3))
# Calculate mean sat vapor pressure
etData['meanSatVapPress'] = (etData['maxSatVapPress']+etData['minSatVapPress'])/2
# Calculate actual vapor pressure
etData['actualVapPress'] = etData['smRelHum']/100*etData['meanSatVapPress']
# Determine day of year
etData['dayOfYear'] = etData['Timestamp'].dt.dayofyear
# Calculate inverse rel dist earth-sun
etData['invRelDist'] = 1+0.033*np.cos(2*np.pi/365*etData['dayOfYear'])
# Calculate solar declination
etData['solarDeclin'] = 0.409*np.sin(2*np.pi/365*etData['dayOfYear']-1.39)
# Calculate sunset hour angle
etData['sunsetHrAng'] = np.arccos(-np.tan(latRad)*np.tan(etData['solarDeclin']))
# Calculate extraterrestial radiation
etData['extraRadiation'] = 24*60/np.pi*solar*etData['invRelDist']*(etData['sunsetHrAng']*np.sin(latRad)*np.sin(etData['solarDeclin'])+np.cos(latRad)*np.cos(etData['solarDeclin'])*np.sin(etData['sunsetHrAng']))
# Calculate clear sky solar radiation
etData['clearSkyRadiation'] = (0.75+2*10**(-5)*avgElev)*etData['extraRadiation']
# Calculate net shortwave radiation
etData['netShortRadiation'] = (1-albedo)*etData['smInsInc']
# Calculate net outgoing longwave radiation
etData['netLongRadiation'] = boltzman*((etData['smMaxTemp']+273.16)**4+(etData['smMinTemp']+273.16)**4)/2*(0.34-0.14*etData['actualVapPress']**0.5)*(1.35*etData['smInsInc']/etData['clearSkyRadiation']-0.35)
# Calculate net radiation equivalent evapotranspiration
etData['netEquivEvapo'] = (etData['netShortRadiation']-etData['netLongRadiation'])*0.408
# Calculate radiation term
etData['radiationTerm'] = etData['deltaTerm']*etData['netEquivEvapo']
# Calculate wind term
etData['windTerm'] = etData['psiTerm']*etData['tempTerm']*(etData['meanSatVapPress']-etData['actualVapPress'])
# Calculate reference evapotranspiration
etData['refEvapo'] = etData['radiationTerm'] + etData['windTerm']
# Calculate adjusted reference evapotranspiration
etData['adjRefEvapo'] = etData['refEvapo'].apply(lambda x: 0 if x < 0 else x)

# Grab only data that is greater than or equal to midnight today
midnightStartDate = datetime.combine(date.today(), datetime.min.time())
etDataShort = etData.loc[etData['Timestamp']>=midnightStartDate]

# Split Timestamp and adjRefEvapo into their own lists
tsDate = etDataShort['Timestamp'].tolist()
# Convert tsDate to string
tsDate = []
for ts in tsDate:
        tsDate.append(ts.strftime("%m/%d/%Y %H:%M"))
tsEvap = etDataShort['adjRefEvapo'].tolist()

# write calculated PET back to output channel
tsEvap.columns['time','value']
tsEvap.to_csv('Potential Evapotranspiration')
