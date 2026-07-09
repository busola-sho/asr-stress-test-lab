# ASR Diagnostic: whisper-small

Overall WER: **34.5%**

## Likely failure areas

- **Numbers Dates Amounts**: 45.9% WER
- **Negations**: 43.2% WER
- **Sound Confusions**: 37.4% WER
- ** accent**: 96.8% WER
- **Hong Kong English accent**: 28.6% WER

## Example failures

### Numbers Dates Amounts

Reference: ASSUMED ALL AT ONCE AN APPEARANCE OF NOISE AND DISORDER NEVER BELIEVE HOWEVER DISINTERESTED THE LOVE OF A KEPT WOMAN MAY BE THAT IT WILL COST ONE NOTHING

Prediction:  Assumed all at once an appearance of noise and disorder. Never believe, however disinterested, the love of a kept woman may be, that it will cost one nothing.

### Negations

Reference: ASSUMED ALL AT ONCE AN APPEARANCE OF NOISE AND DISORDER NEVER BELIEVE HOWEVER DISINTERESTED THE LOVE OF A KEPT WOMAN MAY BE THAT IT WILL COST ONE NOTHING

Prediction:  Assumed all at once an appearance of noise and disorder. Never believe, however disinterested, the love of a kept woman may be, that it will cost one nothing.

### Sound Confusions

Reference: ASSUMED ALL AT ONCE AN APPEARANCE OF NOISE AND DISORDER NEVER BELIEVE HOWEVER DISINTERESTED THE LOVE OF A KEPT WOMAN MAY BE THAT IT WILL COST ONE NOTHING

Prediction:  Assumed all at once an appearance of noise and disorder. Never believe, however disinterested, the love of a kept woman may be, that it will cost one nothing.

###  accent

Reference: ASSUMED ALL AT ONCE AN APPEARANCE OF NOISE AND DISORDER NEVER BELIEVE HOWEVER DISINTERESTED THE LOVE OF A KEPT WOMAN MAY BE THAT IT WILL COST ONE NOTHING

Prediction:  Assumed all at once an appearance of noise and disorder. Never believe, however disinterested, the love of a kept woman may be, that it will cost one nothing.

### Hong Kong English accent

Reference: Not everybody agrees that globalisation is progress

Prediction:  Not everybody agrees that globalization is progress.
