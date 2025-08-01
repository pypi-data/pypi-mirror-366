import os
import random
import string

from .utils import ensure_folder, download_file

from .setup_logger import setup_logger

logger = setup_logger(__name__) 


def _parse_size(size_str):
    """
    Converts '2mb' or '400kb' to bytes.
    """
    size_str = size_str.lower().strip()
    if size_str.endswith('mb'):
        return int(float(size_str[:-2]) * 1024 * 1024)
    elif size_str.endswith('kb'):
        return int(float(size_str[:-2]) * 1024)
    else:
        return int(size_str)


def fetch_images(config: dict, folder: str):
    """
    Downloads images per user config.

    Example config:
    {
        "jpg": {
            "count": 3,
            "min_size": "3kb",
            "max_size": "2mb",
            "height": 600,
            "width": 300
        },
        "jpeg": {
            "count": 2,
            "min_size": "5kb",
            "max_size": "500kb",
            "height": 400,
            "width": 400
        }
    }
    Returns list of saved file paths.
    """
    ensure_folder(folder)
    saved_paths = []

    for fmt, props in config.items():
        count = props.get("count", 1)
        height = props.get("height", 600)
        width = props.get("width", 800)
        min_size = _parse_size(props.get("min_size", "1kb"))
        max_size = _parse_size(props.get("max_size", "3mb"))

        logger.info(f"[{fmt.upper()}] Requesting {count} images of size {width}x{height}, {min_size}-{max_size} bytes")

        downloaded = 0
        attempts = 0
        while downloaded < count and attempts < count * 5:
            seed = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
            dest = os.path.join(folder, f"image_{downloaded + 1}_{seed}.{fmt}")

            try:
                download_file(url, dest)

                file_size = os.path.getsize(dest)
                if min_size <= file_size <= max_size:
                    saved_paths.append(dest)
                    logger.info(f"Downloaded: {dest} ({file_size} bytes)")
                    downloaded += 1
                else:
                    logger.warning(f"Rejected (size {file_size} bytes not in range): {dest}")
                    os.remove(dest)

            except Exception as e:
                logger.error(f"Failed to download image: {e}")
            attempts += 1

    return saved_paths
