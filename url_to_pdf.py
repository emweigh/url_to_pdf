import sys
import asyncio
from playwright.sync_api import sync_playwright, Route, Request
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
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
global error_url_log

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
    # Check if url ends in a file extension
    parsed_url=urlparse(url)
    path=parsed_url.path
    return os.path.splitext(path)[1] not in ['','.html','.php','.aspx']

def override_content_disposition_handler(route: Route, request: Request) -> None:
    response = route.fetch() # performs the request
    overridden_headers = {
        **response.headers,
        "content-disposition": response.headers.get('content-disposition', 'attachment').replace('inline', 'attachment')
    }
    route.fulfill(response=response, headers=overridden_headers)

def save_pdf(url: str, filenum: str = None, run_headful: bool = False):
    global error_url_log
    error_url_log = ''
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=run_headful, slow_mo=0)
        context = browser.new_context()
        page = context.new_page()
        page.route("**/*.{pdf,png,jpeg,jpg}", handler=override_content_disposition_handler)
        print(page.title())
        if check_url(url):
            with page.expect_download() as download_info:
                try:
                    page.goto(url)
                    #page.on("download", lambda download: print(download.path()))
                except:
                    #error_url_log += f'{url}\n'
                    pass
            download=download_info.value
            download.save_as(f'{os.getcwd()}/{filenum.zfill(4)} - {download.suggested_filename}')
            print(f"{url} saved as {download.suggested_filename}")
        else:
            # Remove fixed and sticky elements
            page.goto(url,timeout=0)
            page.emulate_media(media='print')
            page.wait_for_load_state('load')
            page.evaluate('''() => {document.querySelectorAll("body *").forEach(function(node){if(["fixed","sticky"].includes(getComputedStyle(node).position)){node.parentNode.removeChild(node)}});document.querySelectorAll("html *").forEach(function(node){var s=getComputedStyle(node);if("hidden"===s["overflow"]){node.style["overflow"]="visible"}if("hidden"===s["overflow-x"]){node.style["overflow-x"]="visible"}if("hidden"===s["overflow-y"]){node.style["overflow-y"]="visible"}});var htmlNode=document.querySelector("html");htmlNode.style["overflow"]="visible";htmlNode.style["overflow-x"]="visible";htmlNode.style["overflow-y"]="visible"}''')

            print("Saving PDF")
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            title = soup.title.string if soup.title else "untitled"
            title = get_filename(title, filenum)
            output_path = f"{title}.pdf"

            page.pdf(path=output_path, format="Letter")
            print(f"{url} saved as {output_path}")
    #context.close()
    #browser.close()

def main():
    filename = None
    global numeric_naming
    numeric_naming = False
    global error_url_log
    
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

            print(index, " - Retrieving PDF from:", url)
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
                print(index, " - Retrieving PDF from:", url)
                save_pdf(url, str(index) if numeric_naming else None, run_headful=args.headful)
                index += 1
        sys.exit(0)

    print(error_url_log)

main()