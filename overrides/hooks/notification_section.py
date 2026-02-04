"""
Hook to expose notification.md content and video to the home page context.
Reads docs/notification.md, strips front matter, converts markdown to HTML,
so the home page displays the 3-column section with images and optional video.
"""

import re
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

try:
    import markdown
except ImportError:
    markdown = None

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_front_matter(source: str):
    """Extract YAML front matter. Returns (meta_dict, content_without_front_matter)."""
    match = FRONT_MATTER_RE.match(source)
    if not match:
        return {}, source
    yaml_str = match.group(1).strip()
    content = source[match.end() :]
    if not yaml_str or yaml is None:
        return {}, content
    try:
        meta = yaml.safe_load(yaml_str)
        return meta if isinstance(meta, dict) else {}, content
    except Exception:
        return {}, content


def _markdown_to_html(content: str, config) -> str:
    """Convert markdown to HTML using extensions compatible with notification content."""
    if markdown is None:
        return content
    # md_in_html for markdown="1" in divs; attr_list for { .md-button .md-button--primary }
    extensions = ["md_in_html", "attr_list"]
    try:
        md = markdown.Markdown(extensions=extensions)
        return md.convert(content)
    except Exception:
        try:
            md = markdown.Markdown(extensions=[])
            return md.convert(content)
        except Exception:
            return content


def on_page_context(context, page, config, nav):
    """When building the home page context, add notification content (HTML) and video from notification.md."""
    if not page or not getattr(page, "file", None):
        return context
    src_path = getattr(page.file, "src_path", None)
    if src_path != "index.md":
        return context

    docs_dir = Path(config["docs_dir"])
    notification_path = docs_dir / "notification.md"
    if not notification_path.exists():
        return context

    try:
        raw = notification_path.read_text(encoding="utf-8")
    except Exception:
        return context

    meta, content = _parse_front_matter(raw)
    video = meta.get("video") if isinstance(meta, dict) else None
    if video and not isinstance(video, str):
        video = None

    html = _markdown_to_html(content.strip(), config)
    context["notification_content"] = html
    context["notification_video"] = video
    return context
