from datetime import datetime, timedelta
from bluepy import btle
import inkbird_ibsth1_connect
import requests

# InkBird MAC ADDRESS
PERIPHERAL_MAC_ADDRESS = '**:**:**:**:**:**'
# GAS WebAPP URL
WEB_APP_URL = 'https://script.google.com/macros/s/******/exec'
# Google SpreadSheet Sheetname
deviceName = '*******'

# ----

#現在時刻を取得
date = datetime.today()
#現在時刻を分単位で丸める
masterDate = date.replace(second=0, microsecond=0)
if date.second >= 30:
    masterDate += timedelta(minutes=1)

#センサ値取得
sensorValue = inkbird_ibsth1_connect.get_ibsth1_data(PERIPHERAL_MAC_ADDRESS)

#Googleスプレッドシートにアップロードする処理
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
    'BatteryVoltage': ''
}

response = requests.post( WEB_APP_URL, data=data)

