# ASR Diagnostic: gpt-4o-transcribe

Overall WER: **11.7%**

## Likely failure areas

- **Dialect Words**: 14.2% WER
- **Named Entities**: 14.2% WER
- **Sound Confusions**: 12.6% WER
- **nigerian accent**: 23.2% WER
- **Scottish English accent**: 15.0% WER

## Example failures

### Dialect Words

Dataset: data/raw/scots

Accent: Scottish English

Reference: Oh- my- I love my- I love my wee Jackson. That was my wee French papillon, my wee dog. But he- he passed away two years ago but, do you know, he’s- he was just so protective towards me. He also- ‘cause I was always- if I was at work or I was buzzing aboot- I would sit doon at night and he would make sure he pounced on me to get me, thinking “Oh that’s me, I’ve got her noo”. Anyway, one of my daughters would say “you’d think you bored him” as if he was my child – he was just lovable. But anyway, he passed away. So, my pets are my grandcats and my granddog. I’ve got a wee dog that, um, one of my daughters have got and I’ve got two cats two other daughters have got. And I’ve grown to love the cats. I’m no a cat person but I’ve grown to love them and my other wee dog.

Prediction: Oh, but I love my wee Jack. His name's my wee French Bapio and my wee dog. He passed away two years ago, but he was just so protective towards me. He also, because I was always, if I was at work or I was buzzing about, I would sit down at night and he would make sure he pounced on me to get me thinking, oh, that's me, I've got her now. Anyway, one of my daughters would say, you think you bored him? Because if he was my child, he was just lovable. But anyway, he passed away. So my pets are my grand cats and my grand dog. I've got a wee dog. One of my daughters has got two cats. Two other daughters have got. And I've grown to love the cats. I'm not a cat person, but I've grown to love them and my other wee dog.
### Named Entities

Dataset: benjaminogbonna/nigerian_accented_english_dataset

Accent: nigerian

Reference: Set an alarm for Saturday.

Prediction: Seċem a lamfo Saturday.
### Sound Confusions

Dataset: benjaminogbonna/nigerian_accented_english_dataset

Accent: nigerian

Reference: This is the full reflection. Ok. Because the water is kind of boiling. Ok.  So this is a bird the bird is black and blue. It's facing, its face is facing us but its full physique is facing left. Okay, yes.

Prediction: Its face is facing us.
### Scottish English accent

Dataset: data/raw/scots

Accent: Scottish English

Reference: I would say internet because it’s quite educational if you need to find something out you can just go into internet. Google is a great one as well, Google Maps for driving, getting you to a destination. So that’s gr- you know, I think all these- it’s got a great advantage th- the technology that’s moved on. Um, and that is, you know, really educational.

Prediction: Obviously internet, because it's quite educational. If you need to find something out you can just get into internet. Google is a great one as well, Google Maps for driving, getting you to a destination. So I think it's got a great advantage, the technology that's moved on and that is really educational.