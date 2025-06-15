from abc import ABC, abstractmethod


class EyeTrackerAdapter(ABC):
    @abstractmethod
    def initialize(self):
        """
        Perform any initialization or setup for the tracker.
        """
        pass

    @abstractmethod
    def calibrate(self):
        """
        Run any calibration routine (if supported).
        """
        pass

    @abstractmethod
    def analyze_frame(self, frame):
        """
        Process a single video frame and return a dictionary with keys:
            - horizontal_ratio: Optional[float]
            - vertical_ratio: Optional[float]
            - pupil_left: Optional[tuple]
            - pupil_right: Optional[tuple]
        Or, for a simplified adapter, any structure you choose.
        """
        pass
