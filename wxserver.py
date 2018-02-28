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
import time
from gribclass import Zipcode,KDTree

app = Flask(__name__)

#loop through forecast files and save it in t
t={}
i=0
for f in glob.iglob('/Users/elaineyang/Downloads/hrrr/files/*.grib2'):
    print (f)
    t[i]=KDTree(f)
    t[i].createKDTree()
    i+=1

#load zipcode information in z
z=Zipcode('/Users/elaineyang/Downloads/zipcode/zipcode.csv')
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
    zip=""
    if 'zip' in request.args:
        zipcode=request.args.get("zip")
        lat,lon=z.lookupZip(zipcode)
    elif 'lat' and 'lon' in request.args:
        lat=float(request.args.get("lat"))
        lon=float(request.args.get("lon"))
    elif 'city' and 'state' in request.args:
        city=request.args.get("city")
        state=request.args.get("state")
        lat,lon,zipcode=z.lookupCityState(city,state)
    else:
        results="Please enter zip, lat,lon or city,state\n"
        return json.dumps(results)

    results['cityInfo']={}
    if len(zipcode)==5:
         results['cityInfo']=z.basicInfo(zipcode)
    else:
        results['cityInfo']['lat']=float(lat)
        results['cityInfo']['lon']=float(lon)

    results['forecast']={}

    for j in t:
        results['forecast'][j]=t[j].displayValues(lat,lon)

    return json.dumps(results, indent=4,cls=DateTimeEncoder)
        
