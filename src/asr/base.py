from abc import ABC, abstractmethod


class ASRModel(ABC):
    @abstractmethod
    def transcribe(self, audio_input) -> str:
        """
        Takes an audio path/array and returns transcript text.
        """
        pass