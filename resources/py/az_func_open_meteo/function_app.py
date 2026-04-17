# Import packages
import os
import json
import logging
import requests
import azure.functions as func
from datetime import datetime as dt
from azure.storage.blob import BlobServiceClient

def get_makati_weather_data():
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
	response = requests.get(url, params = params)
	
    # Return the response in JSON format on successful call. Otherwise, return nothing.
	try:
		response.raise_for_status()
		data = response.json()
		logging.info("Successfully extracted weather data from the API.")
		return json.dumps(data)
	except Exception as e:
		raise Exception(f"Error fetching weather data: {e}")

def upload_to_blob_storage(blob_name, blob_data):
	# Set up Azure Blob Storage connection
	AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
	BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

	# Create blob service client
	blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
	container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

	# Upload blob
	try:
		container_client.upload_blob(name=blob_name, data=blob_data, overwrite=True)
		logging.info(f"Successfully uploaded {blob_name} to Azure Blob Storage.")
	except Exception as e:
		raise Exception(f"Error uploading to Azure Blob Storage: {e}")

app = func.FunctionApp()

@app.timer_trigger(
    schedule="0 0 * * * *", 
    arg_name="myTimer", 
    run_on_startup=True,
    use_monitor=False
) 
def hourly_run(myTimer: func.TimerRequest) -> None:
	
	# Get current timestamp for blob naming
	now = dt.now().strftime("%Y%m%d%H%M%S")

	if myTimer.past_due:
		logging.info('The timer is past due!')

	blob_data = get_makati_weather_data()
	if not blob_data is None:
		# Define blob name with timestamp
		blob_name = f"dumps/open_meteo/open_meteo_{now}.json"
		upload_to_blob_storage(blob_name, blob_data)
		logging.info('Weather data extraction completed.')
