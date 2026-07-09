from openai import OpenAI

from src.asr.base import ASRModel


class OpenAIASR(ASRModel):
    def __init__(self, model_id: str = "gpt-4o-transcribe"):
        self.model_id = model_id
        self.client = OpenAI()

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as audio_file:
            result = self.client.audio.transcriptions.create(
                model=self.model_id,
                file=audio_file,
            )

        return result.text.strip()