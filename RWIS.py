#IMPORTS DATA FROM API AND INSERTS TO DATABASE
#ROAD SURFACE INFORMATION AND ROAD TEMPERATURE INFORMATION
import requests
#from findtemp_weather import findtemperature, findcreated_at
#from pprint import pprint
#from database_connection import cursor, connection
import json
import _thread
from threading import Timer
import random
from datetime import datetime
import sched, time
s = sched.scheduler(time.time, time.sleep)
import pydb2

def atmospheric_data():
     url = 'https://services.arcgis.com/8lRhdTsQyJpO52F1/arcgis/rest/services/RWIS_Atmospheric_Data_View/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
     url_surface = 'https://services.arcgis.com/8lRhdTsQyJpO52F1/arcgis/rest/services/RWIS_Surface_Data_View/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
     res = requests.get(url)
     data = res.json()
     x=data['features']
     res_surface = requests.get(url_surface)
     data_surface = res_surface.json()
     x_surface = data_surface['features']
     Surface_Condition = x_surface[80]['attributes']['SURFACE_CONDITION']
     Surface_temp = x_surface[80]['attributes']['SURFACE_TEMP']
     #x is a list of disctionaries
     ObjectId=x[0]['attributes']['OBJECTID']
     Status = x[0]['attributes']['STATUS']
     WindDirection = x[0]['attributes']['WIND_DIRECTION']
     Precipitationtype = x[0]['attributes']['PRECIPITATION_TYPE']
     PrecipitationIntensity = x[0]['attributes']['PRECIPITATION_INTENSITY']
     RPUID = x[0]['attributes']['RPUID']
     Township = x[0]['attributes']['TOWNSHIP']
     SECTION = x[0]['attributes']['SECTION']
     RANGE = x[0]['attributes']['RANGE']
     SITE_NUMBER = x[0]['attributes']['SITE_NUMBER']
     RPUID_NAME = x[0]['attributes']['RPUID_NAME']
     NWS_ID = x[0]['attributes']['NWS_ID']
     LATITUDE = x[0]['attributes']['LATITUDE']
     LONGITUDE = x[0]['attributes']['LONGITUDE']
     GPS_ALTITUDE = x[0]['attributes']['GPS_ALTITUDE']
     COUNTY_NAME = x[0]['attributes']['COUNTY_NAME']
     ROUTE_NAME = x[0]['attributes']['ROUTE_NAME']
     MILE_POST = x[0]['attributes']['MILE_POST']
     GARAGE_NAME = x[0]['attributes']['GARAGE_NAME']
     COUNTY_NO = x[0]['attributes']['COUNTY_NO']
     DATA_LAST_UPDATED = x[0]['attributes']['DATA_LAST_UPDATED']
     REST_LAST_UPDATED = x[0]['attributes']['REST_LAST_UPDATED']
     COST_CENTER = x[0]['attributes']['COST_CENTER']
     DISTRICT_NO = x[0]['attributes']['DISTRICT_NO']
     AIR_TEMP = x[0]['attributes']['AIR_TEMP']
     RELATIVE_HUMIDITY = x[0]['attributes']['RELATIVE_HUMIDITY']
     DEW_POINT = x[0]['attributes']['DEW_POINT']
     VISIBILITY = x[0]['attributes']['VISIBILITY']
     AVG_WINDSPEED_MPH = x[0]['attributes']['AVG_WINDSPEED_MPH']
     MAX_WINDSPEED_MPH = x[0]['attributes']['MAX_WINDSPEED_MPH']
     AVG_WINDSPEED_KNOTS = x[0]['attributes']['AVG_WINDSPEED_KNOTS']
     MAX_WINDSPEED_KNOTS = x[0]['attributes']['MAX_WINDSPEED_KNOTS']
     WIND_DIRECTION_DEG = x[0]['attributes']['WIND_DIRECTION_DEG']
     PRECIPITATION_RATE = x[0]['attributes']['PRECIPITATION_RATE']
     PRECIPITATION_ACCUMULATION = x[0]['attributes']['PRECIPITATION_ACCUMULATION']
     SENSOR_ID = x[0]['attributes']['SENSOR_ID']
     UTC_OFFSET = x[0]['attributes']['UTC_OFFSET']
     ROUTE_ID = x[0]['attributes']['ROUTE_ID']
     ROUTE_MEASURE= x[0]['attributes']['ROUTE_MEASURE']

     Surface_Condition = "Dry"
     Surface_temp = 60

     #postgres_update_queryess = """UPDATE public."RWIS" set "Status"=%s, "WIND_DIRECTION"=%s, "PRECIPITATION_TYPE"=%s, "PRECIPITATION_INTENSITY"=%s, "RPUID"=%s, "TOWNSHIP"=%s, "SECTION"=%s, "RANGE"=%s, "SITE_NUMBER"=%s, "RPUID_NAME"=%s, "NWS_ID"=%s, "LATITUDE"=%s, "LONGITUDE"=%s, "GPS_ALTITUDE"=%s, "COUNTY_NAME"=%s, "ROUTE_NAME"=%s, "MILE_POST"=%s, "GARAGE_NAME"=%s, "COUNTY_NO"=%s, "COST_CENTER"=%s, "DISTRICT_NO"=%s, "AIR_TEMP"=%s, "RELATIVE_HUMIDITY"=%s, "DEW_POINT"=%s, "VISIBILITY"=%s, "AVG_WINDSPEED_MPH"=%s, "MAX_WINDSPEED_MPH"=%s, "AVG_WINDSPEED_KNOTS"=%s, "MAX_WINDSPEED_KNOTS"=%s, "WIND_DIRECTION_DEG"=%s, "PRECIPITATION_RATE"=%s, "PRECIPITATION_ACCUMULATION"=%s, "SENSOR_ID"=%s, "ROUTE_ID"=%s, "ROUTE_MEASURE"=%s, "UTC_OFFSET"=%s,"DATA_LAST_UPDATED"=%s, "REST_LAST_UPDATED"=%s,"Surface_Condition"=%s,"Surface_temp"=%s  where "ObjectId"=%s""";
     
     pydb2.runsqlquery(f'INSERT INTO RWIS VALUE("{ObjectId}", "{Status}", "{WindDirection}", "{Precipitationtype}", "{PrecipitationIntensity}", "{RPUID}", "{Township}", "{SECTION}", "{RANGE}", "{SITE_NUMBER}", "{RPUID_NAME}", "{NWS_ID}", "{LATITUDE}", "{LONGITUDE}", "{GPS_ALTITUDE}", "{COUNTY_NAME}", "{ROUTE_NAME}", "{MILE_POST}", "{GARAGE_NAME}", "{COUNTY_NO}", "{COST_CENTER}", "{DISTRICT_NO}", "{AIR_TEMP}", "{RELATIVE_HUMIDITY}", "{DEW_POINT}", "{VISIBILITY}", "{AVG_WINDSPEED_MPH}", "{MAX_WINDSPEED_MPH}", "{AVG_WINDSPEED_KNOTS}", "{MAX_WINDSPEED_KNOTS}", "{WIND_DIRECTION_DEG}", "{PRECIPITATION_RATE}", "{PRECIPITATION_ACCUMULATION}", "{SENSOR_ID}", "{ROUTE_ID}", "{ROUTE_MEASURE}", "{UTC_OFFSET}","{DATA_LAST_UPDATED}", "{REST_LAST_UPDATED}","{Surface_Condition}","{Surface_temp}");')
     

     #print("Record inserted successfully into RWIS table:",Surface_Condition,Surface_temp)
     return Surface_Condition,Surface_temp

     
     #Timer(300, atmospheric_data).start()

#atmospheric_data()