# Import packages
import os
import json
import pandas as pd
import requests
from datetime import datetime as dt
from dotenv import load_dotenv
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
	
	try:
		response.raise_for_status()
		data = response.json()
		return data
	except Exception as e:
		print(f"Error fetching weather data: {e}")
		return None
	
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
		print(f"Successfully uploaded {blob_name} to Azure Blob Storage.")
	except Exception as e:
		print(f"Error uploading to Azure Blob Storage: {e}")

if __name__ == "__main__":

	# Load environment variables
	load_dotenv()

	# Get current timestamp for blob naming
	now = dt.now().strftime("%Y%m%d%H%M%S")

	# Define blob name with timestamp
	blob_name = f"dumps/open_meteo/open_meteo_{now}.json"

	# Fetch weather data for Makati
	weather_data = get_makati_weather_data()

	if weather_data:
		# Convert weather data to JSON
		blob_data = json.dumps(weather_data)

		# Upload to Azure Blob Storage
		upload_to_blob_storage(blob_name, blob_data)