# chatgpt generated

from typing import List, Optional
import re


def _format_author_apa(author: str) -> str:
    parts = [p for p in re.split(r"\s+", author.strip()) if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    last = parts[-1]
    initials = " ".join(f"{p[0]}." for p in parts[:-1] if p)
    return f"{last}, {initials}"


def format_apa_citation(authors: List[str], year: Optional[int], title: str, publisher: Optional[str] = None, doi: Optional[str] = None, url: Optional[str] = None) -> str:
    """Return a consistent APA-like citation string.

    Examples:
      Smith, J. (2022). Title of article. Journal Name. https://doi.org/...
    """
    authors_part = ""
    if authors:
        if len(authors) == 1:
            authors_part = _format_author_apa(authors[0])
        elif len(authors) == 2:
            authors_part = f"{_format_author_apa(authors[0])} & {_format_author_apa(authors[1])}"
        else:
            formatted = ", ".join(_format_author_apa(a) for a in authors[:-1])
            formatted += f", & {_format_author_apa(authors[-1])}"
            authors_part = formatted

    year_part = f"({year})" if year else "(n.d.)"
    title_part = title.rstrip('.') if title else ""
    publisher_part = publisher or ""
    doi_part = doi or ""
    if doi_part and not doi_part.startswith("http") and doi_part.startswith("10."):
        doi_part = f"https://doi.org/{doi_part}"
    url_part = url or ""

    parts = [p for p in [authors_part, year_part + ".", title_part + ".", publisher_part + ("." if publisher_part and not publisher_part.endswith('.') else ""), doi_part, url_part] if p]
    citation = " ".join(parts)
    return citation.strip()
