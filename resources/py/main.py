
# Import packages
import pandas as pd
import requests
import requests_cache
import openmeteo_requests
from datetime import datetime as dt
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    # Asendion, Makati, Philippines
	"latitude": 14.559571295922172,
	"longitude": 121.0165314944657,
	"current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "weather_code"],
	"timezone": "Asia/Singapore",
}
responses = openmeteo.weather_api(url, params = params)
responses_2 = requests.get(url, params = params)
print(responses_2.text)

# Get the first response (there should only be one since we made one request)
response = responses[0]

# Process the location
latitude = response.Latitude()
longitude = response.Longitude()
elevation = response.Elevation()
timezone = response.Timezone()
timezone_abbreviation = response.TimezoneAbbreviation()
timezone_offset_seconds = response.UtcOffsetSeconds()

# Process current data. The order of variables needs to be the same as requested.
current = response.Current()
current_timestamp = dt.fromtimestamp(current.Time())
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
current_precipitation = current.Variables(2).Value()
current_rain = current.Variables(3).Value()
current_weather_code = current.Variables(4).Value()

# Construct a DataFrame for current data
data = {
    "latitude": latitude,
    "longitude": longitude,
    "elevation": elevation,
    "timezone": timezone,
    "timezone_abbreviation": timezone_abbreviation,
    "timezone_offset_seconds": timezone_offset_seconds,
    "current_timestamp": current_timestamp,
    "current_temperature_2m": current_temperature_2m,
    "current_relative_humidity_2m": current_relative_humidity_2m,
    "current_precipitation": current_precipitation,
    "current_rain": current_rain,
    "current_weather_code": current_weather_code,
}

df = pd.DataFrame([data])
print (data)