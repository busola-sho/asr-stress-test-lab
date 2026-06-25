"""
suggest_categories.py v1

Rule-based category suggester for Accent Stress Test Lab.

Given a reference transcript, suggest which stress-test categories it may belong to:
- negation_tiny_words
- named_entities
- numbers_dates_amounts
- dialect_words_slang_idioms
- accent_sound_confusions

Important: this does not give final labels. It only suggests candidate categories
for manual review.
"""

import re
 
NEGATION_TERMS = [
    "not", "no", "never", "without", "unless",
    "didn't", "doesn't", "don't", "can't", "cannot",
    "won't", "wasn't", "weren't", "isn't", "aren't",
    "before", "after", "only"
]

DIALECT_VOCAB = {
    "scottish": ["wee", "aye", "nae", "ken", "bairn"],
    "nigerian_pidgin": ["wahala", "abi", "dey", "sha", "oga", "sabi"]
}

SOUND_CONFUSION_TERMS = [
    "three", "thirty", "think", "thing", "this", "that",
    "ship", "sheep", "sit", "seat",
    "walk", "work",
    "full", "fool",
    "car", "care"
]


NUMBER_WORDS = [
    "zero", "one", "two", "three", "four", "five", "six",
    "seven", "eight", "nine", "ten", "eleven", "twelve",
    "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
    "eighteen", "nineteen", "twenty", "thirty", "forty",
    "fifty", "sixty", "seventy", "eighty", "ninety",
    "hundred", "thousand", "million", "billion"
]


MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]

def find_terms(text: str, terms: list[str]) -> list[str]:
    """
    Return terms that appear in the text.
    Uses word boundaries so 'no' does not match inside 'nobody'.
    """
    text=text.lower()
    matches=[]

    for term in terms:
        pattern=r"\b" + re.escape(term.lower()) + r"\b"
        if re.search(pattern, text):
            matches.append(term)
    return matches

def find_numbers_dates_amounts(text: str) -> list[str]:
    text_lower = text.lower()
    matches = []

    regex_patterns = {
        "digit": r"\d",
        "time": r"\b\d{1,2}:\d{2}\b",
        "money_symbol": r"[£$€]",
        "date_suffix": r"\b\d{1,2}(st|nd|rd|th)\b",
        "year": r"\b(19|20)\d{2}\b",
        "four_digit_number": r"\b\d{4}\b" #could be pin, year or anything.
    }

    for label, pattern in regex_patterns.items():
        if re.search(pattern, text_lower):
            matches.append(label)

    matches.extend(find_terms(text_lower, NUMBER_WORDS))
    matches.extend(find_terms(text_lower, MONTHS))
    matches.extend(find_terms(text_lower, ["pounds", "dollars", "euros"]))

    return sorted(set(matches))

def find_named_entities(text):
    """
    This will be replaced later by spaCy, but for now
    let's just find the capitalised words not at the start of the sentence.
    """
    pattern = r"\b[A-Z][a-zA-Z'-]+\b"
    capitalised_words=re.findall(pattern, text)
    words=text.split()

    if not words:
        return []

    #let's get the first word out and cleaned, if not it'll be confused as a named entity all the time.
    first_word=re.sub(r"\b[^a-zA-z'-]","",words[0])

    entities=[
        word for word in capitalised_words if word!=first_word
    ]

    return entities
    
def normalise_text(text:str):
    return text.lower().strip()


def suggest_categories(text:str, use_named_entities):
    """
    This fxn and it's components will get more and more intelligent per version.
    """
    suggestions=[]

    number_dates=find_numbers_dates_amounts(text)
    if number_dates:
        suggestions.append({
            "category": "numbers_dates_amounts",
            "matched_terms": number_dates
        })

    negations=find_terms(text, NEGATION_TERMS)
    if negations:
        suggestions.append({
            "category": "negations",
            "matched_terms": negations
        })

    dialects=[]
    for dialect, words in DIALECT_VOCAB.items():
        found=find_terms(text,words)
        if found:
            dialects.append(found)
    if dialects:
        suggestions.append({
            "category": "dialect_words",
            "matched_terms": dialects
        })
    
    confusions=find_terms(text, SOUND_CONFUSION_TERMS)
    if confusions:
        suggestions.append({
            "category": "sound_confusions",
            "matched_terms": confusions
        })
    
    if use_named_entities:
        named_entities=find_named_entities(text)
        if named_entities:
            suggestions.append({
                        "category": "named_entities",
                        "matched_terms": named_entities
                    })

    return suggestions


if __name__ == "__main__":
    examples = [
        "I did not see him leave before midnight.",
        "Olubusolami met Euan at St John's College.",
        "The appointment is on the 13th of February at 4:15.",
        "That was a wee bit strange.",
        "Three officers searched the car.",
        "I did not meet Chinedu on the 14th of March.",
        "There really is a lot of wahala o."
    ]

    for example in examples:
        print("\nTEXT:", example)
        print("SUGGESTIONS:", suggest_categories(example))