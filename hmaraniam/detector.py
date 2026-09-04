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


def strip_diacritics(s: str) -> str:
    """Normalize string to plain ASCII representation (ṭ -> t, removing circumflexes)."""
    s_norm = s.replace("ṭ", "t").replace("Ṭ", "T")
    return "".join(c for c in unicodedata.normalize("NFD", s_norm) if unicodedata.category(c) != "Mn")


class Detector:
    """
    Hmar Language Identification Detector Engine.
    
    Provides high-precision, dual-lens language detection for clean Hmar text strings,
    distinguishing Hmar from English and other Kuki-Chin / Zo languages.
    """

    def __init__(
        self,
        mode: str = "basic",  # "basic" (core set 001) or "high" (all shards set_*.json)
        cdn_base_url: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours in seconds
        force_remote: bool = False,
        offline_only: bool = False,
        custom_unigrams: Optional[Union[List[str], Set[str]]] = None,
        extra_unigrams: Optional[Union[List[str], Set[str]]] = None,
        custom_stopwords: Optional[Union[List[str], Set[str]]] = None,
        disable_default_stopwords: bool = False,
    ):
        """
        Initialize Detector Engine.

        :param mode: Detection mode - "basic" (fast ~30k core unigrams) or "high" (all unigram shards).
        :param cdn_base_url: Optional custom CDN base URL for remote unigram shards.
        :param cache_ttl: Time-to-live for local cache in seconds (default: 24h).
        :param force_remote: Force redownload from CDN on initialization.
        :param offline_only: Disable network calls and use local cache/bundled data only.
        :param custom_unigrams: Override built-in unigrams with a custom wordlist.
        :param extra_unigrams: Supplemental unigrams to augment built-in vocabulary.
        :param custom_stopwords: Override/supplement English stopwords.
        :param disable_default_stopwords: Disable built-in English stopwords.
        """
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

        # 1. Load Stopwords
        if not disable_default_stopwords:
            self._load_stopwords()

        if custom_stopwords:
            if disable_default_stopwords:
                self.english_stopwords = {w.lower() for w in custom_stopwords}
            else:
                self.english_stopwords.update({w.lower() for w in custom_stopwords})

        # 2. Load Unigrams
        if custom_unigrams:
            exact_words = {w.lower() for w in custom_unigrams}
        else:
            exact_words = self._load_unigram_shards(force_remote=force_remote)

        if extra_unigrams:
            exact_words.update({w.lower() for w in extra_unigrams})

        self.exact_hmar_vocab = exact_words
        self.normalized_hmar_vocab = {strip_diacritics(w) for w in exact_words}

    def _load_stopwords(self) -> None:
        """Load English stopwords from bundled data."""
        if BUNDLED_STOPWORDS.exists():
            with open(BUNDLED_STOPWORDS, "r", encoding="utf-8") as f:
                self.english_stopwords = {w.lower() for w in json.load(f)}
        else:
            self.english_stopwords = {
                "the", "and", "that", "for", "was", "with", "they", "have", 
                "from", "had", "by", "but", "what", "there", "were", "your"
            }

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

    def detect(self, text_or_tokens: Union[str, List[str]], return_tokens: bool = False) -> Dict[str, Any]:
        """
        Pure token or string language classification with standardized schema output.

        :param text_or_tokens: Clean text string OR pre-tokenized list of word tokens (1 word per item).
        :param return_tokens: Include token-by-token classification breakdown in output.
        :return: Standardized result dict.
        """
        if isinstance(text_or_tokens, (list, tuple)):
            # Pre-tokenized input (1 word per item - evaluated "as is")
            words = [str(w).lower().strip() for w in text_or_tokens if str(w).strip()]
        elif isinstance(text_or_tokens, str):
            if not text_or_tokens or not text_or_tokens.strip():
                return self._empty_result()
            # Strip URLs and emails before tokenization
            cleaned_text = re.sub(r"https?://\S+|www\.\S+", " ", text_or_tokens)
            cleaned_text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", " ", cleaned_text)
            words = [w.lower() for w in re.findall(r"\b[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]+\b", cleaned_text)]
        else:
            raise TypeError(f"Expected input to be a string or list of tokens, got {type(text_or_tokens).__name__}")

        total_words = len(words)
        if total_words == 0:
            return self._empty_result()

        # 1. Match Counts & Breakdown
        token_breakdown = []
        casual_matches = 0
        formal_matches = 0
        eng_stop_matches = 0
        diacritic_words_count = 0

        for w in words:
            w_norm = strip_diacritics(w)
            is_casual_hmar = w_norm in self.normalized_hmar_vocab
            is_formal_hmar = w in self.exact_hmar_vocab
            is_eng_stop = w in self.english_stopwords
            has_diacritic = any(c in w for c in "âêîôûṭ")

            if is_casual_hmar: casual_matches += 1
            if is_formal_hmar: formal_matches += 1
            if is_eng_stop: eng_stop_matches += 1
            if has_diacritic: diacritic_words_count += 1

            if return_tokens:
                token_breakdown.append({
                    "word": w,
                    "is_hmar": is_casual_hmar,
                    "is_formal_hmar": is_formal_hmar,
                    "is_english_stop": is_eng_stop,
                    "has_diacritic": has_diacritic,
                })

        non_hmar_words_count = total_words - casual_matches

        # 2. Ratios
        casual_hmar_ratio = casual_matches / total_words
        formal_hmar_ratio = formal_matches / total_words
        eng_stop_ratio = eng_stop_matches / total_words

        # 3. Orthography Tagging
        if diacritic_words_count >= 2:
            orthography = "formal_literary"
        elif diacritic_words_count == 1:
            orthography = "casual_qwerty"
        else:
            orthography = "casual_qwerty"

        # 4. Classification Logic
        if casual_hmar_ratio >= 0.65:
            language = "hmar"
        elif casual_hmar_ratio >= 0.45 and eng_stop_ratio < 0.025:
            language = "hmar"
        elif eng_stop_ratio >= 0.025 and casual_hmar_ratio < 0.40:
            language = "english"
        elif casual_hmar_ratio < 0.40 and eng_stop_ratio < 0.02:
            language = "other"  # Mizo, Kuki, Paite, or unclassified
        else:
            if casual_hmar_ratio >= 0.40 or casual_hmar_ratio > eng_stop_ratio * 5:
                language = "hmar"
            elif eng_stop_ratio > 0.02:
                language = "english"
            else:
                language = "other"

        # 5. Continuous Mathematical Confidence Score calculation [0.0000 - 1.0000]
        # Bayesian Length Weighting: W_len = 1 - exp(-N / 8)
        len_weight = 1.0 - math.exp(-total_words / 8.0)

        if language == "hmar":
            signal = (casual_hmar_ratio - eng_stop_ratio) / 0.60
            raw_conf = signal * len_weight
        elif language == "english":
            signal = (eng_stop_ratio - (casual_hmar_ratio / 5.0)) / 0.04
            raw_conf = signal * len_weight
        else:
            raw_conf = 0.50 * len_weight

        confidence_score = round(min(1.0, max(0.0, raw_conf)), 4)

        result = {
            "language": language,
            "confidence_score": confidence_score,
            "orthography": orthography,
            "mode": self.mode,
            "scores": {
                "casual_hmar_ratio": round(casual_hmar_ratio, 4),
                "formal_hmar_ratio": round(formal_hmar_ratio, 4),
                "english_stopword_ratio": round(eng_stop_ratio, 4),
                "total_words": total_words,
                "hmar_words_count": casual_matches,
                "non_hmar_words_count": non_hmar_words_count,
                "english_stopwords_count": eng_stop_matches,
                "diacritic_words_count": diacritic_words_count,
            },
        }

        if return_tokens:
            result["tokens"] = token_breakdown

        return result

    def _empty_result(self) -> Dict[str, Any]:
        """Return standardized result structure for empty input."""
        return {
            "language": "unknown",
            "confidence_score": 0.0,
            "orthography": "none",
            "mode": self.mode,
            "scores": {
                "casual_hmar_ratio": 0.0,
                "formal_hmar_ratio": 0.0,
                "english_stopword_ratio": 0.0,
                "total_words": 0,
                "hmar_words_count": 0,
                "non_hmar_words_count": 0,
                "english_stopwords_count": 0,
                "diacritic_words_count": 0,
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
    mode: str = "basic",
    return_tokens: bool = False
) -> Dict[str, Any]:
    """
    Top-level helper function to detect language of a text string OR pre-tokenized list of word tokens.

    >>> import hmaraniam
    >>> res = hmaraniam.detect(["khawvel", "fe", "dan", "phung"])
    >>> res["language"]
    'hmar'
    """
    if mode == "basic":
        return get_default_detector().detect(text_or_tokens, return_tokens=return_tokens)
    detector = Detector(mode=mode)
    return detector.detect(text_or_tokens, return_tokens=return_tokens)
