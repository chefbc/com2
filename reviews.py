# /// script
# dependencies = [
#   "google-api-python-client",
#   "google-auth-httplib2",
#   "google-auth-oauthlib"
# ]
# ///

"""
Google Reviews Data Fetcher

This script provides multiple methods to fetch Google reviews:
1. Google Places API (official, limited to 5 reviews)
2. Google Business Profile API (for businesses you own/manage)

Requirements:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

import json
import csv
import os
import sys
from typing import List, Dict, Optional
import argparse

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Warning: Google API libraries not installed. Install with:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GoogleReviewsFetcher:
    """Fetches Google reviews using various methods"""
    
    def __init__(self, api_key: Optional[str] = None, credentials_path: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        self.credentials_path = credentials_path
        self.places_service = None
        self.business_service = None
        
        if GOOGLE_API_AVAILABLE and self.api_key:
            try:
                self.places_service = build('places', 'v1', developerKey=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Places API: {e}")
    
    def _generate_review_urls(self, place_id: str) -> Dict[str, str]:
        """
        Generate URLs for linking to Google reviews
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Dictionary with 'place_url' and 'reviews_url'
        """
        return {
            'place_url': f'https://www.google.com/maps/search/?api=1&query_place_id={place_id}',
            'reviews_url': f'https://search.google.com/local/reviews?placeid={place_id}',
            'write_review_url': f'https://search.google.com/local/writereview?placeid={place_id}'
        }
    
    def fetch_places_reviews(self, place_id: str) -> List[Dict]:
        """
        Fetch reviews using Google Places API (limited to 5 reviews)
        
        Args:
            place_id: Google Place ID
            
        Returns:
            List of review dictionaries with URLs
        """
        if not self.places_service:
            raise ValueError(
                "Places API not initialized. Provide API key via --api-key flag or "
                "GOOGLE_PLACES_API_KEY environment variable."
            )
        
        try:
            # Places API v1 requires FieldMask header
            # Specify the fields we need for reviews
            field_mask = 'id,displayName,reviews'
            
            # Get the http object and add the FieldMask header
            http = self.places_service._http
            original_request = http.request
            
            def request_with_fieldmask(uri, method='GET', body=None, headers=None, **kwargs):
                # Add the FieldMask header
                if headers is None:
                    headers = {}
                headers['X-Goog-FieldMask'] = field_mask
                # Call original request with updated headers
                return original_request(uri, method, body, headers, **kwargs)
            
            # Temporarily replace the request method
            http.request = request_with_fieldmask
            
            try:
                place_details = self.places_service.places().get(
                    name=f"places/{place_id}",
                    languageCode='en'
                ).execute()
            finally:
                # Restore original request method
                http.request = original_request
            
            reviews = place_details.get('reviews', [])
            
            # Generate URLs for the place
            urls = self._generate_review_urls(place_id)
            
            formatted_reviews = []
            for review in reviews:
                formatted_reviews.append({
                    'review_id': review.get('name', ''),
                    'author': review.get('authorAttribution', {}).get('displayName', 'Unknown'),
                    'rating': review.get('rating', 0),
                    'text': review.get('text', {}).get('text', ''),
                    'time': review.get('publishTime', ''),
                    'relative_time': review.get('relativePublishTimeDescription', ''),
                    # 'place_url': urls['place_url'],
                    # 'reviews_url': urls['reviews_url'],
                    # 'write_review_url': urls['write_review_url'],
                })
            
            # Sort reviews by publishTime (newest first)
            # Reviews come sorted by relevance, so we need to sort by date
            formatted_reviews.sort(
                key=lambda x: x['time'] if x['time'] else '',
                reverse=True  # Newest first
            )
            
            return formatted_reviews
            
        except HttpError as e:
            print(f"Error fetching Places reviews: {e}")
            return []
    
    def fetch_business_profile_reviews(self, account_id: str, location_id: str, 
                                       credentials_path: Optional[str] = None) -> List[Dict]:
        """
        Fetch reviews using Google Business Profile API (for businesses you own/manage)
        
        Args:
            account_id: Google Business Profile account ID
            location_id: Location ID
            credentials_path: Path to OAuth2 credentials JSON file
            
        Returns:
            List of review dictionaries
        """
        if not GOOGLE_API_AVAILABLE:
            raise ImportError("Google API libraries not installed")
        
        # Set up OAuth2 flow
        SCOPES = ['https://www.googleapis.com/auth/business.manage']
        creds = None
        
        if credentials_path and os.path.exists(credentials_path):
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            # Try to use existing token
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            raise ValueError("Valid credentials required for Business Profile API")
        
        try:
            service = build('mybusiness', 'v4', credentials=creds)
            parent = f'accounts/{account_id}/locations/{location_id}'
            
            reviews = []
            page_token = None
            
            while True:
                response = service.accounts().locations().reviews().list(
                    parent=parent,
                    pageSize=50,
                    pageToken=page_token
                ).execute()
                
                batch_reviews = response.get('reviews', [])
                reviews.extend(batch_reviews)
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            formatted_reviews = []
            for review in reviews:
                formatted_reviews.append({
                    'review_id': review.get('reviewId', ''),
                    'author': review.get('reviewer', {}).get('displayName', 'Unknown'),
                    'rating': review.get('starRating', ''),
                    'text': review.get('comment', ''),
                    'time': review.get('createTime', ''),
                    'reply': review.get('reviewReply', {}).get('comment', '') if review.get('reviewReply') else '',
                })
            
            return formatted_reviews
            
        except HttpError as e:
            print(f"Error fetching Business Profile reviews: {e}")
            return []
    
    def search_place_id(self, query: str) -> Optional[str]:
        """
        Search for a place and return its Place ID
        
        Args:
            query: Business name and location (e.g., "Starbucks New York")
            
        Returns:
            Place ID or None
        """
        if not self.places_service:
            raise ValueError("Places API not initialized")
        
        try:
            response = self.places_service.places().searchText(
                textQuery=query
            ).execute()
            
            places = response.get('places', [])
            if places:
                return places[0].get('id', '').replace('places/', '')
            
            return None
            
        except HttpError as e:
            print(f"Error searching for place: {e}")
            return None
    
    def _generate_markdown(self, reviews: List[Dict]) -> str:
        """
        Generate markdown content from reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Markdown string
        """
        if not reviews:
            return "# Reviews\n\nNo reviews found.\n"
        
        markdown = "# Reviews\n\n"
        markdown += f"Total reviews: {len(reviews)}\n\n"
        markdown += "---\n\n"
        
        for i, review in enumerate(reviews, 1):
            author = review.get('author', 'Unknown')
            rating = review.get('rating', 0)
            text = review.get('text', '').strip()
            time = review.get('time', '')
            relative_time = review.get('relative_time', '')
            
            # Format date if available
            date_str = relative_time if relative_time else time[:10] if time else ''
            
            # Generate stars
            stars = '⭐' * int(rating) if rating else ''
            
            #markdown += f"## Review {i}: {author} {stars}\n\n"
            markdown += f"## {author} {stars}\n\n"
            markdown += f"**Rating:** {rating}/5  \n"
            if date_str:
                markdown += f"**Date:** {date_str}  \n"
            markdown += "\n"
            markdown += f"{text}\n\n"
            markdown += "---\n\n"
        
        return markdown
    
    def save_reviews(self, reviews: List[Dict], output_file: str, format: str = 'json'):
        """
        Save reviews to a file
        
        Args:
            reviews: List of review dictionaries
            output_file: Output file path
            format: 'json', 'csv', or 'markdown'
        """
        if format.lower() == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, indent=2, ensure_ascii=False)
        elif format.lower() == 'csv':
            if not reviews:
                print("No reviews to save")
                return
            
            fieldnames = reviews[0].keys()
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(reviews)
        elif format.lower() == 'markdown' or format.lower() == 'md':
            markdown_content = self._generate_markdown(reviews)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json', 'csv', or 'markdown'")
        
        print(f"Saved {len(reviews)} reviews to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Fetch Google Reviews or convert JSON to Markdown')
    parser.add_argument('--method', choices=['places', 'business', 'search', 'convert'], 
                       default='places', help='Method to use (or "convert" to convert JSON to markdown)')
    parser.add_argument('--input', help='Input JSON file (for convert method)')
    parser.add_argument('--place-id', help='Google Place ID')
    parser.add_argument('--query', help='Business name and location (for search)')
    parser.add_argument('--account-id', help='Business Profile account ID')
    parser.add_argument('--location-id', help='Business Profile location ID')
    parser.add_argument('--api-key', help='Google Places API key (or set GOOGLE_PLACES_API_KEY)')
    parser.add_argument('--credentials', help='Path to OAuth2 credentials JSON')
    parser.add_argument('--output', default='reviews.json', help='Output file path')
    parser.add_argument('--format', choices=['json', 'csv', 'markdown', 'md'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    # Handle convert method first (doesn't need API)
    if args.method == 'convert':
        if not args.input:
            print("Error: --input required for convert method")
            print("Example: python reviews.py --method convert --input reviews.json --output reviews.md")
            sys.exit(1)
        
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}")
            sys.exit(1)
        
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                reviews = json.load(f)
            
            fetcher = GoogleReviewsFetcher()
            fetcher.save_reviews(reviews, args.output, 'markdown')
            print(f"\nConverted {len(reviews)} reviews from {args.input} to {args.output}")
            sys.exit(0)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error converting file: {e}")
            sys.exit(1)
    
    # Validate API key for places/search methods
    if args.method in ['places', 'search']:
        if not args.api_key and not os.getenv('GOOGLE_PLACES_API_KEY'):
            print("Error: API key required for Places API methods.")
            print("Provide it via --api-key flag or set GOOGLE_PLACES_API_KEY environment variable.")
            print("\nExample:")
            print("  uv run reviews.py --method places --place-id '...' --api-key YOUR_API_KEY")
            print("  OR")
            print("  export GOOGLE_PLACES_API_KEY='YOUR_API_KEY'")
            print("  uv run reviews.py --method places --place-id '...'")
            sys.exit(1)
    
    fetcher = GoogleReviewsFetcher(api_key=args.api_key, credentials_path=args.credentials)
    
    reviews = []
    
    if args.method == 'places':
        if args.place_id:
            place_id = args.place_id
        elif args.query:
            print(f"Searching for: {args.query}")
            place_id = fetcher.search_place_id(args.query)
            if not place_id:
                print("Place not found")
                sys.exit(1)
            print(f"Found Place ID: {place_id}")
        else:
            print("Error: Provide either --place-id or --query")
            sys.exit(1)
        
        reviews = fetcher.fetch_places_reviews(place_id)
        print(f"Fetched {len(reviews)} reviews (Places API limit: 5)")
        
    elif args.method == 'business':
        if not args.account_id or not args.location_id:
            print("Error: --account-id and --location-id required for business method")
            sys.exit(1)
        
        reviews = fetcher.fetch_business_profile_reviews(
            args.account_id, 
            args.location_id,
            args.credentials
        )
        print(f"Fetched {len(reviews)} reviews")
        
    elif args.method == 'search':
        if not args.query:
            print("Error: --query required for search method")
            sys.exit(1)
        
        place_id = fetcher.search_place_id(args.query)
        if place_id:
            print(f"Found Place ID: {place_id}")
            reviews = fetcher.fetch_places_reviews(place_id)
        else:
            print("Place not found")
            sys.exit(1)
    
    if reviews:
        fetcher.save_reviews(reviews, args.output, args.format)
        print(f"\nSample review:")
        print(json.dumps(reviews[0], indent=2))
    else:
        print("No reviews found")


if __name__ == '__main__':
    main()
