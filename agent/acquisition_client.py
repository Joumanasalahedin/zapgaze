from app.acquisition.mediapipe_adapter import MediaPipeAdapter
from app.acquisition.camera_manager import CameraManager
import time
import argparse
import requests
import logging
import sys
import os

# Add parent directory to Python path to find app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Configure logging
template = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=template)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Acquisition Client: capture eye-tracking data and send to backend in batches"
    )
    parser.add_argument(
        "--session-uid",
        type=str,
        required=True,
        help="Session UID returned by /intake endpoint",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000/acquisition/data",
        help="Single-record backend endpoint",
    )
    parser.add_argument(
        "--fps", type=float, default=20.0, help="Capture frames per second"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        help="Number of frames to batch before sending (default = fps)",
    )
    return parser.parse_args()


def run_acquisition(session_uid, api_url, fps, batch_size=None, stop_event=None):
    """Run acquisition with direct parameters (for use in threads or standalone)"""
    camera = CameraManager()
    adapter = MediaPipeAdapter()

    camera.start_camera()
    adapter.initialize()

    # Compute intervals and batch size
    interval = 1.0 / fps
    batch_size = batch_size or int(fps)

    # Derive batch endpoint from api-url
    base = api_url.rstrip("/")
    batch_url = base.rsplit("/", 1)[0] + "/batch"

    logging.info(f"Starting acquisition client: {fps} FPS, batch size {batch_size}")

    buffer = []
    try:
        while True:
            # Check stop flag if provided
            if stop_event and stop_event.is_set():
                logging.info("Stop flag detected, stopping acquisition...")
                break
            frame = camera.get_frame()
            result = adapter.analyze_frame(frame)

            # Build single record
            le = result.get("eye_centers", [])
            record = {
                "session_uid": session_uid,
                "timestamp": time.time(),
                "left_eye": (
                    {"x": le[0][0], "y": le[0][1]}
                    if len(le) > 0
                    else {"x": None, "y": None}
                ),
                "right_eye": (
                    {"x": le[1][0], "y": le[1][1]}
                    if len(le) > 1
                    else {"x": None, "y": None}
                ),
                "ear": result.get("ear"),
                "blink": result.get("blink"),
                "pupil_size": result.get("pupil_size"),
            }
            buffer.append(record)

            # Flush batch when full
            if len(buffer) >= batch_size:
                logging.info(f"Sending batch of {len(buffer)} records to backend")
                try:
                    resp = requests.post(batch_url, json=buffer, timeout=5)
                    resp.raise_for_status()
                    logging.debug("Batch response: {resp.json()}")
                except requests.RequestException as e:
                    logging.warning(f"Failed to send batch: {e}")
                buffer.clear()

            time.sleep(interval)
            
            # Check stop flag again after sleep
            if stop_event and stop_event.is_set():
                logging.info("Stop flag detected, stopping acquisition...")
                break

    except KeyboardInterrupt:
        logging.info("Interrupted by user, flushing remaining data...")
    except Exception as e:
        logging.error(f"Acquisition error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Flush remaining buffer before stopping
        if buffer:
            try:
                resp = requests.post(batch_url, json=buffer, timeout=5)
                resp.raise_for_status()
                logging.info(f"Sent final batch of {len(buffer)} records")
            except Exception as e:
                logging.warning(f"Failed to send final batch: {e}")
        
        camera.release_camera()
        logging.info("Camera released, exiting.")


def main():
    args = parse_args()
    run_acquisition(args.session_uid, args.api_url, args.fps, args.batch_size)


if __name__ == "__main__":
    main()
