from flask import Flask, request
from json import dumps
from datetime import datetime
import json
import numpy as np
from Grib import ForecastData
from Geocoder import Geocoder

forecast=ForecastData()
forecast.gribKDTree()
geocoder = Geocoder("data/zipcode/zipcode.csv")

app = Flask(__name__)

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
    zipcode=""
    if 'zip' in request.args:
        zipcode=request.args.get("zip")
        cityinfo=geocoder.lookupZip(zipcode)
        lat=float(cityinfo['latitude'])
        lon=float(cityinfo['longitude'])
    elif 'lat' and 'lon' in request.args:
        lat=float(request.args.get("lat"))
        lon=float(request.args.get("lon"))
    elif 'city' and 'state' in request.args:
        city=request.args.get("city")
        state=request.args.get("state")
        cityinfo=geocoder.lookupCityState(city,state)
        lat=float(cityinfo['latitude'])
        lon=float(cityinfo['longitude'])
        zipcode=str(cityinfo['zip'])
    else:
        results="Please enter zip, lat,lon or city,state\n"
        return json.dumps(results)

    results['cityInfo']={}
    if len(zipcode)==5:
        results['cityInfo']=cityinfo
    else:
        results['cityInfo']['lat']=float(lat)
        results['cityInfo']['lon']=float(lon)

    results['forecast']=forecast.forecastDisplay(lat,lon)

    return json.dumps(results, indent=4,cls=DateTimeEncoder)
        
