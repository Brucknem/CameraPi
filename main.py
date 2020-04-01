import inspect
from datetime import datetime

from sense_hat import SenseHat

file_date_format_string = '%Y_%m_%d_%H_%M_%S'
log_date_format_string = '%d-%m-%Y (%H:%M:%S)'
datetime_now = datetime.now()
sense = SenseHat()

log_file = '/home/pi/script_log_' + datetime_now.strftime(file_date_format_string) + '.txt'


def write_to_log(key: any, value: any = None):
    try:
        with open(log_file, 'a+') as file:
            output_string: str = '[' + datetime.now().strftime(log_date_format_string) + ']\t'

            output_string += inspect.stack()[1][3] + ':\t'
            output_string += str(key)
            if value:
                output_string += ':\t' + str(value)

            output_string += '\n'
            print(output_string)
            file.write(output_string)
    except Exception as err:
        print(err)


write_to_log('Started monitoring')


# Define the functions
def pressure(event):
    if event.action == 'released':
        return

    try:
        sense.clear(255, 0, 0)
        pressure_value = sense.get_pressure()
        write_to_log('Pressure', pressure_value)
    except Exception as err:
        write_to_log(err)


def temperature(event):
    if event.action == 'released':
        return

    try:
        sense.clear(0, 0, 255)
        temperature_humidity = sense.get_temperature_from_humidity()
        temperature_pressure = sense.get_temperature_from_pressure()

        write_to_log('Temperature (Humidity)', temperature_humidity)
        write_to_log('Temperature (Pressure)', temperature_pressure)
    except Exception as err:
        write_to_log(err)


def humidity(event):
    if event.action == 'released':
        return

    try:
        sense.clear(0, 255, 0)

        humidity_value = sense.get_humidity()
        write_to_log('Humidity', humidity_value)
    except Exception as err:
        write_to_log(err)


def start_camera(event):
    if event.action == 'released':
        return
    
    try:
        sense.clear(255, 255, 0)
        write_to_log('Camera', 'started')
    except Exception as err:
        write_to_log(err)


# Tell the program which function to associate with which direction
sense.stick.direction_up = humidity
sense.stick.direction_down = pressure
sense.stick.direction_left = temperature
sense.stick.direction_right = start_camera
sense.stick.direction_middle = sense.clear  # Press the enter key

while True:
    pass  # This keeps the program running to receive joystick events
