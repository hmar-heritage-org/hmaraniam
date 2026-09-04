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

# CDN Source of Truth
DEFAULT_CDN_URL = "https://cdn.jsdelivr.net/gh/hmar-heritage-org/hmaraniam@main/hmaraniam/data/unigrams.json"
CACHE_DIR = Path.home() / ".cache" / "hmaraniam"
CACHE_FILE = CACHE_DIR / "unigrams.json"
CACHE_META = CACHE_DIR / "cache_meta.json"

# Package bundled data paths
PACKAGE_DIR = Path(__file__).parent
BUNDLED_UNIGRAMS = PACKAGE_DIR / "data" / "unigrams.json"
BUNDLED_STOPWORDS = PACKAGE_DIR / "data" / "stopwords.json"


class Detector:
    """
    Hmar Language Identification Detector.
    
    Provides high-precision language detection for Hmar text,
    distinguishing Hmar from English and other Kuki-Chin / Zo languages.
    """

    def __init__(
        self,
        cdn_url: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours in seconds
        force_remote: bool = False,
        offline_only: bool = False,
    ):
        """
        Initialize Detector.

        :param cdn_url: Optional custom CDN URL for remote unigrams dataset.
        :param cache_ttl: Time-to-live for local cache in seconds (default: 24h).
        :param force_remote: Force redownload from CDN on initialization.
        :param offline_only: Disable network calls and use local cache/bundled data only.
        """
        self.cdn_url = cdn_url or DEFAULT_CDN_URL
        self.cache_ttl = cache_ttl
        self.offline_only = offline_only

        self.hmar_vocab: set = set()
        self.english_stopwords: set = set()

        self._load_stopwords()
        self._load_unigrams(force_remote=force_remote)

    def _load_stopwords(self) -> None:
        """Load English stopwords from bundled data."""
        if BUNDLED_STOPWORDS.exists():
            with open(BUNDLED_STOPWORDS, "r", encoding="utf-8") as f:
                self.english_stopwords = set(json.load(f))
        else:
            # Fallback basic stopwords
            self.english_stopwords = {
                "the", "and", "of", "to", "is", "that", "for", "was", "with", 
                "they", "have", "from", "had", "by", "but", "what", "there", "we"
            }

    def _load_unigrams(self, force_remote: bool = False) -> None:
        """Load Hmar unigrams vocabulary using remote CDN, cache, or bundled fallback."""
        loaded_data: Optional[List[str]] = None

        # 1. Try Remote CDN if network enabled and (force_remote or cache expired)
        if not self.offline_only:
            if force_remote or self._should_fetch_remote():
                loaded_data = self._fetch_from_cdn()

        # 2. Try Local Cache if CDN fetch didn't happen or failed
        if loaded_data is None and CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
            except Exception:
                loaded_data = None

        # 3. Fallback to package bundled unigrams data
        if loaded_data is None and BUNDLED_UNIGRAMS.exists():
            with open(BUNDLED_UNIGRAMS, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)

        if loaded_data:
            self.hmar_vocab = {word.lower() for word in loaded_data}
        else:
            raise RuntimeError("Failed to load Hmar unigrams data from CDN, cache, or bundled assets.")

    def _should_fetch_remote(self) -> bool:
        """Check if local cache is missing or older than cache_ttl."""
        if not CACHE_FILE.exists() or not CACHE_META.exists():
            return True
        try:
            with open(CACHE_META, "r", encoding="utf-8") as f:
                meta = json.load(f)
            fetch_time = meta.get("fetched_at", 0)
            return (time.time() - fetch_time) > self.cache_ttl
        except Exception:
            return True

    def _fetch_from_cdn(self) -> Optional[List[str]]:
        """Fetch latest unigrams dataset from CDN and save to local disk cache."""
        try:
            req = urllib.request.Request(
                self.cdn_url,
                headers={"User-Agent": "hmaraniam-detector/0.1.0"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    raw_content = resp.read().decode("utf-8")
                    data = json.loads(raw_content)

                    # Save to local cache asynchronously/safely
                    CACHE_DIR.mkdir(parents=True, exist_ok=True)
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        f.write(raw_content)

                    with open(CACHE_META, "w", encoding="utf-8") as f:
                        json.dump({"fetched_at": time.time(), "source": self.cdn_url}, f)

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
        if not text or not text.strip():
            return {
                "language": "unknown",
                "confidence": "uncertain",
                "scores": {
                    "hmar_ratio": 0.0,
                    "english_stopword_ratio": 0.0,
                    "total_words": 0,
                    "hmar_matches": 0,
                    "english_stop_matches": 0,
                },
            }

        # Tokenize text into words (supporting Latin and Unicode diacritics)
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]+\b", text)]
        total_words = len(words)

        if total_words == 0:
            return {
                "language": "unknown",
                "confidence": "uncertain",
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
        if hmar_ratio >= 0.70 and eng_stop_ratio < 0.01:
            language = "hmar"
            confidence = "definitely"
        elif hmar_ratio >= 0.45 and eng_stop_ratio < 0.025:
            language = "hmar"
            confidence = "likely"
        elif eng_stop_ratio >= 0.03 and hmar_ratio < 0.40:
            language = "english"
            confidence = "definitely" if eng_stop_ratio >= 0.05 else "likely"
        elif hmar_ratio < 0.40 and eng_stop_ratio < 0.02:
            language = "other"  # Mizo, Kuki, Paite, or unclassified
            confidence = "likely"
        else:
            # Code-switched / mixed text
            if hmar_ratio > eng_stop_ratio * 10:
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
            "scores": {
                "hmar_ratio": round(hmar_ratio, 4),
                "english_stopword_ratio": round(eng_stop_ratio, 4),
                "total_words": total_words,
                "hmar_matches": hmar_matches,
                "english_stop_matches": eng_stop_matches,
            },
        }

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
        _default_detector = Detector()
    return _default_detector


def detect(text: str) -> Dict[str, Any]:
    """
    Top-level helper function to detect language of a text string.

    >>> import hmaraniam
    >>> res = hmaraniam.detect("Tuking chanchinbu a hung suok tlangval a nih.")
    >>> res["language"]
    'hmar'
    """
    return get_default_detector().detect(text)


def detect_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Helper function to read a text file and detect its language."""
    path = Path(filepath)
    text = path.read_text(encoding="utf-8", errors="ignore")
    return detect(text)
