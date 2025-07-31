import os
from pathlib import Path

from generate.gen_code import fetch_code
from generate.gen_json import fetch_json
from generate.gen_gifs import fetch_gifs
from generate.gen_images import fetch_images
from generate.gen_videos import fetch_videos
from generate.gen_text import fetch_text
from generate.gen_pdfs import fetch_pdfs

class Smpldta:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self._ensure_dir(self.output_dir)

    def _ensure_dir(self, folder):
        Path(folder).mkdir(parents=True, exist_ok=True)

    def fetch_images(self, config=None, subdir="images"):
        folder = os.path.join(self.output_dir, subdir)
        self._ensure_dir(folder)
        fetch_images(config, folder)

    def fetch_videos(self, config=None, subdir="videos"):
        folder = os.path.join(self.output_dir, subdir)
        self._ensure_dir(folder)
        fetch_videos(config, folder)

    def fetch_gifs(self, count=3, subdir="gifs"):
        folder = os.path.join(self.output_dir, subdir)
        self._ensure_dir(folder)
        fetch_gifs(count, folder)

    def fetch_code(self, config=None,subdir="code"):
        folder = os.path.join(self.output_dir, subdir)
        self._ensure_dir(folder)
        fetch_code(config, folder)

    def fetch_text(self, config=None, subdir="text"):
        folder = os.path.join(self.output_dir, subdir)
        self._ensure_dir(folder)
        fetch_text(config, folder)

    def fetch_json(self, config=None, subdir="json"):
        folder = os.path.join(self.output_dir, subdir)
        self._ensure_dir(folder)
        fetch_json(config, folder)
    
    def fetch_pdfs(self, config=None, subdir="pdfs"):
        folder = os.path.join(self.output_dir, subdir)
        self._ensure_dir(folder)
        fetch_pdfs(config, folder)

__all__ = ["Smpldta"]