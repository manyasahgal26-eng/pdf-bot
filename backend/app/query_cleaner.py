import re

from rapidfuzz import fuzz, process

from app.keyword_extractor import load_all_terms


def correct_query_terms(question: str) -> str:
    terms = load_all_terms()

    if not terms:
        return question

    single_word_terms = [term for term in terms if " " not in term]
    phrase_terms = [term for term in terms if " " in term]

    words = question.split()
    corrected_words = []

    for word in words:
        clean_word = re.sub(r"[^a-zA-Z0-9_-]", "", word.lower())

        if len(clean_word) < 4 or not single_word_terms:
            corrected_words.append(word)
            continue

        match = process.extractOne(
            clean_word,
            single_word_terms,
            scorer=fuzz.ratio,
        )

        if match and match[1] >= 82:
            corrected_words.append(match[0])
        else:
            corrected_words.append(word)

    corrected_question = " ".join(corrected_words)

    phrase_matches = process.extract(
        corrected_question,
        phrase_terms,
        scorer=fuzz.partial_ratio,
        limit=3,
    )

    helpful_phrases = [
        match[0]
        for match in phrase_matches
        if match[1] >= 85 and match[0] not in corrected_question.lower()
    ]

    if helpful_phrases:
        corrected_question = corrected_question + " " + " ".join(helpful_phrases)

    return corrected_question