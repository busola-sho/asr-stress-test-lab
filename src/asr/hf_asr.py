from transformers import pipeline
from src.asr.base import ASRModel
import torch


class HuggingFaceASR(ASRModel):
    def __init__(self, model_id: str, device="auto"):
        """
        device = -1 means CPU.
        device = 0 means first GPU, if available.
        """
        self.device = self._resolve_device(device)
        self.model_id = model_id
        self.pipe = pipeline(
            task="automatic-speech-recognition",
            model=model_id,
            device=self.device,
        )
    
    def _resolve_device(self, device):
        if device == "auto":
            if torch.cuda.is_available():
                return 0
            if torch.backends.mps.is_available():
                return torch.device("mps")
            return -1

        if device == "cpu":
            return -1

        if device == "cuda":
            return 0

        if device == "mps":
            return torch.device("mps")

        return device

    def transcribe(self, audio_input) -> str:
        output = self.pipe(
            audio_input,
            return_timestamps=True,
            generate_kwargs={
                "language": "english",
                "task": "transcribe",
            },
        )
        if isinstance(output, dict):
            return output.get("text", "")
        return str(output).strip()