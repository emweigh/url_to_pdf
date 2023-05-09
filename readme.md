This script will download the given urls as pdf files, using Microsoft Playwright (Chromium). 

## Installation

The script has a dependency on [Playwright](https://playwright.dev/) and BeautifulSoup4, which can be installed using pip:

```bash
pip install playwright
playwright install
pip install bs4
```

## Usage

To download pages directly, run the script with urls as the arguments:

```bash
python download.py <url> <url> <url>...
```

### Downloading from urls in a file
To download pages from a file, run the script with the file as the argument:

```bash
python download.py -f <file>
```

The file should contain one url per line.


## Known issues

There's a bug where Playwright will get stuck on `browser.new_page()` if you have `DISPLAY` environment variable set with no X Server running. Clear the `DISPLAY` environment variable to fix this.



## Tips

If you download multiple PDF-files, and want to combine them into one, you can use the `poppler-utils` package, which contains the `pdfunite`:

```bash
pdfunite *.pdf output.pdf
```

Or if you're on macOS, you can use the built-in `sips` tool:

```bash
sips -s format pdf *.pdf --out combined.pdf
```