#!/usr/bin/env python3
"""
Complete AWS Deployment Verification
"""

import boto3
import json
import requests

REGION = 'us-east-2'
ACCOUNT_ID = '358262661344'
API_ENDPOINT = 'https://83d0wk5nj8.execute-api.us-east-2.amazonaws.com/prod'
WEBSITE_URL = 'http://autoops-frontend-358262661344.s3-website.us-east-2.amazonaws.com'

print("="*80)
print("AutoOps AI - Deployment Verification")
print("="*80)

# Initialize clients
dynamodb = boto3.client('dynamodb', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)
iam = boto3.client('iam', region_name=REGION)
apigateway = boto3.client('apigateway', region_name=REGION)

results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0
}

def test(name, func):
    """Run a test and track results"""
    try:
        func()
        print(f"  ✅ {name}")
        results['passed'] += 1
        return True
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:80]}")
        results['failed'] += 1
        return False

# 1. DynamoDB Tables
print("\n[1/7] DynamoDB Tables")
def check_dynamodb():
    tables = dynamodb.list_tables()['TableNames']
    required = ['AutoOps-Policies', 'AutoOps-Actions', 'AutoOps-Vulnerabilities', 'AutoOps-Patches']
    for table in required:
        assert table in tables, f"Missing table: {table}"

test("All 4 DynamoDB tables exist", check_dynamodb)

# 2. S3 Buckets
print("\n[2/7] S3 Buckets")
def check_s3():
    response = s3.list_buckets()
    buckets = [b['Name'] for b in response['Buckets']]
    required = [
        'autoops-playbooks-358262661344',
        'autoops-logs-358262661344',
        'autoops-frontend-358262661344'
    ]
    for bucket in required:
        assert bucket in buckets, f"Missing bucket: {bucket}"

test("All 3 S3 buckets exist", check_s3)

def check_frontend_file():
    response = s3.head_object(Bucket='autoops-frontend-358262661344', Key='index.html')
    assert response['ContentLength'] > 0

test("Frontend index.html uploaded", check_frontend_file)

def check_website_config():
    response = s3.get_bucket_website(Bucket='autoops-frontend-358262661344')
    assert response['IndexDocument']['Suffix'] == 'index.html'

test("S3 website hosting enabled", check_website_config)

# 3. IAM Role
print("\n[3/7] IAM Role")
def check_iam():
    role = iam.get_role(RoleName='AutoOpsLambdaExecutionRole')
    assert 'Role' in role

test("AutoOpsLambdaExecutionRole exists", check_iam)

def check_iam_policies():
    policies = iam.list_attached_role_policies(RoleName='AutoOpsLambdaExecutionRole')
    policy_names = [p['PolicyName'] for p in policies['AttachedPolicies']]
    assert 'AWSLambdaBasicExecutionRole' in policy_names

test("IAM role has required policies", check_iam_policies)

# 4. Lambda Function
print("\n[4/7] Lambda Function")
def check_lambda():
    response = lambda_client.get_function(FunctionName='autoops-ai-agents')
    assert response['Configuration']['Runtime'] == 'python3.11'
    assert response['Configuration']['MemorySize'] == 2048
    assert response['Configuration']['Timeout'] == 180

test("Lambda function configured correctly", check_lambda)

def check_lambda_env():
    response = lambda_client.get_function_configuration(FunctionName='autoops-ai-agents')
    env = response.get('Environment', {}).get('Variables', {})
    assert 'BEDROCK_MODEL' in env
    assert 'USE_CREWAI' in env

test("Lambda environment variables set", check_lambda_env)

# 5. API Gateway
print("\n[5/7] API Gateway")
def check_api_gateway():
    apis = apigateway.get_rest_apis()
    api_names = [api['name'] for api in apis['items']]
    assert 'AutoOps-AI-API' in api_names

test("API Gateway exists", check_api_gateway)

# 6. API Endpoints
print("\n[6/7] API Endpoints")
def check_api_status():
    response = requests.get(f"{API_ENDPOINT}/ai/agents/status", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert 'bedrock_service' in data

test("Status endpoint responding", check_api_status)

def test_api_prioritize():
    payload = {
        "patches": [
            {
                "id": "KB5012345",
                "title": "Security Update",
                "severity": "CRITICAL",
                "cvssScore": 9.8
            }
        ]
    }
    response = requests.post(f"{API_ENDPOINT}/ai/agents/prioritize", json=payload, timeout=10)
    assert response.status_code == 200

test("Prioritize endpoint responding", test_api_prioritize)

# 7. Frontend Website
print("\n[7/7] Frontend Website")
def check_website():
    response = requests.get(WEBSITE_URL, timeout=10)
    assert response.status_code == 200
    assert 'AutoOps AI' in response.text

test("Frontend website accessible", check_website)

def check_website_api_integration():
    response = requests.get(WEBSITE_URL, timeout=10)
    assert API_ENDPOINT in response.text

test("Frontend has correct API endpoint", check_website_api_integration)

# Summary
print("\n" + "="*80)
print("DEPLOYMENT VERIFICATION SUMMARY")
print("="*80)
print(f"\n✅ Passed:   {results['passed']}")
print(f"❌ Failed:   {results['failed']}")
print(f"⚠️  Warnings: {results['warnings']}")

if results['failed'] == 0:
    print("\n🎉 ALL TESTS PASSED - DEPLOYMENT IS COMPLETE AND WORKING!")
else:
    print(f"\n⚠️  {results['failed']} test(s) failed - review errors above")

print("\n" + "="*80)
print("DEPLOYMENT URLS")
print("="*80)
print(f"\n📱 Frontend:  {WEBSITE_URL}")
print(f"🔌 API:       {API_ENDPOINT}")
print("\nTest Commands:")
print(f"  curl {WEBSITE_URL}")
print(f"  curl {API_ENDPOINT}/ai/agents/status")
print("="*80)
