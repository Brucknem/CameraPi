import logging
import threading
import time

from src.RecordingsFolder import RecordingsFolder
from src.camera.camera_state import CameraState
from src.utils.Observable import Observable
from src.utils.Utils import is_raspbian

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident

__instance = None


def get_camera(chunk_length=300,
               recordings_path: str = './recordings'):
    """
    Factory method for the camera interface
    """
    if is_raspbian():
        from src.camera.camera_pi import Camera
    else:
        from src.camera.camera_image_stream import Camera

    global __instance
    if not __instance:
        __instance = Camera(chunk_length=chunk_length,
                            recordings_path=recordings_path)
    else:
        __instance.chunk_length = chunk_length
        __instance.recordings_folder = RecordingsFolder(recordings_path)
    return __instance


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """

    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()


class CameraBase(Observable):
    """
    Base class for all cameras.

    Partly taken from:
    https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
    """

    def __init__(self, chunk_length: int = 5 * 60,
                 recordings_path: str = './recordings'):
        super().__init__()
        # Actual camera
        self.camera_state = CameraState.IDLE

        # Streaming
        self.streaming_thread = None
        self.frame = None
        self.last_access = 0
        self.event = CameraEvent()

        # Recording
        self.chunk_length = chunk_length
        self.record_thread = None
        self.recordings_folder = RecordingsFolder(recordings_path)

    def __enter__(self):
        """
        Called via with
        """
        self.start_recording()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when with ended
        """
        self.stop_recording()

    def set_camera_state(self, new_mode: CameraState):
        """
        Setter for camera mode.
        """
        logging.debug(str(new_mode))
        self.camera_state = new_mode
        self.notify(state=self.camera_state)

    def start_recording(self):
        """
        Start the recording.
        """
        if not self.camera_state == CameraState.IDLE:
            return

        logging.info('Start recording')
        if self.is_real_camera():
            self.recordings_folder.create_new_recording()

        self.record_thread = threading.Thread(target=self.record, args=())
        self.record_thread.daemon = True
        self.record_thread.start()

    def record(self):
        """
        Record functionality of the camera.
        """
        self.set_camera_state(CameraState.RECORDING)

    def stop_recording(self):
        """
        Stop the recording.
        """
        if self.camera_state is not CameraState.RECORDING:
            return False
        logging.info('Stop recording')
        self.record_thread = None
        self.set_camera_state(CameraState.IDLE)
        return True

    def start_streaming(self):
        """
        Start streaming.
        """
        if self.streaming_thread is None:
            self.last_access = time.time()

            # start background frame thread
            self.streaming_thread = threading.Thread(
                target=self._streaming_thread)
            self.streaming_thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """
        Return the current camera frame.
        """
        self.start_streaming()

        self.last_access = time.time()

        # wait for a signal from the camera thread
        self.event.wait()
        self.event.clear()

        return self.frame

    def frames(self):
        """"
        Generator that returns frames from the camera.
        """
        raise RuntimeError('Must be implemented by subclasses.')

    def _streaming_thread(self):
        """
        Camera streaming background thread.
        """
        print('Starting camera thread.')
        frames_iterator = self.frames()
        for frame in frames_iterator:
            self.frame = frame
            self.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - self.last_access > 10:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        self.streaming_thread = None

    def is_real_camera(self):
        """
        Is this instance a real physical camera
        """
        return False

    def is_recording(self):
        """
        Is recording
        """
        return self.camera_state == CameraState.RECORDING

    def is_idle(self):
        """
        Is idle
        """
        return self.camera_state == CameraState.IDLE
