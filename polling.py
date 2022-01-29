import time
import serial
import RPi.GPIO as GPIO
from aps_yc600 import ApsYc600

SER_PORT = serial.serial_for_url('/dev/ttyS0')
SER_PORT.baudrate = 115200

RESET_PIN = 19
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
print(INVERTER.poll_inverter(0))

GPIO.cleanup() # cleanup all GPIO 
