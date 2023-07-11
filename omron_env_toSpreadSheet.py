from datetime import datetime, timedelta
from bluepy import btle
import inkbird_ibsth1_connect
import requests

import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
PERIPHERAL_MAC_ADDRESS = os.environ.get("MAC_ADDRESS")
WEB_APP_URL = os.environ.get("WEB_APP_URL")
deviceName = os.environ.get("DEVICE_NAME")

# ----

# get the current time
date = datetime.today()
# round the current time to the nearest minute 
masterDate = date.replace(second=0, microsecond=0)
if date.second >= 30:
    masterDate += timedelta(minutes=1)

# get the sensor value
sensorValue = inkbird_ibsth1_connect.get_ibsth1_data(PERIPHERAL_MAC_ADDRESS)

# upload to the spreadsheet
data = {
    'DeviceName': deviceName,
    'Date_Master': str(masterDate),
    'Date': str(date),
    'SensorType': '',
    'Temperature': str(sensorValue['Temperature']),
    'Humidity': str(sensorValue['Humidity']),
    'Light': '',
    'UV': '',
    'Pressure': '',
    'Noise': '',
    'BatteryVoltage': str(sensorValue['Battery'])
}

response = requests.post( WEB_APP_URL, data=data)

