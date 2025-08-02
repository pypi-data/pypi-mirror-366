import re
import json
from collections import Counter
import string
import os

# Optional: set of basic English stopwords
STOPWORDS = {
    "the", "and", "is", "in", "it", "of", "to", "a", "that", "with", "as", "for", "on",
    "this", "an", "be", "by", "are", "from", "or", "at", "was", "but", "not", "have", "has"
}

def count_words(text, exclude_stopwords=False):
    words = re.findall(r'\b\w+\b', text.lower())
    if exclude_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    return len(words)

def count_sentences(text):
    sentences = re.split(r'[.!?]+', text.strip())
    return len([s for s in sentences if s.strip()])

def count_characters(text, include_spaces=True):
    return len(text) if include_spaces else len(text.replace(" ", ""))

def average_word_length(text, exclude_stopwords=False):
    words = re.findall(r'\b\w+\b', text)
    if exclude_stopwords:
        words = [w for w in words if w.lower() not in STOPWORDS]
    return sum(len(w) for w in words) / len(words) if words else 0

def most_frequent_words(text, n=3, exclude_stopwords=False):
    words = re.findall(r'\b\w+\b', text.lower())
    if exclude_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    return Counter(words).most_common(n)

def flesch_reading_ease(text):
    words = re.findall(r'\b\w+\b', text)
    num_words = len(words)
    num_sentences = count_sentences(text)
    num_syllables = sum(len(re.findall(r'[aeiouy]+', word.lower())) for word in words)

    if num_words == 0 or num_sentences == 0:
        return 0.0

    return round(206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (num_syllables / num_words), 2)

def get_text_statistics(text, exclude_stopwords=False):
    stats = {
        "word_count": count_words(text, exclude_stopwords),
        "sentence_count": count_sentences(text),
        "character_count_with_spaces": count_characters(text, include_spaces=True),
        "character_count_without_spaces": count_characters(text, include_spaces=False),
        "average_word_length": round(average_word_length(text, exclude_stopwords), 2),
        "most_frequent_words": most_frequent_words(text, n=5, exclude_stopwords=exclude_stopwords),
        "flesch_reading_ease": flesch_reading_ease(text)
    }
    return stats

def save_text_statistics_to_json(text, filepath="text_stats.json", exclude_stopwords=False):
    stats = get_text_statistics(text, exclude_stopwords)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)
    return filepath

def analyze_text_file(file_path, exclude_stopwords=False):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return get_text_statistics(text, exclude_stopwords=exclude_stopwords)