import os
import random
import string

from .utils import ensure_folder

from .setup_logger import setup_logger 

logger = setup_logger(__name__) 

LOREM_SENTENCES = [
    "Lorem ipsum dolor sit amet.",
    "Consectetur adipiscing elit.",
    "Sed do eiusmod tempor incididunt.",
    "Ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam.",
    "Quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident.",
    "Sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "Integer nec odio. Praesent libero. Sed cursus ante dapibus diam.",
    "Nam nec ante. Sed lacinia, urna non tincidunt mattis, tortor neque adipiscing diam."
]

def _parse_size(size_str):
    size_str = size_str.lower().strip()
    if size_str.endswith("kb"):
        return int(float(size_str[:-2]) * 1024)
    elif size_str.endswith("mb"):
        return int(float(size_str[:-2]) * 1024 * 1024)
    else:
        return int(size_str)

def fetch_text(config: dict, folder: str):
    """
    config = {
        "max_words": 1000,
        "min_words": 100,
        "max_size": "200kb",
        "count": 4
    }
    Returns: list of valid text file paths.
    """
    ensure_folder(folder)

    count = config.get("count", 1)
    min_words = config.get("min_words", 100)
    max_words = config.get("max_words", 1000)
    max_size = _parse_size(config.get("max_size", "200kb"))

    saved_paths = []
    attempts = 0

    while len(saved_paths) < count and attempts < count * 5:
        word_count = random.randint(min_words, max_words)
        words = []
        while len(words) < word_count:
            sentence = random.choice(LOREM_SENTENCES)
            words.extend(sentence.split())

        text = ' '.join(words[:word_count])
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        filename = f"text_{len(saved_paths)+1}_{rand_suffix}.txt"
        path = os.path.join(folder, filename)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

            size = os.path.getsize(path)
            if size <= max_size:
                logger.info(f"Saved: {path} ({len(words)} words, {size} bytes)")
                saved_paths.append(path)
            else:
                os.remove(path)
                logger.warning(f"Rejected {filename} (too large: {size} bytes)")

        except Exception as e:
            logger.error(f"Failed to write file: {e}")

        attempts += 1

    return saved_paths
