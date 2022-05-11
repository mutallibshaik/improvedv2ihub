# RUNS OK
# INSERT ATM DATA FROM API
# CALCULATES SLIP FACTOR AND UPDATES DATABASE WITH SLIP_MESSAGE
# CALCULATES visibility_factor FACTOR AND UPDATES DATABASE WITH visibility_factor MESSAGE
# ATM DATA is 24hr prediction
from re import X
from typing import Counter
from unittest import result
import requests
import json
import time
import pydb2
from datetime import datetime
import time
import RWIS
import fisanalysis
import surfacetexttonumber
import MODIFIED_TEST_FUZZY
import COMBINED_FIS_ANALYSIS
#import the client1

LATITUDE = "43.038"
LONGITUDE = "-93.3418"
API_KEY = "8L475N2CA7HWBUSL6MPFTLSPF"
ATMOSPHERIC_DATA_API_ENDPOINT = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LATITUDE}%2C{LONGITUDE}?unitGroup=metric&elements=datetime%2CdatetimeEpoch%2Clatitude%2Clongitude%2Ctemp%2Cdew%2Chumidity%2Cprecip%2Cprecipprob%2Cpreciptype%2Cwindspeed%2Cvisibility%2Cconditions%2Cdescription&include=hours&key={API_KEY}&contentType=json"


response = requests.get(url=ATMOSPHERIC_DATA_API_ENDPOINT)

jsonResponse = response.json()
#print(jsonResponse['days'][1]['datetime'])
#print(jsonResponse['days'][1]['hours'][0]['datetime'])
#print(jsonResponse['days'][1]['hours'][0]['temp'])
#print(jsonResponse['days'][1]['hours'][0]['dew'])
#print(jsonResponse['days'][1]['hours'][0]['windspeed'])
global x1
global y1

def get_atmdata():
    pydb2.runsqlquery("truncate atmdata")
    count=0
    while count < 23:
        for row in jsonResponse:
            jsonResponse['days'][1]['datetime']
            currentdate = jsonResponse['days'][1]['datetime']
            hour = jsonResponse['days'][1]['hours'][count]['datetime']
            temp = jsonResponse['days'][1]['hours'][count]['temp']
            dew = jsonResponse['days'][1]['hours'][count]['dew']
            windspeed = jsonResponse['days'][1]['hours'][count]['windspeed']
            diff = round((temp-dew),2)
        
            #Surface_temp = (Surface_temp - 32) / 1.8
            Surface_Condition_text,Surface_temp = RWIS.atmospheric_data()
            Surface_Condition =  surfacetexttonumber.convertsurfacetonumber(Surface_Condition_text,Surface_temp )
            slip_factor = fisanalysis.road_condition(Surface_Condition,Surface_temp)
            slip_message = surfacetexttonumber.slip_message(slip_factor)
            celcius_temp = round((Surface_temp - 32) / 1.8,2)
            slip_factor = round(slip_factor,2)
            visibility_factor = MODIFIED_TEST_FUZZY.visibilityFactor((temp-dew),windspeed)
            visibility_factor = round(visibility_factor,2)     
            visibility_message = MODIFIED_TEST_FUZZY.visibility_message(visibility_factor)
            safe_factor = COMBINED_FIS_ANALYSIS.combined_fis(slip_factor,visibility_factor)
            safe_factor = round(safe_factor,2)
            safe_message = COMBINED_FIS_ANALYSIS.combined_message(safe_factor)
            pydb2.runsqlquery(f'INSERT INTO atmdata(difference,id,date,hour,temp,dew,windspeed,Surface_Condition,Surface_temp,slip_factor,slip_message,visibility_factor,visibility_message,safe_factor,safe_message) values("{diff}","{count+1}","{currentdate}","{hour}","{temp}","{dew}", "{windspeed}","{Surface_Condition_text}", "{celcius_temp}","{slip_factor}","{slip_message}","{visibility_factor}","{visibility_message}","{safe_factor}","{safe_message}");')
            #print(f"Processed {count+1} Rows!")
            count = count+1
print("TEST_ATMOSPHERE_DATA.py: INSERTED LATEST ATMDATA/Knowledge INTO DB")

def get_visibility_factor():
    return get_atmdata().visibility_factor
def get_slip_factor():
    return get_atmdata().slip_factor

#get_atmdata()
