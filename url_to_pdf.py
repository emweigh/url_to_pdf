import sys
import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import re

global numericNaming

def getFilename(title):
    filename = title.lower().replace(" ", "_").replace("/", "_").replace("|", "_")
    filename = re.sub(r'[^a-zA-Z0-9_\-]+', '', filename)

    global numericNaming
    if numericNaming:
        filename = filename.zfill(4)

    # Check if file already exists
    if os.path.isfile(filename):
        match = re.search(r'(\d+)$', filename)
        if match:
            num = int(match.group(1))
            filename = re.sub(r'\d+$', str(num + 1), filename)
        else:
            filename = filename + "_2"

    return filename


def save_pdf(url: str, filename: str = None):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        print(page.title())

        # Remove fixed and sticky elements
        page.evaluate('''() => {document.querySelectorAll("body *").forEach(function(node){if(["fixed","sticky"].includes(getComputedStyle(node).position)){node.parentNode.removeChild(node)}});document.querySelectorAll("html *").forEach(function(node){var s=getComputedStyle(node);if("hidden"===s["overflow"]){node.style["overflow"]="visible"}if("hidden"===s["overflow-x"]){node.style["overflow-x"]="visible"}if("hidden"===s["overflow-y"]){node.style["overflow-y"]="visible"}});var htmlNode=document.querySelector("html");htmlNode.style["overflow"]="visible";htmlNode.style["overflow-x"]="visible";htmlNode.style["overflow-y"]="visible"}''')

        print("Saving PDF")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string if soup.title else "untitled"
        title = getFilename(filename if filename else title)
        output_path = f"{title}.pdf"

        page.pdf(path=output_path, format="A4")
        browser.close()
        print(f"PDF saved as {output_path}")


if __name__ == "__main__":
    filename = None
    numericNaming = False

    if len(sys.argv) < 2:
        print("Usage: python url_to_pdf.py <url>")
        sys.exit(1)

    if '-h' in sys.argv or '--help' in sys.argv:
        print("Usage: python url_to_pdf.py <url>")
        sys.exit(0)

    if '-f' in sys.argv or '--file' in sys.argv:
        if len(sys.argv) < 3:
            print("Usage: python url_to_pdf.py -f <file>")
            sys.exit(1)

        filename=sys.argv[-1]

    index = 1
    if '-n' in sys.argv or '--numeric' in sys.argv:
        numericNaming = True

    if filename:
        if not os.path.isfile(filename):
            print("File not found: ", filename)
            sys.exit(1)

        with open(filename, "r") as f:
            urls = f.readlines()
            for url in urls:
                print(index, " - Downloading PDF from:", url)
                save_pdf(url, str(index) if numericNaming else None)
                index += 1
        sys.exit(0)

    input_args = sys.argv[1:]
    for url in input_args:
        if url.startswith('-'):
            continue

        print(index, " - Downloading PDF from:", url)
        save_pdf(url, filename = str(index) if numericNaming else None)
        index += 1
