# Import libraries
import busio
import digitalio
import time
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import RPi.GPIO as GPIO

# Set of globals
buzzer = 17         # We are using BCM numbering convention
stop_button = 27

# This will be used to determine whether the system should stop monitoring the terrarium environment
# It is defaulted to false as initially the system is monitoring
stop = False


def setup_stop_button():
    GPIO.setup(stop_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # Detect rising edge since we are using a pull down resistor
    GPIO.add_event_detect(stop_button, GPIO.RISING, callback=stop_start_monitoring, bouncetime=200)

# Function which will either stop or start monitoring the terrarium environment
def stop_start_monitoring(channel):
    global stop

    # Toggle the switch state to determine whether or not the user was stopping or starting monitoring
    stop = False if stop else True
    
    if (stop):
        print('stopping the monitoring')
    else:
        print('starting the monitoring')

    

def setup_buzzer():
    GPIO.setup(buzzer, GPIO.OUT)

def setup():
    setup_buzzer()
    setup_stop_button()

if __name__ == "__main__":
    try:
        setup()
        while True:
            time.sleep(0.1)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()