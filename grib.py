rom flask import jsonify,make_response
from flask import Flask, render_template, redirect, url_for, request
from flask import current_app
from json import dumps
from datetime import datetime
import json
import glob
import pygrib
import numpy as np
import pandas as pd
import pytz
import calendar
import time
from scipy import spatial
app = Flask(__name__)

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

def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""
    indent = current_app.config.get('JSON_INDENT', None)
    sort_keys = current_app.config.get('JSON_SORT_KEYS', False)

    dumped = json.dumps(data, indent=indent, sort_keys=sort_keys)

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp

class KDTree:

    #A tree that holds all grib data that is flattened
    def __init__(self,filename):
        self.filename=filename
        self.KDT={}
        self.ndata={}

    #Holds all the info of parameters we want
    def get_parameter_info(self):
        parameters=['Temperature','Dew point temperature','Relative humidity','u-component of wind',
                    'v-component of wind','Wind speed','Wind speed [gust]','Total cloud cover','Total precipitation',
                    'Total snowfall','Categorical snow','Categorical ice pellets','Categorical freezing rain',
                    'Categorical rain','Visibility','Mean Sea Level Pressure']
        shortNames=['2t','2d','2r','10u','10v','10si','gust','tcc','tp','asnow','csnow','cicep','cfrzr','crain','vis',
                    'mslma']
        levels=[2,2,2,10,10,10,0,0,0,0,0,0,0,0,0,0]
        info = zip(parameters,shortNames,levels)
        for i in info: yield i

    def createKDTree(self):
        grbs = pygrib.open(self.filename)
        grib=grbs.select(parameterName='Temperature',typeOfLevel='surface')[0]
        lats,lons=grib.latlons()
            nlat=np.asarray(lats)
        nlon=np.asarray(lons)
        nlat=nlat.flatten()
        nlon=nlon.flatten()
        nlatlon=np.stack((nlat,nlon),axis=-1)
        self.validDate=grib.validDate

        info=self.get_parameter_info()
        for var1 in info:
            print (var1[1],var1[2])
            grib=grbs.select(shortName=var1[1],level=var1[2])[0]
            data=grib.values
            ndata=np.asarray(data)
            ndata=ndata.flatten()
            self.KDT[var1[0]]=spatial.KDTree(nlatlon)
            self.ndata[var1[0]]=ndata

    def displayValues(self,lat,lon):
        self.latlon=(lat,lon)
        results={}
        results['validDate']=self.validDate
        #results['location']=self.latlon
        info=self.get_parameter_info()

        for var2 in info:
            distance,index=self.KDT[var2[0]].query(self.latlon)
            if var2[1]=='2t' or var2[1]=='2d':
                results[var2[0]]=int(round(KtoF(self.ndata[var2[0]][index]),0))
            elif var2[1]=='10si' or var2[1]=='gust':
                results[var2[0]]=int(round(msToMph(self.ndata[var2[0]][index]),0))
            elif var2[1]=='tp':
                results[var2[0]]=round(kgmmToInches(self.ndata[var2[0]][index]),2)
            elif var2[1]=='vis':
                results[var2[0]]=round(metersToSM(self.ndata[var2[0]][index]),1)
            elif var2[1]=='mslma':
                results[var2[0]]=round(paToMb(self.ndata[var2[0]][index]),1)
            elif var2[1]=='asnow':
                results[var2[0]]=round(metersToInches(self.ndata[var2[0]][index]),2)
            else:
                results[var2[0]]=round(self.ndata[var2[0]][index],2)
                  
        #convert u,v into degrees
        u=results['u-component of wind']
        v=results['v-component of wind']
        rh=results['Relative humidity']
        results['wind in degrees']=int((270 - (180/np.pi)*np.arctan2(v,u))%360)
        del results['u-component of wind']
        del results['v-component of wind']
        results['Relative humidity']=int(round(rh,0))
        results['epoch']=DatetimeToEpoch(self.validDate)

        return results

class Zipcode:
    def __init__(self,filename):
        self.filename=filename

    def loadZipFile(self):
        zipcodes=pd.io.parsers.read_csv(self.filename, dtype={'zip': 'str'})
        self.zipcodes=pd.DataFrame(zipcodes)

    def lookupZip(self,zipcode):
        self.zipcode=zipcode
        row =self.zipcodes['zip']==self.zipcode
        print(self.zipcodes[row]['zip'].values)
        lat=self.zipcodes[row]['latitude'].values
        lon=self.zipcodes[row]['longitude'].values
        return (float(lat),float(lon))

#loop through forecast files
t={}
i=0
for f in glob.iglob('~/Downloads/hrrr/files/*.grib2'):
    print (f)
    t[i]=KDTree(f)
    t[i].createKDTree()
    i+=1

z=Zipcode('~/Downloads/zipcode/zipcode.csv')
z.loadZipFile()

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)

        return json.JSONEncoder.default(self, o)


@app.route('/api/grib')
def grib():
    results={}
    if 'zip' in request.args:
        zip=request.args.get("zip")
        lat,lon=z.lookupZip(zip)
    else:
            lat=float(request.args.get("lat"))
        lon=float(request.args.get("lon"))

    for j in t:
        #results[j]=t[j].displayValues(lat,lon)
        results[j]=t[j].displayValues(lat,lon)

    return json.dumps(results, indent=4,cls=DateTimeEncoder)
