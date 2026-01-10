import random
import time


class GoNoGoTask:
    def __init__(self, trials, go_prob, stim_duration, isi):
        self.trials = trials
        self.go_prob = go_prob
        self.stim_duration = stim_duration
        self.isi = isi

    def run(self):
        """
        Generator yielding (stimulus, onset_timestamp)
        """
        for _ in range(self.trials):
            stimulus = "X" if random.random() > self.go_prob else "O"
            onset = time.time()
            print(f"\r{stimulus}", end="", flush=True)
            time.sleep(self.stim_duration)
            print("\r ", end="", flush=True)
            yield stimulus, onset
            time.sleep(self.isi)

    def wait_for_response(self, timeout=1.0):
        """
        Waits up to `timeout` seconds for the user to press Enter.
        Returns (response: bool, rt: float)
        """
        start = time.time()
        print("Press Enter for Go...", end="", flush=True)
        import sys
        import select

        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            _ = sys.stdin.readline()
            rt = time.time() - start
            return True, rt
        return False, None
