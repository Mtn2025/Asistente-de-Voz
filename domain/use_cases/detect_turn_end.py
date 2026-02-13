"""
Use Case: Detect Turn End
Determines if the user has finished speaking based on silence duration.
"""
from ..ports import STTEvent

class DetectTurnEndUseCase:
    """
    Encapsulates logic for detecting end of turn (EOS).
    """

    def __init__(self, silence_threshold_ms: int = 500):
        self.silence_threshold_ms = silence_threshold_ms

    def execute(self, silence_duration_ms: float) -> bool:
        """
        Check if silence duration exceeds threshold.
        """
        return silence_duration_ms >= self.silence_threshold_ms
