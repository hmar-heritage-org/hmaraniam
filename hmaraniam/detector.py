"""
Core Language Identification Detector for Hmar (hmaraniam).
"Hmar a ni am?" -> "Is it Hmar?"
"""

import json
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# CDN Base URL for sharded dataset
DEFAULT_CDN_BASE_URL = "https://cdn.jsdelivr.net/gh/hmar-heritage-org/hmaraniam@main/hmaraniam/data/shards/"
CACHE_DIR = Path.home() / ".cache" / "hmaraniam"
CACHE_SHARDS_DIR = CACHE_DIR / "shards"
CACHE_META = CACHE_DIR / "cache_meta.json"

# Package bundled data paths
PACKAGE_DIR = Path(__file__).parent
BUNDLED_SHARDS_DIR = PACKAGE_DIR / "data" / "shards"
BUNDLED_STOPWORDS = PACKAGE_DIR / "data" / "stopwords.json"


class Detector:
    """
    Hmar Language Identification Detector.
    
    Provides high-precision language detection for Hmar text,
    distinguishing Hmar from English and other Kuki-Chin / Zo languages.
    """

    def __init__(
        self,
        mode: str = "basic",  # "basic" (core set 001) or "high" (all shards set_*.json)
        cdn_base_url: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours in seconds
        force_remote: bool = False,
        offline_only: bool = False,
    ):
        """
        Initialize Detector.

        :param mode: Detection mode - "basic" (fast ~30k core unigrams) or "high" (all unigram shards).
        :param cdn_base_url: Optional custom CDN base URL for remote unigram shards.
        :param cache_ttl: Time-to-live for local cache in seconds (default: 24h).
        :param force_remote: Force redownload from CDN on initialization.
        :param offline_only: Disable network calls and use local cache/bundled data only.
        """
        self.mode = mode.lower()
        if self.mode not in ["basic", "high"]:
            raise ValueError(
                f"Invalid detection mode '{mode}'. Supported modes are 'basic' (default) and 'high' (extended dataset)."
            )

        self.cdn_base_url = (cdn_base_url or DEFAULT_CDN_BASE_URL).rstrip("/") + "/"
        self.cache_ttl = cache_ttl
        self.offline_only = offline_only

        self.hmar_vocab: set = set()
        self.english_stopwords: set = set()

        self._load_stopwords()
        self._load_unigram_shards(force_remote=force_remote)

    def _load_stopwords(self) -> None:
        """Load English stopwords from bundled data."""
        if BUNDLED_STOPWORDS.exists():
            with open(BUNDLED_STOPWORDS, "r", encoding="utf-8") as f:
                self.english_stopwords = set(json.load(f))
        else:
            self.english_stopwords = {
                "the", "and", "that", "for", "was", "with", "they", "have", 
                "from", "had", "by", "but", "what", "there", "were", "your"
            }

    def _get_shard_filenames(self) -> List[str]:
        """Determine which shard filenames to load based on mode."""
        if self.mode == "basic":
            return ["unigrams_set_001.json"]

        # For "high" mode, dynamically discover all unigrams_set_*.json in bundled or cached dir
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

    def _load_unigram_shards(self, force_remote: bool = False) -> None:
        """Load Hmar unigrams vocabulary from shards based on current mode."""
        shard_filenames = self._get_shard_filenames()
        accumulated_words = set()

        for shard_name in shard_filenames:
            words = self._load_single_shard(shard_name, force_remote=force_remote)
            if words:
                accumulated_words.update(words)

        if accumulated_words:
            self.hmar_vocab = {w.lower() for w in accumulated_words}
        else:
            raise RuntimeError("Failed to load any Hmar unigram shards.")

    def _load_single_shard(self, shard_name: str, force_remote: bool = False) -> Optional[List[str]]:
        """Load a single unigram shard using CDN, cache, or bundled fallback."""
        cache_path = CACHE_SHARDS_DIR / shard_name
        bundled_path = BUNDLED_SHARDS_DIR / shard_name
        loaded_data: Optional[List[str]] = None

        # 1. Try Remote CDN if network enabled
        if not self.offline_only:
            if force_remote or self._should_fetch_remote(cache_path):
                loaded_data = self._fetch_shard_from_cdn(shard_name, cache_path)

        # 2. Try Local Cache if CDN fetch didn't happen or failed
        if loaded_data is None and cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
            except Exception:
                loaded_data = None

        # 3. Fallback to package bundled shards
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
            pass  # Fail gracefully to cache or bundled data
        return None

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect language of a given text string.

        :param text: Input text to classify.
        :return: Structured result dict containing language label, confidence, and score breakdown.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected text input to be a string, got {type(text).__name__}")

        if not text or not text.strip():
            return {
                "language": "unknown",
                "confidence": "uncertain",
                "mode": self.mode,
                "scores": {
                    "hmar_ratio": 0.0,
                    "english_stopword_ratio": 0.0,
                    "total_words": 0,
                    "hmar_matches": 0,
                    "english_stop_matches": 0,
                },
            }

        # Strip URLs and email addresses before tokenization
        cleaned_text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        cleaned_text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", " ", cleaned_text)

        words = [w.lower() for w in re.findall(r"\b[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]+\b", cleaned_text)]
        total_words = len(words)

        if total_words == 0:
            return {
                "language": "unknown",
                "confidence": "uncertain",
                "mode": self.mode,
                "scores": {
                    "hmar_ratio": 0.0,
                    "english_stopword_ratio": 0.0,
                    "total_words": 0,
                    "hmar_matches": 0,
                    "english_stop_matches": 0,
                },
            }

        hmar_matches = sum(1 for w in words if w in self.hmar_vocab)
        eng_stop_matches = sum(1 for w in words if w in self.english_stopwords)

        hmar_ratio = hmar_matches / total_words
        eng_stop_ratio = eng_stop_matches / total_words

        # Classification & Confidence Logic
        if hmar_ratio >= 0.65:
            language = "hmar"
            confidence = "definitely" if hmar_ratio >= 0.75 else "likely"
        elif hmar_ratio >= 0.45 and eng_stop_ratio < 0.025:
            language = "hmar"
            confidence = "likely"
        elif eng_stop_ratio >= 0.025 and hmar_ratio < 0.40:
            language = "english"
            confidence = "definitely" if eng_stop_ratio >= 0.04 else "likely"
        elif hmar_ratio < 0.40 and eng_stop_ratio < 0.02:
            language = "other"  # Mizo, Kuki, Paite, or unclassified
            confidence = "likely"
        else:
            if hmar_ratio >= 0.40 or hmar_ratio > eng_stop_ratio * 5:
                language = "hmar"
                confidence = "likely"
            elif eng_stop_ratio > 0.02:
                language = "english"
                confidence = "likely"
            else:
                language = "other"
                confidence = "uncertain"

        return {
            "language": language,
            "confidence": confidence,
            "mode": self.mode,
            "scores": {
                "hmar_ratio": round(hmar_ratio, 4),
                "english_stopword_ratio": round(eng_stop_ratio, 4),
                "total_words": total_words,
                "hmar_matches": hmar_matches,
                "english_stop_matches": eng_stop_matches,
            },
        }

    def detect_html(self, raw_html: str) -> Dict[str, Any]:
        """
        Extract clean body text from raw HTML and detect language.

        :param raw_html: Raw HTML string.
        :return: Structured result dict.
        """
        if not raw_html:
            return self.detect("")

        # Strip HTML comments, scripts, styles, and tags
        text = re.sub(r"<!--.*?-->", " ", raw_html, flags=re.DOTALL)
        text = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        return self.detect(text.strip())

    def detect_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into paragraphs and classify each paragraph independently.

        :param text: Input multi-paragraph text.
        :return: List of dicts per non-empty paragraph.
        """
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


def detect(text: str, mode: str = "basic") -> Dict[str, Any]:
    """
    Top-level helper function to detect language of a text string.

    >>> import hmaraniam
    >>> res = hmaraniam.detect("Tuking chanchinbu a hung suok tlangval a nih.")
    >>> res["language"]
    'hmar'
    """
    if mode == "basic":
        return get_default_detector().detect(text)
    detector = Detector(mode=mode)
    return detector.detect(text)


def detect_html(raw_html: str, mode: str = "basic") -> Dict[str, Any]:
    """Top-level helper function to extract text from HTML and detect language."""
    if mode == "basic":
        return get_default_detector().detect_html(raw_html)
    detector = Detector(mode=mode)
    return detector.detect_html(raw_html)


def detect_file(filepath: Union[str, Path], mode: str = "basic") -> Dict[str, Any]:
    """Helper function to read a text file and detect its language."""
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Target file does not exist or is not a valid file: '{filepath}'")

    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() in [".html", ".htm", ".xhtml"]:
        return detect_html(text, mode=mode)
    return detect(text, mode=mode)
