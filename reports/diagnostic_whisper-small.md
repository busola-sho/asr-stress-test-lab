# ASR Diagnostic: whisper-small

Overall WER: **11.7%**

## Likely failure areas

- **Dialect Words**: 20.1% WER
- **Named Entities**: 18.4% WER
- **Sound Confusions**: 11.9% WER
- **Scottish English accent**: 17.0% WER
- **nigerian accent**: 16.8% WER

## Example failures

### Dialect Words

Dataset: data/raw/scots

Accent: Scottish English

Reference: I’ve got this precious object- I do- I treasure it. Um, it was when I was expecting my fourth child, eh, my friend that I knew, she was really lovely, she gave me this as a gift and it was a Black Madonna. It was wooden, the- the way it was a' carved oot was stunning. And it’s the Black Madonna with her wee baby in her arms, and I thought- it just always- you know, I’ve always treasured it. It’s just lovely.

Prediction:  I've got this precious object I do, I treasure it, it was when I was expecting my fourth child, my friend that I knew, she was really lovely, she gave me this as a gift and it was a black Madonna, the weight was all carved out, it was stunning and it's the black Madonna with wee baby near her arms and I've always treasured it, it's just lovely.
### Named Entities

Dataset: benjaminogbonna/nigerian_accented_english_dataset

Accent: nigerian

Reference: Head south on Ibo Road towards Emir Road

Prediction:  It's out on the Igbo route towards Emia route.
### Sound Confusions

Dataset: benjaminogbonna/nigerian_accented_english_dataset

Accent: nigerian

Reference: Try out this ear worm.

Prediction:  Try out this earworm.