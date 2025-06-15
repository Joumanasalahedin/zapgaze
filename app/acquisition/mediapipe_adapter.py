import cv2
import numpy as np
import mediapipe as mp
from eye_tracker_adapter import EyeTrackerAdapter


class MediaPipeAdapter(EyeTrackerAdapter):
    def __init__(self,
                 ear_threshold: float = 0.30,
                 consecutive_frames: int = 2):
        # MediaPipe Face Mesh setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False,
                                                    max_num_faces=1,
                                                    refine_landmarks=True,
                                                    min_detection_confidence=0.5,
                                                    min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # EAR and blink detection parameters
        self.EAR_THRESHOLD = ear_threshold
        self.CONSEC_FRAMES = consecutive_frames
        self.frame_counter = 0
        self.blink_count = 0
        self.ear_history = []  # Store recent EAR values
        self.max_ear = 0.0     # Track maximum EAR value
        self.min_ear = float('inf')  # Track minimum EAR value
        self.ear_window = 30   # Window size for min/max calculation

        # Updated indices for eye landmarks from MediaPipe Face Mesh
        # Left eye (using more precise landmarks around the iris)
        self.LEFT_EYE = [33, 7, 163, 144, 145, 153, 154,
                         155, 133, 173, 157, 158, 159, 160, 161, 246]
        # Right eye (using more precise landmarks around the iris)
        self.RIGHT_EYE = [362, 382, 381, 380, 374, 373, 390,
                          249, 263, 466, 388, 387, 386, 385, 384, 398]

    def initialize(self):
        pass

    def calibrate(self):
        pass

    def _eye_aspect_ratio(self, landmarks, eye_indices, image_w, image_h):
        # Extract coordinates
        coords = [(int(landmarks[idx].x * image_w), int(landmarks[idx].y * image_h))
                  for idx in eye_indices]

        # Calculate the center of the eye using all landmarks
        center_x = sum(x for x, _ in coords) // len(coords)
        center_y = sum(y for _, y in coords) // len(coords)
        eye_center = (center_x, center_y)

        # Compute distances for EAR
        # vertical distances
        A = np.linalg.norm(np.array(coords[1]) - np.array(coords[5]))
        B = np.linalg.norm(np.array(coords[2]) - np.array(coords[4]))
        # horizontal distance
        C = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
        ear = (A + B) / (2.0 * C + 1e-6)

        return ear, eye_center

    def analyze_frame(self, frame):
        # Convert to RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)

        blink_detected = False
        eye_centers = []
        ear_val = 0.0
        num_faces = 0

        if results.multi_face_landmarks:
            num_faces = len(results.multi_face_landmarks)
            face_landmarks = results.multi_face_landmarks[0].landmark
            h, w, _ = frame.shape

            # Compute EAR for each eye
            left_ear, left_center = self._eye_aspect_ratio(
                face_landmarks, self.LEFT_EYE, w, h)
            right_ear, right_center = self._eye_aspect_ratio(
                face_landmarks, self.RIGHT_EYE, w, h)
            ear_val = float(np.mean([left_ear, right_ear]))

            # Store EAR history
            self.ear_history.append(ear_val)
            if len(self.ear_history) > self.ear_window:
                self.ear_history.pop(0)

            # Update max and min EAR values
            if len(self.ear_history) >= self.ear_window:
                self.max_ear = max(self.ear_history)
                self.min_ear = min(self.ear_history)
                ear_range = self.max_ear - self.min_ear

                # Calculate relative EAR (0 to 1 scale)
                if ear_range > 0:
                    relative_ear = (ear_val - self.min_ear) / ear_range
                    # Blink is detected when relative EAR drops below 0.3
                    if relative_ear < 0.3:
                        self.frame_counter += 1
                    else:
                        if self.frame_counter >= self.CONSEC_FRAMES:
                            blink_detected = True
                            self.blink_count += 1
                        self.frame_counter = 0

            # Eye centers
            eye_centers = [left_center, right_center]

        return {
            "num_faces": num_faces,
            "eye_centers": eye_centers,
            "blink": blink_detected,
            "ear": round(ear_val, 3),
            "total_blinks": self.blink_count
        }
