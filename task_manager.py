import time
import argparse
import requests
import logging
from app.tasks.task_manager import GoNoGoTask

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")


def parse_args():
    p = argparse.ArgumentParser("Go/No-Go Task Manager")
    p.add_argument("--user-id",    type=int,   required=True)
    p.add_argument("--session-uid", type=str,   required=True)
    p.add_argument("--api-base",   type=str,   default="http://localhost:8000")
    p.add_argument("--trials",     type=int,   default=100)
    p.add_argument("--go-prob",    type=float, default=0.8,
                   help="Probability of a Go stimulus")
    p.add_argument("--stim-duration", type=float, default=0.5,
                   help="Seconds stimulus on screen")
    p.add_argument("--isi",        type=float, default=1.0,
                   help="Inter-stimulus interval (s)")
    return p.parse_args()


def main():
    args = parse_args()
    base = args.api_base.rstrip('/')
    start_url = f"{base}/session/start"
    event_url = f"{base}/session/event"
    stop_url = f"{base}/session/stop"

    resp = requests.post(start_url, json={"user_id": args.user_id})
    resp.raise_for_status()
    logging.info(f"Session started: {resp.json()}")

    task = GoNoGoTask(
        trials=args.trials,
        go_prob=args.go_prob,
        stim_duration=args.stim_duration,
        isi=args.isi
    )

    for trial_idx, (stimulus, onset_time) in enumerate(task.run()):
        requests.post(event_url, json={
            "user_id": args.user_id,
            "session_uid": args.session_uid,
            "timestamp": onset_time,
            "event_type": "stimulus_onset",
            "stimulus": stimulus
        })

        response, rt = task.wait_for_response()
        requests.post(event_url, json={
            "user_id": args.user_id,
            "session_uid": args.session_uid,
            "timestamp": time.time(),
            "event_type": "response",
            "stimulus": stimulus,
            "response": response
        })

    resp = requests.post(stop_url, json={"user_id": args.user_id})
    resp.raise_for_status()
    logging.info(f"Session stopped: {resp.json()}")


if __name__ == "__main__":
    main()
