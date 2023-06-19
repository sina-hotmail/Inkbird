from bluepy import btle
import inkbird_ibsth1_connect

# InkBird MAC ADDRESS
PERIPHERAL_MAC_ADDRESS = '**:**:**:**:**:**'

sensorValue = inkbird_ibsth1_connect.get_ibsth1_data(PERIPHERAL_MAC_ADDRESS)

print(sensorValue['Temperature'])
