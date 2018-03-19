from datetime import datetime
import glob
import pygrib
import numpy as np
import calendar
import time
from scipy import spatial

class ForecastData:

    #Holds all the info of parameters we want
    def parameterInfo(self):
        parameters=['Temperature','Dew point temperature','Relative humidity','u-component of wind',
                    'v-component of wind','Wind speed','Wind speed [gust]','Total cloud cover','Total precipitation',
                    'Total snowfall','Categorical snow','Categorical ice pellets','Categorical freezing rain',
                    'Categorical rain','Visibility','Mean Sea Level Pressure']
        shortNames=['2t','2d','2r','10u','10v','10si','gust','tcc','tp','asnow','csnow','cicep','cfrzr','crain','vis',
                    'mslma']
        levels=[2,2,2,10,10,10,0,0,0,0,0,0,0,0,0,0]
        info = zip(parameters,shortNames,levels)
        for i in info: yield i

    #A tree that holds all grib data that is flattened
    def __init__(self):
        self.KDT={}

    def gribKDTree(self):
        gribdata={} #contains the entire grib data 
        i=0

        for f in glob.iglob('/Users/elaineyang/Downloads/hrrr/files/*.grib2'):
            start=datetime.now()
            gribdata[i]={}
            print (f)
            #We only want to create a kdtree once
            grbs = pygrib.open(f)
            if i==0:
                start=datetime.now()
                grib=grbs.select(parameterName='Temperature',typeOfLevel='surface')[0]
                lats,lons=grib.latlons()
                nlat=np.asarray(lats)
                nlon=np.asarray(lons)
                nlat=nlat.flatten()
                nlon=nlon.flatten()
                nlatlon=np.stack((nlat,nlon),axis=-1)
                self.KDT=spatial.KDTree(nlatlon) #the tree that we will be using for looking up lat,lon index

            info=self.parameterInfo()
            validDateSet=0
            for var in info:
                grib=grbs.select(shortName=var[1],level=var[2])[0]
                if validDateSet==0:
                    gribdata[i]['validDate']=grib.validDate
                    validDateSet=1
                data=grib.values
                ndata=np.asarray(data)
                gribdata[i][var[1]]=ndata.flatten()

            i+=1
            print (datetime.now()-start)

        self.numOfFctPeriod=i
        self.gribdata=gribdata

    def forecastDisplay(self,lat,lon):
        def KtoF(K):
            F =  (K * 9)/5 - 459.67
            return F

        def msToMph(ms):
            return(ms*2.23694)

        def kgmmToInches(kgmm):
            return (kgmm*0.039370)

	    #visibility meters to Statue miles
        def metersToSM(m):
            return(m*0.000621371)

        def paToMb(pa):
            return(pa*0.01)

        def metersToInches(m):
            return(m*39.3701)

        def DatetimeToEpoch(datetime):
            date_time = '2018-02-20T23:00:00'
            pattern = '%Y-%m-%dT%H:%M:%S'
            epoch = int(calendar.timegm(time.strptime(date_time, pattern)))
            return epoch

        #find the index right away for this pair of lat,lon
        latlon=(lat,lon)
        distance,index=self.KDT.query(latlon)
        results={}# contains json forecast data
        i=0
        while i < self.numOfFctPeriod: 
            results[i]={}
            info=self.parameterInfo()
            for var in info:
                if var[1]=='2t' or var[1]=='2d':
                    results[i][var[0]]=int(round(KtoF(self.gribdata[i][var[1]][index]),0))
                elif var[1]=='10si' or var[1]=='gust':
                    results[i][var[0]]=int(round(msToMph(self.gribdata[i][var[1]][index]),0))
                elif var[1]=='tp':
                    results[i][var[0]]=round(kgmmToInches(self.gribdata[i][var[1]][index]),2)
                elif var[1]=='vis':
                    results[i][var[0]]=round(metersToSM(self.gribdata[i][var[1]][index]),1)
                elif var[1]=='mslma':
                    results[i][var[0]]=round(paToMb(self.gribdata[i][var[1]][index]),1)
                elif var[1]=='asnow':
                    results[i][var[0]]=round(metersToInches(self.gribdata[i][var[1]][index]),2)
                elif var[1]=='2r':
                    results[i][var[0]]=int(round(self.gribdata[i][var[1]][index],0))
                else:
                    results[i][var[0]]=round(self.gribdata[i][var[1]][index],2)

            #convert u,v into degrees
            u=results[i]['u-component of wind']
            v=results[i]['v-component of wind']
            results[i]['wind in degrees']=int((270 - (180/np.pi)*np.arctan2(v,u))%360)
            del results[i]['u-component of wind']
            del results[i]['v-component of wind']
            validDate=self.gribdata[i]['validDate']
            results[i]['validDate']=validDate
            results[i]['epoch']=DatetimeToEpoch(validDate)
            i+=1

        return results


if __name__ == "__main__":
    forecast = ForecastData()
    forecast.gribKDTree()
    start=datetime.now()
    f={}
    f['forecast']={}
    f['forecast']=forecast.forecastDisplay(38.8,-121.4)
    print (datetime.now()-start)
#    print (f)
   #print(geocoder.lookupCityState('San Francisc','CA'))
   #print(geocoder.lookupZip('94107'))
