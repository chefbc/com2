uv run reviews.py --method places \
  --place-id "ChIJ5WO-o53_BIgRt-iSWeAY-lw" \
  --format json \
  --api-key AIzaSyDJEb2owvc5kJT2cU5MtMXstPPZAXGlXxY \
  --output reviews.json


uv run reviews.py --method search \
--query "Starbucks New York" \
--api-key AIzaSyDJEb2owvc5kJT2cU5MtMXstPPZAXGlXxY \
--output reviews.json
  

export GOOGLE_PLACES_API_KEY="AIzaSyDJEb2owvc5kJT2cU5MtMXstPPZAXGlXxY"
uv run reviews.py --method places \
  --place-id "ChIJ5WO-o53_BIgRt-iSWeAY-lw" \
  --format json \
  --output reviews.json


uv run reviews.py --method search \
--query "Starbucks New York" \
--format json \
--output reviews.json


uv run reviews.py --method places \
  --place-id "ChIJ5WO-o53_BIgRt-iSWeAY-lw" \
  --format markdown \
  --output docs/reviews/reviews.md