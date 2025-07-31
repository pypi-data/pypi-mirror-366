from pathlib import Path
import requests

def download_file(url, dest_path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
                
def ensure_folder(path):
    Path(path).mkdir(parents=True, exist_ok=True)