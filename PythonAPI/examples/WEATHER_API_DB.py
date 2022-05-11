# RUNS OK
# call get_weather_data() to retun the weather string to the caller, for further transmission to MQTT
import requests
import pydb2

LATITUDE = "43.038"
LONGITUDE = "-93.3418"
API_KEY = 'f83cc592796647678dc222950221603'
#CITY = 'New York'
#URL =f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={CITY}&days=1&aqi=yes&alerts=no"
URL = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={LATITUDE},{LONGITUDE}&aqi=no'

def get_weather_data():
    response = requests.get(URL)
    location=             response.json().get('location').get('name')
    weather_descriptions= response.json().get('current').get('condition').get("text")
    feelslike=            response.json().get('current').get('feelslike_c')
    windspeed=            response.json().get('current').get('wind_kph')
    winddir=              response.json().get('current').get('wind_dir')
    humidity=             response.json().get('current').get('humidity')
    cloud=                response.json().get('current').get('cloud')
    uv=                   response.json().get('current').get('uv')
    weatherinfo =f"The weather in {location} is {weather_descriptions}, it feels like {feelslike} with wind speed {windspeed} towards {winddir}, humidity {humidity}, clouds {cloud}% and UV is {uv}"
    #print(weatherinfo)
    #pydb2.runsqlquery("truncate weatherupdates")
    query = f" insert into weatherupdates value('{weatherinfo}')"
    #pydb2.runsqlquery(query)
    return weatherinfo
