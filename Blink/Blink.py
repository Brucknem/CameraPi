import RPi.GPIO as GPIO
import time

ledPin = 11

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.output(ledPin, GPIO.LOW)
    print('using pin %d' %ledPin)

def loop():
    while True:
        GPIO.output(ledPin, GPIO.HIGH)
        print('... led on')
        time.sleep(1)
        GPIO.output(ledPin, GPIO.LOW)
        print('... led off')
        time.sleep(1)

def destroy():
    GPIO.output(ledPin, GPIO.LOW)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()