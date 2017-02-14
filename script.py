###### WUR Geo-scripting course
### Paulo Bernardino
### February 9th 2017
### Exercise 14

## Import modules
import os
from twython import TwythonStreamer
import string, json, pprint
import urllib
from datetime import datetime
from datetime import date
from time import *
import string, os, sys, subprocess, time
import psycopg2
from twython import Twython
import json
import folium
from osgeo import ogr,osr

# Get access to the twitter API
APP_KEY = 'dpNbmX9XPN1hiNSQ8rfX0824e'
APP_SECRET = 'x5RlcE6Lqun2a1W7BGhPBRjXT769kfBtyNEUww0qmI6ceZmo8j'
OAUTH_TOKEN = '55728344-ZhHGhdvpFKIvSBu47jvPFyOojNXuqPyWYaXvFne58'
OAUTH_TOKEN_SECRET = 'XZUF9LNAsPkMtExwB9GHPaboPTRVs6mFOLH5J2RTlWQsJ'

## Set working directory
os.chdir('/home/ubuntu/Exercise14')

##### Task 1: Information tweeted real time from São Paulo

#Class to process JSON data comming from the twitter stream API. 
class MyStreamer(TwythonStreamer):
    def on_success(self, data):
         tweet_lat = 0.0
         tweet_lon = 0.0
         tweet_name = ""
         retweet_count = 0

         if 'id' in data:
               tweet_id = data['id']
         if 'text' in data:
               tweet_text = data['text'].encode('utf-8').replace("'","''").replace(';','')
         if 'coordinates' in data:    
               geo = data['coordinates']
               if not geo is None:
                    latlon = geo['coordinates']
                    tweet_lon = latlon[0]
                    tweet_lat= latlon[1]
         if 'created_at' in data:
                    dt = data['created_at']
                    tweet_datetime = datetime.strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')

         if 'user' in data:
                    users = data['user']
                    tweet_name = users['screen_name']

         if 'retweet_count' in data:
                    retweet_count = data['retweet_count']
                    
         if tweet_lat != 0:
                    #some elementary output to console    
                    string_to_write = str(tweet_datetime)+", "+str(tweet_lat)+", "+str(tweet_lon)+": "+str(tweet_text)
                    print string_to_write
                    #write_tweet(string_to_write)
                 
    def on_error(self, status_code, data):
         print "OOPS FOUTJE: " +str(status_code)
         #self.disconnect

## Generate an unique filename if needed
output_file = '/home/ubuntu/Exercise14/result_'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.csv'

## Main procedure
def main():
    try:
        stream = MyStreamer(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        print 'Connecting to twitter: will take a minute'
    except ValueError:
        print 'OOPS! that hurts, something went wrong while making connection with Twitter: '+str(ValueError)
    #global target
    
    
    # Filter based on bounding box see twitter api documentation for more info
    try:
        stream.statuses.filter(locations='-46.75231,-23.69344,-46.50749,-23.45749')
    except ValueError:
        print 'OOPS! that hurts, something went wrong while getting the stream from Twitter: '+str(ValueError)
                
if __name__ == '__main__':
    main()
    
## Wait one or two minutes and stop the live stream 
## by pressing "Ctrl+C" in the console

## Visualize in a map
map_1 = folium.Map(location=[-23.55052,-46.63330],tiles='Stamen Toner', zoom_start=12)
folium.Marker([-23.531492,-46.704846]).add_to(map_1)
folium.Marker([-23.561388,-46.656388]).add_to(map_1)
folium.Marker([-23.565890,-46.650851]).add_to(map_1)
folium.Marker([-23.544917,-46.648045]).add_to(map_1)
folium.Marker([-23.558392,-46.673620]).add_to(map_1)
folium.Marker([-23.516364,-46.624049]).add_to(map_1)
folium.Marker([-23.57937,-46.605618]).add_to(map_1)
folium.Marker([-23.626486,-46.659758]).add_to(map_1)
map_1.save('Task1.html')

   
##### Task 2: Traffic jam last week in New York

## Initiating Twython object 
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

## Fire a question
search_results=twitter.search(q='traffic:( since:2017-02-05 until:2017-02-12',count=500,geocode='40.7524,-73.9492,16mi')

## Just checking
geotweets=[i for i in search_results['statuses'] if i['geo'] is not None]
len(geotweets)

## Parsing out
for tweet in search_results["statuses"]:
    coordinates=tweet['coordinates']
    if coordinates !=None:
        print coordinates        

result=[]
for tweet in search_results["statuses"]:
    coordinates=tweet['coordinates']
    if coordinates !=None:
        result.append(coordinates)
        
res_coord=[]
for r in result:
    a=list(r.values())    
    res_coord.append(a[1])

res_coord

## Creating a shapefile
driverName = "ESRI Shapefile"
drv = ogr.GetDriverByName( driverName )
fn = "points.shp"
layername = "l1"
ds = drv.CreateDataSource(fn)
spatialReference = osr.SpatialReference()
spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
layer=ds.CreateLayer(layername, spatialReference, ogr.wkbPoint)
point1 = ogr.Geometry(ogr.wkbPoint)
point2 = ogr.Geometry(ogr.wkbPoint)
point1.SetPoint(0,-74.0064,40.7142) 
point2.SetPoint(0,-73.9739,40.8299)
layerDefinition = layer.GetLayerDefn()
feature1 = ogr.Feature(layerDefinition)
feature2 = ogr.Feature(layerDefinition)
feature1.SetGeometry(point1)
feature2.SetGeometry(point2)
layer.CreateFeature(feature1)
layer.CreateFeature(feature2)
ds.Destroy()

## Convert to geoJSON
shellCommand1="cd /home/ubuntu/Exercise14"
shellCommand2="ogr2ogr -f GeoJSON -t_srs crs:84 points.geojson points.shp"
os.system(shellCommand1)
os.system(shellCommand2)

## Visualize in a map
pointsGeo=os.path.join("points.geojson")
map_points = folium.Map(location=[40.752, -73.949],tiles='Mapbox Bright', zoom_start=10)
map_points.choropleth(geo_path=pointsGeo)
map_points.save('Task2.html')


###### Task 3: Home countries of people backpacking in Amsterdam

## Initiating Twython object 
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

## Fire a question
search_results=twitter.search(q='#backpacking',count=15,geo='52.3702,4.8951,7mi')

## Parsing out
for tweet in search_results["statuses"]:
    location=tweet['user']['location']
    print location
    
result=[]
for tweet in search_results["statuses"]:
    location=tweet['user']['location']
    if location !=None:
        result.append(location)
result

## Visualize in a map
map_3 = folium.Map(location=[0,0],tiles='Mapbox Bright', zoom_start=2)
folium.Marker([-40.9005,174.8859],popup='New Zeland').add_to(map_3)
folium.Marker([51.5073,-0.1277],popup='London').add_to(map_3)
folium.Marker([56.8796,24.6031],popup='Latvia').add_to(map_3)
folium.Marker([51.0576,-1.3080],popup='Hampshire').add_to(map_3)
folium.Marker([-27.4697,153.0251],popup='Brisbane').add_to(map_3)
folium.Marker([12.9715,77.5945],popup='Bengaluru').add_to(map_3)
folium.Marker([35.7595,-79.0192],popup='North Carolina').add_to(map_3)
folium.Marker([44.3148,-85.6023],popup='Michigan').add_to(map_3)
map_3.save('Task3.html')

###### Task 4: Mapping buildings at UNICAMP

## Initiating Twython object 
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

## Fire a question
search_results=twitter.search(q='#unicampbdngs',count=15)

## Parsing out
result=[]
for tweet in search_results["statuses"]:
    result.append(tweet['text'])
    result.append(tweet['coordinates'])
result

## Visualize in a map
map_4 = folium.Map(location=[-22.818439,-47.064721],tiles='Stamen Toner', zoom_start=16)
folium.Marker([-22.819948,-47.0702309],popup='Department of Botany').add_to(map_4)
folium.Marker([-22.819111,-47.069351],popup='Institute of Biology').add_to(map_4)
folium.Marker([-22.8189266,-47.068773],popup='Institute of Chemistry').add_to(map_4)
folium.Marker([-22.817498,-47.067933],popup='Institute of Physics').add_to(map_4)
folium.Marker([-22.8175242,-47.068526],popup='Basic Circle').add_to(map_4)
folium.Marker([-22.8171858,-47.0696008],popup='Central Square').add_to(map_4)
folium.Marker([-22.8165132,-47.0703418],popup='Mute Radio').add_to(map_4)
folium.Marker([-22.8165126,-47.07105],popup='Central Library').add_to(map_4)
map_4.save('Task4.html')