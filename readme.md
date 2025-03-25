## Revisions from @emweigh

1. Rewrote argument handling to use argparse module
2. Added argument/flag to run in headful mode
3. Rewrote numeric naming so that it includes actual filename, i.e. "NUM - ORIGINAL_FILENAME.pdf"
4. Added a text file with test URLs for generating PDFs

### Future ToDo:
- [ ] Implement a PDF generator with nicer formatting.
- [ ] [STRETCH] Evaluate if webpage has print button; if so, print document and save that as PDF
- [ ] [STRETCH] Evaluate if URL points to PDF or non-PDF/html (e.g. .DOCX); if so, save document as is instead of generating PDF

##

This script will download the given urls as pdf files, using Microsoft Playwright (Chromium).

## Installation

The script has a dependency on [Playwright](https://playwright.dev/) and [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/), which can be installed using pip:

```bash
pip install playwright
playwright install
pip install beautifulsoup4
```

## Usage

**NOTE: You might have to add `https://` to the start of the urls!**

To download pages directly, run the script with urls as the arguments:

```bash
python url_to_pdf.py <url> <url> <url>...
```

### Downloading from urls in a file

To download pages from a file, run the script with the file as the argument:

```bash
python url_to_pdf.py -f <file>
```

The file should contain one url per line.

### Downloading multiple files using numeric names

Maybe you want to download a bunch of pages as pdfs, and then combine them into a single large pdf file (see tips for suggestions on how to combine them), so you can read a bunch of articles while you're stuck on a plane without internet.

You can use the `-n` flag to specify that the script should save the urls using sequential numbers as the names. Ex. `0001.pdf`, `0002.pdf`, `0003.pdf` etc.

```bash
python url_to_pdf.py -n <url> <url> <url>...
```

Or

```bash
python url_to_pdf.py -n -f <file>
```

## Known issues

There's a bug where Playwright will get stuck on `browser.new_page()` if you have `DISPLAY` environment variable set with no X Server running. Clear the `DISPLAY` environment variable to fix this.

## Tips

If you download multiple PDF-files, and want to combine them into one, you can use the `poppler-utils` package, which contains the `pdfunite` tool:

```bash
pdfunite *.pdf output.pdf
```

Or if you're on macOS, you can use the built-in `sips` tool. Though my understanding is that sips is not specifically designed for combining PDFs, so there may be some limitations or issues with certain PDF files.

```bash
sips -s format pdf *.pdf --out combined.pdf
```
