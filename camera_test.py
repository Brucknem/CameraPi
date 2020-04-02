import picamera

dir = 'recordings/'

camera = picamera.PiCamera(resolution=(640, 480))
camera.hflip = False
camera.start_recording(dir + '1.h264')
camera.wait_recording(5)
while i in range(2, 11):
    camera.split_recording(dir + '%d.h264' % i)
    camera.wait_recording(5)
camera.stop_recording()
