# import os
# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# import logging
# import time


# logger = logging.getLogger(__name__)

# def download_pdf(component, download_folder):
#     # Ensure the download folder exists
#     download_folder = os.path.abspath(download_folder)
#     os.makedirs(download_folder, exist_ok=True)

#     # Define file path
#     file_path = os.path.join(download_folder, f"{component.name}.pdf")
#     logging.info(f"Downloading {component.name} from {component.url} to {file_path}")

#     # Check if the file already exists
#     if os.path.exists(file_path):
#         logging.info(f"File {file_path} already exists. Skipping download.")
#         return file_path

#     # Set headers to mimic a browser
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#         "Accept": "application/pdf",
#         "Referer": component.url,
#         "Connection": "keep-alive",
#     }

#     # Create a session with retries
#     session = requests.Session()
#     retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
#     session.mount("https://", HTTPAdapter(max_retries=retries))

#     time.sleep(3)

#     try:
#         with session.get(component.url, headers=headers, stream=True, timeout=10) as r:
#             r.raise_for_status()
#             with open(file_path, "wb") as f:
#                 for chunk in r.iter_content(chunk_size=8192):
#                     f.write(chunk)
#     except requests.RequestException as e:
#         logging.warning(f"Failed to download {component.name}: {e}")

#     return file_path

import os
from urllib.parse import unquote
import httpx


async def download_pdf(component, pdf_path):
    url = component.url
    async with httpx.AsyncClient(follow_redirects=True) as client:
        decoded_url = unquote(url)
        response = await client.get(
            decoded_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:117.0) Gecko/20100101 Firefox/117.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.mouser.com/"
            }
        )
        response.raise_for_status()

        # Ensure folder exists
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        with open(pdf_path, "wb") as f:
            f.write(response.content)
