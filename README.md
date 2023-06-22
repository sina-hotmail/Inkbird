## はじめに
この記事は[Inkbird IBS-TH1の値をRaspberryPiでロギング](https://qiita.com/c60evaporator/items/fcc16ac9ab582a25c376)を参考に BeagleBone Black で動かした時の記録です。


## 使用機材
- Inkbird IBS-TH1PLUS
- PLANEX BT-Micro4 (BlueTooth USBアダプタ) 
- BeagleBone Black rev.A5A
- BeagleBone Black OSイメージ(https://debian.beagle.cc/images/bone-eMMC-flasher-debian-10.3-console-armhf-2020-04-06-1gb.img.xz)



## 1.BeagleBone Black で Inkbird のセンサ値を取得

### BeagleBone Blackにbluepyをインストール
bluepy を使うのでインストールします。
```
sudo apt-get install libglib2.0-dev python3-venv python3-pip
pip3 install bluepy
```

BLEの動作確認として、以下のコマンドを実行してエラーが出なければOK
```
sudo hcitool lescan
```

### センサ値取得スクリプトの作成
[参考記事](https://qiita.com/c60evaporator/items/fcc16ac9ab582a25c376#センサ値取得スクリプトの作成)からセンサ値取得のスクリプトを作成します。

```py:inkbird_ibsth1_connect.py
from bluepy import btle
import struct

def get_ibsth1_data(macaddr):
    peripheral = btle.Peripheral(macaddr)
    characteristic = peripheral.readCharacteristic(0x2d)
    (temp, humid, unknown1, unknown2, unknown3) = struct.unpack('<hhBBB', characteristic)
    sensorValue = {
            'Temperature': temp / 100,
            'Humidity': humid / 100,
            'unknown1': unknown1,
            'unknown2': unknown2,
            'unknown3': unknown3,
        }
    return sensorValue
```
参考記事のhandleは0x28ですが、[Inkbird IBS-TH1PLUS のhandle は0x2dなので修正します。](https://qiita.com/junara/items/f396c1c4c15c78cde89f#inkbird-ibs-th1-からデータを取得してみる)


### メインスクリプトの作成
センサ値取得スクリプトを呼び出すため、メインスクリプトを作成します。

```py:inkbird_toSpreadSheet.py
from bluepy import btle
import inkbird_ibsth1_connect

# InkBird MAC ADDRESS
PERIPHERAL_MAC_ADDRESS = '**:**:**:**:**:**'

sensorValue = inkbird_ibsth1_connect.get_ibsth1_data(PERIPHERAL_MAC_ADDRESS)

print(sensorValue['Temperature'])
```

MACアドレスは[InkBirdの公式アプリ](https://play.google.com/store/apps/details?id=com.inkbird.engbird)で確認してスクリプトに入力したら、コンソールから実行します。

```
$ python3 inkbird_toSpreadSheet.py
27.07
```
InkBird の温度と同じであれば動作確認完了です。


## 2.BeagleBone Blackからスプレッドシートにセンサ値を書き込み

### スプレッドシートにセンサ値を書き込むGASスクリプトをWebAppとして公開
[参考記事](https://qiita.com/c60evaporator/items/ed2ffde4c87001111c12#gasスクリプトを作成)を元にスプレッドシートのIDを入力しないように修正したものが以下になります。

```js:postSensorData.gs
var book = SpreadsheetApp.getActiveSpreadsheet();

//Postされたデータを受け取り
function doPost(e){
  var data = [      
    e.parameter.Date_Master, // マスター日時     
    e.parameter.Date, // 測定日時    
    e.parameter.Temperature, // 気温    
    e.parameter.Humidity, // 湿度    
    e.parameter.Light, // 照度    
    e.parameter.UV, // UV    
    e.parameter.Pressure, // 圧力    
    e.parameter.Noise, // 騒音    
    e.parameter.BatteryVoltage, // 電池電圧    
    new Date(), // アップロード終了時刻    
  ];
  //取得したデータをログに記載
  Logger.log(new Date());
  //スプレッドシートへのデータ行書き込み
  addData(e.parameter.DeviceName, data);
  return ContentService.createTextOutput("ok");
}

//スプレッドシートへのデータ行書き込み
function addData(sheetName, data){
  var sheet =  book.getSheetByName(sheetName);
  sheet.appendRow(data);
}
```



### WebAppへPOSTするスクリプトの作成
BeagleBone BlackへRequestライブラリをインストールします。
```
pip3 install requests
```

[参考記事](https://qiita.com/c60evaporator/items/ed2ffde4c87001111c12#pythonコードにアップロード処理を追加)を元に、持ってないセンサ値は無しに変更したものが以下になります。

```py:omron_env_toSpreadSheet.py
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

```
PERIPHERAL_MAC_ADDRESS へ InkbirdのMACアドレスを、
WEB_APP_URL へ　GASのWebAPPのUrl を、
deviceName へ Googleスプレッドシートのシート名を、それぞれ入力します。

その後、以下のコマンドを実行してスプレッドシートに値が書き込まれていたら動作確認完了です。

```
python3 omron_env_toSpreadSheet.py
```


## 3.BeagleBone Black でスケジュール実行
cronは有効になってるので、[cronでスケジュール実行させるだけです。](https://qiita.com/c60evaporator/items/ed2ffde4c87001111c12#cronでスケジュール実行)


cronで指定した時間がすぎて、スプレッドシートに値が書き込まれていたら動作確認完了です。


## その他
[BeagleBone BlackのLED、暗闇だとチカチカして寝れないので消しておきます。](https://ftvoid.com/blog/post/106)
```
echo none > /sys/class/leds/beaglebone:green:usr0/trigger
```


## 参考
- [Inkbird IBS-TH1の値をRaspberryPiでロギング](https://qiita.com/c60evaporator/items/fcc16ac9ab582a25c376)
