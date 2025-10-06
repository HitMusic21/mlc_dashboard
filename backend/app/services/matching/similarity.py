"""Similarity algorithms for catalog matching.

Implements various string and numeric similarity measures:
- Jaro-Winkler similarity
- Levenshtein distance/ratio
- Cosine similarity with TF-IDF
- Duration similarity (bucket-based)
"""

import re
import string
from typing import Optional

import jellyfish
from Levenshtein import ratio as levenshtein_ratio_impl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_text(text: str) -> str:
    """Normalize text for comparison.

    Args:
        text: Input text

    Returns:
        Normalized text (lowercase, no punctuation, stripped)
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Remove extra whitespace
    text = " ".join(text.split())

    return text.strip()


def jaro_winkler_similarity(s1: str, s2: str) -> float:
    """Calculate Jaro-Winkler similarity between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not s1 or not s2:
        return 0.0

    # Normalize strings
    s1_norm = normalize_text(s1)
    s2_norm = normalize_text(s2)

    if not s1_norm or not s2_norm:
        return 0.0

    # Calculate Jaro-Winkler similarity
    score = jellyfish.jaro_winkler_similarity(s1_norm, s2_norm)

    return round(score, 4)


def levenshtein_ratio(s1: str, s2: str) -> float:
    """Calculate Levenshtein ratio (similarity) between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not s1 or not s2:
        return 0.0

    # Normalize strings
    s1_norm = normalize_text(s1)
    s2_norm = normalize_text(s2)

    if not s1_norm or not s2_norm:
        return 0.0

    # Calculate Levenshtein ratio
    score = levenshtein_ratio_impl(s1_norm, s2_norm)

    return round(score, 4)


def cosine_similarity_tfidf(s1: str, s2: str) -> float:
    """Calculate cosine similarity using TF-IDF vectors.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not s1 or not s2:
        return 0.0

    # Normalize strings
    s1_norm = normalize_text(s1)
    s2_norm = normalize_text(s2)

    if not s1_norm or not s2_norm:
        return 0.0

    try:
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",  # Character n-grams including word boundaries
            ngram_range=(2, 3),  # Bigrams and trigrams
            lowercase=True,
        )

        # Fit and transform both strings
        tfidf_matrix = vectorizer.fit_transform([s1_norm, s2_norm])

        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = similarity_matrix[0][0]

        return round(float(score), 4)

    except Exception:
        # Fallback to 0.0 if TF-IDF fails (e.g., very short strings)
        return 0.0


def duration_similarity(d1: Optional[int], d2: Optional[int]) -> float:
    """Calculate duration similarity using bucket-based scoring.

    Args:
        d1: First duration in seconds (can be None)
        d2: Second duration in seconds (can be None)

    Returns:
        Similarity score between 0.0 and 1.0
    """
    # If either duration is missing, return neutral score
    if d1 is None or d2 is None:
        return 0.5

    # Calculate absolute difference
    diff = abs(d1 - d2)

    # Bucket-based scoring
    if diff == 0:
        return 1.0  # Exact match
    elif diff <= 5:
        return 0.95  # Within 5 seconds
    elif diff <= 10:
        return 0.85  # Within 10 seconds
    elif diff <= 30:
        return 0.70  # Within 30 seconds
    elif diff <= 60:
        return 0.50  # Within 1 minute
    elif diff <= 120:
        return 0.30  # Within 2 minutes
    else:
        return 0.0  # More than 2 minutes difference


def combined_string_similarity(s1: str, s2: str) -> float:
    """Calculate combined string similarity using multiple algorithms.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Weighted average similarity score between 0.0 and 1.0
    """
    if not s1 or not s2:
        return 0.0

    # Calculate individual scores
    jw_score = jaro_winkler_similarity(s1, s2)
    lev_score = levenshtein_ratio(s1, s2)
    cos_score = cosine_similarity_tfidf(s1, s2)

    # Weighted average (Jaro-Winkler gets more weight for names)
    weighted_score = (jw_score * 0.5) + (lev_score * 0.3) + (cos_score * 0.2)

    return round(weighted_score, 4)
