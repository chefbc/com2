"""
Hook to generate gallery content from images in docs/downloads/

This works around the mkdocs-image-gallery-plugin bug (issue #3) where
images aren't being recognized/loaded.

Uses on_page_content to inject HTML after Markdown rendering so mkdocs-glightbox
can properly process the data-glightbox attributes.
"""

import os
from pathlib import Path
from typing import Dict, List

try:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.pages import Page
except ImportError:
    # Fallback if imports fail
    MkDocsConfig = None
    Page = None


def get_gallery_images(docs_dir: str, image_folder: str = "downloads") -> Dict[str, List[Dict]]:
    """
    Scan the downloads folder and organize images by album (subfolder)
    
    Returns:
        Dictionary with album names as keys and lists of image info as values
    """
    downloads_path = Path(docs_dir) / image_folder
    
    if not downloads_path.exists():
        return {}
    
    albums = {}
    
    # Get all subdirectories (albums)
    for album_dir in downloads_path.iterdir():
        if album_dir.is_dir() and not album_dir.name.startswith('.'):
            album_name = album_dir.name
            images = []
            
            # Get all image files in this album
            for img_file in album_dir.iterdir():
                if img_file.is_file():
                    ext = img_file.suffix.lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']:
                        # Get relative path from docs/ for use in markdown
                        rel_path = img_file.relative_to(Path(docs_dir))
                        # Convert to forward slashes
                        img_path = str(rel_path).replace('\\', '/')
                        images.append({
                            'name': img_file.name,
                            'path': img_path,  # e.g., "downloads/gallery1/1.png"
                            'album': album_name
                        })
            
            if images:
                albums[album_name] = sorted(images, key=lambda x: x['name'])
    
    return albums


def on_page_context(context, page, config, nav):
    """
    For the home page, provide gallery images for the gallery_scroller section
    (two rows: row1 scrolls left, row2 scrolls right).
    Limits total images and tries to represent all galleries (round-robin).
    """
    if not page or not getattr(page, "file", None):
        return context
    if getattr(page.file, "src_path", None) != "index.md":
        return context

    context["gallery_url"] = "gallery/"
    docs_dir = config.docs_dir
    albums = get_gallery_images(docs_dir, "downloads")

    # Max total images in scroller (split between two rows)
    max_scroller_images = 16

    # Build list by taking from each gallery in turn so all galleries are represented
    flat = []
    sorted_albums = sorted(albums.items())
    if not sorted_albums:
        context["gallery_scroller_row1"] = []
        context["gallery_scroller_row2"] = []
        return context

    # Round-robin: take one image from each album in turn until we have max_scroller_images.
    # Skip any image we've already added so the scroller has no duplicates.
    seen_paths = set()
    indices = {name: 0 for name, _ in sorted_albums}
    while len(flat) < max_scroller_images:
        round_added = 0
        for album_name, images in sorted_albums:
            if len(flat) >= max_scroller_images:
                break
            i = indices[album_name]
            while i < len(images):
                img = images[i]
                path = img["path"]
                if path in seen_paths:
                    i += 1
                    indices[album_name] = i
                    continue
                seen_paths.add(path)
                indices[album_name] = i + 1
                url = "/" + path if not path.startswith("/") else path
                flat.append({"path": path, "name": img["name"], "url": url})
                round_added += 1
                break
            else:
                indices[album_name] = len(images)
        if round_added == 0:
            break

    mid = (len(flat) + 1) // 2
    context["gallery_scroller_row1"] = flat[:mid]
    context["gallery_scroller_row2"] = flat[mid:]
    return context


def on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files):
    """
    Replace gallery shortcodes with placeholders that will be replaced in on_page_content.
    We use placeholders here because we need to inject HTML after Markdown rendering
    so mkdocs-glightbox can process it properly.
    """
    # Only process gallery.md
    if page.file.src_path != 'gallery.md':
        return markdown
    
    # Replace shortcodes with unique placeholders that won't be processed by Markdown
    markdown = markdown.replace('{{gallery_html}}', '<!-- GALLERY_HTML_PLACEHOLDER -->')
    markdown = markdown.replace('{{gallery_preview}}', '<!-- GALLERY_HTML_PLACEHOLDER -->')
    markdown = markdown.replace('{{youtube_gallery}}', '<!-- YOUTUBE_GALLERY_PLACEHOLDER -->')
    
    return markdown


def on_page_content(html: str, *, page: Page, config: MkDocsConfig, files):
    """
    Replace gallery placeholders with actual gallery HTML after Markdown rendering.
    Using on_page_content so HTML is available when glightbox's JavaScript runs.
    """
    # Only process gallery.md
    if page.file.src_path != 'gallery.md':
        return html
    
    # Check if we have a placeholder to replace
    if 'GALLERY_HTML_PLACEHOLDER' not in html and 'YOUTUBE_GALLERY_PLACEHOLDER' not in html:
        return html
    
    docs_dir = config.docs_dir
    albums = get_gallery_images(docs_dir, "downloads")
    
    if not albums:
        # No images found
        html = html.replace('<!-- GALLERY_HTML_PLACEHOLDER -->', '<p>No images found in gallery.</p>')
        html = html.replace('<!-- YOUTUBE_GALLERY_PLACEHOLDER -->', '')
        return html
    
    # Generate gallery HTML
    total_images = sum(len(imgs) for imgs in albums.values())
    
    gallery_html = f"""
<div class="gallery-container">
    <div class="gallery-header">
        <h2>Photo Gallery</h2>
        <p>{len(albums)} album(s) • {total_images} image(s)</p>
    </div>
"""
    
    # Generate gallery for each album
    for album_name, images in sorted(albums.items()):
        # Escape album name for HTML attribute
        album_name_escaped = album_name.replace("'", "&#39;").replace('"', "&quot;")
        
        gallery_html += f"""
    <div class="album-section">
        <h3>{album_name}</h3>
        <div class="gallery-grid">
"""
        
        for img in images:
            # Use absolute path from site root to avoid relative path issues
            # The page might be at /gallery/ but images should be at /downloads/...
            # So we need absolute paths starting with /
            img_path = img['path']  # e.g., "downloads/gallery1/1.png"
            
            # Use absolute path from site root
            # MkDocs serves files from docs/ at the site root
            # So "downloads/gallery1/1.png" becomes "/downloads/gallery1/1.png"
            # The site_url base path is handled by MkDocs automatically
            img_url = '/' + img_path if not img_path.startswith('/') else img_path
            
            # Escape for HTML
            img_url_escaped = img_url.replace("'", "&#39;").replace('"', "&quot;")
            img_name_escaped = img['name'].replace("'", "&#39;").replace('"', "&quot;")
            
            # Use anchor tags with data-glightbox - this is the format glightbox expects
            # The href points to the full-size image, and data-gallery groups them
            # Adding 'glightbox' class to ensure mkdocs-glightbox detects it
            gallery_html += f"""
            <div class="gallery-item">
                <a href="{img_url_escaped}" class="glightbox" data-glightbox data-gallery="{album_name_escaped}" data-title="{img_name_escaped}">
                    <img src="{img_url_escaped}" alt="{img_name_escaped}" loading="lazy" 
                         onerror="console.error('Failed to load:', '{img_url_escaped}');">
                </a>
                <div class="gallery-caption">{img_name_escaped}</div>
            </div>
"""
        
        gallery_html += """
        </div>
    </div>
"""
    
    gallery_html += """
</div>

<style>
.gallery-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.gallery-header {
    text-align: center;
    margin-bottom: 30px;
}

.gallery-header h2 {
    margin-bottom: 10px;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.gallery-item {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.gallery-item:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.gallery-item img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
}

.gallery-caption {
    padding: 8px;
    font-size: 12px;
    color: #666;
    text-align: center;
    background: white;
}

.album-section {
    margin-bottom: 40px;
}

.album-section h3 {
    margin-bottom: 20px;
    color: #333;
}
</style>

<script>
// Ensure glightbox processes our gallery images
// mkdocs-glightbox should auto-detect links with class="glightbox" or data-glightbox
// Our HTML is injected via on_page_content, so it's in the DOM when glightbox initializes
(function() {
    // Wait for glightbox to be available and DOM to be ready
    function initGallery() {
        if (typeof window.GLightbox === 'undefined') {
            setTimeout(initGallery, 100);
            return;
        }
        
        const galleryLinks = document.querySelectorAll('.gallery-item a.glightbox[data-glightbox]');
        console.log('Gallery: Found', galleryLinks.length, 'gallery links');
        
        // GLightbox should automatically detect these links
        // If it doesn't work, mkdocs-glightbox might need to be configured differently
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGallery);
    } else {
        initGallery();
    }
    
    // Also try after a delay to ensure glightbox has fully initialized
    setTimeout(initGallery, 1000);
})();
</script>
"""
    
    # Replace placeholders
    html = html.replace('<!-- GALLERY_HTML_PLACEHOLDER -->', gallery_html)
    html = html.replace('<!-- YOUTUBE_GALLERY_PLACEHOLDER -->', '')
    
    return html
