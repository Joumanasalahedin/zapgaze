import cv2
import numpy as np
import mediapipe as mp
from eye_tracker_adapter import EyeTrackerAdapter


class PyGazeAdapter(EyeTrackerAdapter):
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Enhanced blink detection parameters
        self.EAR_THRESHOLD = 0.15  # Lowered threshold for better blink detection
        self.CONSECUTIVE_FRAMES = 2  # Frames below threshold to confirm blink
        self.ear_history = []  # Store recent EAR values
        self.frames_below_threshold = 0
        self.blink_count = 0

        # Define the indices for the eye landmarks
        self.LEFT_EYE_INDICES = [362, 382, 381, 380, 374, 373,
                                 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE_INDICES = [33, 7, 163, 144, 145, 153,
                                  154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

    def initialize(self):
        # Nothing special required
        pass

    def calibrate(self):
        # Calibration stub; no-op for now
        pass

    def calculate_ear(self, landmarks, eye_indices):
        """
        Calculate Eye Aspect Ratio (EAR) using MediaPipe landmarks.
        """
        # Get the coordinates of the eye landmarks
        points = np.array([(landmarks[idx].x, landmarks[idx].y)
                          for idx in eye_indices])

        # Calculate the vertical distances
        v1 = np.linalg.norm(points[1] - points[5])
        v2 = np.linalg.norm(points[2] - points[4])

        # Calculate the horizontal distance
        h = np.linalg.norm(points[0] - points[3])

        # Calculate EAR
        ear = (v1 + v2) / (2.0 * h)
        return ear

    def analyze_frame(self, frame):
        """
        Detect face and eyes using MediaPipe Face Mesh.
        Returns:
            {
                "num_faces": int,
                "eye_centers": List[(x, y)],
                "blink": bool   # True if a blink was detected this frame
            }
        """
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Face Mesh
        results = self.face_mesh.process(rgb_frame)

        eye_centers = []
        blink_detected = False
        current_ear = 0.0

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]

            # Calculate EAR for both eyes
            left_ear = self.calculate_ear(
                face_landmarks.landmark, self.LEFT_EYE_INDICES)
            right_ear = self.calculate_ear(
                face_landmarks.landmark, self.RIGHT_EYE_INDICES)

            # Average EAR
            current_ear = (left_ear + right_ear) / 2.0

            # Get eye centers for visualization
            h, w = frame.shape[:2]
            left_eye_center = (
                int(face_landmarks.landmark[self.LEFT_EYE_INDICES[0]].x * w),
                int(face_landmarks.landmark[self.LEFT_EYE_INDICES[0]].y * h)
            )
            right_eye_center = (
                int(face_landmarks.landmark[self.RIGHT_EYE_INDICES[0]].x * w),
                int(face_landmarks.landmark[self.RIGHT_EYE_INDICES[0]].y * h)
            )
            eye_centers = [left_eye_center, right_eye_center]

            # Store EAR history for smoothing
            self.ear_history.append(current_ear)
            if len(self.ear_history) > 10:
                self.ear_history.pop(0)

            # Use smoothed EAR if we have enough history
            if len(self.ear_history) >= 3:
                smoothed_ear = np.mean(self.ear_history[-3:])
            else:
                smoothed_ear = current_ear

            # Check if EAR is below blink threshold
            if smoothed_ear < self.EAR_THRESHOLD:
                self.frames_below_threshold += 1
            else:
                # EAR is above threshold - check if we had a blink
                if self.frames_below_threshold >= self.CONSECUTIVE_FRAMES:
                    blink_detected = True
                    self.blink_count += 1
                self.frames_below_threshold = 0
        else:
            # No face detected - reset counters
            self.frames_below_threshold = 0

        return {
            "num_faces": 1 if results.multi_face_landmarks else 0,
            "eye_centers": eye_centers,
            "blink": blink_detected,
            "ear": round(current_ear, 3),
            "total_blinks": self.blink_count
        }
