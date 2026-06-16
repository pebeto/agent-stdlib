"""Text helpers: word frequencies and the most common words."""
from collections import Counter


def word_frequencies(text):
    """Return a Counter mapping each lowercased word to its count."""
    words = (w.strip(".,!?;:\"'()[]").lower() for w in text.split())
    return Counter(w for w in words if w)


def top_words(text, n=5):
    """Return the n most common (word, count) pairs, most frequent first."""
    return word_frequencies(text).most_common(n)
