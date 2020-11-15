import argparse
import RPi.GPIO as GPIO
from time import sleep
import sys, signal

def runMotor():
    # 4-wire bipolar stepper motor - NEMA-17 42BYGHW609
    GPIO.setmode(GPIO.BCM)

    # Enable pins for IN1-4
    control_pin = [4,17,27,22]
    delay = 0.001 #change for speed

    def signal_handler(signal, frame):
        print('Exiting program...')
        GPIO.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)


    # IN1-4 pin setup
    for pin in control_pin:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0) #counter-clockwise rotation

    halfstep_seq = [[1,0,0,0],
                    [1,1,0,0],
                    [0,1,0,0],
                    [0,1,1,0],
                    [0,0,1,0],
                    [0,0,1,0],
                    [0,0,0,1],
                    [1,0,0,1]]

    #setting stepper
    time = 10.0//delay
    counter = 0
    while counter<time:
        counter += 1
        for i in range(512):
            for step in range(8):
                for pin in range(4):
                    GPIO.output(control_pin[pin],halfstep_seq[step][pin])
                sleep(delay)
