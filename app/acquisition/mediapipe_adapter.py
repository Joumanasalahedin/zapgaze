import cv2
import numpy as np
import mediapipe as mp
import math
from .eye_tracker_adapter import EyeTrackerAdapter


class MediaPipeAdapter(EyeTrackerAdapter):
    def __init__(
        self,
        ear_threshold_ratio: float = 0.7,
        consecutive_frames: int = 2,
        calibration_frames: int = 50,
        refractory_frames: int = 10,
    ):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.drawing_spec = mp.solutions.drawing_utils.DrawingSpec(
            color=(0, 255, 0), thickness=1
        )

        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]

        self.consec_frames = consecutive_frames
        self.refractory_frames = refractory_frames

        self.calibration_frames = calibration_frames
        self.ear_history_calib = []
        self.calibrated = False
        self.baseline_ear = None
        self.ear_threshold_ratio = ear_threshold_ratio
        self.ear_threshold = None

        self.frame_counter = 0
        self.blink_count = 0
        self.frames_since_blink = refractory_frames

    def initialize(self):
        pass

    def calibrate(self):
        pass

    def _eye_aspect_ratio_and_center(self, landmarks, eye_indices, width, height):
        coords = [
            (int(landmarks[idx].x * width), int(landmarks[idx].y * height))
            for idx in eye_indices
        ]
        A = np.linalg.norm(np.array(coords[1]) - np.array(coords[5]))
        B = np.linalg.norm(np.array(coords[2]) - np.array(coords[4]))
        C = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
        ear = (A + B) / (2.0 * C + 1e-6)
        xs, ys = zip(*coords)
        center = (int(np.mean(xs)), int(np.mean(ys)))
        return ear, center

    def analyze_frame(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)
        pupil_size = None

        blink = False
        eye_centers = []
        ear_val = 0.0
        num_faces = 0
        landmarks = None
        h, w, _ = frame.shape

        if results.multi_face_landmarks:
            num_faces = 1
            landmarks = results.multi_face_landmarks[0].landmark

            left_ear, left_center = self._eye_aspect_ratio_and_center(
                landmarks, self.LEFT_EYE, w, h
            )
            right_ear, right_center = self._eye_aspect_ratio_and_center(
                landmarks, self.RIGHT_EYE, w, h
            )
            ear_val = float(min(left_ear, right_ear))
            eye_centers = [left_center, right_center]

        if landmarks is not None:
            LEFT_IRIS_IDX = [468, 469, 470, 471, 472, 473]
            pts = []
            for idx in LEFT_IRIS_IDX:
                lm = landmarks[idx]
                pts.append((lm.x * w, lm.y * h))
                cx = sum(x for x, y in pts) / len(pts)
                cy = sum(y for x, y in pts) / len(pts)
                radius = sum(math.hypot(x - cx, y - cy) for x, y in pts) / len(pts)
            pupil_size = float(radius * 2)

        if not self.calibrated:
            if ear_val > 0:
                self.ear_history_calib.append(ear_val)
            if len(self.ear_history_calib) >= self.calibration_frames:
                self.baseline_ear = float(np.median(self.ear_history_calib))
                self.ear_threshold = self.baseline_ear * self.ear_threshold_ratio
                self.calibrated = True

        if self.calibrated:
            if ear_val < self.ear_threshold:
                self.frame_counter += 1
            else:
                if (
                    self.frame_counter >= self.consec_frames
                    and self.frames_since_blink >= self.refractory_frames
                ):
                    blink = True
                    self.blink_count += 1
                    self.frames_since_blink = 0
                self.frame_counter = 0
            self.frames_since_blink += 1

        return {
            "num_faces": num_faces,
            "eye_centers": eye_centers,
            "blink": blink,
            "ear": round(ear_val, 3),
            "pupil_size": round(pupil_size, 1) if pupil_size is not None else None,
            "baseline_ear": round(self.baseline_ear, 3) if self.calibrated else None,
            "ear_threshold": round(self.ear_threshold, 3) if self.calibrated else None,
            "total_blinks": self.blink_count,
        }
