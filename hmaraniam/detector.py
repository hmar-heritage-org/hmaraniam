"""
Core Language Identification Detector Engine for Hmar (hmaraniam).
"Hmar a ni am?" -> "Is it Hmar?"

Pure string-in, standardized-classification-out engine.
"""

import json
import math
import os
import re
import time
import unicodedata
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# CDN Base URL for sharded dataset
DEFAULT_CDN_BASE_URL = "https://cdn.jsdelivr.net/gh/hmar-heritage-org/hmaraniam@main/hmaraniam/data/shards/"
CACHE_DIR = Path.home() / ".cache" / "hmaraniam"
CACHE_SHARDS_DIR = CACHE_DIR / "shards"
CACHE_META = CACHE_DIR / "cache_meta.json"

# Package bundled data paths
PACKAGE_DIR = Path(__file__).parent
BUNDLED_SHARDS_DIR = PACKAGE_DIR / "data" / "shards"
BUNDLED_STOPWORDS = PACKAGE_DIR / "data" / "stopwords.json"
BUNDLED_SIBLING_STOPWORDS = PACKAGE_DIR / "data" / "sibling_zo_stopwords.json"


def strip_diacritics(s: str) -> str:
    """Normalize string to plain ASCII representation (ṭ -> t, removing circumflexes)."""
    s_norm = s.replace("ṭ", "t").replace("Ṭ", "T")
    return "".join(c for c in unicodedata.normalize("NFD", s_norm) if unicodedata.category(c) != "Mn")


def load_tokens(input_data: Union[str, List[str], Tuple[str, ...], Path]) -> List[str]:
    """
    Load clean, deterministic word tokens from structured inputs (JSON array, CSV, line-delimited TXT, or Python List).
    Preserves exact token boundaries without internal guessing.
    """
    if isinstance(input_data, (list, tuple)):
        # Pre-tokenized Python list (1 word per item - evaluated "as is")
        return [str(w).lower().strip() for w in input_data if str(w).strip()]

    if isinstance(input_data, (str, Path)):
        s_input = str(input_data)

        is_path_obj = isinstance(input_data, Path)
        has_file_ext = s_input.endswith((".json", ".csv", ".txt"))
        
        is_existing_file = False
        if not is_path_obj and not has_file_ext:
            try:
                is_existing_file = Path(input_data).is_file()
            except Exception:
                is_existing_file = False

        is_file_like = is_path_obj or has_file_ext or is_existing_file

        if is_file_like:
            p = Path(input_data)
            if not p.exists():
                raise FileNotFoundError(f"Input file not found: '{s_input}'")
            if not p.is_file():
                raise ValueError(f"Path is not a regular file: '{s_input}'")

            if p.suffix == ".json":
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse JSON file '{s_input}': {e}") from e
                if not isinstance(data, list):
                    raise ValueError(f"Invalid JSON file '{s_input}': expected a JSON array/list of string tokens [\"token1\", \"token2\", ...]")
                return [str(w).lower().strip() for w in data if str(w).strip()]

            elif p.suffix == ".csv":
                import csv
                words = []
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row:
                                words.append(row[0].lower().strip())
                except Exception as e:
                    raise ValueError(f"Failed to parse CSV file '{s_input}': {e}") from e
                # Drop header row if 'token' or 'word'
                if words and words[0] in ["token", "word", "tokens", "words"]:
                    words = words[1:]
                return [w for w in words if w]

            elif p.suffix == ".txt":
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read()
                # If file contains spaces, tokenize as raw text article; otherwise 1 token per line
                if re.search(r"[ \t]", content.strip()):
                    cleaned_text = re.sub(r"https?://\S+|www\.\S+", " ", content)
                    cleaned_text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", " ", cleaned_text)
                    return [w.lower() for w in re.findall(r"\b[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF'-]+\b", cleaned_text)]
                else:
                    lines = content.splitlines()
                    return [line.lower().strip() for line in lines if line.strip()]

        # Line-delimited string (1 token per line)
        if isinstance(input_data, str) and "\n" in input_data and not re.search(r"[ \t]", input_data.strip()):
            lines = input_data.splitlines()
            return [line.lower().strip() for line in lines if line.strip()]

        # Fallback raw string processing
        if not input_data or not s_input.strip():
            return []

        cleaned_text = re.sub(r"https?://\S+|www\.\S+", " ", s_input)
        cleaned_text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", " ", cleaned_text)
        return [w.lower() for w in re.findall(r"\b[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF'-]+\b", cleaned_text)]

    raise TypeError(f"Expected input to be a text string, list of tokens, or file path (.json, .csv, .txt), got {type(input_data).__name__}")

def _resolve_wordlist(data: Optional[Union[List[str], Set[str], Tuple[str, ...], str, Path]]) -> Set[str]:
    """Resolve wordlist from Python sequences, sets, or file paths (.json, .csv, .txt)."""
    if not data:
        return set()
    if isinstance(data, (str, Path)):
        s_data = str(data)
        try:
            p = Path(data)
            if p.exists() and p.is_file():
                return {w.lower() for w in load_tokens(p)}
        except Exception:
            pass
        if isinstance(data, Path) or s_data.endswith((".json", ".csv", ".txt")):
            raise FileNotFoundError(f"Custom wordlist file not found: '{s_data}'")
    if isinstance(data, (list, tuple, set)):
        return {str(w).lower().strip() for w in data if str(w).strip()}
    if isinstance(data, str):
        return {data.lower().strip()}
    return set()


class Detector:
    """
    Hmar Language Identification Detector Engine.
    
    Provides dual-lens language detection for Hmar text strings,
    distinguishing Hmar from English and sibling Zo (Kuki-Chin) languages.
    """


    def __init__(
        self,
        mode: str = "basic",  # "basic" (core set 001) or "high" (all shards set_*.json)
        cdn_base_url: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours in seconds
        force_remote: bool = False,
        offline_only: bool = True,  # Default offline-first (zero network latency)
        custom_unigrams: Optional[Union[List[str], Set[str]]] = None,
        extra_unigrams: Optional[Union[List[str], Set[str]]] = None,
        custom_stopwords: Optional[Union[List[str], Set[str]]] = None,
        disable_default_stopwords: bool = False,
    ):
        self.mode = mode.lower()
        if self.mode not in ["basic", "high"]:
            raise ValueError(
                f"Invalid detection mode '{mode}'. Supported modes are 'basic' (default) and 'high' (extended dataset)."
            )

        self.cdn_base_url = (cdn_base_url or DEFAULT_CDN_BASE_URL).rstrip("/") + "/"
        self.cache_ttl = cache_ttl
        self.offline_only = offline_only

        self.exact_hmar_vocab: Set[str] = set()
        self.normalized_hmar_vocab: Set[str] = set()
        self.english_stopwords: Set[str] = set()
        self.sibling_zo_stopwords: Set[str] = set()
        self.sibling_zo_stopwords_by_lang: Dict[str, Set[str]] = {}

        # 1. Load Stopwords
        if not disable_default_stopwords:
            self._load_stopwords()

        if custom_stopwords:
            custom_stops = _resolve_wordlist(custom_stopwords)
            if disable_default_stopwords:
                self.english_stopwords = custom_stops
            else:
                self.english_stopwords.update(custom_stops)

        # 2. Load Unigrams
        if custom_unigrams:
            exact_words = _resolve_wordlist(custom_unigrams)
        else:
            exact_words = self._load_unigram_shards(force_remote=force_remote)

        if extra_unigrams:
            extra_words = _resolve_wordlist(extra_unigrams)
            exact_words.update(extra_words)

        self.exact_hmar_vocab = exact_words
        self.normalized_hmar_vocab = {strip_diacritics(w) for w in exact_words}

    def _load_stopwords(self) -> None:
        """Load English and sibling Zo stopwords from bundled data."""
        if BUNDLED_STOPWORDS.exists():
            with open(BUNDLED_STOPWORDS, "r", encoding="utf-8") as f:
                self.english_stopwords = {w.lower() for w in json.load(f)}
        else:
            self.english_stopwords = {
                "the", "and", "that", "for", "was", "with", "they", "have", 
                "from", "had", "by", "but", "what", "there", "were", "your"
            }

        if BUNDLED_SIBLING_STOPWORDS.exists():
            with open(BUNDLED_SIBLING_STOPWORDS, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                if isinstance(raw_data, dict):
                    self.sibling_zo_stopwords_by_lang = {
                        lang: {strip_diacritics(w.lower()) for w in words}
                        for lang, words in raw_data.items()
                    }
                    self.sibling_zo_stopwords = set().union(*self.sibling_zo_stopwords_by_lang.values())
                elif isinstance(raw_data, list):
                    all_stops = {strip_diacritics(w.lower()) for w in raw_data}
                    self.sibling_zo_stopwords = all_stops
                    self.sibling_zo_stopwords_by_lang = {"sibling": all_stops}
        else:
            self.sibling_zo_stopwords = set()
            self.sibling_zo_stopwords_by_lang = {}

    def _get_shard_filenames(self) -> List[str]:
        """Determine which shard filenames to load based on mode."""
        if self.mode == "basic":
            return ["unigrams_set_001.json"]

        shard_names = set()
        if BUNDLED_SHARDS_DIR.exists():
            for p in BUNDLED_SHARDS_DIR.glob("unigrams_set_*.json"):
                shard_names.add(p.name)

        if CACHE_SHARDS_DIR.exists():
            for p in CACHE_SHARDS_DIR.glob("unigrams_set_*.json"):
                shard_names.add(p.name)

        if not shard_names:
            shard_names = {"unigrams_set_001.json"}

        return sorted(list(shard_names))

    def _load_unigram_shards(self, force_remote: bool = False) -> Set[str]:
        """Load Hmar unigrams vocabulary from shards based on current mode."""
        shard_filenames = self._get_shard_filenames()
        accumulated_words = set()

        for shard_name in shard_filenames:
            words = self._load_single_shard(shard_name, force_remote=force_remote)
            if words:
                accumulated_words.update(words)

        if accumulated_words:
            return {w.lower() for w in accumulated_words}
        else:
            raise RuntimeError("Failed to load any Hmar unigram shards.")

    def _load_single_shard(self, shard_name: str, force_remote: bool = False) -> Optional[List[str]]:
        """Load a single unigram shard using CDN, cache, or bundled fallback."""
        cache_path = CACHE_SHARDS_DIR / shard_name
        bundled_path = BUNDLED_SHARDS_DIR / shard_name
        loaded_data: Optional[List[str]] = None

        if not self.offline_only:
            if force_remote or self._should_fetch_remote(cache_path):
                loaded_data = self._fetch_shard_from_cdn(shard_name, cache_path)

        if loaded_data is None and cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
            except Exception:
                loaded_data = None

        if loaded_data is None and bundled_path.exists():
            try:
                with open(bundled_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
            except Exception:
                loaded_data = None

        return loaded_data

    def _should_fetch_remote(self, cache_path: Path) -> bool:
        """Check if local cache shard is missing or older than cache_ttl."""
        if not cache_path.exists() or not CACHE_META.exists():
            return True
        try:
            with open(CACHE_META, "r", encoding="utf-8") as f:
                meta = json.load(f)
            fetch_time = meta.get("fetched_at", 0)
            return (time.time() - fetch_time) > self.cache_ttl
        except Exception:
            return True

    def _fetch_shard_from_cdn(self, shard_name: str, cache_path: Path) -> Optional[List[str]]:
        """Fetch a specific shard file from CDN and cache it locally."""
        try:
            cdn_url = self.cdn_base_url + shard_name
            req = urllib.request.Request(
                cdn_url,
                headers={"User-Agent": "hmaraniam-detector/0.1.0"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    raw_content = resp.read().decode("utf-8")
                    data = json.loads(raw_content)

                    CACHE_SHARDS_DIR.mkdir(parents=True, exist_ok=True)
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(raw_content)

                    with open(CACHE_META, "w", encoding="utf-8") as f:
                        json.dump({"fetched_at": time.time(), "source": cdn_url}, f)

                    return data
        except Exception:
            pass
        return None

    def detect(self, text_or_tokens: Union[str, List[str], Path]) -> Dict[str, Any]:
        """
        Pure token, file, or string language classification with standardized schema output.

        :param text_or_tokens: Pre-tokenized list of tokens, path to .json/.csv/.txt token file, or text string.
        :return: Standardized result dict.
        """
        words = load_tokens(text_or_tokens)
        total_words = len(words)
        if total_words == 0:
            return self._empty_result()

        # 1. Match Counts
        casual_matches = sum(1 for w in words if strip_diacritics(w) in self.normalized_hmar_vocab)
        formal_matches = sum(1 for w in words if w in self.exact_hmar_vocab)
        eng_stop_matches = sum(1 for w in words if w in self.english_stopwords)
        sibling_zo_matches = sum(1 for w in words if strip_diacritics(w) in self.sibling_zo_stopwords)

        # Count sibling stopword hits per specific language
        sibling_lang_counts: Dict[str, int] = {}
        for lang_code, stop_set in self.sibling_zo_stopwords_by_lang.items():
            cnt = sum(1 for w in words if strip_diacritics(w) in stop_set)
            if cnt > 0:
                sibling_lang_counts[lang_code] = cnt

        best_sibling_lang = None
        if sibling_lang_counts:
            best_sibling_lang = max(sibling_lang_counts, key=sibling_lang_counts.get)

        # Diacritic breakdown
        hmar_diacritic_words_count = 0
        non_hmar_diacritic_words_count = 0

        for w in words:
            has_diacritic = (strip_diacritics(w) != w) or any(c in w for c in "âêîôûṭÂÊÎÔÛṬ")
            if has_diacritic:
                if strip_diacritics(w) in self.normalized_hmar_vocab:
                    hmar_diacritic_words_count += 1
                else:
                    non_hmar_diacritic_words_count += 1

        total_diacritic_words_count = hmar_diacritic_words_count + non_hmar_diacritic_words_count
        non_hmar_words_count = total_words - casual_matches
        unknown_words_count = non_hmar_words_count
        unknown_words_ratio = non_hmar_words_count / total_words

        # 2. Ratios
        casual_hmar_ratio = casual_matches / total_words
        formal_hmar_ratio = formal_matches / total_words
        eng_stop_ratio = eng_stop_matches / total_words
        sibling_zo_ratio = sibling_zo_matches / total_words

        # 3. Classification Logic
        sibling_heuristic = False
        if eng_stop_ratio >= 0.025 and casual_hmar_ratio < 0.40:
            language = "english"
        elif casual_hmar_ratio >= 0.82 and unknown_words_ratio <= 0.18:
            language = "hmar"
        elif casual_hmar_ratio >= 0.70 and eng_stop_ratio < 0.01 and non_hmar_diacritic_words_count == 0:
            language = "hmar"
        elif eng_stop_ratio >= 0.02:
            language = "english"
        elif best_sibling_lang:
            language = best_sibling_lang  # "mizo", "paite", "thadou", "gangte", "zou", "vaiphei"
            sibling_heuristic = True
        else:
            language = "other"  # Unclassified non-Hmar text

        # 4. Continuous Mathematical Confidence Score calculation [0.0000 - 1.0000]
        # Bayesian Length Weighting: W_len = 1 - exp(-N / 6)
        len_weight = 1.0 - math.exp(-total_words / 6.0)

        # 4a. Permanent Hmar Confidence (Answers: "How confident are we that this text is Hmar?")
        # Penalizes high unknown_words_ratio and English stopwords
        hmar_signal = max(0.0, casual_hmar_ratio - (unknown_words_ratio * 1.5) - (eng_stop_ratio * 3.0))
        hmar_conf_raw = min(1.0, hmar_signal / 0.75) * len_weight
        hmar_confidence = round(min(1.0, max(0.0, hmar_conf_raw)), 4)

        # 4b. Detected Language Confidence (Confidence in the overall classification choice)
        if language == "hmar":
            detected_language_confidence = hmar_confidence
        elif language == "english":
            eng_signal = max(0.0, eng_stop_ratio - (casual_hmar_ratio / 5.0))
            eng_conf_raw = min(1.0, eng_signal / 0.04) * len_weight
            detected_language_confidence = round(min(1.0, max(0.0, eng_conf_raw)), 4)
        elif sibling_heuristic or language == "other":
            if sibling_zo_matches > 0 or sibling_zo_ratio >= 0.01:
                # Actively verified non-Hmar Zo (Kuki-Chin) sibling language match!
                sibling_signal = max(0.0, (sibling_zo_ratio * 4.0) + (unknown_words_ratio * 0.5))
                other_conf_raw = min(1.0, sibling_signal) * len_weight
                detected_language_confidence = round(min(1.0, max(0.75, other_conf_raw)), 4)
            else:
                # Out-of-scope external language or unclassified noise
                other_signal = max(0.0, unknown_words_ratio - eng_stop_ratio)
                other_conf_raw = min(0.50, other_signal * 0.5) * len_weight
                detected_language_confidence = round(min(0.50, max(0.0, other_conf_raw)), 4)
        else:
            detected_language_confidence = 0.0

        return {
            "language": language,
            "hmar_confidence": hmar_confidence,
            "detected_language_confidence": detected_language_confidence,
            "sibling_heuristic": sibling_heuristic,
            "mode": self.mode,
            "scores": {
                "casual_hmar_ratio": round(casual_hmar_ratio, 4),
                "formal_hmar_ratio": round(formal_hmar_ratio, 4),
                "english_stopword_ratio": round(eng_stop_ratio, 4),
                "sibling_zo_stopword_ratio": round(sibling_zo_ratio, 4),
                "unknown_words_ratio": round(unknown_words_ratio, 4),
                "total_words": total_words,
                "hmar_words_count": casual_matches,
                "non_hmar_words_count": non_hmar_words_count,
                "unknown_words_count": unknown_words_count,
                "english_stopwords_count": eng_stop_matches,
                "sibling_zo_stopwords_count": sibling_zo_matches,
                "sibling_lang_counts": sibling_lang_counts,
                "hmar_diacritic_words_count": hmar_diacritic_words_count,
                "non_hmar_diacritic_words_count": non_hmar_diacritic_words_count,
                "total_diacritic_words_count": total_diacritic_words_count,
            },
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return standardized result structure for empty input."""
        return {
            "language": "unknown",
            "hmar_confidence": 0.0,
            "detected_language_confidence": 0.0,
            "sibling_heuristic": False,
            "mode": self.mode,
            "scores": {
                "casual_hmar_ratio": 0.0,
                "formal_hmar_ratio": 0.0,
                "english_stopword_ratio": 0.0,
                "sibling_zo_stopword_ratio": 0.0,
                "unknown_words_ratio": 0.0,
                "total_words": 0,
                "hmar_words_count": 0,
                "non_hmar_words_count": 0,
                "unknown_words_count": 0,
                "english_stopwords_count": 0,
                "sibling_zo_stopwords_count": 0,
                "hmar_diacritic_words_count": 0,
                "non_hmar_diacritic_words_count": 0,
                "total_diacritic_words_count": 0,
            },
        }

    def detect_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into paragraphs and classify each paragraph independently.

        :param text: Input multi-paragraph text string.
        :return: List of dicts per non-empty paragraph.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected text input to be a string, got {type(text).__name__}")

        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        results = []
        for index, paragraph in enumerate(paragraphs):
            res = self.detect(paragraph)
            res["paragraph_index"] = index
            res["text_snippet"] = paragraph[:80] + ("..." if len(paragraph) > 80 else "")
            results.append(res)
        return results


# Global singleton instance for quick top-level imports
_default_detector: Optional[Detector] = None


def get_default_detector() -> Detector:
    """Retrieve or initialize global default Detector instance."""
    global _default_detector
    if _default_detector is None:
        _default_detector = Detector(mode="basic")
    return _default_detector


def detect(
    text_or_tokens: Union[str, List[str]],
    mode: str = "basic"
) -> Dict[str, Any]:
    """
    Top-level helper function to detect language of a text string OR pre-tokenized list of word tokens.

    >>> import hmaraniam
    >>> res = hmaraniam.detect(["khawvel", "fe", "dan", "phung"])
    >>> res["language"]
    'hmar'
    """
    if mode == "basic":
        return get_default_detector().detect(text_or_tokens)
    detector = Detector(mode=mode)
    return detector.detect(text_or_tokens)
