from multiprocessing import Process
from time import sleep

from src.camera.camera_base import get_camera
from src.web.flask_server import FlaskAppWrapper

if __name__ == '__main__':
    flask_app_wrapper = FlaskAppWrapper(get_camera())
    server = Process(target=flask_app_wrapper.run)
    server.start()

    print('runnning')
    for i in range(10):
        sleep(1)

    server.terminate()
    server.join()
