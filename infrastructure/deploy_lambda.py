#!/usr/bin/env python3
"""
Deploy Lambda Functions for AutoOps AI
"""

import boto3
import os
import zipfile
import time
from pathlib import Path

REGION = 'us-east-2'
ACCOUNT_ID = '358262661344'
ROLE_ARN = f'arn:aws:iam::{ACCOUNT_ID}:role/AutoOpsLambdaExecutionRole'

print("="*80)
print("AutoOps AI - Lambda Functions Deployment")
print("="*80)

lambda_client = boto3.client('lambda', region_name=REGION)
apigateway = boto3.client('apigateway', region_name=REGION)

# Package Lambda function
print("\n[1/3] Packaging Lambda function...")

package_dir = Path('../backend/lambda_package')
package_dir.mkdir(exist_ok=True)

# Create deployment package
zip_path = Path('../backend/ai_agents_lambda.zip')

print("  Creating ZIP package...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # Add handler
    handler_path = Path('../backend/src/handlers/ai_agents_handler.py')
    if handler_path.exists():
        zipf.write(handler_path, 'ai_agents_handler.py')
        print(f"    ✓ Added ai_agents_handler.py")
    
    # Add ai_agents module
    ai_agents_dir = Path('../backend/src/ai_agents')
    if ai_agents_dir.exists():
        for py_file in ai_agents_dir.glob('*.py'):
            zipf.write(py_file, f'ai_agents/{py_file.name}')
            print(f"    ✓ Added ai_agents/{py_file.name}")
    
    # Add integrations
    integrations_dir = Path('../backend/src/integrations')
    if integrations_dir.exists():
        for py_file in integrations_dir.glob('*.py'):
            zipf.write(py_file, f'integrations/{py_file.name}')
            print(f"    ✓ Added integrations/{py_file.name}")

print(f"  ✓ Package created: {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")

# Deploy Lambda function
print("\n[2/3] Deploying Lambda function...")

function_name = 'autoops-ai-agents'

try:
    # Check if function exists
    try:
        lambda_client.get_function(FunctionName=function_name)
        print(f"  Updating existing function: {function_name}")
        
        # Update code
        with open(zip_path, 'rb') as f:
            lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=f.read()
            )
        
        # Update configuration
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Runtime='python3.11',
            Handler='ai_agents_handler.lambda_handler',
            Role=ROLE_ARN,
            Timeout=180,
            MemorySize=2048,
            Environment={
                'Variables': {
                    'BEDROCK_MODEL': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                    'USE_CREWAI': 'true'
                }
            }
        )
        print(f"  ✓ Updated {function_name}")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"  Creating new function: {function_name}")
        
        with open(zip_path, 'rb') as f:
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=ROLE_ARN,
                Handler='ai_agents_handler.lambda_handler',
                Code={'ZipFile': f.read()},
                Timeout=180,
                MemorySize=2048,
                Environment={
                    'Variables': {
                        'BEDROCK_MODEL': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                        'USE_CREWAI': 'true'
                    }
                }
            )
        
        print(f"  ✓ Created {function_name}")
        print(f"    ARN: {response['FunctionArn']}")
        
        # Wait for function to be active
        print("  Waiting for function to be active...")
        time.sleep(5)
    
    # Add API Gateway permission
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='apigateway-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com'
        )
        print("  ✓ Added API Gateway permission")
    except lambda_client.exceptions.ResourceConflictException:
        print("  ✓ API Gateway permission already exists")
        
except Exception as e:
    print(f"  ❌ Failed to deploy Lambda: {e}")
    exit(1)

# Create API Gateway
print("\n[3/3] Creating API Gateway...")

api_name = 'AutoOps-AI-API'

try:
    # Check if API exists
    apis = apigateway.get_rest_apis()
    existing_api = next((api for api in apis['items'] if api['name'] == api_name), None)
    
    if existing_api:
        api_id = existing_api['id']
        print(f"  ✓ Using existing API: {api_id}")
    else:
        # Create REST API
        response = apigateway.create_rest_api(
            name=api_name,
            description='AutoOps AI Agent API',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        api_id = response['id']
        print(f"  ✓ Created API: {api_id}")
    
    # Get root resource
    resources = apigateway.get_resources(restApiId=api_id)
    root_id = next(r['id'] for r in resources['items'] if r['path'] == '/')
    
    # Create /ai resource
    try:
        ai_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='ai'
        )
        ai_id = ai_resource['id']
        print(f"  ✓ Created /ai resource")
    except apigateway.exceptions.ConflictException:
        ai_id = next(r['id'] for r in resources['items'] if r.get('pathPart') == 'ai')
        print(f"  ✓ Using existing /ai resource")
    
    # Create /ai/agents resource
    try:
        resources = apigateway.get_resources(restApiId=api_id)
        agents_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=ai_id,
            pathPart='agents'
        )
        agents_id = agents_resource['id']
        print(f"  ✓ Created /ai/agents resource")
    except apigateway.exceptions.ConflictException:
        resources = apigateway.get_resources(restApiId=api_id)
        agents_id = next(r['id'] for r in resources['items'] if r.get('pathPart') == 'agents')
        print(f"  ✓ Using existing /ai/agents resource")
    
    # Create {proxy+} resource for all paths
    try:
        proxy_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=agents_id,
            pathPart='{proxy+}'
        )
        proxy_id = proxy_resource['id']
        print("  ✓ Created /ai/agents/{proxy+} resource")
    except apigateway.exceptions.ConflictException:
        resources = apigateway.get_resources(restApiId=api_id)
        proxy_id = next((r['id'] for r in resources['items'] if r.get('pathPart') == '{proxy+}'), None)
        print("  ✓ Using existing /ai/agents/{proxy+} resource")
    
    # Create ANY method
    lambda_arn = f'arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{function_name}'
    
    try:
        apigateway.put_method(
            restApiId=api_id,
            resourceId=proxy_id,
            httpMethod='ANY',
            authorizationType='NONE'
        )
        print(f"  ✓ Created ANY method")
    except apigateway.exceptions.ConflictException:
        print(f"  ✓ ANY method already exists")
    
    # Set up Lambda integration
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=proxy_id,
        httpMethod='ANY',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f'arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    )
    print(f"  ✓ Configured Lambda integration")
    
    # Deploy API
    try:
        apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Production deployment'
        )
        print(f"  ✓ Deployed to prod stage")
    except Exception as e:
        print(f"  ⚠ Deployment note: {e}")
    
    # Get API endpoint
    endpoint = f"https://{api_id}.execute-api.{REGION}.amazonaws.com/prod"
    
    print("\n" + "="*80)
    print("✅ Lambda and API Gateway deployment complete!")
    print("="*80)
    print(f"\nAPI Endpoint: {endpoint}")
    print(f"\nTest endpoints:")
    print(f"  {endpoint}/ai/agents/status")
    print(f"  {endpoint}/ai/agents/prioritize")
    print(f"  {endpoint}/ai/agents/correlate-alerts")
    print(f"  {endpoint}/ai/agents/decide-remediation")
    print(f"  {endpoint}/ai/agents/learn")
    print("="*80)
    
except Exception as e:
    print(f"  ❌ Failed to create API Gateway: {e}")
    import traceback
    traceback.print_exc()
