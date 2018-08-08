import RPi.GPIO as gpio

ledPin = 11
buttonPin = 12
ledState = False

def setup():
    print('Program is starting...')
    gpio.setmode(gpio.BOARD)
    gpio.setup(ledPin, gpio.OUT)
    gpio.setup(buttonPin, gpio.IN, pull_up_down = gpio.PUD_UP)

def buttonEvent(channel):
    global ledState
    print('buttonEvent GPIO %d' %channel)

    ledState = not ledState
    if ledState:
        print('Turn on LED ... ')
    else:
        print('Turn off LED ... ')
    gpio.output(ledPin, ledState)

def loop():
    gpio.add_event_detect(buttonPin, gpio.FALLING, callback = buttonEvent, bouncetime = 300)
    while True:
        pass

def destroy():
    gpio.output(ledPin, gpio.LOW)
    gpio.cleanup()

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()