import busio
import digitalio
import time
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import RPi.GPIO as GPIO

GPIO.setup(17, GPIO.OUT)

value = True

if __name__ == "__main__":
    try:
        while True:
            time.sleep(0.5)
            value = False if value else True
            print(value)
            GPIO.output(17,value)

    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()