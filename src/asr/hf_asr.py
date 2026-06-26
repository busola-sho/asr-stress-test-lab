from transformers import pipeline
from src.asr.base import ASRModel


class HuggingFaceASR(ASRModel):
    def __init__(self, model_id: str, device: int = -1):
        """
        device = -1 means CPU.
        device = 0 means first GPU, if available.
        """
        self.model_id = model_id
        self.pipe = pipeline(
            task="automatic-speech-recognition",
            model=model_id,
            device=device,
        )

    def transcribe(self, audio_input) -> str:
        output = self.pipe(audio_input)

        if isinstance(output, dict):
            return output.get("text", "")

        return str(output)