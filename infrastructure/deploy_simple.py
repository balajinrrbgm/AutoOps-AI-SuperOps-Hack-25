#!/usr/bin/env python3
"""
Simplified AWS Infrastructure Deployment for AutoOps AI
Uses default AWS credentials from ~/.aws/credentials
"""

import boto3
import json
from botocore.exceptions import ClientError

REGION = 'us-east-2'
ACCOUNT_ID = '358262661344'

print("="*80)
print("AutoOps AI - Simple Infrastructure Deployment")
print("="*80)
print(f"Region: {REGION}")
print(f"Account: {ACCOUNT_ID}")
print("="*80)

# Initialize AWS clients (will use credentials from ~/.aws/credentials)
try:
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    s3 = boto3.client('s3', region_name=REGION)
    iam = boto3.client('iam', region_name=REGION)
    sts = boto3.client('sts', region_name=REGION)
    
    # Verify credentials
    identity = sts.get_caller_identity()
    print(f"\n✓ Connected as: {identity['Arn']}")
    print(f"✓ Account: {identity['Account']}\n")
except Exception as e:
    print(f"\n❌ Failed to connect to AWS: {e}")
    exit(1)

# 1. Create DynamoDB Tables
print("\n[1/4] Creating DynamoDB Tables...")

tables = [
    {
        'name': 'AutoOps-Policies',
        'key': [{'AttributeName': 'policyId', 'KeyType': 'HASH'}],
        'attributes': [{'AttributeName': 'policyId', 'AttributeType': 'S'}]
    },
    {
        'name': 'AutoOps-Actions',
        'key': [
            {'AttributeName': 'actionId', 'KeyType': 'HASH'},
            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
        ],
        'attributes': [
            {'AttributeName': 'actionId', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'S'}
        ]
    },
    {
        'name': 'AutoOps-Vulnerabilities',
        'key': [{'AttributeName': 'cveId', 'KeyType': 'HASH'}],
        'attributes': [{'AttributeName': 'cveId', 'AttributeType': 'S'}]
    },
    {
        'name': 'AutoOps-Patches',
        'key': [{'AttributeName': 'patchId', 'KeyType': 'HASH'}],
        'attributes': [{'AttributeName': 'patchId', 'AttributeType': 'S'}]
    }
]

for table_config in tables:
    try:
        # Check if table exists
        try:
            response = dynamodb.describe_table(TableName=table_config['name'])
            print(f"  ✓ {table_config['name']} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table
                response = dynamodb.create_table(
                    TableName=table_config['name'],
                    KeySchema=table_config['key'],
                    AttributeDefinitions=table_config['attributes'],
                    BillingMode='PAY_PER_REQUEST'
                )
                print(f"  ✓ Created {table_config['name']}")
            else:
                raise
    except Exception as e:
        print(f"  ❌ Failed to create {table_config['name']}: {e}")

# 2. Create S3 Buckets
print("\n[2/4] Creating S3 Buckets...")

buckets = [
    {
        'name': f'autoops-playbooks-{ACCOUNT_ID}',
        'versioning': True
    },
    {
        'name': f'autoops-logs-{ACCOUNT_ID}',
        'lifecycle': True
    },
    {
        'name': f'autoops-frontend-{ACCOUNT_ID}',
        'website': True
    }
]

for bucket_config in buckets:
    try:
        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=bucket_config['name'])
            print(f"  ✓ {bucket_config['name']} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Create bucket
                if REGION == 'us-east-1':
                    s3.create_bucket(Bucket=bucket_config['name'])
                else:
                    s3.create_bucket(
                        Bucket=bucket_config['name'],
                        CreateBucketConfiguration={'LocationConstraint': REGION}
                    )
                print(f"  ✓ Created {bucket_config['name']}")
                
                # Configure versioning
                if bucket_config.get('versioning'):
                    s3.put_bucket_versioning(
                        Bucket=bucket_config['name'],
                        VersioningConfiguration={'Status': 'Enabled'}
                    )
                
                # Configure website hosting
                if bucket_config.get('website'):
                    s3.put_bucket_website(
                        Bucket=bucket_config['name'],
                        WebsiteConfiguration={
                            'IndexDocument': {'Suffix': 'index.html'},
                            'ErrorDocument': {'Key': 'index.html'}
                        }
                    )
            else:
                raise
    except Exception as e:
        print(f"  ❌ Failed to create {bucket_config['name']}: {e}")

# 3. Create IAM Role
print("\n[3/4] Creating IAM Role...")

role_name = 'AutoOpsLambdaExecutionRole'

trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

try:
    # Check if role exists
    try:
        iam.get_role(RoleName=role_name)
        print(f"  ✓ {role_name} already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            # Create role
            iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Execution role for AutoOps Lambda functions'
            )
            print(f"  ✓ Created {role_name}")
            
            # Attach policies
            policies = [
                'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
                'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                'arn:aws:iam::aws:policy/AmazonS3FullAccess'
            ]
            
            for policy_arn in policies:
                iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            
            # Create custom Bedrock policy
            bedrock_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": ["bedrock:InvokeModel"],
                    "Resource": "*"
                }]
            }
            
            iam.put_role_policy(
                RoleName=role_name,
                PolicyName='BedrockInvokeModel',
                PolicyDocument=json.dumps(bedrock_policy)
            )
            print(f"  ✓ Attached policies to {role_name}")
        else:
            raise
except Exception as e:
    print(f"  ❌ Failed to create {role_name}: {e}")

# 4. Summary
print("\n[4/4] Deployment Summary")
print("="*80)

# Check DynamoDB
print("\nDynamoDB Tables:")
try:
    response = dynamodb.list_tables()
    autoops_tables = [t for t in response['TableNames'] if t.startswith('AutoOps-')]
    for table in autoops_tables:
        print(f"  ✓ {table}")
except Exception as e:
    print(f"  ❌ Error listing tables: {e}")

# Check S3
print("\nS3 Buckets:")
try:
    response = s3.list_buckets()
    autoops_buckets = [b['Name'] for b in response['Buckets'] if b['Name'].startswith('autoops-')]
    for bucket in autoops_buckets:
        print(f"  ✓ {bucket}")
except Exception as e:
    print(f"  ❌ Error listing buckets: {e}")

# Check IAM
print("\nIAM Roles:")
try:
    response = iam.get_role(RoleName=role_name)
    print(f"  ✓ {role_name}")
    print(f"    ARN: {response['Role']['Arn']}")
except Exception as e:
    print(f"  ❌ Error getting role: {e}")

print("\n" + "="*80)
print("✅ Infrastructure deployment complete!")
print("="*80)
print("\nNext steps:")
print("1. Package Lambda functions")
print("2. Deploy Lambda code")
print("3. Create API Gateway")
print("4. Deploy frontend to S3")
print("="*80)
