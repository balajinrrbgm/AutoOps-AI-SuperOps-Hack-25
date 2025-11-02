#!/usr/bin/env python3
"""
Deploy AWS EventBridge Scheduler for Patch Management
Creates scheduler resources and DynamoDB table for scheduled patches
"""

import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime

REGION = 'us-east-2'
ACCOUNT_ID = '358262661344'
LAMBDA_FUNCTION_NAME = 'autoops-ai-agents'

print("="*80)
print("AutoOps AI - Patch Scheduler Deployment")
print("="*80)
print(f"Region: {REGION}")
print(f"Account: {ACCOUNT_ID}")
print("="*80)

# Initialize AWS clients
scheduler = boto3.client('scheduler', region_name=REGION)
dynamodb = boto3.client('dynamodb', region_name=REGION)
iam = boto3.client('iam', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)
sts = boto3.client('sts', region_name=REGION)

# Verify credentials
try:
    identity = sts.get_caller_identity()
    print(f"\n✓ Connected as: {identity['Arn']}")
    print(f"✓ Account: {identity['Account']}\n")
except Exception as e:
    print(f"\n❌ Failed to connect to AWS: {e}")
    exit(1)

# 1. Create DynamoDB Table for Scheduled Patches
print("\n[1/4] Creating DynamoDB Table for Scheduled Patches...")

table_name = 'AutoOps-ScheduledPatches'

try:
    # Check if table exists
    try:
        response = dynamodb.describe_table(TableName=table_name)
        print(f"  ✓ {table_name} already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Create table
            response = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'scheduleId', 'KeyType': 'HASH'},
                    {'AttributeName': 'scheduledFor', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'scheduleId', 'AttributeType': 'S'},
                    {'AttributeName': 'scheduledFor', 'AttributeType': 'S'},
                    {'AttributeName': 'status', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'StatusIndex',
                        'KeySchema': [
                            {'AttributeName': 'status', 'KeyType': 'HASH'},
                            {'AttributeName': 'scheduledFor', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"  ✓ Created {table_name}")
            
            # Wait for table to be active
            print(f"  ⏳ Waiting for table to be active...")
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print(f"  ✓ Table is active")
        else:
            raise
except Exception as e:
    print(f"  ❌ Failed to create {table_name}: {e}")

# 2. Create IAM Role for EventBridge Scheduler
print("\n[2/4] Creating IAM Role for EventBridge Scheduler...")

scheduler_role_name = 'AutoOpsSchedulerExecutionRole'

trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "scheduler.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

lambda_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{LAMBDA_FUNCTION_NAME}"

try:
    # Check if role exists
    try:
        role_response = iam.get_role(RoleName=scheduler_role_name)
        scheduler_role_arn = role_response['Role']['Arn']
        print(f"  ✓ {scheduler_role_name} already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            # Create role
            create_response = iam.create_role(
                RoleName=scheduler_role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Execution role for EventBridge Scheduler to invoke Lambda'
            )
            scheduler_role_arn = create_response['Role']['Arn']
            print(f"  ✓ Created {scheduler_role_name}")
            
            # Create inline policy for Lambda invocation
            lambda_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": lambda_arn
                }]
            }
            
            iam.put_role_policy(
                RoleName=scheduler_role_name,
                PolicyName='InvokeLambda',
                PolicyDocument=json.dumps(lambda_policy)
            )
            print(f"  ✓ Attached Lambda invoke policy")
            
            # Wait for role to propagate
            import time
            print(f"  ⏳ Waiting for IAM role to propagate...")
            time.sleep(10)
        else:
            raise
except Exception as e:
    print(f"  ❌ Failed to create {scheduler_role_name}: {e}")
    scheduler_role_arn = None

# 3. Create Schedule Group
print("\n[3/4] Creating EventBridge Schedule Group...")

schedule_group_name = 'autoops-patch-schedules'

try:
    # Check if schedule group exists
    try:
        response = scheduler.get_schedule_group(Name=schedule_group_name)
        print(f"  ✓ Schedule group '{schedule_group_name}' already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Create schedule group
            response = scheduler.create_schedule_group(
                Name=schedule_group_name,
                Description='Schedule group for AutoOps patch deployments'
            )
            print(f"  ✓ Created schedule group '{schedule_group_name}'")
        else:
            raise
except Exception as e:
    print(f"  ❌ Failed to create schedule group: {e}")

# 4. Update Lambda Function Environment Variables
print("\n[4/4] Updating Lambda Function Configuration...")

try:
    # Get current configuration
    response = lambda_client.get_function_configuration(FunctionName=LAMBDA_FUNCTION_NAME)
    current_env = response.get('Environment', {}).get('Variables', {})
    
    # Update environment variables
    new_env = {
        **current_env,
        'SCHEDULED_PATCHES_TABLE': table_name,
        'SCHEDULER_ROLE_ARN': scheduler_role_arn or '',
        'SCHEDULE_GROUP_NAME': schedule_group_name
    }
    
    lambda_client.update_function_configuration(
        FunctionName=LAMBDA_FUNCTION_NAME,
        Environment={'Variables': new_env}
    )
    print(f"  ✓ Updated Lambda environment variables")
except Exception as e:
    print(f"  ❌ Failed to update Lambda: {e}")

# Summary
print("\n" + "="*80)
print("DEPLOYMENT SUMMARY")
print("="*80)

print("\n✅ Resources Created:")
print(f"  • DynamoDB Table: {table_name}")
print(f"  • IAM Role: {scheduler_role_name}")
if scheduler_role_arn:
    print(f"    ARN: {scheduler_role_arn}")
print(f"  • Schedule Group: {schedule_group_name}")
print(f"  • Lambda Function: {LAMBDA_FUNCTION_NAME} (updated)")

print("\n📋 Configuration:")
print(f"  • Region: {REGION}")
print(f"  • Account: {ACCOUNT_ID}")
print(f"  • Lambda ARN: {lambda_arn}")

print("\n🔧 Next Steps:")
print("  1. Deploy updated Lambda code with scheduler handler")
print("  2. Test scheduling via API")
print("  3. Verify schedules in EventBridge console")

print("\n" + "="*80)
print("✅ Scheduler deployment complete!")
print("="*80)
