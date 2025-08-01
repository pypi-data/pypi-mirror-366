import os
import random
from .utils import ensure_folder, download_file
from .setup_logger import setup_logger  

logger = setup_logger(__name__)  

def fetch_gifs(n, folder):
    ensure_folder(folder)

    gif_ids = [
    "ICOgUNjpvO0PC",
    "3o6Zt6Dfu7bAqbnCzm",
    "xT9IgDEI1iZyb2wqo8",
    "26tPplGWjN0xLybiU",
    "l2JJKs3I69qfaQleE",
    "3o7btNaFh9JvnL7lIc",
    "13CoXDiaCcCoyk",
    "xUPGcceW4e0rqRxM4c",
    "l0MYEqEzwMWFCg8rm",
    "3oriO7A7bt1wsEP4cw",
    "iIqmM5tTjmpOB9mpbn",
    "fAnEC88LccN7a"
]

    saved_paths = []
    for i in range(n):
        gid = random.choice(gif_ids)
        url = f"https://media.giphy.com/media/{gid}/giphy.gif"
        dest = os.path.join(folder, f'gif_{i+1}_{gid}.gif')
        try:
            download_file(url, dest)
            logger.info(f"Downloaded: {dest}")
            saved_paths.append(dest)
        except Exception as e:
            logger.error(f"Failed to download GIF {gid}: {e}")

    return saved_paths
