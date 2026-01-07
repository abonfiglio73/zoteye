import unicodedata
import os
import re

EXPLICIT_SUPERSUB_MAP = {
    # superscript/subscript letters
    "ₐ": "a",
    "ₑ": "e",
    "ₒ": "o",
    "ₓ": "x",
    "ₙ": "n",
    "ₜ": "t",
    "ₖ": "k",
    "ₗ": "l",
    "ᵢ": "i",
    "ⱼ": "j",
    "ᵣ": "r",
    "ᵤ": "u",
    "ᵥ": "v",
    # superscript/subscript numbers
    "⁰": "0",
    "¹": "1",
    "²": "2",
    "³": "3",
    "⁴": "4",
    "⁵": "5",
    "⁶": "6",
    "⁷": "7",
    "⁸": "8",
    "⁹": "9",
    "₀": "0",
    "₁": "1",
    "₂": "2",
    "₃": "3",
    "₄": "4",
    "₅": "5",
    "₆": "6",
    "₇": "7",
    "₈": "8",
    "₉": "9",
    # Greek letters (standard)
    "α": "alpha",
    "β": "beta",
    "γ": "gamma",
    "δ": "delta",
    "ε": "epsilon",
    "ζ": "zeta",
    "η": "eta",
    "θ": "theta",
    "κ": "kappa",
    "λ": "lambda",
    "μ": "mu",
    "ν": "nu",
    "π": "pi",
    "ρ": "rho",
    "σ": "sigma",
    "τ": "tau",
    "φ": "phi",
    "χ": "chi",
    "ψ": "psi",
    "ω": "omega",
    # Greek superscript/subscript
    "ᵅ": "alpha",
    "ᵦ": "beta",
    "ᵧ": "gamma",
    "ᵨ": "rho",
    "ᵩ": "phi",
    "ᵪ": "chi",
}


def normalize_supersubs(text: str) -> str:
    out = []
    for ch in text:
        if ch in EXPLICIT_SUPERSUB_MAP:
            out.append(EXPLICIT_SUPERSUB_MAP[ch])
            continue
        name = unicodedata.name(ch, "")
        if "SUBSCRIPT" in name or "SUPERSCRIPT" in name:
            base = unicodedata.normalize("NFKD", ch)
            if base and base.isalnum():
                out.append(base)
        else:
            out.append(ch)

    return "".join(out)


def remove_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )


def normalize_text(text: str):
    return normalize_symbols(re.sub(r"[^\w\s]", "", text)).lower()


def normalize_symbols(text: str) -> str:
    text = normalize_supersubs(text)
    text = remove_accents(text)
    return text


def normalize_path(path: str) -> str:
    path = os.path.normpath(path)
    if os.name == "nt" and len(path) > 1 and path[1] == ":":
        path = path[0].upper() + path[1:]
    return path


def normalize_sections(sections_str: str) -> str:
    if not sections_str:
        return ""
    parts = [s.strip().lower() for s in sections_str.split(";") if s.strip()]
    return ";".join(sorted(set(parts)))
