import io
import requests
import zipfile

def download_zip(url: str) -> zipfile.ZipFile:
    response = requests.get(url)
    response.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(response.content))
