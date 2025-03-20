import sys
import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import re
import argparse

"""
TODO:
1. Rewrite argument handling use argparse module
2. Add argument/flag to run in headful mode
3. Figure out a better way to generate and format PDFs.
4. Rewrite numeric naming so it includes actual filename, i.e. "NUM - ORIGINAL_FILENAME.pdf"
4. ?Optional? Check if webpage has print button; if so, use it to generate PDF instead

"""


global numeric_naming

def get_filename(title, filenum: str = None):
    filename = title.lower().replace(" ", "_").replace("/", "_").replace("|", "_")
    filename = re.sub(r'[^a-zA-Z0-9_\-]+', '', filename)

    global numeric_naming
    if numeric_naming:
        filename = filenum.zfill(4)+" - "+filename

    # Check if file already exists
    if os.path.isfile(filename):
        match = re.search(r'(\d+)$', filename)
        if match:
            num = int(match.group(1))
            filename = re.sub(r'\d+$', str(num + 1), filename)
        else:
            filename = filename + "_2"

    return filename


def save_pdf(url: str, filenum: str = None, run_headful: bool = False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=run_headful)
        page = browser.new_page()
        page.goto(url)
        print(page.title())

        # Remove fixed and sticky elements
        page.evaluate('''() => {document.querySelectorAll("body *").forEach(function(node){if(["fixed","sticky"].includes(getComputedStyle(node).position)){node.parentNode.removeChild(node)}});document.querySelectorAll("html *").forEach(function(node){var s=getComputedStyle(node);if("hidden"===s["overflow"]){node.style["overflow"]="visible"}if("hidden"===s["overflow-x"]){node.style["overflow-x"]="visible"}if("hidden"===s["overflow-y"]){node.style["overflow-y"]="visible"}});var htmlNode=document.querySelector("html");htmlNode.style["overflow"]="visible";htmlNode.style["overflow-x"]="visible";htmlNode.style["overflow-y"]="visible"}''')

        print("Saving PDF")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string if soup.title else "untitled"
        title = get_filename(title, filenum)
        output_path = f"{title}.pdf"

        page.pdf(path=output_path, format="Letter")
        browser.close()
        print(f"PDF saved as {output_path}")

def main_loop():
    filename = None
    global numeric_naming
    numeric_naming = False
    
    parser = argparse.ArgumentParser(prog="url_to_pdf",description="Save a webpage as a PDF!",epilog="And that's how can you save a batch of URLS as PDFs!")
    parser.add_argument("url",help="Webpage/html you want to save as a PDF",nargs="*")
    parser.add_argument("-f","--file",help="File containing list of URLs to download")
    parser.add_argument("-n","--numeric",help="Number the PDFs that are saved",action="store_true")
    parser.add_argument("-H","--headful",help="Run chromium in headful mode",action="store_false")
    args = parser.parse_args()

    index=1
    numeric_naming=args.numeric

    if args.url:
        for url in args.url:
            if url.startswith('-'):
                continue

            print(index, " - Downloading PDF from:", url)
            save_pdf(url, filenum=str(index) if numeric_naming else None, run_headful=args.headful)
            index += 1


    if args.file:
        filename = args.file
        if not os.path.isfile(filename):
            print("File not found: ", filename)
            sys.exit(1)

        with open(filename, "r") as f:
            urls = f.readlines()
            for url in urls:
                print(index, " - Downloading PDF from:", url)
                save_pdf(url, str(index) if numeric_naming else None, run_headful=args.headful)
                index += 1
        sys.exit(0)

main_loop()