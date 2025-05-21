import os
from typing import List
import requests

URLS: List[str] = [
    "https://en.wikipedia.org/wiki/Babylon",
    "https://en.wikipedia.org/wiki/Mesopotamia",
    "https://en.wikipedia.org/wiki/Achaemenid_Empire",
]


def download_wikipedia_pdf(title: str, output_dir: str) -> None:
    """
    Download the Wikipedia page with the given title as a PDF and save it.

    :param title: The title of the Wikipedia page to download.
    :param output_dir: Directory where the PDF file will be saved.
    """
    endpoint = f"https://en.wikipedia.org/api/rest_v1/page/pdf/{title}"
    response = requests.get(endpoint, stream=True)
    response.raise_for_status()

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{title}.pdf")
    with open(filepath, "wb") as pdf_file:
        for chunk in response.iter_content(chunk_size=8192):
            pdf_file.write(chunk)


def extract_title_from_url(url: str) -> str:
    """
    Extract the page title from a Wikipedia URL.

    :param url: Full URL of the Wikipedia page.
    :return: The page title suitable for the PDF-API endpoint.
    """
    if "/wiki/" not in url:
        raise ValueError(f"Invalid Wikipedia URL: {url}")
    return url.split("/wiki/")[1].split("?", 1)[0]


def main() -> None:
    output_dir = "files"
    for url in URLS:
        title = extract_title_from_url(url)
        download_wikipedia_pdf(title, output_dir)
        print(f"✔ Saved: {os.path.join(output_dir, title)}.pdf")


if __name__ == "__main__":
    main()
