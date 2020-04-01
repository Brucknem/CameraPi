from sense_hat import SenseHat
from datetime import datetime

file_date_format_string = '%Y_%m_%d_%H_%M_%S'
log_date_format_string = '%d-%m-%Y (%H:%M:%S)'
datetime_now = datetime.now()
sense = SenseHat()

log_file = '/home/pi/script_log_' + datetime_now.strftime(file_date_format_string) + '.txt'


def write_to_log(message):
    with open(log_file, 'a+') as file:
        file.write('[' + datetime.now().strftime(log_date_format_string)
                + ']\t')
        file.write(message)
        file.write('\n')

write_to_log('Started monitoring')

# Define the functions
def red():
    try:    
        sense.clear(255, 0, 0)
        pressure = sense.get_pressure()
        print(pressure)
    

def blue():
  sense.clear(0, 0, 255)
  temperature_humidity = sense.get_temperature_from_humidity()
  temperature_pressure = sense.get_temperature_from_pressure()

  print(temperature_humidity)
  print(temperature_pressure)

def green():
  sense.clear(0, 255, 0)

  humidity = sense.get_humidity()
  print(humidity)
  
def yellow():
  sense.clear(255, 255, 0)

# Tell the program which function to associate with which direction
sense.stick.direction_up = red
sense.stick.direction_down = blue
sense.stick.direction_left = green
sense.stick.direction_right = yellow
sense.stick.direction_middle = sense.clear    # Press the enter key

while True:
  pass  # This keeps the program running to receive joystick events
