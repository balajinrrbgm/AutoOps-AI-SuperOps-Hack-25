#!/usr/bin/env python3
"""
Generate pre-signed URL for S3 frontend access
"""

import boto3
from datetime import timedelta

REGION = 'us-east-2'
BUCKET_NAME = 'autoops-frontend-358262661344'
OBJECT_KEY = 'index.html'

s3 = boto3.client('s3', region_name=REGION)

# Generate a pre-signed URL valid for 24 hours
url = s3.generate_presigned_url(
    'get_object',
    Params={
        'Bucket': BUCKET_NAME,
        'Key': OBJECT_KEY
    },
    ExpiresIn=86400  # 24 hours
)

print("="*80)
print("Frontend Access URL (Valid for 24 hours)")
print("="*80)
print(f"\n{url}\n")
print("="*80)
print("\nThis URL bypasses S3 block public access restrictions.")
print("Copy and paste this URL in your browser to access the frontend.")
print("="*80)
