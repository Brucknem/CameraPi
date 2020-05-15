from src.utils.Utils import is_raspbian
from src.web.flask_server import run_threaded

if __name__ == '__main__':
    if is_raspbian():
        from src.camera.camera_pi import Camera
    else:
        from src.camera.camera_image_stream import Camera

    run_threaded(Camera())

    while True:
        pass
