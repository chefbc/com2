# /// script
# dependencies = [
#   "google-api-python-client",
#   "google-auth-oauthlib",
#   "requests",
# ]
# ///

"""
Google Drive Gallery Creator

Reads images from a Google Drive folder structure and creates a dynamic HTML gallery.

Folder Structure:
    Root Folder/
        Album 1/
            photo1.jpg
            photo2.jpg
        Album 2/
            photo3.jpg
            ...

Usage:
    uv run photos2.py --folder-id FOLDER_ID              # Create gallery from Drive folder
    uv run photos2.py --folder-name "My Photos"          # Find folder by name
    uv run photos2.py --folder-id FOLDER_ID --download  # Also download images
    uv run photos2.py --folder-id FOLDER_ID --output gallery.html  # Custom output file
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

# Google Drive API scopes
DRIVE_SCOPE = 'https://www.googleapis.com/auth/drive.readonly'
SCOPES = [DRIVE_SCOPE]

# Image MIME types
IMAGE_MIME_TYPES = [
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
    'image/bmp', 'image/tiff', 'image/svg+xml'
]

def get_credentials():
    """Get OAuth2 credentials for Google Drive"""
    creds = None
    token_file = 'token-drive.json'
    
    # Load existing token
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception:
            pass
    
    # If no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_drive_service():
    """Get Google Drive service"""
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)

def find_folder_by_name(service, folder_name):
    """Find a folder by name"""
    query = (
        f"name='{folder_name}' "
        "and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false"
    )
    
    results = service.files().list(
        q=query,
        fields='files(id, name)',
        pageSize=10
    ).execute()
    
    folders = results.get('files', [])
    if not folders:
        return None
    if len(folders) == 1:
        return folders[0]['id']
    
    # Multiple folders with same name
    print(f"Found {len(folders)} folders named '{folder_name}':")
    for i, folder in enumerate(folders, 1):
        print(f"  {i}. {folder['name']} (ID: {folder['id']})")
    return folders[0]['id']  # Return first one

def list_folders_in_folder(service, folder_id):
    """List all subfolders in a folder"""
    query = (
        f"'{folder_id}' in parents "
        "and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false"
    )
    
    folders = []
    page_token = None
    
    while True:
        try:
            response = service.files().list(
                q=query,
                fields='nextPageToken, files(id, name, modifiedTime)',
                pageSize=100,
                orderBy='name',
                pageToken=page_token
            ).execute()
            
            items = response.get('files', [])
            folders.extend(items)
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break
                
        except HttpError as error:
            print(f"Error listing folders: {error}")
            break
    
    return folders

def list_images_in_folder(service, folder_id):
    """List all image files in a folder"""
    query = (
        f"'{folder_id}' in parents "
        "and trashed=false "
        "and (mimeType='image/jpeg' or mimeType='image/jpg' or "
        "mimeType='image/png' or mimeType='image/gif' or "
        "mimeType='image/webp' or mimeType='image/bmp' or "
        "mimeType='image/tiff' or mimeType contains 'image/')"
    )
    
    images = []
    page_token = None
    
    while True:
        try:
            response = service.files().list(
                q=query,
                fields='nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink, thumbnailLink)',
                pageSize=100,
                orderBy='name',
                pageToken=page_token
            ).execute()
            
            items = response.get('files', [])
            images.extend(items)
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break
                
        except HttpError as error:
            print(f"Error listing files: {error}")
            break
    
    return images

def get_albums_with_images(service, root_folder_id):
    """Get all album folders and their images from root folder"""
    print(f"Scanning root folder for album folders...")
    
    # Get all subfolders (albums)
    album_folders = list_folders_in_folder(service, root_folder_id)
    
    if not album_folders:
        print("No subfolders found. Checking for images directly in root folder...")
        # If no subfolders, treat root as single album
        images = list_images_in_folder(service, root_folder_id)
        if images:
            return [{
                'id': root_folder_id,
                'name': 'Root Folder',
                'images': images
            }]
        return []
    
    print(f"✓ Found {len(album_folders)} album folder(s)\n")
    
    albums = []
    for i, folder in enumerate(album_folders, 1):
        print(f"Processing album {i}/{len(album_folders)}: {folder['name']}")
        images = list_images_in_folder(service, folder['id'])
        
        if images:
            albums.append({
                'id': folder['id'],
                'name': folder['name'],
                'images': images
            })
            print(f"  ✓ Found {len(images)} image(s)")
        else:
            print(f"  ⚠ No images found")
        print()
    
    return albums

def get_image_url(service, file_id):
    """Get a shareable URL for an image"""
    try:
        # Get file metadata
        file = service.files().get(
            fileId=file_id,
            fields='webContentLink, thumbnailLink'
        ).execute()
        
        # Try webContentLink first (direct download)
        if 'webContentLink' in file:
            return file['webContentLink'].replace('&export=download', '')
        
        # Fall back to thumbnail (smaller but works)
        if 'thumbnailLink' in file:
            return file['thumbnailLink']
        
        # Generate view link
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except Exception as e:
        print(f"Warning: Could not get URL for {file_id}: {e}")
        return f"https://drive.google.com/uc?export=view&id={file_id}"

def download_image(service, file_id, filename, output_dir):
    """Download an image file from Google Drive using the API"""
    try:
        filepath = Path(output_dir) / filename
        
        # Ensure unique filename
        counter = 1
        original_path = filepath
        while filepath.exists():
            name_part = original_path.stem
            ext = original_path.suffix
            filepath = Path(output_dir) / f"{name_part}_{counter}{ext}"
            counter += 1
        
        # Get credentials for authenticated download
        creds = service._http.credentials
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
        
        # Download using Drive API with alt=media parameter
        headers = {'Authorization': f'Bearer {creds.token}'}
        download_url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media'
        
        response = requests.get(download_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            # Got HTML instead of image - this shouldn't happen with proper auth
            print(f"      Warning: Received HTML instead of image for {filename}")
            return None
        
        # Write the file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify it's actually an image file
        import subprocess
        try:
            result = subprocess.run(['file', '-b', '--mime-type', str(filepath)], 
                                  capture_output=True, text=True, timeout=2)
            mime_type = result.stdout.strip().lower()
            if 'image' not in mime_type:
                print(f"      Warning: Downloaded file is not an image (got {mime_type})")
                filepath.unlink()
                return None
        except Exception:
            # file command not available, skip verification
            pass
        
        return str(filepath)
    except Exception as e:
        print(f"      Error downloading {filename}: {e}")
        return None

def create_gallery_html(albums, service, output_file='gallery.html', download_dir=None):
    """Create an HTML gallery from albums (each album contains images)"""
    print(f"Creating gallery HTML...")
    
    output_path = Path(output_file)
    output_dir = output_path.parent
    
    # Process all albums and images
    albums_data = []
    all_images_flat = []  # For lightbox navigation
    
    for album_idx, album in enumerate(albums, 1):
        print(f"Processing album {album_idx}/{len(albums)}: {album['name']}")
        
        album_images = []
        for img_idx, img in enumerate(album['images'], 1):
            print(f"  Image {img_idx}/{len(album['images'])}: {img['name']}")
            
            image_url = get_image_url(service, img['id'])
            
            # Download if requested
            local_path = None
            if download_dir:
                download_path = Path(download_dir).resolve()
                album_download_dir = download_path / album['name']
                album_download_dir.mkdir(parents=True, exist_ok=True)
                local_path = download_image(service, img['id'], img['name'], album_download_dir)
                if local_path:
                    # Calculate relative path from HTML file location to downloaded image
                    local_path_obj = Path(local_path).resolve()
                    output_dir_resolved = output_dir.resolve() if output_dir.exists() else output_dir
                    
                    try:
                        # Try to get relative path from HTML location to image
                        rel_path = local_path_obj.relative_to(output_dir_resolved)
                        image_url = f"./{rel_path}"
                    except ValueError:
                        # Paths are not in same directory tree
                        # Calculate path relative to download_dir, then from output_dir
                        rel_to_download = local_path_obj.relative_to(download_path)
                        # If output is in download_dir, use simple relative path
                        try:
                            output_relative_to_download = output_dir_resolved.relative_to(download_path)
                            # Image is at: download_dir/album/image
                            # HTML is at: output_dir (which might be download_dir or a subdir)
                            image_url = f"./{rel_to_download}"
                        except ValueError:
                            # Output is outside download_dir, need to go up
                            # Count how many levels up we need to go
                            download_name = download_path.name
                            image_url = f"./{download_name}/{rel_to_download}"
            
            image_data = {
                'id': img['id'],
                'name': img['name'],
                'url': image_url,
                'mime_type': img.get('mimeType', 'image/jpeg'),
                'modified': img.get('modifiedTime', ''),
                'size': img.get('size', '0'),
                'local_path': local_path,
                'album_name': album['name']
            }
            
            album_images.append(image_data)
            all_images_flat.append(image_data)
        
        albums_data.append({
            'id': album['id'],
            'name': album['name'],
            'images': album_images
        })
    
    total_images = sum(len(album['images']) for album in albums_data)
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Photo Gallery - {len(albums_data)} albums, {total_images} images</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
        }}
        
        .album-section {{
            margin-bottom: 40px;
        }}
        
        .album-header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .album-header h2 {{
            color: #333;
            margin-bottom: 5px;
        }}
        
        .album-header .count {{
            color: #666;
            font-size: 14px;
        }}
        
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .gallery-item {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        
        .gallery-item:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .gallery-item img {{
            width: 100%;
            height: 250px;
            object-fit: cover;
            display: block;
            background: #f0f0f0;
        }}
        
        .gallery-item img[src=""], .gallery-item img:not([src]) {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .error-message {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 20px auto;
            max-width: 800px;
            color: #856404;
        }}
        
        .error-message h3 {{
            margin-bottom: 10px;
            color: #856404;
        }}
        
        .error-message code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }}
        
        .gallery-item-info {{
            padding: 12px;
        }}
        
        .gallery-item-info .name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 4px;
            font-size: 14px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .gallery-item-info .meta {{
            font-size: 12px;
            color: #999;
        }}
        
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        
        .lightbox.active {{
            display: flex;
        }}
        
        .lightbox-content {{
            max-width: 90%;
            max-height: 90%;
            position: relative;
        }}
        
        .lightbox img {{
            max-width: 100%;
            max-height: 90vh;
            object-fit: contain;
        }}
        
        .lightbox-close {{
            position: absolute;
            top: -40px;
            right: 0;
            color: white;
            font-size: 30px;
            cursor: pointer;
            background: none;
            border: none;
            padding: 10px;
        }}
        
        .lightbox-nav {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 15px 20px;
            cursor: pointer;
            font-size: 24px;
            border-radius: 4px;
        }}
        
        .lightbox-nav:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .lightbox-prev {{
            left: 20px;
        }}
        
        .lightbox-next {{
            right: 20px;
        }}
        
        .lightbox-info {{
            position: absolute;
            bottom: -40px;
            left: 0;
            right: 0;
            text-align: center;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Photo Gallery</h1>
        <p>{len(albums_data)} albums • {total_images} images • Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div id="local-file-warning" class="error-message" style="display: none;">
        <h3>⚠️ Images Not Loading?</h3>
        <p>If images aren't showing, you may need to serve this page via HTTP instead of opening it directly.</p>
        <p>From the downloads directory, run:</p>
        <p><code>python3 -m http.server 8000</code></p>
        <p>Then open: <code>http://localhost:8000/gallery.html</code></p>
    </div>
    
    <div id="albums-container">
"""
    
    image_index = 0
    for album in albums_data:
        html_content += f"""        <div class="album-section">
            <div class="album-header">
                <h2>{album['name']}</h2>
                <div class="count">{len(album['images'])} image(s)</div>
            </div>
            <div class="gallery">
"""
        
        for img in album['images']:
            html_content += f"""                <div class="gallery-item" onclick="openLightbox({image_index})">
                    <img src="{img['url']}" alt="{img['name']}" loading="lazy" 
                         onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'250\\' height=\\'250\\'%3E%3Crect width=\\'250\\' height=\\'250\\' fill=\\'%23f0f0f0\\'/%3E%3Ctext x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\' font-size=\\'14\\' fill=\\'%23999\\'%3E{img['name']}%3C/text%3E%3Ctext x=\\'50%25\\' y=\\'60%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\' font-size=\\'12\\' fill=\\'%23ccc\\'%3ENot available%3C/text%3E%3C/svg%3E'; console.error('Failed to load:', '{img['url']}');">
                    <div class="gallery-item-info">
                        <div class="name">{img['name']}</div>
                        <div class="meta">{img['modified'][:10] if img['modified'] else ''}</div>
                    </div>
                </div>
"""
            image_index += 1
        
        html_content += """            </div>
        </div>
"""
    
    html_content += """    </div>
    
    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
        <button class="lightbox-nav lightbox-prev" onclick="changeImage(-1, event)">&larr;</button>
        <div class="lightbox-content">
            <img id="lightbox-img" src="" alt="">
            <div class="lightbox-info">
                <div id="lightbox-name"></div>
                <div id="lightbox-album"></div>
            </div>
        </div>
        <button class="lightbox-nav lightbox-next" onclick="changeImage(1, event)">&rarr;</button>
    </div>
    
    <script>
        const images = """ + json.dumps(all_images_flat) + """;
        let currentIndex = 0;
        
        function openLightbox(index) {
            currentIndex = index;
            updateLightbox();
            document.getElementById('lightbox').classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeLightbox(event) {
            if (!event || event.target.id === 'lightbox' || event.target.classList.contains('lightbox-close')) {
                document.getElementById('lightbox').classList.remove('active');
                document.body.style.overflow = '';
            }
        }
        
        function changeImage(direction, event) {
            event.stopPropagation();
            currentIndex += direction;
            if (currentIndex < 0) currentIndex = images.length - 1;
            if (currentIndex >= images.length) currentIndex = 0;
            updateLightbox();
        }
        
        function updateLightbox() {
            const img = images[currentIndex];
            document.getElementById('lightbox-img').src = img.url;
            document.getElementById('lightbox-name').textContent = img.name;
            document.getElementById('lightbox-album').textContent = img.album_name || '';
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (document.getElementById('lightbox').classList.contains('active')) {
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowLeft') changeImage(-1, {stopPropagation: () => {}});
                if (e.key === 'ArrowRight') changeImage(1, {stopPropagation: () => {}});
            }
        });
        
        // Check if images are loading (detect file:// protocol issues)
        window.addEventListener('load', function() {
            const images = document.querySelectorAll('.gallery-item img');
            let failedCount = 0;
            let checkedCount = 0;
            
            images.forEach(function(img) {
                img.addEventListener('error', function() {
                    failedCount++;
                    checkedCount++;
                    if (checkedCount === images.length && failedCount > 0) {
                        // Check if we're using file:// protocol
                        if (window.location.protocol === 'file:') {
                            document.getElementById('local-file-warning').style.display = 'block';
                        }
                    }
                });
                
                img.addEventListener('load', function() {
                    checkedCount++;
                    if (checkedCount === images.length && failedCount === 0) {
                        // All images loaded successfully
                        document.getElementById('local-file-warning').style.display = 'none';
                    }
                });
            });
        });
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Gallery created: {output_file}\n")
    return output_file

def main():
    parser = argparse.ArgumentParser(
        description='Create a gallery from images in a Google Drive folder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create gallery from root folder ID (scans subfolders as albums)
  uv run photos2.py --folder-id 1ABC123xyz789
  
  # Find root folder by name and create gallery
  uv run photos2.py --folder-name "My Photos"
  
  # Download images and create gallery with local images
  uv run photos2.py --folder-id 1ABC123xyz789 --download --output-dir ./images
  
  # Place HTML in download directory (ensures correct paths)
  uv run photos2.py --folder-id 1ABC123xyz789 --download --html-in-download-dir
  
  # Custom output file
  uv run photos2.py --folder-id 1ABC123xyz789 --output my-gallery.html

Folder Structure:
  The script expects:
    Root Folder/
      Album 1/ (subfolder)
        photo1.jpg
        photo2.jpg
      Album 2/ (subfolder)
        photo3.jpg
        ...

Getting Folder ID:
  - Open the root folder in Google Drive
  - The folder ID is in the URL: drive.google.com/drive/folders/FOLDER_ID
        """
    )
    parser.add_argument(
        '--folder-id',
        type=str,
        help='Google Drive folder ID'
    )
    parser.add_argument(
        '--folder-name',
        type=str,
        help='Find folder by name (uses first match)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='gallery.html',
        help='Output HTML file (default: gallery.html)'
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download images locally (creates ./downloads directory)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./downloads',
        help='Directory for downloaded images (default: ./downloads)'
    )
    parser.add_argument(
        '--html-in-download-dir',
        action='store_true',
        help='Place HTML file in download directory (ensures correct paths)'
    )
    
    args = parser.parse_args()
    
    if not args.folder_id and not args.folder_name:
        parser.error("Must specify either --folder-id or --folder-name")
    
    try:
        service = get_drive_service()
        
        # Get folder ID
        folder_id = args.folder_id
        if not folder_id and args.folder_name:
            print(f"Searching for folder: {args.folder_name}")
            folder_id = find_folder_by_name(service, args.folder_name)
            if not folder_id:
                print(f"✗ Folder '{args.folder_name}' not found")
                return
            print(f"✓ Found folder ID: {folder_id}\n")
        
        # Get albums (subfolders) and their images
        albums = get_albums_with_images(service, folder_id)
        
        if not albums:
            print("No albums or images found.")
            return
        
        total_images = sum(len(album['images']) for album in albums)
        print(f"{'='*60}")
        print(f"Summary: {len(albums)} album(s), {total_images} image(s) total")
        print(f"{'='*60}\n")
        
        # Prepare download directory if needed
        download_dir = None
        output_path = Path(args.output)
        
        if args.download:
            download_dir = Path(args.output_dir)
            download_dir.mkdir(parents=True, exist_ok=True)
            print(f"Images will be downloaded to: {download_dir.absolute()}")
            print(f"Each album will have its own subfolder.")
            
            # Option to place HTML in download directory
            if args.html_in_download_dir:
                output_path = download_dir / output_path.name
                print(f"HTML file will be placed in download directory: {output_path.absolute()}\n")
            elif download_dir.resolve() != output_path.parent.resolve():
                print(f"\nNote: HTML file will be at: {output_path.absolute()}")
                print(f"      Images will be at: {download_dir.absolute()}")
                print(f"      Use --html-in-download-dir to place HTML with images for correct paths.\n")
            else:
                print(f"HTML and images will be in the same directory.\n")
        
        # Create gallery
        create_gallery_html(albums, service, str(output_path), download_dir)
        
        print(f"{'='*60}")
        print("Gallery created successfully!")
        output_file_path = Path(args.output)
        if args.download and args.html_in_download_dir:
            output_file_path = Path(args.output_dir) / Path(args.output).name
        print(f"  HTML file: {output_file_path.absolute()}")
        if args.download:
            print(f"  Images: {download_dir.absolute()}")
            if not args.html_in_download_dir:
                print(f"\n  Tip: Use --html-in-download-dir to place HTML with images for correct paths.")
        print(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
