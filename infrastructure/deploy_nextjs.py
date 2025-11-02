#!/usr/bin/env python3
"""
Deploy Next.js Frontend to S3
"""

import boto3
import os
from pathlib import Path
import mimetypes

REGION = 'us-east-2'
BUCKET_NAME = 'autoops-frontend-358262661344'
BUILD_DIR = Path('../frontend/out')

print("="*80)
print("Deploying Next.js Frontend to S3")
print("="*80)
print(f"Build Directory: {BUILD_DIR}")
print(f"S3 Bucket: {BUCKET_NAME}")
print("="*80)

s3 = boto3.client('s3', region_name=REGION)

# Check if build directory exists
if not BUILD_DIR.exists():
    print(f"\n❌ Error: Build directory not found: {BUILD_DIR}")
    print("Run 'npm run build' first in the frontend directory")
    exit(1)

# Upload all files
uploaded_files = 0
for file_path in BUILD_DIR.rglob('*'):
    if file_path.is_file():
        # Get relative path for S3 key
        relative_path = file_path.relative_to(BUILD_DIR)
        s3_key = str(relative_path).replace('\\', '/')
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(str(file_path))
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Special handling for HTML files
        extra_args = {
            'ContentType': content_type
        }
        
        # Cache control
        if file_path.suffix in ['.html']:
            extra_args['CacheControl'] = 'no-cache'
        elif file_path.suffix in ['.js', '.css', '.json']:
            extra_args['CacheControl'] = 'public, max-age=31536000, immutable'
        else:
            extra_args['CacheControl'] = 'public, max-age=86400'
        
        try:
            s3.upload_file(
                str(file_path),
                BUCKET_NAME,
                s3_key,
                ExtraArgs=extra_args
            )
            uploaded_files += 1
            
            if uploaded_files % 10 == 0:
                print(f"  Uploaded {uploaded_files} files...")
        except Exception as e:
            print(f"  ❌ Failed to upload {s3_key}: {e}")

print(f"\n✅ Upload complete! {uploaded_files} files deployed.")

# Configure index document routing for SPA
print("\nConfiguring S3 website...")
try:
    s3.put_bucket_website(
        Bucket=BUCKET_NAME,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': '404.html'}
        }
    )
    print("  ✅ Website configuration updated")
except Exception as e:
    print(f"  ⚠ Website config: {e}")

website_url = f"http://{BUCKET_NAME}.s3-website.{REGION}.amazonaws.com"

print("\n" + "="*80)
print("🎉 DEPLOYMENT COMPLETE!")
print("="*80)
print(f"\nFrontend URL: {website_url}")
print(f"Files Deployed: {uploaded_files}")
print("\nThe Next.js application is now live on AWS!")
print("="*80)
