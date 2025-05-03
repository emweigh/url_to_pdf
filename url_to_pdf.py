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

# Boolean variable for numeric naming, i.e. 1 - File_1, 2 - File_2, and so on
global numeric_naming

# String variable for holding urls that are
global error_url_log

def get_filename(title, filenum: str = None):
    # Replace whitespace, incompatible characters from the filename with underscore _
    filename = title.lower().replace(" ", "_").replace("/", "_").replace("|", "_")
    # Remove any incompatible characters from filename
    filename = re.sub(r'[^a-zA-Z0-9_\-]+', '', filename)

    global numeric_naming
    # If numeric naming is enabled then add on numbering to filename with leading zeroes
    if numeric_naming:
        filename = filenum.zfill(4)+" - "+filename

    # Check if file already exists
    if os.path.isfile(filename):
        # Check if the already existing file has been numbered
        match = re.search(r'(\d+)$', filename)
        if match:
            # If already exisitng file is numbered, increment by one for 'new' filename
            num = int(match.group(1))
            filename = re.sub(r'\d+$', str(num + 1), filename)
        else:
            # If already existing file is not numbered, then add '_2' at end of filename
            filename = filename + "_2"
    return filename

def check_url(url : str):
    # Check if url ends in a file extension
    parsed_url=urlparse(url)
    path=parsed_url.path

    # Run boolean check against file extension to make sure it's not a webpage
    return os.path.splitext(path)[1] not in ['','.html','.php','.aspx']

def override_content_disposition_handler(route: Route, request: Request) -> None:
    # Borrowed code from https://github.com/microsoft/playwright/issues/15163
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
        # Setup browser
        browser = p.chromium.launch(headless=run_headful, slow_mo=0)
        context = browser.new_context()
        page = context.new_page()

        # Here we want to make sure that our browser will treat certain documents as attachments to autmatically download
        # instead of openining in the browser's builtin viewer
        page.route("**/*.{pdf,png,jpeg,jpg}", handler=override_content_disposition_handler)
        print(page.title())

        # We still have to run a check on the url to iniitiate document downloads
        if check_url(url):
            with page.expect_download() as download_info:
                try:
                    # Navigate to url to document. This forces the browser to download the document.
                    page.goto(url)

                    #page.on("download", lambda download: print(download.path()))
                except:
                    #error_url_log += f'{url}\n'

                    # By default, playwright will throw an error after navigating to a page and starting the download
                    # We include this error handling to keep the script running
                    pass
            # Initiate the download
            download=download_info.value
            download.save_as(f'{os.getcwd()}/{filenum.zfill(4)} - {download.suggested_filename}')
            print(f"{url} saved as {download.suggested_filename}")
        else:
            # Webpage pdf render and download
            page.goto(url,timeout=0)
            page.emulate_media(media='print')
            page.wait_for_load_state('load')

            # Remove fixed and sticky elements
            page.evaluate('''() => {document.querySelectorAll("body *").forEach(function(node){if(["fixed","sticky"].includes(getComputedStyle(node).position)){node.parentNode.removeChild(node)}});
                document.querySelectorAll("html *").forEach(function(node){var s=getComputedStyle(node);
                if("hidden"===s["overflow"]){node.style["overflow"]="visible"}if("hidden"===s["overflow-x"]){node.style["overflow-x"]="visible"}if("hidden"===s["overflow-y"]){node.style["overflow-y"]="visible"}});
                var htmlNode=document.querySelector("html");
                htmlNode.style["overflow"]="visible";
                htmlNode.style["overflow-x"]="visible";
                htmlNode.style["overflow-y"]="visible"}''')

            # Render webpage as pdf
            print("Saving PDF")
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            title = soup.title.string if soup.title else "untitled"
            title = get_filename(title, filenum)
            output_path = f"{title}.pdf"

            # Save webpage as pdf
            page.pdf(path=output_path, format="Letter")
            print(f"{url} saved as {output_path}")
    #context.close()
    #browser.close()

def main():
    filename = None
    global numeric_naming
    numeric_naming = False
    global error_url_log
    
    # Argument handling with argparse
    parser = argparse.ArgumentParser(prog="url_to_pdf",description="Save a webpage as a PDF!",epilog="And that's how can you save a batch of URLS as PDFs!")
    parser.add_argument("url",help="Webpage/html you want to save as a PDF",nargs="*")
    parser.add_argument("-f","--file",help="File containing list of URLs to download")
    parser.add_argument("-n","--numeric",help="Number the PDFs that are saved",action="store_true")
    parser.add_argument("-H","--headful",help="Run chromium in headful mode",action="store_false")
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    index=1
    numeric_naming=args.numeric

    # For retrieving single url or multiple urls
    if args.url:
        for url in args.url:
            if url.startswith('-'):
                continue

            print(index, " - Retrieving PDF from:", url)
            save_pdf(url, filenum=str(index) if numeric_naming else None, run_headful=args.headful)
            index += 1

    # For retrieving from a text file of urls
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