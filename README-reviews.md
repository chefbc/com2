# Google Reviews Data Fetcher

A Python script to fetch Google reviews data using multiple methods.

## Installation

The script uses PEP 723 inline script dependencies. Install dependencies with:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Or if using a tool that supports PEP 723 (like `pipx` or `uv`), you can run the script directly and dependencies will be installed automatically.

## Setup

### For Google Places API (Method 1)

1. Get a Google Places API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Places API in your project
3. Set the API key:
   ```bash
   export GOOGLE_PLACES_API_KEY="your-api-key-here"
   ```
   Or pass it via `--api-key` flag

### For Google Business Profile API (Method 2)

1. Create OAuth2 credentials in [Google Cloud Console](https://console.cloud.google.com/)
2. Download the credentials JSON file
3. Enable the Google My Business API
4. Use the credentials file path with `--credentials` flag

## Finding a Place ID

There are several ways to find a Google Place ID:

### Method 1: Use the script's search function (Easiest)

```bash
python reviews.py --method search --query "Starbucks New York" --api-key YOUR_API_KEY
```

This will search for the business and display the Place ID, then fetch reviews automatically.

### Method 2: Google Place ID Finder

1. Go to [Google Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id#find-id)
2. Search for the business location
3. Click on the business to get its Place ID
4. Copy the Place ID (looks like: `ChIJN1t_tDeuEmsRUsoyG83frY4`)



### Method 3: From Google Maps URL

1. Open Google Maps and search for the business
2. Click on the business to open its details
3. Look at the URL - the Place ID is in the URL parameter `data=!4m...` or you can use the Place ID Finder tool above

### Method 4: Using Places API Search

You can also use the Places API search endpoint directly, or use this script with the `--method search` option.

## Usage

### Method 1: Fetch reviews by Place ID

```bash
python reviews.py --method places --place-id "ChIJN1t_tDeuEmsRUsoyG83frY4" --api-key YOUR_API_KEY --output reviews.json
```

### Method 2: Search for a business and fetch reviews (automatically finds Place ID)

```bash
python reviews.py --method search --query "Starbucks New York" --api-key YOUR_API_KEY --output reviews.json
```

This will automatically search for the business, find its Place ID, and fetch the reviews.

### Method 3: Fetch reviews from your own business (Business Profile API)

```bash
python reviews.py --method business \
  --account-id "your-account-id" \
  --location-id "your-location-id" \
  --credentials credentials.json \
  --output reviews.json
```

## Output Formats

### JSON (default)
```bash
python reviews.py --method places --place-id "..." --format json --output reviews.json
```

### CSV
```bash
python reviews.py --method places --place-id "..." --format csv --output reviews.csv
```

## Examples

### Search and get Place ID (without fetching reviews)
If you just want to find a Place ID without fetching reviews, you can modify the script or use the search method and check the output. The script will display the Place ID when using the search method.

### Fetch reviews and save as CSV
```bash
python reviews.py --method places \
  --place-id "ChIJN1t_tDeuEmsRUsoyG83frY4" \
  --format csv \
  --output pizza_reviews.csv
```

## Limitations

- **Places API**: Limited to 5 most relevant reviews only
- **Business Profile API**: Only works for businesses you own/manage
- **Rate Limits**: Be mindful of API rate limits

## Notes

- The Places API method is free but limited to 5 reviews
- The Business Profile API requires OAuth2 authentication
- Always respect Google's Terms of Service
