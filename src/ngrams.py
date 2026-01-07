from collections import defaultdict
from normalizer import normalize_text


def get_ngrams(paragraph: str, n: int) -> list[tuple[str, int]]:

    words = normalize_text(paragraph).split()

    if len(words) < n:
        return []

    ngrams: list[tuple[str, int]] = []
    for i in range(len(words) - n + 1):
        ngram = " ".join(words[i : i + n])
        ngrams.append((ngram, i))
    return ngrams


def build_ngram_index(pdf_df, n: int) -> dict[str, list[tuple[int, int]]]:

    index = defaultdict(list)
    for _, row in pdf_df.iterrows():
        page = row["page"]
        paragraph = row["paragraph"]
        for ngram, pos in get_ngrams(paragraph, n):
            index[ngram.lower()].append((page, pos + 1))
    return index


def calculate_similarity(
    target_ngram_index: dict, pdf_ngram_index: dict
) -> tuple[dict, float, float, float]:

    target_ngrams = set(target_ngram_index.keys())

    all_pdf_ngrams = set()
    per_pdf_scores = {}

    for pdf_path, pdf_dict in pdf_ngram_index.items():
        pdf_ngrams = set(pdf_dict.keys())
        common = target_ngrams & pdf_ngrams
        perc = len(common) / len(target_ngrams) * 100 if target_ngrams else 0.0
        per_pdf_scores[pdf_path] = perc
        all_pdf_ngrams |= pdf_ngrams

    common_total = target_ngrams & all_pdf_ngrams
    overall_similarity = (
        len(common_total) / len(target_ngrams) * 100 if target_ngrams else 0.0
    )

    max_similarity = max(per_pdf_scores.values(), default=0.0)

    avg_similarity = (
        sum(per_pdf_scores.values()) / len(per_pdf_scores) if per_pdf_scores else 0.0
    )

    return per_pdf_scores, overall_similarity, max_similarity, avg_similarity
