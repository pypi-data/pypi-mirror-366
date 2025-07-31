import os
import random
import string

from .utils import ensure_folder, download_file
from .setup_logger import setup_logger  # <- import once

logger = setup_logger(__name__) 

BASE_VIDEO_URL = "https://www.sample-videos.com/video321"

SIZE_OPTIONS = [1, 2, 5, 10, 20, 30]
SIZE_3GP = [1, 2, 5, 10]

RESOLUTION_MAP = {
    "mp4": ["720", "480", "360", "240"],
    "flv": ["720", "480", "360", "240"],
    "mkv": ["720", "480", "360", "240"],
    "3gp": ["144", "240"]
}


def fetch_videos(config: dict, folder: str):
    """
    Downloads videos based on config:
    {
        "mp4": {"count": 4, "min_size": "5mb", "max_size": "20mb"},
        "3gp": {"count": 2, "max_size": "10mb"}
    }
    Returns list of successfully downloaded file paths.
    """
    ensure_folder(folder)
    saved_paths = []

    for fmt, props in config.items():
        count = props.get("count", 1)
        min_size = int(props.get("min_size", "1mb").replace("mb", ""))
        max_size = int(props.get("max_size", "30mb").replace("mb", ""))

        sizes = SIZE_3GP if fmt == "3gp" else SIZE_OPTIONS
        size_list = [s for s in sizes if min_size <= s <= max_size]

        if not size_list:
            logger.warning(f"[SKIP] No valid sizes for {fmt} in {min_size}-{max_size}MB")
            continue

        resolutions = RESOLUTION_MAP.get(fmt, [])
        if not resolutions:
            logger.warning(f"[SKIP] Unknown format: {fmt}")
            continue

        for i in range(count):
            size = random.choice(size_list)
            resolution = random.choice(resolutions)

            url = f"{BASE_VIDEO_URL}/{fmt}/{resolution}/big_buck_bunny_{resolution}p_{size}mb.{fmt}"
            # print(url)
            rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            dest = os.path.join(folder, f"{fmt}_{i+1}_{rand_suffix}.{fmt}")

            try:
                download_file(url, dest)
                logger.info(f"Downloaded: {dest}")
                saved_paths.append(dest)
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")

    return saved_paths
