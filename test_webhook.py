# /// script
# dependencies = [
#   "requests"
# ]
# ///


"""
Test script for n8n webhook endpoint
Tests the contact form webhook with sample data
"""

import requests
import json
from pathlib import Path
from typing import Optional

# Webhook URL
WEBHOOK_URL = "https://n8n.chefbc.com/webhook/webhook-form"
#WEBHOOK_URL = "https://n8n.chefbc.com/webhook-test/webhook-form"


def create_sample_data():
    """Create sample form data matching the contact form structure"""
    return {
        # Personal Information
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        
        # Vehicle Information
        "vehicleYear": "2020",
        "vehicleMake": "Toyota",
        "vehicleModel": "Camry",
        
        # Vehicle Condition (good, moderate, bad)
        "condition": "good",
        
        # Services
        "services": ["repair", "maintenance", "inspection"],
        "preferredDate": "2026-02-15",
        
        # Additional Information
        "additionalInfo": "This is a test submission from the webhook test script.",
        "howDidYouHear": "search-engine"
    }


def test_webhook_with_json_only(include_files: bool = False):
    """Test webhook with JSON data only (no file uploads)"""
    print("=" * 60)
    print("Testing Webhook - JSON Data Only")
    print("=" * 60)
    
    data = create_sample_data()
    
    if include_files:
        # Create FormData for file upload
        files = {}
        form_data = {"formData": json.dumps(data)}
        
        # Try to add a test image if it exists
        test_image_path = Path("test_image.jpg")
        if test_image_path.exists():
            files["vehiclePhoto_0"] = open(test_image_path, "rb")
            print(f"✓ Found test image: {test_image_path}")
        else:
            print("⚠ No test image found (test_image.jpg)")
            print("  Creating dummy file data...")
            # Create a small dummy file
            files["vehiclePhoto_0"] = ("test_image.jpg", b"fake image data", "image/jpeg")
        
        print("\nSending FormData with files...")
        response = requests.post(WEBHOOK_URL, data=form_data, files=files)
        
        # Close file if it was opened
        if isinstance(files.get("vehiclePhoto_0"), file):
            files["vehiclePhoto_0"].close()
    else:
        # Send as JSON wrapped in formData (matches contact form payload)
        payload = {"formData": data}
        print("\nSending JSON data...")
        print(f"URL: {WEBHOOK_URL}")
        print(f"\nData being sent:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
    
    print(f"\n{'=' * 60}")
    print(f"Response Status Code: {response.status_code}")
    print(f"{'=' * 60}")
    
    if response.status_code == 200:
        print("✓ Success! Webhook responded successfully.")
    else:
        print(f"⚠ Warning: Received status code {response.status_code}")
    
    print(f"\nResponse Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\nResponse Body:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
    except json.JSONDecodeError:
        print(response.text)
    
    return response


def test_webhook_with_formdata():
    """Test webhook with FormData (matching the actual form submission)"""
    print("\n" + "=" * 60)
    print("Testing Webhook - FormData (Matching Form Submission)")
    print("=" * 60)
    
    data = create_sample_data()
    
    # Create FormData
    form_data = {
        "formData": json.dumps(data)
    }
    
    files = {}
    
    # Try to add test images if they exist
    test_images = ["test_image.jpg", "test_image.png"]
    for idx, img_name in enumerate(test_images):
        img_path = Path(img_name)
        if img_path.exists():
            files[f"vehiclePhoto_{idx}"] = open(img_path, "rb")
            print(f"✓ Adding file: {img_name}")
    
    if not files:
        print("⚠ No test images found. Creating dummy file...")
        files["vehiclePhoto_0"] = ("test_image.jpg", b"fake image data", "image/jpeg")
    
    print(f"\nSending FormData to: {WEBHOOK_URL}")
    print(f"JSON Data:")
    print(json.dumps(data, indent=2))
    print(f"\nFiles: {list(files.keys())}")
    
    response = requests.post(WEBHOOK_URL, data=form_data, files=files)
    
    # Close any opened files
    for file_obj in files.values():
        if hasattr(file_obj, 'close'):
            file_obj.close()
    
    print(f"\n{'=' * 60}")
    print(f"Response Status Code: {response.status_code}")
    print(f"{'=' * 60}")
    
    if response.status_code == 200:
        print("✓ Success! Webhook responded successfully.")
    else:
        print(f"⚠ Warning: Received status code {response.status_code}")
    
    print(f"\nResponse Body:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
    except json.JSONDecodeError:
        print(response.text)
    
    return response


def main():
    """Main function to run tests. Runs one test by default (sends one email)."""
    import sys
    print("\n" + "=" * 60)
    print("n8n Webhook Test Script")
    print("=" * 60)
    print(f"Testing webhook: {WEBHOOK_URL}\n")
    
    run_both = "--all" in sys.argv
    try:
        # Test 1: JSON (matches contact form payload – one email)
        print("\n[TEST 1] Testing with JSON (formData wrapper)...")
        test_webhook_with_json_only(include_files=False)
        
        if run_both:
            # Test 2: FormData – only when you pass --all (sends a second email)
            print("\n[TEST 2] Testing with FormData...")
            test_webhook_with_formdata()
        else:
            print("\n(Skip second test unless you run: python test_webhook.py --all)")
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to webhook URL")
        print(f"   Please check that {WEBHOOK_URL} is accessible")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
