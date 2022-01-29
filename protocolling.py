#!/usr/bin/env python
from influxdb import InfluxDBClient
from time import sleep
import time
import datetime
import serial
import RPi.GPIO as GPIO
from aps_yc600 import ApsYc600

SER_PORT = serial.serial_for_url('/dev/ttyS0')
SER_PORT.baudrate = 115200

RESET_PIN = 22
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RESET_PIN, GPIO.OUT)

def reset_modem():
    '''
    Reset modem by toggling reset pin
    '''
    GPIO.output(RESET_PIN, 0)
    time.sleep(1)
    GPIO.output(RESET_PIN, 1)

reset_modem()
time.sleep(1)
INVERTER = ApsYc600(SER_PORT, SER_PORT)
# Inverter ID in this example is 3E9D
INVERTER.add_inverter('408000199410', '3E9D', 2)
print(INVERTER.start_coordinator())
print(INVERTER.ping_radio())

client = InfluxDBClient(host='localhost', port=8086)

timestamp_old = int(time.time()) # later 0 if df_ts is used
energy_panel1_old = 0
energy_panel2_old = 0 

while True:

  try:

    s = INVERTER.poll_inverter(0)

    if s["crc"] == False:
      print(str(datetime.datetime.now().replace(microsecond=0)) + ' CRC error')
    else:
      data = s["data"]
      timestamp = int(time.time()) #later data["dataframe_timestamp"]

      data["watt_panel1"] = (data["energy_panel1"] - energy_panel1_old) / (timestamp - timestamp_old) * 3600
      data["watt_panel2"] = (data["energy_panel2"] - energy_panel2_old) / (timestamp - timestamp_old) * 3600

      writeout = []
      writeout.append(
        {
                "measurement": "YC600",
                "fields": data,
                "time": timestamp * 1000
        }
)

      client.write_points(writeout, database='solaranzeige', time_precision='ms', batch_size=10000, protocol='json')

      timestamp_old = timestamp
      energy_panel1_old = data["energy_panel1"]
      energy_panel2_old = data["energy_panel2"]

      sleep(60)

  except KeyboardInterrupt:
    GPIO.cleanup()
    break

  except:
    if s["error"] == 'timeout':
      print(str(datetime.datetime.now().replace(microsecond=0)) + ' timeout')
      sleep(60) #dark night?
    elif s["error"] == 'NoRoute':
      print(str(datetime.datetime.now().replace(microsecond=0)) + ' NoRoute')
      sleep(60) #dark night?
    else:
      print(str(datetime.datetime.now().replace(microsecond=0)) + ' error: ',s)
#    break
