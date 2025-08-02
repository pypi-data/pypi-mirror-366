import urllib
import zipfile
from pathlib import Path

def download_and_unzip(url: str, extract_dir: Path):

    zip_path, _ = urllib.request.urlretrieve(url)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(extract_dir)