import RPi.GPIO as gpio
import time
import Helpers

ledPins = [24, 5, 3, 22, 18, 16, 15, 13, 12, 11]

def setup():
    print('Program is starting ...')
    gpio.setmode(gpio.BOARD)

    for pin in ledPins:
        gpio.setup(pin, gpio.OUT)
        gpio.output(pin, gpio.HIGH)

def loop():
    field = Helpers.bitfield(2 + 8 + 32 + 128 + 512, 10)
    print(field)

    # while True:
    #     for pin in ledPins:
    #         toggle(pin)
    #     for pin in ledPins[::-1]:
    #         toggle(pin)

    for i in range(10):
        gpio.output(ledPins[i], (field[i] + 1) % 2)

    while True:
        pass

def toggle(pin):
    gpio.output(pin, gpio.LOW)
    time.sleep(0.1)
    gpio.output(pin, gpio.HIGH)

def destroy():
    for pin in ledPins:
        gpio.output(pin, gpio.HIGH)
    gpio.cleanup()

if __name__ == '__main__':
    setup()

    try:
        loop()
    except KeyboardInterrupt:
        destroy()