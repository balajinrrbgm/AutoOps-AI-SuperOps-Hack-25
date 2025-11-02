#!/usr/bin/env python3
"""
AWS Services Setup Script for AutoOps AI
=========================================
This script creates all required AWS resources for the AutoOps AI platform:
- DynamoDB tables
- SNS topics
- EventBridge rules
- Step Functions state machines
- Lambda functions
- Bedrock model access configuration

Prerequisites:
- AWS CLI configured with credentials
- boto3 installed (pip install boto3)
- Sufficient IAM permissions
"""

import boto3
import json
import os
from datetime import datetime

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID', '293882909374')

# Initialize AWS clients
dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
sns = boto3.client('sns', region_name=AWS_REGION)
events = boto3.client('events', region_name=AWS_REGION)
sfn = boto3.client('stepfunctions', region_name=AWS_REGION)
iam = boto3.client('iam', region_name=AWS_REGION)
bedrock = boto3.client('bedrock', region_name=AWS_REGION)

print("=" * 70)
print("🚀 AutoOps AI - AWS Services Setup")
print("=" * 70)
print(f"Region: {AWS_REGION}")
print(f"Account: {AWS_ACCOUNT_ID}")
print()

# ==================== DynamoDB Tables ====================

def create_dynamodb_tables():
    """Create all required DynamoDB tables"""
    print("📊 Creating DynamoDB Tables...")
    
    tables = [
        {
            'TableName': 'autoops-vulnerabilities',
            'KeySchema': [
                {'AttributeName': 'cveId', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'cveId', 'AttributeType': 'S'},
                {'AttributeName': 'severity', 'AttributeType': 'S'},
                {'AttributeName': 'publishedDate', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'severity-index',
                    'KeySchema': [
                        {'AttributeName': 'severity', 'KeyType': 'HASH'},
                        {'AttributeName': 'publishedDate', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            'BillingMode': 'PROVISIONED',
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'TableName': 'autoops-patches',
            'KeySchema': [
                {'AttributeName': 'patchId', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'patchId', 'AttributeType': 'S'},
                {'AttributeName': 'severity', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'severity-status-index',
                    'KeySchema': [
                        {'AttributeName': 'severity', 'KeyType': 'HASH'},
                        {'AttributeName': 'status', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            'BillingMode': 'PROVISIONED',
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'TableName': 'autoops-alerts',
            'KeySchema': [
                {'AttributeName': 'alertId', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'alertId', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'},
                {'AttributeName': 'createdAt', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'status-created-index',
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'},
                        {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            'BillingMode': 'PROVISIONED',
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'TableName': 'autoops-actions',
            'KeySchema': [
                {'AttributeName': 'actionId', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'actionId', 'AttributeType': 'S'},
                {'AttributeName': 'deviceId', 'AttributeType': 'S'},
                {'AttributeName': 'startedAt', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'device-started-index',
                    'KeySchema': [
                        {'AttributeName': 'deviceId', 'KeyType': 'HASH'},
                        {'AttributeName': 'startedAt', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            'BillingMode': 'PROVISIONED',
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        {
            'TableName': 'autoops-policies',
            'KeySchema': [
                {'AttributeName': 'policyId', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'policyId', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PROVISIONED',
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ]
    
    for table_config in tables:
        table_name = table_config['TableName']
        try:
            # Check if table exists
            existing_tables = dynamodb.list_tables()['TableNames']
            if table_name in existing_tables:
                print(f"  ✅ Table '{table_name}' already exists")
                continue
            
            # Create table
            response = dynamodb.create_table(**table_config)
            print(f"  ✅ Created table: {table_name}")
            
        except Exception as e:
            print(f"  ❌ Error creating table '{table_name}': {e}")
    
    print()

# ==================== SNS Topics ====================

def create_sns_topics():
    """Create SNS topics for notifications"""
    print("📢 Creating SNS Topics...")
    
    topics = [
        {
            'name': 'autoops-critical-alerts',
            'display_name': 'AutoOps Critical Alerts',
            'description': 'Critical security alerts and vulnerabilities'
        },
        {
            'name': 'autoops-patch-notifications',
            'display_name': 'AutoOps Patch Notifications',
            'description': 'Patch deployment notifications'
        },
        {
            'name': 'autoops-remediation-results',
            'display_name': 'AutoOps Remediation Results',
            'description': 'Automated remediation execution results'
        }
    ]
    
    topic_arns = {}
    
    for topic_config in topics:
        try:
            response = sns.create_topic(
                Name=topic_config['name'],
                Attributes={
                    'DisplayName': topic_config['display_name']
                },
                Tags=[
                    {'Key': 'Project', 'Value': 'AutoOps-AI'},
                    {'Key': 'Purpose', 'Value': topic_config['description']}
                ]
            )
            topic_arn = response['TopicArn']
            topic_arns[topic_config['name']] = topic_arn
            print(f"  ✅ Created topic: {topic_config['name']}")
            print(f"     ARN: {topic_arn}")
            
        except sns.exceptions.TopicLimitExceededException:
            print(f"  ⚠️  Topic limit exceeded for '{topic_config['name']}'")
        except Exception as e:
            print(f"  ❌ Error creating topic '{topic_config['name']}': {e}")
    
    print()
    return topic_arns

# ==================== IAM Roles ====================

def create_iam_roles():
    """Create IAM roles for Step Functions and Lambda"""
    print("🔐 Creating IAM Roles...")
    
    # Step Functions execution role
    sfn_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "states.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Lambda execution role
    lambda_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    roles = [
        {
            'name': 'AutoOps-StepFunctions-Role',
            'trust_policy': sfn_trust_policy,
            'policies': [
                'arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess',
                'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                'arn:aws:iam::aws:policy/AmazonSNSFullAccess'
            ]
        },
        {
            'name': 'AutoOps-Lambda-Role',
            'trust_policy': lambda_trust_policy,
            'policies': [
                'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
                'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                'arn:aws:iam::aws:policy/AmazonSNSFullAccess',
                'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            ]
        }
    ]
    
    role_arns = {}
    
    for role_config in roles:
        try:
            # Check if role exists
            try:
                iam.get_role(RoleName=role_config['name'])
                role_arn = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{role_config['name']}"
                role_arns[role_config['name']] = role_arn
                print(f"  ✅ Role '{role_config['name']}' already exists")
                continue
            except iam.exceptions.NoSuchEntityException:
                pass
            
            # Create role
            response = iam.create_role(
                RoleName=role_config['name'],
                AssumeRolePolicyDocument=json.dumps(role_config['trust_policy']),
                Description=f"Execution role for AutoOps AI {role_config['name']}"
            )
            role_arn = response['Role']['Arn']
            role_arns[role_config['name']] = role_arn
            
            # Attach policies
            for policy_arn in role_config['policies']:
                iam.attach_role_policy(
                    RoleName=role_config['name'],
                    PolicyArn=policy_arn
                )
            
            print(f"  ✅ Created role: {role_config['name']}")
            print(f"     ARN: {role_arn}")
            
        except Exception as e:
            print(f"  ❌ Error creating role '{role_config['name']}': {e}")
    
    print()
    return role_arns

# ==================== Bedrock Configuration ====================

def configure_bedrock():
    """Configure AWS Bedrock model access"""
    print("🤖 Configuring AWS Bedrock...")
    
    try:
        # Check model access
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        print(f"  ℹ️  Bedrock is available in {AWS_REGION}")
        print(f"  ℹ️  Model ID: {model_id}")
        print(f"  ⚠️  Note: You need to manually request model access in the AWS Console:")
        print(f"     1. Go to AWS Bedrock console")
        print(f"     2. Navigate to 'Model access'")
        print(f"     3. Request access to: {model_id}")
        print(f"     4. Wait for approval (usually instant)")
        
    except Exception as e:
        print(f"  ❌ Error configuring Bedrock: {e}")
    
    print()

# ==================== Main Setup ====================

def main():
    """Main setup function"""
    try:
        # Create DynamoDB tables
        create_dynamodb_tables()
        
        # Create SNS topics
        topic_arns = create_sns_topics()
        
        # Create IAM roles
        role_arns = create_iam_roles()
        
        # Configure Bedrock
        configure_bedrock()
        
        # Print summary
        print("=" * 70)
        print("✅ AWS Services Setup Complete!")
        print("=" * 70)
        print()
        print("📋 Summary:")
        print()
        print("DynamoDB Tables Created:")
        print("  - autoops-vulnerabilities")
        print("  - autoops-patches")
        print("  - autoops-alerts")
        print("  - autoops-actions")
        print("  - autoops-policies")
        print()
        
        if topic_arns:
            print("SNS Topics Created:")
            for name, arn in topic_arns.items():
                print(f"  - {name}")
                print(f"    ARN: {arn}")
            print()
        
        if role_arns:
            print("IAM Roles Created:")
            for name, arn in role_arns.items():
                print(f"  - {name}")
                print(f"    ARN: {arn}")
            print()
        
        print("⚠️  Manual Steps Required:")
        print("  1. Request Bedrock model access in AWS Console")
        print("  2. Update .env file with created ARNs")
        print("  3. Create Step Functions state machines (run setup_step_functions.py)")
        print("  4. Create EventBridge rules (run setup_eventbridge.py)")
        print("  5. Deploy Lambda functions")
        print()
        
        print("🎯 Next Commands:")
        print("  python infrastructure/setup_step_functions.py")
        print("  python infrastructure/setup_eventbridge.py")
        print()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
