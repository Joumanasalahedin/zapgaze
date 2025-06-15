import time
import cv2
from camera_manager import CameraManager
from mediapipe_adapter import MediaPipeAdapter


def run_acquisition_loop():
    camera = CameraManager()
    adapter = MediaPipeAdapter()

    camera.start_camera()
    adapter.initialize()

    print("Starting Mediapipe acquisition. Press 'q' to stop.")

    try:
        while True:
            frame = camera.get_frame()
            result = adapter.analyze_frame(frame)

            # Draw eye centers
            for center in result['eye_centers']:
                cv2.circle(frame, center, 3, (0, 255, 0), -1)  # Inner dot
                cv2.circle(frame, center, 5, (0, 255, 0), 1)   # Outer circle

            # Overlay EAR and blink count
            cv2.putText(frame, f"EAR: {result['ear']}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Blinks: {result['total_blinks']}", (
                10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            if result['blink']:
                cv2.putText(frame, 'BLINK!', (100, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            cv2.imshow('ZapGaze Mediapipe', frame)

            print(
                f"Faces: {result['num_faces']}, Eyes: {len(result['eye_centers'])}, "
                f"Blink: {result['blink']}, EAR: {result['ear']}, Blinks: {result['total_blinks']}"
            )

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.03)

    except KeyboardInterrupt:
        pass

    finally:
        camera.release_camera()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    run_acquisition_loop()
