## WeatherServer (Flask server with API) : using rtree to solve n suqre problem and caching grib index to save memory
### A Quick Overview of Weather Models
1. Global models: 
 * Global Forecast System(GFS): It is at about 18 miles (28 kilometers) between grid points. You can read more about it through [NOAA](https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs). It is free and you can download the data from this [link](http://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/).
 * European Centre for Medium-Range Weather Forecasts(ECMWF): New cycle reduces the horizontal grid spacing for high-resolution forecasts from 16 km to just 9 km. You can read more about [ECMWF here](https://www.ecmwf.int/en/about/media-centre/news/2016/new-forecast-model-cycle-brings-highest-ever-resolution). It is **NOT** free.

2. Regional models:
 * NAM: It is the North American Mesoscale Forecast System. You can see the coverage [here](http://www.emc.ncep.noaa.gov/mmb/namgrids/g212.12km.jpg). It is at horizontal resolution of 12km, 3-hourly, +00 to +84 hours. 
 * HRRR: High Resolution Rapid Refresh run by NCEP. Its resolution is at 3km, hourly from 00-18 hours only. Here is more information about [HRRR](https://rapidrefresh.noaa.gov/hrrr/).
 
### More about girb data
The data is stored in grib2 file format, and the files are a collection of self-contained records of 2D or 3D data. A GRIB file contains one or more data records, arranged as a sequential bit stream. Each record begins with a header, followed by packed binary data. The header is composed of unsigned 8-bit numbers (octets). It contains information about : the qualitative nature of the data (field, level, date of production, forecast valid time, etc),
the header itself (meta-information on header length, header byte usage, presence of optional sub-headers),
the method and parameters to be used to decode the packed data,
the layout and geographical characteristics of the grid the data is to be plotted on. [Here](http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc.shtml) is NCEP WMO GRIB2 Documentation.

There are many more weather forecast models out there. For this purpose, we are only going to show how HRRR works. 
 
### Steps to running the server
1. install Flask: try to see if you can ask your server to produce "Hello, World!" in json format. You can follow the [tutorial](http://flask.pocoo.org/docs/0.12/tutorial/) here.
2.  Download HRRR grib2 files into your local directory [HRRR](http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/). 

#### Table (a quick dump of some variables)

parameterName | shortName | typeOfLevel | level
:----------------:|:-------------:|:---------------:|:---------:
Temperature |2t |heightAboveGround |2
Potential temperature| pt| heightAboveGround| 2
Specific humidity| q |heightAboveGround| 2
Dew point temperature |2d |heightAboveGround| 2
Relative humidity| 2r| heightAboveGround| 2
u-component of wind| 10u| heightAboveGround| 10
v-component of wind |10v| heightAboveGround| 10
Wind speed |10si |heightAboveGround| 10
Percent frozen precipitation| cpofp |surface |0
Precipitation rate| prate| surface| 0
Total precipitation |tp |surface| 0
Water equivalent of accumulated snow depth |sdwe| surface| 0

3. Process grib2 files in pygrib: 
 *  [KDTree](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.html#scipy.spatial.KDTree): create a KDTree class that holds all the grib data in memory so we can grab a piece of the data as we need either it is a lat/lon or zip code query. This class provides an index into a set of 2-dimensional points which can be used to rapidly look up the nearest neighbors of any point.  All values of a variable(i.e. temperature, pressure etc.) in a grib file is flattened into a 2D array for a quick nearest-neighbor lookup.
 *  HRRR's forecast goes from +00 to +18 hours. Thus, you will need to have a loop in the main function that loops through 18 files and create a single KDTree for each file. 
 *  How to choose variables: most of the surface variables are trivial, just by looking at the parameter names. It gets more complicated as you try to predict some surface phenomena that correlates with upper layer conditions such as CAPE, Lifted Index etc. For the purpose here, we aren't going into details about that. 

4. Zipcode and geo-lookup source
 * Download a zipcode file from [ZIP-CODES](https://www.zip-codes.com/) 
 * 2017 Census shapefiles from [2017 TIGER/Line Shapefiles](https://www.census.gov/geo/maps-data/data/tiger-line.html)
 * [Zillow's](https://www.zillow.com/howto/api/neighborhood-boundaries.htm) neighborhood files 
 
### API output
![Screenshot](https://github.com/weatherdivagit/WeatherServer/blob/master/Screen%20Shot%202018-03-14%20at%2010.24.27%20AM.png)
