import pandas as pd
import jellyfish

class Geocoder:
    def __init__(self,filename):
        zipcodes=pd.io.parsers.read_csv(filename, dtype={'zip': 'str'})
        self.zipcodes=pd.DataFrame(zipcodes)

    def lookupZip(self,zipcode):
        self.zipcode=zipcode
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
            j=0
            # add a column with this value, and pick the "max" one pandas - idxmax
            for i in y.city:
                if jellyfish.jaro_winkler(i,city) > 0.9:
                    x = y.iloc[j]
                    return x.to_dict()

                j+=1



#if __name__ == "__main__":
#   geocoder = Geocoder("data/zipcode/zipcode.csv")
#   print(geocoder.lookupZip('94107'))
#   print(geocoder.lookupCityState('San Francisco','CA'))
#   print(geocoder.lookupCityState('San Francisc','CA'))
#   print(geocoder.lookupZip('94107'))
