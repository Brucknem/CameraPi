import RPi.GPIO as gpio

ledPin = 11
buttonPin = 12

def setup():
    print('Program is starting...')
    gpio.setmode(gpio.BOARD)
    gpio.setup(ledPin, gpio.OUT)
    gpio.setup(buttonPin, gpio.IN, pull_up_down = gpio.PUD_UP)

def loop():
    while True:
        if gpio.input(buttonPin) == gpio.LOW:
            gpio.output(ledPin, gpio.HIGH)
            print('led on ...')
        else:
            gpio.output(ledPin, gpio.LOW)
            print('led off ...')

def destroy():
    gpio.output(ledPin, gpio.LOW)
    gpio.cleanup()

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()