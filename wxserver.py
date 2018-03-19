from flask import Flask, request
from json import dumps
from datetime import datetime
import json
import numpy as np
from forecastdata import ForecastData
from Geocoder import Geocoder

#make some comments 
forecast=ForecastData()
forecast.gribKDTree()
geocoder = Geocoder("/Users/elaineyang/Documents/WeatherServer/data/zipcode/uszip.csv")

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
    elif 'lat' and 'lon' in request.args:
        lat=float(request.args.get("lat"))
        lon=float(request.args.get("lon"))
        cityinfo=geocoder.lookupLatLon(lat,lon)
    elif 'city' and 'state' in request.args:
        city=request.args.get("city")
        state=request.args.get("state")
        cityinfo=geocoder.lookupCityState(city,state)
    else:
        results="Please enter zip, lat,lon or city,state\n"
        return json.dumps(results)

    results['cityInfo']={}
    results['cityInfo']=cityinfo
    results['forecast']=forecast.forecastDisplay(lat,lon)

    return json.dumps(results, indent=4,cls=DateTimeEncoder)
        
