from bluepy import btle
import inkbird_ibsth1_connect

import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
PERIPHERAL_MAC_ADDRESS = os.environ.get("MAC_ADDRESS")

sensorValue = inkbird_ibsth1_connect.get_ibsth1_data(PERIPHERAL_MAC_ADDRESS)

print(sensorValue['Temperature'])
print(sensorValue['Humidity'])
print(sensorValue['Battery'])