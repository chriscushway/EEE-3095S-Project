# Import libraries
import busio
import digitalio
import time
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import ES2EEPROMUtils
import os
import threading
import RPi.GPIO as GPIO

# Set of globals
buzzer = 17         # We are using BCM numbering convention
stop_button = 27

# This will be used to determine whether the system should stop monitoring the terrarium environment
# It is defaulted to false as initially the system is monitoring
stop = False

start_time = time.time()
sys_time = start_time

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

#create eeprom object
eeprom = ES2EEPROMUtils.ES2EEPROM()

def setup_stop_button():
    GPIO.setup(stop_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # Detect rising edge since we are using a pull down resistor
    GPIO.add_event_detect(stop_button, GPIO.RISING, callback=stop_start_monitoring, bouncetime=200)

# Function which will either stop or start monitoring the terrarium environment
def stop_start_monitoring(channel):
    global stop, printed

    # Toggle the switch state to determine whether or not the user was stopping or starting monitoring
    stop = False if stop else True

    if (stop):
        print('stopping the monitoring')
    else:
        print('starting the monitoring')

# We store the amount of samples that are in the EEPROM memory in the first byte
def fetch_sample_count():
    return eeprom.read_byte(0)

def update_sample_count(sample_count):
    eeprom.write_block(0, [sample_count])

def store_sample(sample_value):
    old_data = fetch_samples()
    num_samples = fetch_sample_count()
    print('there are ' + str(num_samples) + ' samples')
    new_data = old_data

    if (num_samples < 20):
        num_samples += 1
        new_data.append(num_samples)
    else:
        new_data = old_data[1:len(old_data)]
    update_sample_count(num_samples)
    eeprom.write_block(1,new_data)

def fetch_samples():
    num_samples = fetch_sample_count()
    scores = eeprom.read_block(1, 16*4)
    return scores

def print_samples(raw_data):
    print('raw data is printing')
    print(raw_data)
    for i in range(0,len(raw_data),4):
        print(str(raw_data[i]) + str(raw_data[i + 1]) + str(raw_data[i + 2]) + str(raw_data[i + 3]))

# function to convert the voltage on the adc channel into temperature in C
def calculate_temp():
    global chan
    return (chan.voltage - 0.5)/0.01

def setup_buzzer():
    GPIO.setup(buzzer, GPIO.OUT)

def setup():
    setup_buzzer()
    setup_stop_button()

def read_temp_value():
    samples_printed = 0
    while True:
        if (int(time.time() - start_time) % 5 == 0):
            if ((samples_printed + 1) % 5 == 0 or samples_printed == 0):
                print_output(calculate_temp(), '*')
            else:
                print_output(calculate_temp(), '')
            samples_printed += 1
        time.sleep(1)
        


def print_output(temp, buzzer=''):
    curr_time = time.localtime() 
    curr_clock = time.strftime("%H:%M:%S", curr_time)
    syst_time = time.time() - sys_time
    syst_time = time.strftime('%H:%M:%S', time.gmtime(syst_time))

    print('{0}  {1}   {2:.0f} C {3}'.format(curr_clock, syst_time, temp, buzzer))
    
    

if __name__ == "__main__":
    thread = threading.Thread(target=read_temp_value)
    thread.daemon = True #make thread die when program dies
    thread.start()
    try:
        setup()
        print('Time      Sys Timer  Temp  Buzzer')
        while True:
            time.sleep(0.1)
            
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()