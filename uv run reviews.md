uv run reviews.py --method places \
  --place-id "ChIJ5WO-o53_BIgRt-iSWeAY-lw" \
  --format json \
  --api-key x \
  --output reviews.json


uv run reviews.py --method search \
--query "Starbucks New York" \
--api-key x \
--output reviews.json
  

export GOOGLE_PLACES_API_KEY="x"
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