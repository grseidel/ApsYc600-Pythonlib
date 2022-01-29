import serial
import time
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
# The serial is required for pairing, inverter ID is unknown (0000)
INDEX = INVERTER.add_inverter('408000199410', '0000', 2)
print("Inverter ID is", INVERTER.pair_inverter(INDEX))
# The inverter ID needs to be stored for future communications

GPIO.cleanup() # cleanup all GPIO 
