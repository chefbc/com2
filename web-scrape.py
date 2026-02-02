# /// script
# dependencies = [
#   "beautifulsoup4",
#   "requests"
# ]
# ///

"""
Web scraper: scrapes any site by input URL and page filter.
Example: url=specklessauto.com, filter=home,services -> homepage + /services.
Saves Markdown and assets under scrape/{hostname}/.
"""

import argparse
import re
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

# --- Defaults (used if no CLI args) ---
DEFAULT_URL = "https://specklessauto.com"
DEFAULT_PAGES = ["home", "services"]
SCRAPE_ROOT = Path(__file__).resolve().parent / "scrape"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# Set in main() from input URL (scrape/{hostname}/)
OUTPUT_DIR = SCRAPE_ROOT
ASSETS_DIR = SCRAPE_ROOT / "assets"


def normalize_url(url: str) -> tuple[str, str]:
    """Return (base_url with scheme, hostname for paths)."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    hostname = parsed.netloc or parsed.path.split("/")[0] or "site"
    base = f"{parsed.scheme or 'https'}://{hostname}"
    return base.rstrip("/") + "/", hostname


def page_filter_to_path(name: str) -> str:
    """Map filter name to URL path segment. 'home' -> '', rest -> name."""
    n = name.strip().lower()
    if n in ("home", "homepage", "index"):
        return ""
    return n


def build_pages(base_url: str, page_filter: list[str]) -> list[tuple[str, str]]:
    """Build (output_name, full_url) from base URL and page filter list."""
    pages = []
    for name in page_filter:
        path = page_filter_to_path(name)
        slug = name.strip().lower().replace(" ", "-")
        if not slug or slug in ("home", "homepage", "index"):
            slug = "home"
        full_url = urljoin(base_url, path) if path else base_url
        pages.append((slug, full_url))
    return pages


def ensure_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def safe_filename(url: str, suffix: str = "") -> str:
    """Generate a safe local filename from a URL."""
    parsed = urlparse(url)
    path = unquote(parsed.path).strip("/")
    if not path:
        path = hashlib.md5(url.encode()).hexdigest()[:12]
    # Keep only last path segment for readability, sanitize
    name = path.split("/")[-1] if "/" in path else path
    name = re.sub(r"[^\w.\-]", "_", name)
    if suffix and not name.lower().endswith(suffix.lower()):
        name = f"{name}{suffix}"
    return name or "asset"


def get_img_url(tag, base_url: str) -> str:
    """Resolve best image URL from img tag (src, data-src, data-lazy-src, srcset)."""
    for attr in ("src", "data-src", "data-lazy-src", "data-lazy-srcset"):
        val = tag.get(attr, "")
        if not val or val.startswith("data:"):
            continue
        # srcset can be "url 1x, url2 2x" or "url"
        if " " in val:
            val = val.strip().split()[0]
        url = urljoin(base_url, val.strip())
        if url.startswith(("http://", "https://")):
            return url.split("#")[0].split("?")[0]
    # srcset="url 1x, url2 2x"
    srcset = tag.get("srcset", "")
    if srcset:
        first = srcset.strip().split(",")[0].strip().split()[0]
        if first and not first.startswith("data:"):
            url = urljoin(base_url, first)
            if url.startswith(("http://", "https://")):
                return url.split("#")[0].split("?")[0]
    return ""


def download_asset(url: str, url_to_local: dict) -> str:
    """Download asset from URL to ASSETS_DIR; return local path. Dedupes by URL."""
    if not url or url.startswith("data:"):
        return ""
    url = url.split("#")[0].split("?")[0]
    if url in url_to_local:
        return url_to_local[url]
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        ext = ".bin"
        if "image/jpeg" in content_type or "image/jpg" in content_type:
            ext = ".jpg"
        elif "image/png" in content_type:
            ext = ".png"
        elif "image/gif" in content_type:
            ext = ".gif"
        elif "image/webp" in content_type:
            ext = ".webp"
        elif "image/svg" in content_type:
            ext = ".svg"
        base = safe_filename(url, ext)
        path = ASSETS_DIR / base
        # avoid overwrite
        if path.exists():
            base = f"{path.stem}_{hashlib.md5(url.encode()).hexdigest()[:6]}{path.suffix}"
            path = ASSETS_DIR / base
        path.write_bytes(r.content)
        local_ref = f"assets/{base}"
        url_to_local[url] = local_ref
        return local_ref
    except Exception as e:
        print(f"  [skip asset] {url}: {e}")
        return ""


def tag_to_markdown(tag, base_url: str, url_to_local: dict) -> str:
    """Convert a BeautifulSoup tag to markdown (recursive)."""
    if tag is None or not hasattr(tag, "name"):
        return ""
    name = getattr(tag, "name", None)
    if name is None:
        return str(tag) if isinstance(tag, str) else ""

    if isinstance(tag, str):
        return tag.strip()

    children = list(tag.children) if hasattr(tag, "children") else []
    inner = "".join(tag_to_markdown(c, base_url, url_to_local) for c in children).strip()

    if name == "h1":
        return f"\n# {inner}\n\n"
    if name == "h2":
        return f"\n## {inner}\n\n"
    if name == "h3":
        return f"\n### {inner}\n\n"
    if name == "h4":
        return f"\n#### {inner}\n\n"
    if name == "h5":
        return f"\n##### {inner}\n\n"
    if name == "h6":
        return f"\n###### {inner}\n\n"
    if name == "p":
        return f"\n{inner}\n\n" if inner else "\n"
    if name == "br":
        return "\n"
    if name == "strong" or name == "b":
        return f"**{inner}**"
    if name == "em" or name == "i":
        return f"*{inner}*"
    if name == "a":
        href = tag.get("href", "")
        if href:
            full = urljoin(base_url, href)
            return f"[{inner}]({full})"
        return inner
    if name == "img":
        img_url = get_img_url(tag, base_url)
        alt = tag.get("alt", "").strip() or "image"
        if img_url:
            local = download_asset(img_url, url_to_local)
            if local:
                return f"\n![{alt}]({local})\n\n"
        return ""
    if name == "ul":
        items = "".join(
            f"- {tag_to_markdown(li, base_url, url_to_local).strip()}\n"
            for li in tag.find_all("li", recursive=False)
        )
        return f"\n{items}\n" if items else "\n"
    if name == "ol":
        items = "".join(
            f"{i}. {tag_to_markdown(li, base_url, url_to_local).strip()}\n"
            for i, li in enumerate(tag.find_all("li", recursive=False), 1)
        )
        return f"\n{items}\n" if items else "\n"
    if name == "li":
        return inner
    if name in ("div", "span", "section", "article", "main", "header", "footer"):
        return inner
    if name == "hr":
        return "\n---\n\n"
    if name == "blockquote":
        lines = inner.strip().split("\n")
        return "\n".join(f"> {line}" for line in lines) + "\n\n"
    if name in ("script", "style", "nav"):
        return ""
    return inner


def get_main_content(soup: BeautifulSoup) -> BeautifulSoup:
    """Prefer main content area, else body."""
    for selector in ["main", "[role='main']", ".content", "#content", "article", "body"]:
        el = soup.select_one(selector)
        if el and el.get_text(strip=True):
            return el
    return soup.find("body") or soup


def collect_and_download_all_images(soup: BeautifulSoup, base_url: str, url_to_local: dict) -> None:
    """Scan entire document for img tags and download every image (handles lazy-load, sliders)."""
    for img in soup.find_all("img"):
        img_url = get_img_url(img, base_url)
        if img_url:
            download_asset(img_url, url_to_local)


def page_to_markdown(url: str, html: str, url_to_local: dict) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Download all images from full page first (slider, lazy-load, etc.)
    collect_and_download_all_images(soup, url, url_to_local)
    main = get_main_content(soup)
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    md = f"# {title}\n\nSource: {url}\n\n"
    md += tag_to_markdown(main, url, url_to_local)
    # collapse multiple newlines
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md + "\n"


def scrape_page(name: str, url: str, url_to_local: dict) -> None:
    print(f"Scraping: {name} -> {url}")
    html = fetch_html(url)
    md = page_to_markdown(url, html, url_to_local)
    out_file = OUTPUT_DIR / f"{name}.md"
    out_file.write_text(md, encoding="utf-8")
    print(f"  -> {out_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape a website by URL and page filter. Saves Markdown and assets to scrape/{hostname}/."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Base URL (e.g. specklessauto.com or https://specklessauto.com). Default: {DEFAULT_URL}",
    )
    parser.add_argument(
        "--pages",
        nargs="*",
        default=DEFAULT_PAGES,
        metavar="PAGE",
        help=f"Page filter: which paths to scrape. 'home' -> /, others -> /{{name}}. Default: {DEFAULT_PAGES}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Override output root (default: scrape/{hostname})",
    )
    args = parser.parse_args()

    base_url, hostname = normalize_url(args.url)
    global OUTPUT_DIR, ASSETS_DIR
    OUTPUT_DIR = (args.output or SCRAPE_ROOT / hostname).resolve()
    ASSETS_DIR = OUTPUT_DIR / "assets"

    pages = build_pages(base_url, args.pages)
    if not pages:
        print("No pages to scrape (empty --pages). Use e.g. --pages home services")
        return

    ensure_dirs()
    url_to_local = {}
    for name, url in pages:
        scrape_page(name, url, url_to_local)
    print(f"\nDone. Output: {OUTPUT_DIR}")
    print(f"Assets: {ASSETS_DIR} ({len(url_to_local)} files)")


if __name__ == "__main__":
    main()
