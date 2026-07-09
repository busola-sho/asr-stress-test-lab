from src.asr.hf_asr import HuggingFaceASR
from src.asr.openai_asr import OpenAIASR

def create_asr_model(provider: str, model_id: str, device="auto"):
    provider = provider.lower()

    if provider == "hf":
        return HuggingFaceASR(model_id=model_id, device=device)

    if provider == "openai":
        return OpenAIASR(model_id=model_id)

    raise ValueError(f"Unknown ASR provider: {provider}")

