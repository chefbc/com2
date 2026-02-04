# /// script
# dependencies = [
#   "requests",
# ]
# ///
"""
Download car detailing photos from Pexels.com into docs/downloads for the gallery.

Uses the Pexels API (https://www.pexels.com/api/documentation/#photos-search).
All Pexels content is free to use. Requires a Pexels API key from
https://www.pexels.com/api/

Usage:
  python download.py --api-key YOUR_KEY
  python download.py --api-key YOUR_KEY --num-galleries 3 --images-per-gallery 10
  PEXELS_API_KEY=YOUR_KEY python download.py --num-galleries 2
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
DEFAULT_QUERY = "car detailing"
DEFAULT_DOWNLOADS = Path(__file__).resolve().parent / "docs" / "downloads"
MAX_PER_PAGE = 80


def sanitize_filename(name: str) -> str:
    """Make a safe filename from a string."""
    name = re.sub(r"[^\w\s\-.]", "", name)
    name = re.sub(r"[-\s]+", "-", name).strip(".-")
    return name or "image"


def search_pexels(api_key: str, query: str, per_page: int = 80, page: int = 1) -> dict:
    """Search Pexels for photos. Returns JSON response."""
    resp = requests.get(
        PEXELS_SEARCH_URL,
        headers={"Authorization": api_key},
        params={"query": query, "per_page": per_page, "page": page},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def download_image(url: str, path: Path) -> bool:
    """Download image from URL to path. Returns True on success."""
    try:
        r = requests.get(url, timeout=60, stream=True)
        r.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  Failed to download {url}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download car detailing photos from Pexels into docs/downloads galleries."
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("PEXELS_API_KEY"),
        help="Pexels API key (or set PEXELS_API_KEY)",
    )
    parser.add_argument(
        "--num-galleries",
        type=int,
        default=2,
        metavar="N",
        help="Number of gallery folders to create (default: 2)",
    )
    parser.add_argument(
        "--images-per-gallery",
        type=int,
        default=6,
        metavar="N",
        help="Number of images per gallery (default: 6)",
    )
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help=f"Search query (default: {DEFAULT_QUERY!r})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_DOWNLOADS,
        help="Base directory for galleries (default: docs/downloads)",
    )
    parser.add_argument(
        "--size",
        choices=["original", "large2x", "large", "medium", "small"],
        default="medium",
        help="Image size to download (default: medium)",
    )
    args = parser.parse_args()

    if not args.api_key:
        print(
            "Error: Pexels API key required. Set PEXELS_API_KEY or use --api-key.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.num_galleries < 1 or args.images_per_gallery < 1:
        print("Error: --num-galleries and --images-per-gallery must be >= 1.", file=sys.stderr)
        sys.exit(1)

    args.output_dir = args.output_dir.resolve()
    print(f"Output: {args.output_dir}")
    print(f"Query: {args.query!r}")
    print(f"Galleries: {args.num_galleries}, images per gallery: {args.images_per_gallery}")
    print()

    # Collect enough photo URLs from Pexels (paginate if needed)
    all_photos = []
    page = 1
    needed = args.num_galleries * args.images_per_gallery

    while len(all_photos) < needed:
        data = search_pexels(
            args.api_key,
            args.query,
            per_page=min(MAX_PER_PAGE, needed - len(all_photos) + 10),
            page=page,
        )
        photos = data.get("photos") or []
        if not photos:
            break
        all_photos.extend(photos)
        if len(photos) < MAX_PER_PAGE:
            break
        page += 1
        time.sleep(0.3)  # be nice to the API

    if len(all_photos) < needed:
        print(
            f"Warning: Only {len(all_photos)} results found; requested {needed}. "
            "Some galleries may have fewer images.",
            file=sys.stderr,
        )

    # Split photos across galleries and download
    idx = 0
    for g in range(1, args.num_galleries + 1):
        gallery_dir = args.output_dir / f"gallery{g}"
        gallery_dir.mkdir(parents=True, exist_ok=True)
        print(f"Gallery {g}: {gallery_dir}")

        for i in range(args.images_per_gallery):
            if idx >= len(all_photos):
                break
            photo = all_photos[idx]
            idx += 1
            src = photo.get("src") or {}
            url = src.get(args.size) or src.get("medium") or src.get("original")
            if not url:
                continue
            ext = "jpg"
            if ".png" in url.lower():
                ext = "png"
            alt = (photo.get("alt") or str(photo.get("id", ""))).strip()
            safe = sanitize_filename(alt)[:50] or f"pexels-{photo.get('id', idx)}"
            filename = f"{safe}.{ext}"
            # avoid overwrite
            path = gallery_dir / filename
            n = 1
            while path.exists():
                path = gallery_dir / f"{safe}-{n}.{ext}"
                n += 1
            if download_image(url, path):
                print(f"  {path.name}")
            time.sleep(0.2)

        print()

    print("Done. Photos from Pexels are free to use; consider crediting photographers.")


if __name__ == "__main__":
    main()
