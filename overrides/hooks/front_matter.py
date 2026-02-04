"""
Hook to parse YAML front matter from markdown pages and inject into page.meta.
Supports video and other metadata for use in templates (e.g. notification page).
"""

import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None

# Cache: src_path -> parsed front matter (merged into page.meta in on_page_context)
_front_matter_cache: Dict[str, Dict[str, Any]] = {}

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_front_matter(markdown: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Extract YAML front matter from the start of markdown. Returns (meta_dict, rest_content)."""
    match = FRONT_MATTER_RE.match(markdown)
    if not match:
        return None, markdown
    yaml_str = match.group(1).strip()
    content = markdown[match.end() :]
    if not yaml_str:
        return {}, content
    if yaml is None:
        return {}, content
    try:
        meta = yaml.safe_load(yaml_str)
        return meta if isinstance(meta, dict) else {}, content
    except Exception:
        return {}, content


def on_page_markdown(markdown: str, *, page, config, files):
    """Strip YAML front matter and cache it for this page."""
    global _front_matter_cache
    meta, content = _parse_front_matter(markdown)
    if meta is not None:
        _front_matter_cache[page.file.src_path] = meta
        return content
    return markdown


def on_page_context(context, page, config, nav):
    """Merge cached front matter into page.meta for template access."""
    global _front_matter_cache
    src_path = page.file.src_path
    if src_path in _front_matter_cache:
        meta = _front_matter_cache.pop(src_path)
        if not hasattr(page, "meta"):
            page.meta = {}
        if isinstance(page.meta, dict):
            page.meta.update(meta)
        context["page"] = page
    return context
