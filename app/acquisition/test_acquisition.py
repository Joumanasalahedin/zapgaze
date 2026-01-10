import time
import cv2
from camera_manager import CameraManager
from mediapipe_adapter import MediaPipeAdapter


def run_acquisition_loop():
    camera = CameraManager()
    adapter = MediaPipeAdapter(
        ear_threshold_ratio=0.5,
        consecutive_frames=3,
        calibration_frames=50,
        refractory_frames=15,
    )
    camera.start_camera()
    adapter.initialize()

    print("Starting Mediapipe acquisition. Press 'q' to stop.")

    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                print("Failed to get frame from camera")
                break

            result = adapter.analyze_frame(frame)

            # Draw eye centers at computed centroid
            for center in result["eye_centers"]:
                cv2.circle(frame, center, 5, (0, 255, 0), -1)

            # Display EAR, baseline, threshold, and blink count
            cv2.putText(
                frame,
                f"EAR: {result['ear']}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            if result["baseline_ear"] is not None:
                cv2.putText(
                    frame,
                    f"Base: {result['baseline_ear']}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (200, 200, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    f"Thresh: {result['ear_threshold']}",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (200, 0, 0),
                    2,
                )
            cv2.putText(
                frame,
                f"Blinks: {result['total_blinks']}",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            if result["blink"]:
                cv2.putText(
                    frame,
                    "BLINK!",
                    (100, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 0, 255),
                    3,
                )

            cv2.imshow("ZapGaze Mediapipe", frame)

            print(
                f"Faces: {result['num_faces']}, Eyes: {len(result['eye_centers'])}, "
                f"Blink: {result['blink']}, EAR: {result['ear']}, Total: {result['total_blinks']}"
            )

            # Improved key detection with longer wait time
            key = cv2.waitKey(30) & 0xFF
            if key == ord("q") or key == ord("Q"):
                print("Quit key pressed. Exiting...")
                break
            elif key == 27:  # ESC key
                print("ESC key pressed. Exiting...")
                break

            time.sleep(0.03)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Exiting...")
    except Exception as e:
        print(f"Error during acquisition: {e}")
    finally:
        print("Cleaning up...")
        camera.release_camera()
        cv2.destroyAllWindows()
        # Force close all windows
        for i in range(5):
            cv2.waitKey(1)


if __name__ == "__main__":
    run_acquisition_loop()
