import pandas as pd
import shapefile
from rtree import index 
from shapely.geometry import Polygon, Point, MultiPolygon

class Shapes:
    def __init__(self,filename):
        #PATH='/Users/elaineyang/Documents/WeatherServer/data/shapefiles/'
        PATH='data/shapefiles/'
        print("processing " + filename+".shp")
        myshp = open(PATH+filename+".shp", "rb")
        mydbf = open(PATH+filename+".dbf", "rb")
        r = shapefile.Reader(shp=myshp, dbf=mydbf)
        records = r.records()
        self.records=records
        idx = index.Index()
        shapes = r.shapes()
        id_num = 0
        for shape in shapes:
            sh = shape.bbox
            xmin = sh[1]
            ymin = sh[0]
            xmax = sh[3]
            ymax = sh[2]
            idx.insert(id_num, (xmin,ymin,xmax,ymax))
            id_num = id_num + 1 
            self.idx=idx
    
    def getZipFromLatLon(self,lat,lon):
        left, bottom, right, top =(float(lat)-0.0001,float(lon)-0.0001,float(lat)+0.0001,float(lon)+0.0001)
        thisIndex=list(self.idx.intersection((left,bottom,right,top)))[0]
        zipcode=self.records[thisIndex][0]
        return zipcode

    def getNeighborhoodFromLatLon(self,lat,lon):
        left, bottom, right, top =(float(lat)-0.0001,float(lon)-0.0001,float(lat)+0.0001,float(lon)+0.0001)
        thisIndex=list(self.idx.intersection((left,bottom,right,top)))[0]
        neighborhood=self.records[thisIndex][3]
        return neighborhood

class NeighborhoodShapes:
    def __init__(self):
        #load multipolygons from all states for check a point exists in a polygon purpose
        PATH='/Users/elaineyang/Documents/WeatherServer/data/shapefiles/'
        polygon = shapefile.Reader(PATH+"us.shp")
        polygon = polygon.shapes()
        shpfilePoints = [ shape.points for shape in polygon ]
        polygons = shpfilePoints
        self.polygons=polygons

    def check(self,lat,lon):
        point = Point(lon,lat)
        for polygon in self.polygons:
            poly = Polygon(polygon)
            if poly.contains(point):
                return True

        return False

if __name__ == "__main__":
    from Geocoder import Geocoder
#    geocoder = Geocoder("/Users/elaineyang/Documents/WeatherServer/data/zipcode/zip_code.csv")
    geocoder = Geocoder("data/zipcode/uszip.csv")
    shapes = Shapes("tl_2017_us_zcta510") #loading zip shapefiles
    neighborhoodShapes = Shapes("us") #loading neighborhood shapefiles
    zipcode=shapes.getZipFromLatLon(40.755,-74.007)
    cityinfo=geocoder.lookupZip(zipcode)
    neighborhood=neighborhoodShapes.getNeighborhoodFromLatLon(40.755,-74.007,40.755)
#    if len(neighborhood) !=0:
#        cityinfo['neighborhood name']=neighborhood
#    print(cityinfo)

#    print(geocoder.lookupZip('94107'))
#   print(geocoder.lookupCityState('West Farmingtn','ME'))
#   print(geocoder.lookupCityState('San Francisc','CA'))
#   print(geocoder.lookupZip('94107'))
