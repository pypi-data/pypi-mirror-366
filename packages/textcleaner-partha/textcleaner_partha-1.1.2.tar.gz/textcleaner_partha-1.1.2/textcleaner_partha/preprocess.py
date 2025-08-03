# textcleaner_partha/preprocess.py

import os
import re
import json
import spacy
import contractions
import docx
import pypdf
import importlib.resources as pkg_resources
import warnings
from autocorrect import Speller
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning

# Suppress spurious BeautifulSoup warnings for non-HTML text
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Lazy initialization
_nlp = None
_spell = None
_abbrev_map = None

ABBREV_DIR = pkg_resources.files("textcleaner_partha").joinpath("abbreviation_mappings")

def set_abbreviation_dir(path: str):
    """
    Set a custom directory for abbreviation mappings.
    Useful for testing or dynamically loading custom mappings.
    """
    global ABBREV_DIR, _abbrev_map
    ABBREV_DIR = path
    _abbrev_map = None  # Reset cache so it reloads from the new directory

def reset_abbreviation_dir():
    """
    Reset abbreviation mapping directory back to default.
    """
    import importlib.resources as pkg_resources
    global ABBREV_DIR, _abbrev_map
    ABBREV_DIR = pkg_resources.files("textcleaner_partha").joinpath("abbreviation_mappings")
    _abbrev_map = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise OSError("Model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    return _nlp

def get_spell():
    global _spell
    if _spell is None:
        _spell = Speller()
    return _spell

def load_abbreviation_mappings():
    global _abbrev_map

    if _abbrev_map is None:
        _abbrev_map = {}

    if os.path.exists(ABBREV_DIR):
        for fname in os.listdir(ABBREV_DIR):
            if fname.endswith(".json"):
                path = os.path.join(ABBREV_DIR, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        _abbrev_map.update({k.lower(): v for k, v in data.items()})
                except Exception as e:
                        print(f"[textcleaner warning] Failed to load {fname}: {e}")

    return _abbrev_map

def expand_abbreviations(text):
    abbr_map = load_abbreviation_mappings()

    def replace_abbr(match):
        word = match.group(0)
        return abbr_map.get(word.lower(), word)

    return re.sub(r'\b\w+\b', replace_abbr, text)

# def remove_html_tags(text):
#     soup = BeautifulSoup(text, "html.parser")
#     return soup.get_text()
def remove_html_tags(text):
    """
    Removes HTML tags from the input text, even if it's malformed,
    and normalizes whitespace for deterministic output.
    """
    # Use BeautifulSoup to parse HTML safely
    soup = BeautifulSoup(text, "html.parser")

    # Extract text with consistent separators
    clean = soup.get_text(separator=" ")

    # Normalize multiple spaces/newlines into single space
    clean = ' '.join(clean.split())

    return clean

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
        "\U0001FA70-\U0001FAFF"  # extended pictographs
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def remove_extra_whitespace(text):
    return re.sub(r'[ \t\n\r\f\v]+', ' ', text).strip()

def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

def correct_spellings(text):
    spell = get_spell()
    return ' '.join([spell(w) for w in text.split()])

def expand_contractions(text):
    return contractions.fix(text)

def preprocess(
    text,
    lowercase=True,
    remove_stopwords=True,
    remove_html=True,
    remove_emoji=True,
    remove_whitespace=True,
    remove_punct=False,
    expand_contraction=True,
    expand_abbrev=True,
    correct_spelling=True,
    lemmatise=True,
    verbose=False,  # ✅ Reintroduced
):
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    # === Step 1: Basic text cleanup ===
    if lowercase:
        text = text.lower()
    if remove_html:
        text = remove_html_tags(text)
    if remove_emoji:
        text = remove_emojis(text)
    if expand_abbrev:
        text = expand_abbreviations(text)
    if expand_contraction:
        text = expand_contractions(text)
    if correct_spelling:
        text = ' '.join([get_spell()(w) for w in text.split()])
    if remove_punct:
        text = remove_punctuation(text)
    if remove_whitespace:
        text = remove_extra_whitespace(text)

    # === Step 2: NLP tokenization ===
    doc = get_nlp()(text)
    preserve_pron_aux = expand_contraction or expand_abbrev or correct_spelling

    tokens = []
    for token in doc:
        if token.is_space:
            continue
        if remove_stopwords:
            if token.is_alpha and not token.is_stop:
                if token.pos_ in {"NOUN", "VERB", "ADJ", "ADV", "INTJ"} or \
                   (preserve_pron_aux and token.pos_ in {"PRON", "AUX"}):
                    tokens.append(token.lemma_ if lemmatise else token.text)
        else:
            if token.is_alpha:
                tokens.append(token.lemma_ if lemmatise else token.text)

    # === Step 3: Deduplicate and enforce casing ===
    tokens = list(dict.fromkeys(tokens))
    tokens = [t for t in tokens if len(t) > 1 or t in {"i", "a"}]

    final_output = ' '.join(tokens)
    if lowercase:
        final_output = final_output.lower()
    return final_output

def get_tokens(
    text,
    lowercase=True,
    remove_stopwords=True,
    remove_html=True,
    remove_emoji=True,
    remove_whitespace=True,
    remove_punct=True,
    expand_contraction=True,
    expand_abbrev=True,
    correct_spelling=False,
    lemmatise=True,
    verbose=False,  # ✅ Reintroduced
):
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    # === Basic preprocessing without joining ===
    if lowercase:
        text = text.lower()

    if remove_html:
        text = remove_html_tags(text)

    if remove_emoji:
        text = remove_emojis(text)

    if expand_abbrev:
        text = expand_abbreviations(text)

    if expand_contraction:
        text = expand_contractions(text)

    if correct_spelling:
        text = correct_spellings(text)

    if remove_punct:
        text = remove_punctuation(text)

    if remove_whitespace:
        text = remove_extra_whitespace(text)

    # === Tokenize directly ===
    doc = get_nlp()(text)
    tokens = []
    for token in doc:
        if token.is_space:
            continue
        if remove_stopwords:
            if token.is_alpha and not token.is_stop:
                tokens.append(token.lemma_ if lemmatise else token.text)
        else:
            if token.is_alpha:
                tokens.append(token.lemma_ if lemmatise else token.text)

    return tokens  # ✅ preserves order, now supports stopword removal

def load_text_from_file(file_path, pdf_chunk_by_page=False):
    """
    Load raw text from TXT, DOCX, or PDF file.
    Returns:
        - TXT/DOCX: list of lines.
        - PDF: list of lines (flat) or list of dicts with page_number and content if pdf_chunk_by_page=True.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    elif ext == ".docx":
        doc = docx.Document(file_path)
        return [para.text.strip() for para in doc.paragraphs if para.text.strip()]

    elif ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            if pdf_chunk_by_page:
                pages = []
                for i, page in enumerate(reader.pages, start=1):
                    text = page.extract_text()
                    if text:
                        lines = [line.strip() for line in text.split("\n") if line.strip()]
                        pages.append({"page_number": i, "content": lines})
                return pages
            else:
                all_lines = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_lines.extend([line.strip() for line in text.split("\n") if line.strip()])
                return all_lines

    else:
        raise ValueError(f"Unsupported file type: {ext}. Only TXT, DOCX, and PDF are supported.")


def preprocess_file(
    file_path,
    lowercase=True,
    remove_stopwords=True,
    remove_html=True,
    remove_emoji=True,
    remove_whitespace=True,
    remove_punct=False,
    expand_contraction=True,
    expand_abbrev=True,
    correct_spelling=True,
    lemmatise=True,
    verbose=False,
    pdf_chunk_by_page=False,
    merge_pdf_pages=False,
):
    """
    Preprocess a TXT, DOCX, or PDF file and return preprocessed text.
    Options:
        - pdf_chunk_by_page: Returns list of dicts (page_number + content).
        - merge_pdf_pages: Combines all pages into a single list of preprocessed lines.
    """
    raw_texts = load_text_from_file(file_path, pdf_chunk_by_page=pdf_chunk_by_page)

    if pdf_chunk_by_page and isinstance(raw_texts, list) and isinstance(raw_texts[0], dict):
        if merge_pdf_pages:
            # Merge all pages into one list
            merged_lines = [line for page in raw_texts for line in page["content"]]
            processed = [
                preprocess(
                    text=line,
                    lowercase=lowercase,
                    remove_stopwords=remove_stopwords,
                    remove_html=remove_html,
                    remove_emoji=remove_emoji,
                    remove_whitespace=remove_whitespace,
                    remove_punct=remove_punct,
                    expand_contraction=expand_contraction,
                    expand_abbrev=expand_abbrev,
                    correct_spelling=correct_spelling,
                    lemmatise=lemmatise,
                    verbose=verbose,
                )
                for line in merged_lines
            ]
            # Filter out empty strings
            return [line for line in processed if line and line.strip()]
        else:
            # Page-wise preprocessing
            return [
                {
                    "page_number": page["page_number"],
                    "content": [
                        line for line in [
                            preprocess(
                                text=line,
                                lowercase=lowercase,
                                remove_stopwords=remove_stopwords,
                                remove_html=remove_html,
                                remove_emoji=remove_emoji,
                                remove_whitespace=remove_whitespace,
                                remove_punct=remove_punct,
                                expand_contraction=expand_contraction,
                                expand_abbrev=expand_abbrev,
                                correct_spelling=correct_spelling,
                                lemmatise=lemmatise,
                                verbose=verbose,
                            )
                            for line in page["content"]
                        ] if line and line.strip()
                    ],
                }
                for page in raw_texts
            ]
    else:
        # TXT, DOCX, or flat PDF
        processed = [
            preprocess(
                text=line,
                lowercase=lowercase,
                remove_stopwords=remove_stopwords,
                remove_html=remove_html,
                remove_emoji=remove_emoji,
                remove_whitespace=remove_whitespace,
                remove_punct=remove_punct,
                expand_contraction=expand_contraction,
                expand_abbrev=expand_abbrev,
                correct_spelling=correct_spelling,
                lemmatise=lemmatise,
                verbose=verbose,
            )
            for line in raw_texts
        ]
        # Filter out empty strings
        return [line for line in processed if line and line.strip()]

def get_tokens_from_file(
    file_path,
    lowercase=True,
    remove_stopwords=True,
    remove_html=True,
    remove_emoji=True,
    remove_whitespace=True,
    remove_punct=False,
    expand_contraction=True,
    expand_abbrev=True,
    correct_spelling=True,
    lemmatise=True,
    verbose=False,
    pdf_chunk_by_page=False,
    merge_pdf_pages=False,
):
    """
    Get tokens from a TXT, DOCX, or PDF file using preprocessing pipeline.
    Options:
        - pdf_chunk_by_page: Returns tokens per page.
        - merge_pdf_pages: Combines all pages into a single token list.
    """
    raw_texts = load_text_from_file(file_path, pdf_chunk_by_page=pdf_chunk_by_page)

    if pdf_chunk_by_page and isinstance(raw_texts, list) and isinstance(raw_texts[0], dict):
        if merge_pdf_pages:
            merged_lines = [line for page in raw_texts for line in page["content"]]
            return [
                get_tokens(
                    text=line,
                    lowercase=lowercase,
                    remove_stopwords=remove_stopwords,
                    remove_html=remove_html,
                    remove_emoji=remove_emoji,
                    remove_whitespace=remove_whitespace,
                    remove_punct=remove_punct,
                    expand_contraction=expand_contraction,
                    expand_abbrev=expand_abbrev,
                    correct_spelling=correct_spelling,
                    lemmatise=lemmatise,
                    verbose=verbose,
                )
                for line in merged_lines
            ]
        else:
            return [
                {
                    "page_number": page["page_number"],
                    "content": [
                        get_tokens(
                            text=line,
                            lowercase=lowercase,
                            remove_stopwords=remove_stopwords,
                            remove_html=remove_html,
                            remove_emoji=remove_emoji,
                            remove_whitespace=remove_whitespace,
                            remove_punct=remove_punct,
                            expand_contraction=expand_contraction,
                            expand_abbrev=expand_abbrev,
                            correct_spelling=correct_spelling,
                            lemmatise=lemmatise,
                            verbose=verbose,
                        )
                        for line in page["content"]
                    ],
                }
                for page in raw_texts
            ]
    else:
        return [
            get_tokens(
                text=line,
                lowercase=lowercase,
                remove_stopwords=remove_stopwords,
                remove_html=remove_html,
                remove_emoji=remove_emoji,
                remove_whitespace=remove_whitespace,
                remove_punct=remove_punct,
                expand_contraction=expand_contraction,
                expand_abbrev=expand_abbrev,
                correct_spelling=correct_spelling,
                lemmatise=lemmatise,
                verbose=verbose,
            )
            for line in raw_texts
        ]