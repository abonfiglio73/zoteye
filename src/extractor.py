from normalizer import normalize_symbols
import pandas as pd
import re
import fitz  # PyMuPDF – used to read PDF files


RE_HYPHEN = re.compile(
    r"(\w)-\s*\n\s*(\w)"
)  # joins hyphenated words split across lines
RE_SPACES = re.compile(r"\s+")  # collapses multiple whitespace characters
QUOTE_PAIRS = {
    '"': '"',
    "“": "”",
    "‘": "’",
    "'": "'",
}


def strip_quotes(line: str, in_quote: bool, quote_char: str):
    result = []
    i = 0

    while i < len(line):
        ch = line[i]

        if not in_quote and ch in QUOTE_PAIRS:
            in_quote = True
            quote_char = QUOTE_PAIRS[ch]
            i += 1
            continue

        if in_quote and ch == quote_char:
            in_quote = False
            quote_char = None
            i += 1
            continue

        if not in_quote:
            result.append(ch)

        i += 1

    return "".join(result).strip(), in_quote, quote_char


def is_title(line: str) -> bool:

    line = line.strip()

    # Empty lines or extremely long lines are unlikely to be titles
    if len(line) == 0 or len(line) > 120:
        return False

    # Lines ending with sentence‑ending punctuation are probably not titles
    if re.search(r"[.,;:!?)}\]]\s*$", line):
        return False

    # Numbered titles – first word starts with a capital letter
    if re.match(r"^\d+(\.\d+)*\.?\s+[A-Z][A-Za-z0-9\- ]+$", line):
        return True

    # All‑caps titles, limited to 8 words
    if line.isupper() and len(line.split()) <= 8:
        return True

    # Title‑case titles – first letter of each word is capitalised
    words = line.split()
    if len(words) <= 8 and all(w[0].isupper() for w in words if w):
        return True

    return False


def extract_text(
    file_path: str,
    exclude_sections: bool = True,
    sections_excluded: str = "",
    exclude_quotes: bool = True,
) -> pd.DataFrame:

    skip_section = False

    # Build a list of lower‑case section names to look for when excluding sections
    exclude_list = (
        [s.strip().lower() for s in sections_excluded.split(";") if s.strip()]
        if exclude_sections and sections_excluded.strip()
        else []
    )

    pages: list[int] = []
    paragraphs: list[str] = []

    with fitz.open(file_path) as doc:

        if doc.page_count == 0:
            return None

        skip_section = False
        paragraphs = []

        for page_i, page in enumerate(doc, start=1):
            text_page = ""
            words = page.get_text("words", sort=True)
            if not words:
                continue

            # --- This snippet faces an issue related to distant words that are interpreted by PyMuPDF as new paragraphs
            line = [words[0]]
            for w in words[1:]:
                w0 = line[-1]
                # If the vertical distance between two words is small enough, they belong to the same line.
                if abs(w0[3] - w[3]) <= 3:
                    line.append(w)
                else:
                    # End of a line – concatenate its words and start a new line
                    line.sort(key=lambda w: w[0])
                    text = " ".join([w[4] for w in line])
                    text_page += text + "\n"
                    line = [w]
            # Flush the last line on this page
            text = " ".join([w[4] for w in line])

            text_page += text + "\n"

            raw_lines = text_page.splitlines()
            in_quote = False
            quote_char = None
            current_para = ""
            for line in raw_lines:
                line_stripped = line.strip()

                if not line_stripped:
                    continue

                if exclude_sections:
                    lower = line_stripped.lower()

                    if is_title(line_stripped):
                        if any(
                            re.search(rf"\b{re.escape(sec)}\b", lower)
                            for sec in exclude_list
                        ):
                            skip_section = True
                            continue
                        else:
                            skip_section = False

                    if skip_section:
                        continue

                if exclude_quotes:
                    line_stripped, in_quote, quote_char = strip_quotes(
                        line_stripped, in_quote, quote_char
                    )

                line_stripped = normalize_symbols(line_stripped)
                line_stripped = RE_HYPHEN.sub(r"\1\2", line_stripped)
                line_stripped = RE_SPACES.sub(" ", line_stripped.strip())

                if not line_stripped:
                    continue

                if re.fullmatch(r"\d{1,4}", line_stripped):
                    continue
                if re.match(r"^(page|pagina)\s+\d{1,4}$", line_stripped.lower()):
                    continue
                if re.fullmatch(r"[-–—]\s*\d{1,4}\s*[-–—]", line_stripped):
                    continue

                if current_para and is_title(line_stripped):
                    paragraphs.append(current_para.strip())
                    pages.append(page_i)
                    current_para = line_stripped
                else:
                    if current_para:
                        if not is_title(current_para):
                            current_para += " " + line_stripped
                        else:
                            paragraphs.append(current_para.strip())
                            pages.append(page_i)
                            current_para = line_stripped
                    else:
                        current_para = line_stripped

            if current_para:
                paragraphs.append(current_para.strip())
                pages.append(page_i)

    df_joined = join_paragraphs(paragraphs, pages)
    return df_joined


def join_paragraphs(paragraphs: list, pages: list) -> pd.DataFrame:

    fused_paragraphs = []
    fused_pages = []

    is_title_local = is_title

    def ends_with_strong_punct(p):
        return p.endswith((".", "!", "?"))

    def has_open_paren(p):
        return p.count("(") > p.count(")")

    prev = None

    for para, page in zip(paragraphs, pages):
        para = para.strip()

        # First paragraph – initialise accumulator
        if prev is None:
            fused_paragraphs.append(para)
            fused_pages.append(page)
            prev = para
            continue

        para_is_title = is_title_local(para)

        # If the current fragment starts with a lower‑case letter and the previous one
        # does not end with strong punctuation, merge them.
        if (
            not para_is_title
            and para
            and para[0].islower()
            and not ends_with_strong_punct(prev)
        ):
            fused_paragraphs[-1] = prev + " " + para
            prev = fused_paragraphs[-1]
            continue

        # If the previous paragraph ended with a colon (common in lists or definitions),
        # it is likely that the next fragment continues that sentence.
        if prev.endswith(":") and not para_is_title:
            fused_paragraphs[-1] = prev + " " + para
            prev = fused_paragraphs[-1]
            continue

        # Merge when an opening parenthesis in the previous paragraph is closed by the
        # current one – this handles cases like "(see Figure 2) and..."
        if has_open_paren(prev) and ")" in para:
            fused_paragraphs[-1] = prev + " " + para
            prev = fused_paragraphs[-1]
            continue

        # If the fragment starts with a parenthesis, it is usually a continuation.
        if para.startswith("("):
            fused_paragraphs[-1] = prev + " " + para
            prev = fused_paragraphs[-1]
            continue

        # Otherwise treat as a new paragraph
        fused_paragraphs.append(para)
        fused_pages.append(page)
        prev = para

    return pd.DataFrame({"page": fused_pages, "paragraph": fused_paragraphs})
