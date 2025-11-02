"""
AWS Infrastructure Deployment Script
Deploys AutoOps AI infrastructure using boto3 directly
"""
import boto3
import json
import time
import os
from datetime import datetime

# AWS Configuration
REGION = 'us-east-2'
ACCOUNT_ID = '358262661344'

# Disable AWS config and credentials files - use environment vars only
os.environ['AWS_CONFIG_FILE'] = ''
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = ''

print("=" * 80)
print("AutoOps AI - AWS Infrastructure Deployment")
print("=" * 80)
print(f"Region: {REGION}")
print(f"Account: {ACCOUNT_ID}")
print("=" * 80)

# Initialize AWS clients with explicit credentials from environment
try:
    # Use credentials from environment variables only
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    session_token = os.environ.get('AWS_SESSION_TOKEN')
    
    if not access_key or not secret_key:
        raise Exception("AWS credentials not found in environment variables")
    
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
        region_name=REGION
    )
    dynamodb = session.client('dynamodb')
    lambda_client = session.client('lambda')
    iam = session.client('iam')
    apigateway = session.client('apigateway')
    s3 = session.client('s3')
    print("✅ AWS session initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize AWS session: {e}")
    print("Make sure AWS credentials are in environment variables:")
    print("  - AWS_ACCESS_KEY_ID")
    print("  - AWS_SECRET_ACCESS_KEY")
    print("  - AWS_SESSION_TOKEN (if using temporary credentials)")
    exit(1)

def create_dynamodb_tables():
    """Create DynamoDB tables for AutoOps"""
    print("\n📊 Creating DynamoDB Tables...")
    
    tables = [
        {
            'TableName': 'AutoOps-Policies',
            'KeySchema': [
                {'AttributeName': 'policyId', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'policyId', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
        },
        {
            'TableName': 'AutoOps-Actions',
            'KeySchema': [
                {'AttributeName': 'actionId', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'actionId', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'StreamSpecification': {
                'StreamEnabled': True,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'
            }
        },
        {
            'TableName': 'AutoOps-Vulnerabilities',
            'KeySchema': [
                {'AttributeName': 'cveId', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'cveId', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
        },
        {
            'TableName': 'AutoOps-Patches',
            'KeySchema': [
                {'AttributeName': 'patchId', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'patchId', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
        },
    ]
    
    for table_def in tables:
        table_name = table_def['TableName']
        try:
            # Check if table exists
            dynamodb.describe_table(TableName=table_name)
            print(f"  ✓ {table_name} already exists")
        except dynamodb.exceptions.ResourceNotFoundException:
            # Create table
            print(f"  Creating {table_name}...")
            dynamodb.create_table(**table_def)
            print(f"  ✓ {table_name} created")
        except Exception as e:
            print(f"  ❌ Error with {table_name}: {e}")

def create_iam_role():
    """Create IAM role for Lambda functions"""
    print("\n🔐 Creating IAM Role...")
    
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
        iam.get_role(RoleName=role_name)
        print(f"  ✓ {role_name} already exists")
        role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']
    except iam.exceptions.NoSuchEntityException:
        # Create role
        print(f"  Creating {role_name}...")
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Execution role for AutoOps AI Lambda functions'
        )
        role_arn = response['Role']['Arn']
        
        # Attach managed policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess',
        ]
        
        for policy_arn in policies:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        
        # Add Bedrock permissions
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
            PolicyName='BedrockAccess',
            PolicyDocument=json.dumps(bedrock_policy)
        )
        
        print(f"  ✓ {role_name} created")
        time.sleep(10)  # Wait for role to propagate
    except Exception as e:
        print(f"  ❌ Error creating role: {e}")
        return None
    
    return role_arn

def create_s3_buckets():
    """Create S3 buckets"""
    print("\n📦 Creating S3 Buckets...")
    
    buckets = [
        f'autoops-playbooks-{ACCOUNT_ID}',
        f'autoops-logs-{ACCOUNT_ID}',
        f'autoops-frontend-{ACCOUNT_ID}',
    ]
    
    for bucket_name in buckets:
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"  ✓ {bucket_name} already exists")
        except:
            try:
                if REGION == 'us-east-1':
                    s3.create_bucket(Bucket=bucket_name)
                else:
                    s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': REGION}
                    )
                print(f"  ✓ {bucket_name} created")
            except Exception as e:
                print(f"  ❌ Error creating {bucket_name}: {e}")

def print_deployment_summary():
    """Print deployment summary"""
    print("\n" + "=" * 80)
    print("✅ Infrastructure Deployment Complete!")
    print("=" * 80)
    print("\n📋 Resources Created:")
    print("  DynamoDB Tables:")
    print("    - AutoOps-Policies")
    print("    - AutoOps-Actions")
    print("    - AutoOps-Vulnerabilities")
    print("    - AutoOps-Patches")
    print("\n  S3 Buckets:")
    print(f"    - autoops-playbooks-{ACCOUNT_ID}")
    print(f"    - autoops-logs-{ACCOUNT_ID}")
    print(f"    - autoops-frontend-{ACCOUNT_ID}")
    print("\n  IAM:")
    print("    - AutoOpsLambdaExecutionRole")
    print("\n🚀 Next Steps:")
    print("  1. Deploy Lambda functions (CDK or manual)")
    print("  2. Configure API Gateway")
    print("  3. Deploy frontend to S3")
    print("  4. Update .env with new resource ARNs")
    print("=" * 80)

if __name__ == '__main__':
    try:
        create_dynamodb_tables()
        role_arn = create_iam_role()
        create_s3_buckets()
        print_deployment_summary()
        
        print(f"\n💾 IAM Role ARN: {role_arn}")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
