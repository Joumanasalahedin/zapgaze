import time
import argparse
import requests
import logging
from app.acquisition.camera_manager import CameraManager
from app.acquisition.mediapipe_adapter import MediaPipeAdapter

# Configure logging
template = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=template)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Acquisition Client: capture eye-tracking data and send to backend in batches"
    )
    parser.add_argument("--user-id", type=int, required=True,
                        help="User ID from intake step")
    parser.add_argument(
        "--session-uid", type=str, required=True,
        help="Session UID returned by /intake endpoint"
    )
    parser.add_argument(
        "--api-url", type=str,
        default="http://localhost:8000/acquisition/data",
        help="Single-record backend endpoint"
    )
    parser.add_argument(
        "--fps", type=float, default=20.0,
        help="Capture frames per second"
    )
    parser.add_argument(
        "--batch-size", type=int,
        help="Number of frames to batch before sending (default = fps)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    camera = CameraManager()
    adapter = MediaPipeAdapter()

    camera.start_camera()
    adapter.initialize()

    # Compute intervals and batch size
    interval = 1.0 / args.fps
    batch_size = args.batch_size or int(args.fps)

    # Derive batch endpoint from api-url
    base = args.api_url.rstrip('/')
    batch_url = base.rsplit('/', 1)[0] + '/batch'

    logging.info(
        f"Starting acquisition client: {args.fps} FPS, batch size {batch_size}")

    buffer = []
    try:
        while True:
            frame = camera.get_frame()
            result = adapter.analyze_frame(frame)

            # Build single record
            le = result.get("eye_centers", [])
            record = {
                "user_id": args.user_id,
                "session_uid": args.session_uid,
                "timestamp": time.time(),
                "left_eye": {"x": le[0][0], "y": le[0][1]} if len(le) > 0 else {"x": None, "y": None},
                "right_eye": {"x": le[1][0], "y": le[1][1]} if len(le) > 1 else {"x": None, "y": None},
                "ear": result.get("ear"),
                "blink": result.get("blink")
            }
            buffer.append(record)

            # Flush batch when full
            if len(buffer) >= batch_size:
                logging.info(
                    f"Sending batch of {len(buffer)} records to backend")
                try:
                    resp = requests.post(batch_url, json=buffer, timeout=5)
                    resp.raise_for_status()
                    logging.debug("Batch response: {resp.json()}")
                except requests.RequestException as e:
                    logging.warning(f"Failed to send batch: {e}")
                buffer.clear()

            time.sleep(interval)

    except KeyboardInterrupt:
        logging.info("Interrupted by user, flushing remaining data...")
        if buffer:
            try:
                resp = requests.post(batch_url, json=buffer, timeout=5)
                resp.raise_for_status()
                logging.info(f"Sent final batch of {len(buffer)} records")
            except Exception as e:
                logging.warning(f"Failed to send final batch: {e}")
    finally:
        camera.release_camera()
        logging.info("Camera released, exiting.")


if __name__ == "__main__":
    main()
