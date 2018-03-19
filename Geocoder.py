import pandas as pd
import jellyfish
import shapefile
from rtree import index 
from Shapes import Shapes
from Shapes import NeighborhoodShapes

class Geocoder:
    def __init__(self,filename):

        #load zipcodes
        zipcodes=pd.io.parsers.read_csv(filename, dtype={'zip': 'str'})
        self.zipcodes=pd.DataFrame(zipcodes)
        self.zipcodes.city=self.zipcodes.city.str.title()
        
        #load zip shapefiles index
        shapes = Shapes("tl_2017_us_zcta510")
        self.shapes=shapes

        #load neighborhood shapefiles index
        neighborhoods = Shapes("us")
        self.neighborhoods = neighborhoods

        #load multipolygons
        self.neighborhoodShapes=NeighborhoodShapes()

    def lookupZip(self,zipcode):
        x=self.zipcodes[(self.zipcodes.zip==zipcode)]
        x = x.iloc[0]
        return x.to_dict()

    def lookupCityState(self,city,state):
        x=self.zipcodes[(self.zipcodes.city==city) & (self.zipcodes.state==state)]
        if len(x)>0:
            x = x.iloc[0]
            return x.to_dict()
        else:
            y=self.zipcodes[(self.zipcodes.state==state)]
            index = y.index.values
            df = pd.DataFrame(y.city,columns=['city','score'])
            for index, row in df.iterrows():
                row[1]=jellyfish.jaro_winkler(row[0],city)

            maxValueIndex=df['score'].idxmax()
            x=y.loc[maxValueIndex]
            return x.to_dict()

    def lookupLatLon(self,lat,lon):
        zipcode=self.shapes.getZipFromLatLon(lat,lon)
        x=self.lookupZip(zipcode)

        #no neighborhood found case
        if self.neighborhoodShapes.check(lat,lon) is False:
            return x

        neighborhood=self.neighborhoods.getNeighborhoodFromLatLon(lat,lon)
        if len(neighborhood)!=0:
            x['neighborhood name']=neighborhood
        
        return x

#    def NeighborhoodName(self,lat,lon):
#        neighborhood=self.neighborhoodShapes.getNeighborhoodFromLatLon(lon,lat,cityinfo)
#        return neighborhood

if __name__ == "__main__":
    geocoder = Geocoder("data/zipcode/uszip.csv")
   # shapes = Shapes("tl_2017_us_zcta510")
   # print(geocoder.lookupLatLon('94107'))
    print(geocoder.lookupLatLon(40.755,-74.007))
    print(geocoder.lookupLatLon(40.7441,-74.0046))
    print(geocoder.lookupLatLon(37.350,-121.889))
    print(geocoder.lookupLatLon(47.612,-122.323))
    print(geocoder.lookupLatLon(29.758,-95.363))
    print(geocoder.lookupLatLon(42.649,-71.165))
   #print(geocoder.lookupCityState('West Farmingtn','ME'))
   # print(geocoder.lookupCityState('San Francisc','CA'))
   #print(geocoder.lookupZip('94107'))
