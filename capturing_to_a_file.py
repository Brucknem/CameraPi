from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (1600, 1200)
camera.vflip = True


camera.start_preview()
sleep(90000)
# camera.start_recording('/home/pi/nightsight/recordings/video.h264')
# camera.annotate_text = "Hallo Herzii <3"
# camera.wait_recording(10)
# camera.stop_recording()
# camera.stop_preview()
