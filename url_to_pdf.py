import sys
import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import re

def getFilename(title):
    filename = title.replace(" ", "_").replace("/", "_").replace("|", "_")

    # Check if file already exists
    if os.path.isfile(filename):
        match = re.search(r'(\d+)$', filename)
        if match:
            num = int(match.group(1))
            filename = re.sub(r'\d+$', str(num + 1), filename)
        else:
            filename = filename + "_2"

    return filename

def save_pdf(url: str, output_file: str = 'file.pdf'):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        print(page.title())

        print("Saving PDF")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string if soup.title else "untitled"
        title = getFilename(title)
        output_path = f"{title}.pdf"

        page.pdf(path=output_path, format="A4")
        browser.close()
        print(f"PDF saved as {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python url_to_pdf.py <url>")
        sys.exit(1)

    input_args = sys.argv[1:]
    for url in input_args:
        print("Downloading PDF from:", url)
        save_pdf(url)
