import cv2


class CameraManager:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.capture = None

    def start_camera(self):
        """
        Initialize the webcam capture.
        """
        self.capture = cv2.VideoCapture(self.camera_id)
        if not self.capture.isOpened():
            raise RuntimeError("Unable to open webcam.")

    def get_frame(self):
        """
        Capture a single frame from the webcam.
        Returns a BGR image array.
        """
        if self.capture is None:
            raise RuntimeError("Camera not started.")
        ret, frame = self.capture.read()
        if not ret:
            raise RuntimeError("Failed to read frame from webcam.")
        return frame

    def release_camera(self):
        """
        Release the webcam resource and destroy any open windows.
        """
        if self.capture:
            self.capture.release()
            self.capture = None
