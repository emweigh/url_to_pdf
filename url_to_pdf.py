import sys
import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import re

def getFilename(title):
    filename = title.replace(" ", "_").replace("/", "_").replace("|", "_")
    filename = re.sub(r'[^a-zA-Z_\-]+', '', filename)


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

        # Remove fixed and sticky elements
        page.evaluate('''() => {document.querySelectorAll("body *").forEach(function(node){if(["fixed","sticky"].includes(getComputedStyle(node).position)){node.parentNode.removeChild(node)}});document.querySelectorAll("html *").forEach(function(node){var s=getComputedStyle(node);if("hidden"===s["overflow"]){node.style["overflow"]="visible"}if("hidden"===s["overflow-x"]){node.style["overflow-x"]="visible"}if("hidden"===s["overflow-y"]){node.style["overflow-y"]="visible"}});var htmlNode=document.querySelector("html");htmlNode.style["overflow"]="visible";htmlNode.style["overflow-x"]="visible";htmlNode.style["overflow-y"]="visible"}''')

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

    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print("Usage: python url_to_pdf.py <url>")
        sys.exit(0)

    if sys.argv[1] == "-f" or sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Usage: python url_to_pdf.py -f <file>")
            sys.exit(1)

        with open(sys.argv[2], "r") as f:
            urls = f.readlines()
            for url in urls:
                print("Downloading PDF from:", url)
                save_pdf(url)
        sys.exit(0)

    input_args = sys.argv[1:]
    for url in input_args:
        print("Downloading PDF from:", url)
        save_pdf(url)
