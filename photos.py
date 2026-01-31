# /// script
# dependencies = [
#   "google-api-python-client",
#   "google-auth-httplib2",
#   "google-auth-oauthlib",
#   "requests"
# ]
# ///

"""
Google Photos Data Fetcher

This script supports two modes for accessing Google Photos:

1. Picker API (--mode picker): Interactive selection in browser
   - User selects photos through a browser interface
   - Recommended for accessing full photo library
   - Cannot programmatically select entire albums

2. Library API (--mode library): Programmatic access to albums
   - List all albums
   - Get all photos from a specific album by ID or title
   - May be limited to app-created content after March 2025

IMPORTANT LIMITATIONS:
- Service accounts are NOT supported. OAuth2 with a user account is required.
- After March 2025, Library API primarily works with app-created content only.
- Picker API does not support programmatic album selection.

Requirements:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests

Setup:
    1. Create OAuth2 credentials in Google Cloud Console
    2. Enable Google Photos Picker API and/or Photos Library API
    3. Download credentials JSON file
    4. Set GOOGLE_PHOTOS_CREDENTIALS environment variable or use --credentials flag
"""

import json
import os
import sys
import time
import webbrowser
import datetime
from typing import List, Dict, Optional
import argparse

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import requests
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Warning: Required libraries not installed. Install with:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests")


# Google Photos API scopes
PICKER_SCOPE = 'https://www.googleapis.com/auth/photospicker.mediaitems.readonly'
LIBRARY_SCOPE = 'https://www.googleapis.com/auth/photoslibrary.readonly'  # For programmatic album access

# API endpoints
SESSION_CREATE_URL = "https://photospicker.googleapis.com/v1/sessions"
SESSION_GET_URL = "https://photospicker.googleapis.com/v1/sessions/{sessionId}"
MEDIA_ITEMS_LIST_URL = "https://photospicker.googleapis.com/v1/mediaItems"
SESSION_DELETE_URL = "https://photospicker.googleapis.com/v1/sessions/{sessionId}"


class GooglePhotosPickerFetcher:
    """Fetches photos from Google Photos using the Picker API"""
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize Google Photos Picker API client
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token (default: token.json)
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_PHOTOS_CREDENTIALS')
        self.token_path = token_path or os.getenv('GOOGLE_PHOTOS_TOKEN', 'token.json')
        self.credentials = None
        
        if not GOOGLE_API_AVAILABLE:
            print("Error: Required libraries not available")
            return
        
        if not self.credentials_path:
            print("Warning: No credentials path provided. Set GOOGLE_PHOTOS_CREDENTIALS or use --credentials")
            return
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Photos Picker API using OAuth2"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, [PICKER_SCOPE])
                # Check if token has the required scope
                if creds and creds.valid:
                    token_scopes = set(creds.scopes if creds.scopes else [])
                    if PICKER_SCOPE not in token_scopes:
                        print(f"Token has different scopes. Re-authenticating...")
                        print(f"  Token scopes: {token_scopes}")
                        print(f"  Required scope: {PICKER_SCOPE}")
                        creds = None
                        try:
                            os.remove(self.token_path)
                        except Exception:
                            pass
            except Exception as e:
                print(f"Warning: Could not load token from {self.token_path}: {e}")
                creds = None
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Warning: Could not refresh token: {e}")
                    print("Re-authenticating with new scope...")
                    creds = None
                    try:
                        if os.path.exists(self.token_path):
                            os.remove(self.token_path)
                    except Exception:
                        pass
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    print(f"Error: Credentials file not found: {self.credentials_path}")
                    return
                
                try:
                    print(f"Requesting authorization with scope: {PICKER_SCOPE}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, [PICKER_SCOPE])
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error: Could not authenticate: {e}")
                    print("\nTroubleshooting:")
                    print("1. Make sure Google Photos Picker API is enabled in Google Cloud Console")
                    print("2. Add the scope to your OAuth consent screen:")
                    print(f"   {PICKER_SCOPE}")
                    print("3. If testing, add your email as a test user")
                    return
            
            # Save the credentials for the next run
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Warning: Could not save token: {e}")
        
        self.credentials = creds
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers with current token"""
        if not self.credentials:
            raise ValueError("Not authenticated. Run authentication first.")
        
        # Refresh token if needed
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
        
        return {"Authorization": f"Bearer {self.credentials.token}"}
    
    def create_session(self, max_item_count: int = 100) -> Dict:
        """
        Create a new picker session
        
        Args:
            max_item_count: Maximum number of items user can select (max 2000)
            
        Returns:
            Session dictionary with sessionId, pickerUri, etc.
        """
        headers = self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        body = {
            "pickingConfig": {
                "maxItemCount": str(min(max_item_count, 2000))  # API expects string in int64 format, max is 2000
            }
        }
        
        try:
            response = requests.post(SESSION_CREATE_URL, json=body, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Debug: print response if id is missing (API uses "id" not "sessionId")
            if "id" not in result:
                print(f"Warning: Response missing id. Full response: {json.dumps(result, indent=2)}")
            
            return result
        except requests.exceptions.HTTPError as e:
            print(f"Error creating session: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Response text: {e.response.text}")
            
            if hasattr(e, 'response') and e.response and e.response.status_code == 403:
                print("\nTroubleshooting 403 error:")
                print("1. Verify Google Photos Picker API is enabled:")
                print("   https://console.cloud.google.com/apis/library/photospicker.googleapis.com")
                print("2. Add scope to OAuth consent screen:")
                print(f"   {PICKER_SCOPE}")
                print("3. If in testing mode, add your email as a test user")
                print("4. Delete token.json and re-authenticate")
            raise
        except Exception as e:
            print(f"Unexpected error creating session: {e}")
            raise
    
    def poll_session(self, session_id: str) -> Dict:
        """
        Poll session status to check if user has selected items
        
        Args:
            session_id: The session ID to poll
            
        Returns:
            Session status dictionary
        """
        headers = self._get_auth_headers()
        url = SESSION_GET_URL.format(sessionId=session_id)
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error polling session: {e}")
            raise
    
    def list_media_items(self, session_id: str, page_size: int = 50, page_token: Optional[str] = None) -> Dict:
        """
        List media items selected in a session
        
        Args:
            session_id: The session ID
            page_size: Number of items per page (max 50)
            page_token: Token for pagination
            
        Returns:
            Dictionary with mediaItems list and nextPageToken
        """
        headers = self._get_auth_headers()
        params = {
            "sessionId": session_id,
            "pageSize": min(page_size, 50)  # API max is 50
        }
        if page_token:
            params["pageToken"] = page_token
        
        try:
            response = requests.get(MEDIA_ITEMS_LIST_URL, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error listing media items: {e}")
            raise
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            True if successful
        """
        headers = self._get_auth_headers()
        url = SESSION_DELETE_URL.format(sessionId=session_id)
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Warning: Could not delete session: {e}")
            return False
    
    def pick_photos(self, max_item_count: int = 100, timeout: int = 300, auto_open: bool = True) -> List[Dict]:
        """
        Complete flow: create session, open picker, wait for selection, return items
        
        Args:
            max_item_count: Maximum number of items user can select
            timeout: Maximum time to wait for user selection (seconds)
            auto_open: If True, automatically open picker in browser
            
        Returns:
            List of selected media item dictionaries
        """
        if not self.credentials:
            raise ValueError("Not authenticated")
        
        # Create session
        print("Creating picker session...")
        session = self.create_session(max_item_count)
        
        # Check for required fields - API returns "id" not "sessionId"
        if "id" not in session:
            print(f"Error: Session creation failed. Response: {json.dumps(session, indent=2)}")
            raise ValueError("Session creation did not return id")
        
        session_id = session["id"]
        
        if "pickerUri" not in session:
            print(f"Error: Session missing pickerUri. Response: {json.dumps(session, indent=2)}")
            raise ValueError("Session creation did not return pickerUri")
        
        picker_uri = session["pickerUri"]
        polling_config = session.get("pollingConfig", {})
        # Parse pollInterval (comes as "5s" string, need to extract number)
        poll_interval_str = polling_config.get("pollInterval", "2s")
        try:
            # Remove "s" suffix and convert to int
            poll_interval = int(poll_interval_str.rstrip("s"))
        except (ValueError, AttributeError):
            poll_interval = 2  # Default 2 seconds
        
        print(f"Session created: {session_id}")
        print(f"Opening picker in browser...")
        print(f"Picker URI: {picker_uri}")
        
        if auto_open:
            webbrowser.open(picker_uri)
        else:
            print(f"\nPlease open this URL in your browser:\n{picker_uri}\n")
        
        # Poll for completion
        print(f"Waiting for you to select photos (timeout: {timeout}s)...")
        print("Select photos in the browser, then this script will retrieve them.")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(poll_interval)
            status = self.poll_session(session_id)
            
            if status.get("mediaItemsSet"):
                print("Photos selected! Retrieving items...")
                break
            
            if status.get("expireTime"):
                # Check if expired
                expire_time = datetime.datetime.fromisoformat(status["expireTime"].replace('Z', '+00:00'))
                if expire_time < datetime.datetime.now(expire_time.tzinfo):
                    print("Session expired")
                    self.delete_session(session_id)
                    return []
        else:
            print(f"Timeout waiting for photo selection")
            self.delete_session(session_id)
            return []
        
        # Get all selected items
        all_items = []
        page_token = None
        
        while True:
            result = self.list_media_items(session_id, page_size=50, page_token=page_token)
            if "mediaItems" in result:
                all_items.extend(result["mediaItems"])
            
            page_token = result.get("nextPageToken")
            if not page_token:
                break
        
        # Clean up session
        self.delete_session(session_id)
        
        print(f"Retrieved {len(all_items)} media item(s)")
        return all_items


class GooglePhotosLibraryFetcher:
    """
    Fetches albums and photos using the Library API (for programmatic access)
    
    Note: Service accounts are NOT supported. OAuth2 with a user account is required.
    After March 2025, this API primarily works with app-created content only.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize Google Photos Library API client
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token (default: token-library.json)
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_PHOTOS_CREDENTIALS')
        self.token_path = token_path or os.getenv('GOOGLE_PHOTOS_LIBRARY_TOKEN', 'token-library.json')
        self.credentials = None
        self.service = None
        
        if not GOOGLE_API_AVAILABLE:
            print("Error: Required libraries not available")
            return
        
        if not self.credentials_path:
            print("Warning: No credentials path provided. Set GOOGLE_PHOTOS_CREDENTIALS or use --credentials")
            return
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Photos Library API using OAuth2"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, [LIBRARY_SCOPE])
                if creds and creds.valid:
                    token_scopes = set(creds.scopes if creds.scopes else [])
                    if LIBRARY_SCOPE not in token_scopes:
                        print(f"Token has different scopes. Re-authenticating...")
                        creds = None
                        try:
                            os.remove(self.token_path)
                        except Exception:
                            pass
            except Exception as e:
                print(f"Warning: Could not load token from {self.token_path}: {e}")
                creds = None
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Warning: Could not refresh token: {e}")
                    creds = None
                    try:
                        if os.path.exists(self.token_path):
                            os.remove(self.token_path)
                    except Exception:
                        pass
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    print(f"Error: Credentials file not found: {self.credentials_path}")
                    return
                
                try:
                    print(f"Requesting authorization with scope: {LIBRARY_SCOPE}")
                    print("\nIMPORTANT: Make sure this scope is added to your OAuth consent screen!")
                    print("If you see a warning about unverified scopes, that's normal for testing.")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, [LIBRARY_SCOPE])
                    creds = flow.run_local_server(port=0)
                    
                    # Verify the granted scopes
                    if creds and creds.scopes:
                        print(f"\nGranted scopes: {creds.scopes}")
                        if LIBRARY_SCOPE not in creds.scopes:
                            print(f"ERROR: Required scope {LIBRARY_SCOPE} was not granted!")
                            print("This usually means the scope is not configured in OAuth consent screen.")
                            return None
                except Exception as e:
                    print(f"Error: Could not authenticate: {e}")
                    print("\nTroubleshooting:")
                    print("1. Enable Google Photos Library API in Google Cloud Console")
                    print("2. Add scope to OAuth consent screen:")
                    print(f"   {LIBRARY_SCOPE}")
                    print("3. If testing, add your email as a test user")
                    return
            
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Warning: Could not save token: {e}")
        
        self.credentials = creds
        
        # Verify token has correct scope
        if creds and creds.scopes:
            token_scopes = set(creds.scopes)
            if LIBRARY_SCOPE not in token_scopes:
                print(f"Warning: Token scopes: {token_scopes}")
                print(f"Required scope: {LIBRARY_SCOPE}")
                print("Token may not have the correct scope. Try deleting token-library.json and re-authenticating.")
        
        # Build the service
        try:
            try:
                self.service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
            except Exception:
                self.service = build('photoslibrary', 'v1', credentials=creds)
        except Exception as e:
            print(f"Error: Could not build Photos Library API service: {e}")
            print("Note: Make sure Google Photos Library API is enabled in your project")
    
    def get_albums(self, page_size: int = 50) -> List[Dict]:
        """
        Get all albums from Google Photos
        
        Args:
            page_size: Number of albums per page (max 50)
            
        Returns:
            List of album dictionaries
        """
        if not self.service:
            raise ValueError("Library API not initialized")
        
        # Debug: Check token scopes before making request
        if self.credentials and self.credentials.scopes:
            print(f"Debug: Token scopes: {self.credentials.scopes}")
            if LIBRARY_SCOPE not in self.credentials.scopes:
                print(f"Warning: Required scope {LIBRARY_SCOPE} not found in token!")
                print("The token may have been created before the scope was added to OAuth consent screen.")
                print("Please delete token-library.json and re-authenticate.")
        
        albums = []
        page_token = None
        
        try:
            while True:
                params = {'pageSize': min(page_size, 50)}
                if page_token:
                    params['pageToken'] = page_token
                
                response = self.service.albums().list(**params).execute()
                
                if 'albums' in response:
                    albums.extend(response['albums'])
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            return albums
        except HttpError as error:
            print(f"Error fetching albums: {error}")
            if error.resp.status == 403:
                print("\n" + "="*60)
                print("403 Error: Insufficient Authentication Scopes")
                print("="*60)
                
                # Check if this is the deprecated scope issue
                error_details = str(error)
                if "insufficient authentication scopes" in error_details.lower():
                    print("\n⚠️  IMPORTANT: The photoslibrary.readonly scope may be restricted!")
                    print("\nAs of March 2025, Google restricted the photoslibrary.readonly scope.")
                    print("Even though you have the scope, it may only work for app-created content.")
                    print("\nPossible solutions:")
                    print("\n1. Use Picker API instead (recommended for full library access):")
                    print("   uv run photos.py --credentials credentials.json --mode picker")
                    print("\n2. Try app-created data scope (only works for content your app created):")
                    print("   This requires modifying the code to use:")
                    print("   https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata")
                    print("\n3. Verify API is enabled and check for any restrictions:")
                    print("   https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com")
                    print("\n4. Check if your Google account has any restrictions on Photos API access")
                    print("="*60)
                else:
                    print("\nTroubleshooting steps:")
                    print("1. Verify Google Photos Library API is enabled:")
                    print("   https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com")
                    print("\n2. Add scope to OAuth consent screen:")
                    print("   - Go to: APIs & Services > OAuth consent screen")
                    print("   - Click 'Edit App'")
                    print("   - Under 'Scopes', click 'Add or Remove Scopes'")
                    print(f"   - Search for and add: {LIBRARY_SCOPE}")
                    print("   - Save and continue")
                    print("\n3. If your app is in 'Testing' mode:")
                    print("   - Add your email as a test user")
                    print("   - Or publish your app (if ready)")
                    print("\n4. Delete token and re-authenticate:")
                    print("   rm token-library.json")
                    print("   uv run photos.py --credentials credentials.json --mode library --list-albums")
                    print("="*60)
            raise
    
    def get_album_photos(self, album_id: str, page_size: int = 100) -> List[Dict]:
        """
        Get all photos from a specific album
        
        Args:
            album_id: The album ID
            page_size: Number of photos per page (max 100)
            
        Returns:
            List of media item dictionaries
        """
        if not self.service:
            raise ValueError("Library API not initialized")
        
        photos = []
        page_token = None
        
        try:
            while True:
                request_body = {
                    'albumId': album_id,
                    'pageSize': min(page_size, 100)
                }
                if page_token:
                    request_body['pageToken'] = page_token
                
                response = self.service.mediaItems().search(body=request_body).execute()
                
                if 'mediaItems' in response:
                    photos.extend(response['mediaItems'])
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            return photos
        except HttpError as error:
            print(f"Error fetching album photos: {error}")
            if error.resp.status == 403:
                print("\n403 Error: Check OAuth consent screen configuration")
                print("See troubleshooting steps in get_albums() error message")
            raise
    
    def get_album_by_title(self, title: str) -> Optional[Dict]:
        """
        Find an album by title
        
        Args:
            title: Album title to search for
            
        Returns:
            Album dictionary if found, None otherwise
        """
        albums = self.get_albums()
        for album in albums:
            if album.get('title') == title:
                return album
        return None


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Fetch photos and albums from Google Photos',
        epilog="""
IMPORTANT NOTES:
- Service accounts are NOT supported. OAuth2 with a user account is required.
- Picker API: Interactive selection in browser (recommended for full library access)
- Library API: Programmatic access to albums (may be limited after March 2025)
        """
    )
    parser.add_argument(
        '--credentials',
        type=str,
        help='Path to OAuth2 credentials JSON file (or set GOOGLE_PHOTOS_CREDENTIALS)'
    )
    parser.add_argument(
        '--token',
        type=str,
        help='Path to store/load OAuth2 token (default varies by mode)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file path (default: stdout)'
    )
    parser.add_argument(
        '--mode',
        choices=['picker', 'library'],
        default='picker',
        help='API mode: picker (interactive) or library (programmatic albums)'
    )
    
    # Picker-specific arguments
    parser.add_argument(
        '--max-items',
        type=int,
        default=100,
        help='Maximum items user can select in picker mode (default: 100, max: 2000)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Timeout in seconds for picker mode (default: 300)'
    )
    parser.add_argument(
        '--no-open',
        action='store_true',
        help='Do not automatically open picker in browser'
    )
    
    # Library-specific arguments
    parser.add_argument(
        '--album-id',
        type=str,
        help='Album ID to fetch photos from (library mode)'
    )
    parser.add_argument(
        '--album-title',
        type=str,
        help='Album title to fetch photos from (library mode)'
    )
    parser.add_argument(
        '--list-albums',
        action='store_true',
        help='List all albums (library mode)'
    )
    parser.add_argument(
        '--check-scopes',
        action='store_true',
        help='Check what scopes are in the current token'
    )
    
    args = parser.parse_args()
    
    # Check scopes if requested
    if args.check_scopes:
        token_path = args.token or ('token-library.json' if args.mode == 'library' else 'token.json')
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, [])
                print(f"Token file: {token_path}")
                print(f"Scopes in token: {creds.scopes if creds.scopes else 'None'}")
                print(f"Token valid: {creds.valid}")
                if creds.expired:
                    print(f"Token expired: {creds.expiry}")
            except Exception as e:
                print(f"Error reading token: {e}")
        else:
            print(f"Token file not found: {token_path}")
        return
    
    try:
        if args.mode == 'picker':
            # Picker API mode
            fetcher = GooglePhotosPickerFetcher(
                credentials_path=args.credentials,
                token_path=args.token or 'token.json'
            )
            
            if not fetcher.credentials:
                print("Error: Authentication failed")
                sys.exit(1)
            
            result = fetcher.pick_photos(
                max_item_count=args.max_items,
                timeout=args.timeout,
                auto_open=not args.no_open
            )
            
            if not result:
                print("No photos were selected")
                sys.exit(0)
        
        else:
            # Library API mode
            fetcher = GooglePhotosLibraryFetcher(
                credentials_path=args.credentials,
                token_path=args.token or 'token-library.json'
            )
            
            if not fetcher.service:
                print("Error: Library API not initialized")
                sys.exit(1)
            
            if args.list_albums:
                result = fetcher.get_albums()
                print(f"Found {len(result)} album(s)")
            elif args.album_id:
                result = fetcher.get_album_photos(args.album_id)
                print(f"Found {len(result)} photo(s) in album")
            elif args.album_title:
                album = fetcher.get_album_by_title(args.album_title)
                if album:
                    result = fetcher.get_album_photos(album['id'])
                    print(f"Found {len(result)} photo(s) in album '{args.album_title}'")
                else:
                    print(f"Album '{args.album_title}' not found")
                    sys.exit(1)
            else:
                parser.print_help()
                print("\nFor library mode, specify --list-albums, --album-id, or --album-title")
                sys.exit(1)
        
        # Output results
        if result:
            output = json.dumps(result, indent=2, ensure_ascii=False)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Results saved to {args.output}")
            else:
                print("\nResults:")
                print(output)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
