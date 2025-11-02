"""
Add Scheduler Routes to API Gateway
Adds scheduler-related routes to existing API Gateway
"""
import boto3
import sys
import json
from botocore.exceptions import ClientError

REGION = 'us-east-2'
API_GATEWAY_ID = '83d0wk5nj8'
LAMBDA_FUNCTION_ARN = 'arn:aws:lambda:us-east-2:358262661344:function:autoops-ai-agents'
ACCOUNT_ID = '358262661344'

client = boto3.client('apigateway', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)

def get_root_resource():
    """Get the root resource ID"""
    response = client.get_resources(restApiId=API_GATEWAY_ID)
    for item in response['items']:
        if item['path'] == '/':
            return item['id']
    return None

def create_resource(parent_id, path_part):
    """Create a new resource"""
    try:
        response = client.create_resource(
            restApiId=API_GATEWAY_ID,
            parentId=parent_id,
            pathPart=path_part
        )
        print(f"  ✓ Created resource: /{path_part}")
        return response['id']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            # Resource already exists, find it
            resources = client.get_resources(restApiId=API_GATEWAY_ID)
            for item in resources['items']:
                if item.get('pathPart') == path_part:
                    print(f"  ℹ Resource already exists: /{path_part}")
                    return item['id']
        raise

def create_method(resource_id, http_method):
    """Create a method for a resource"""
    try:
        # Create method
        client.put_method(
            restApiId=API_GATEWAY_ID,
            resourceId=resource_id,
            httpMethod=http_method,
            authorizationType='NONE'
        )
        
        # Create integration
        client.put_integration(
            restApiId=API_GATEWAY_ID,
            resourceId=resource_id,
            httpMethod=http_method,
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{LAMBDA_FUNCTION_ARN}/invocations'
        )
        
        print(f"  ✓ Created method: {http_method}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            print(f"  ℹ Method already exists: {http_method}")
            return False
        raise

def add_lambda_permission(resource_path, http_method):
    """Add permission for API Gateway to invoke Lambda"""
    statement_id = f"apigateway-{resource_path.replace('/', '-')}-{http_method}"
    
    try:
        lambda_client.add_permission(
            FunctionName='autoops-ai-agents',
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{API_GATEWAY_ID}/*/{http_method}/{resource_path}'
        )
        print(f"  ✓ Added Lambda permission for {http_method} /{resource_path}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print(f"  ℹ Permission already exists for {http_method} /{resource_path}")
        else:
            print(f"  ⚠ Warning: Could not add permission: {e}")

def deploy_api():
    """Deploy the API to production stage"""
    try:
        client.create_deployment(
            restApiId=API_GATEWAY_ID,
            stageName='production',
            description='Added scheduler endpoints'
        )
        print("  ✓ Deployed API to production stage")
    except ClientError as e:
        print(f"  ❌ Failed to deploy API: {e}")

def main():
    print("=" * 80)
    print("AutoOps AI - Adding Scheduler Routes to API Gateway")
    print("=" * 80)
    print(f"API Gateway ID: {API_GATEWAY_ID}")
    print(f"Region: {REGION}")
    print("=" * 80)
    print()
    
    try:
        # Get root resource
        root_id = get_root_resource()
        if not root_id:
            print("❌ Could not find root resource")
            sys.exit(1)
        
        # Create /schedules resource
        print("[1/5] Creating /schedules resource...")
        schedules_id = create_resource(root_id, 'schedules')
        
        # Add methods to /schedules
        print("\n[2/5] Adding methods to /schedules...")
        create_method(schedules_id, 'GET')  # List schedules
        create_method(schedules_id, 'POST')  # Create schedule
        create_method(schedules_id, 'OPTIONS')  # CORS preflight
        
        # Create /schedules/{scheduleId} resource
        print("\n[3/5] Creating /schedules/{scheduleId} resource...")
        schedule_id_resource = create_resource(schedules_id, '{scheduleId}')
        
        # Add methods to /schedules/{scheduleId}
        print("\n[4/5] Adding methods to /schedules/{scheduleId}...")
        create_method(schedule_id_resource, 'GET')  # Get schedule details
        create_method(schedule_id_resource, 'DELETE')  # Cancel schedule
        create_method(schedule_id_resource, 'OPTIONS')  # CORS preflight
        
        # Add Lambda permissions
        print("\n[5/5] Adding Lambda permissions...")
        add_lambda_permission('schedules', 'GET')
        add_lambda_permission('schedules', 'POST')
        add_lambda_permission('schedules/{scheduleId}', 'GET')
        add_lambda_permission('schedules/{scheduleId}', 'DELETE')
        
        # Deploy API
        print("\n[6/6] Deploying API...")
        deploy_api()
        
        print("\n" + "=" * 80)
        print("✅ Scheduler routes added successfully!")
        print("=" * 80)
        print("\n📋 Available Endpoints:")
        print(f"  • GET    https://{API_GATEWAY_ID}.execute-api.{REGION}.amazonaws.com/production/schedules")
        print(f"  • POST   https://{API_GATEWAY_ID}.execute-api.{REGION}.amazonaws.com/production/schedules")
        print(f"  • GET    https://{API_GATEWAY_ID}.execute-api.{REGION}.amazonaws.com/production/schedules/{{scheduleId}}")
        print(f"  • DELETE https://{API_GATEWAY_ID}.execute-api.{REGION}.amazonaws.com/production/schedules/{{scheduleId}}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
