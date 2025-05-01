import sys
import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import re
import argparse

"""
TODO:
1. Figure out a better way to generate and format PDFs.
2. Check if webpage is actually a PDF being rendered. If so, use built in option to download instead.
3. Add flag to choose browser to run (default is Chromium but we also want WebKit and Firefox)
3. Evaluate Javascript for removing elements
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

def check_url(url : str):
	# Check if url already links to PDF, and if PDF, then download and save instead of print to PDF
	return url.endswith((".PDF",".pdf"))

def save_pdf(url: str, filenum: str = None, run_headful: bool = False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=run_headful, slow_mo=5000)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state('load')
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

def main():
    filename = None
    global numeric_naming
    numeric_naming = False
    
    parser = argparse.ArgumentParser(prog="url_to_pdf",description="Save a webpage as a PDF!",epilog="And that's how can you save a batch of URLS as PDFs!")
    parser.add_argument("url",help="Webpage/html you want to save as a PDF",nargs="*")
    parser.add_argument("-f","--file",help="File containing list of URLs to download")
    parser.add_argument("-n","--numeric",help="Number the PDFs that are saved",action="store_true")
    parser.add_argument("-H","--headful",help="Run chromium in headful mode",action="store_false")
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

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

main()