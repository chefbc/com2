"""
Hook to fetch Google reviews at build time and make them available in template context.
"""
import os
from typing import List, Dict, Optional

# Try to import Google API libraries
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    build = None
    HttpError = None


class GoogleReviewsFetcher:
    """Fetches Google reviews using Google Places API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.places_service = None
        
        if GOOGLE_API_AVAILABLE and self.api_key:
            try:
                self.places_service = build('places', 'v1', developerKey=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Places API: {e}")
    
    def fetch_places_reviews(self, place_id: str) -> List[Dict]:
        """
        Fetch reviews using Google Places API (limited to 5 reviews)
        
        Args:
            place_id: Google Place ID
            
        Returns:
            List of review dictionaries
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
            
            formatted_reviews = []
            for review in reviews:
                formatted_reviews.append({
                    'review_id': review.get('name', ''),
                    'author': review.get('authorAttribution', {}).get('displayName', 'Unknown'),
                    'rating': review.get('rating', 0),
                    'text': review.get('text', {}).get('text', ''),
                    'time': review.get('publishTime', ''),
                    'relative_time': review.get('relativePublishTimeDescription', ''),
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
        except Exception as e:
            print(f"Unexpected error fetching reviews: {e}")
            return []


# Global cache to avoid fetching multiple times
_reviews_cache = None

def on_page_context(context, page, config, nav):
    """
    Fetch Google reviews and add them to the page context.
    Reviews are fetched at build time using the Places API.
    """
    global _reviews_cache
    
    # Use cached reviews if available
    if _reviews_cache is not None:
        context['reviews'] = _reviews_cache
        return context
    
    reviews = []
    
    try:
        # Get configuration from environment variables
        place_id = os.getenv('GOOGLE_PLACE_ID')
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        
        print(f"\n[Reviews Hook] Checking environment variables...")
        print(f"  GOOGLE_PLACE_ID: {'✓ Set' if place_id else '✗ Not set'}")
        print(f"  GOOGLE_PLACES_API_KEY: {'✓ Set' if api_key else '✗ Not set'}")
        print(f"  Google API Available: {'✓ Yes' if GOOGLE_API_AVAILABLE else '✗ No (install google-api-python-client)'}")
        
        # Only fetch if we have the required environment variables
        if place_id and api_key and GOOGLE_API_AVAILABLE:
            try:
                print(f"[Reviews Hook] Fetching reviews for place: {place_id[:20]}...")
                fetcher = GoogleReviewsFetcher(api_key=api_key)
                reviews = fetcher.fetch_places_reviews(place_id)
                
                print(f"[Reviews Hook] ✓ Fetched {len(reviews)} reviews")
            except Exception as e:
                # Log error but don't fail the build
                print(f"[Reviews Hook] ✗ Error fetching reviews: {e}")
                import traceback
                traceback.print_exc()
                reviews = []
        elif not place_id:
            print("[Reviews Hook] ⚠ GOOGLE_PLACE_ID environment variable not set. Reviews will not be fetched.")
        elif not api_key:
            print("[Reviews Hook] ⚠ GOOGLE_PLACES_API_KEY environment variable not set. Reviews will not be fetched.")
        elif not GOOGLE_API_AVAILABLE:
            print("[Reviews Hook] ⚠ Google API libraries not available. Install with: pip install google-api-python-client")
    except Exception as e:
        # If anything fails, just ensure reviews is an empty list
        print(f"[Reviews Hook] ✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        reviews = []
    
    # Cache and add reviews to context
    _reviews_cache = reviews
    context['reviews'] = reviews
    print(f"[Reviews Hook] Added {len(reviews)} reviews to context\n")
    
    return context
