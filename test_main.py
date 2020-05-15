import src.web.FlaskServer as FlaskServer
from src.utils.Utils import is_raspbian

if __name__ == '__main__':
    if is_raspbian():
        from src.camera.camera_pi import Camera
    else:
        from src.camera.camera import Camera
    camera = Camera()
    FlaskServer.run(actual_camera=Camera())
