"""
Main API Handler for AutoOps AI
Handles incoming API requests and routes to appropriate services
"""
import json
import os
import logging
from typing import Dict, Any
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
stepfunctions = boto3.client('stepfunctions')
s3 = boto3.client('s3')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    try:
        # Parse request
        http_method = event.get('httpMethod')
        path = event.get('path')
        body = json.loads(event.get('body', '{}'))

        logger.info(f"Request: {http_method} {path}")

        # Route to appropriate handler
        if path == '/patches/status':
            return handle_patch_status(event, context)
        elif path == '/patches/deploy':
            return handle_patch_deployment(body, context)
        elif path == '/alerts/active':
            return handle_active_alerts(event, context)
        elif path == '/alerts/correlate':
            return handle_alert_correlation(body, context)
        elif path == '/actions/recent':
            return handle_recent_actions(event, context)
        elif path == '/policies/get':
            return handle_get_policies(event, context)
        elif path == '/policies/update':
            return handle_update_policies(body, context)
        else:
            return error_response(404, 'Endpoint not found')

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return error_response(500, str(e))

def handle_patch_status(event: Dict, context: Any) -> Dict:
    """Get current patch status across all devices"""
    from integrations.superops_client import SuperOpsClient

    client = SuperOpsClient()
    devices = client.get_device_inventory()
    patch_status = client.get_patch_status()

    # Aggregate statistics
    total_devices = len(devices)
    compliant = sum(1 for p in patch_status if p.get('complianceStatus') == 'COMPLIANT')
    pending = sum(p.get('pendingPatches', 0) for p in patch_status)

    return success_response({
        'totalDevices': total_devices,
        'compliant': compliant,
        'pending': pending,
        'details': patch_status[:50]  # Return first 50 for dashboard
    })

def handle_patch_deployment(body: Dict, context: Any) -> Dict:
    """Initiate patch deployment workflow"""
    device_ids = body.get('deviceIds', [])
    patch_ids = body.get('patchIds', [])
    approval_required = body.get('approvalRequired', True)

    # Start Step Functions workflow
    state_machine_arn = os.getenv('PATCH_DEPLOYMENT_STATE_MACHINE_ARN')

    execution = stepfunctions.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps({
            'deviceIds': device_ids,
            'patchIds': patch_ids,
            'approvalRequired': approval_required,
            'requestedBy': body.get('requestedBy', 'system')
        })
    )

    return success_response({
        'executionArn': execution['executionArn'],
        'startDate': execution['startDate'].isoformat(),
        'status': 'INITIATED'
    })

def handle_active_alerts(event: Dict, context: Any) -> Dict:
    """Get active alerts from SuperOps"""
    from integrations.superops_client import SuperOpsClient

    client = SuperOpsClient()
    alerts = client.get_alerts({'status': 'ACTIVE'})

    # Sort by severity
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    sorted_alerts = sorted(
        alerts,
        key=lambda x: severity_order.get(x.get('severity', 'low').lower(), 4)
    )

    return success_response(sorted_alerts)

def handle_alert_correlation(body: Dict, context: Any) -> Dict:
    """Trigger AI-based alert correlation"""
    alert_ids = body.get('alertIds', [])

    # Start Step Functions workflow for alert processing
    state_machine_arn = os.getenv('ALERT_PROCESSING_STATE_MACHINE_ARN')

    execution = stepfunctions.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps({
            'alertIds': alert_ids,
            'action': 'correlate'
        })
    )

    return success_response({
        'executionArn': execution['executionArn'],
        'status': 'PROCESSING'
    })

def handle_recent_actions(event: Dict, context: Any) -> Dict:
    """Get recent AI actions from DynamoDB"""
    table_name = os.getenv('ACTIONS_TABLE_NAME')
    table = dynamodb.Table(table_name)

    # Query recent actions
    response = table.scan(Limit=50)
    actions = response.get('Items', [])

    # Sort by timestamp descending
    sorted_actions = sorted(
        actions,
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )

    return success_response(sorted_actions)

def handle_get_policies(event: Dict, context: Any) -> Dict:
    """Get current automation policies"""
    table_name = os.getenv('POLICIES_TABLE_NAME')
    table = dynamodb.Table(table_name)

    response = table.scan()
    policies = response.get('Items', [])

    return success_response(policies)

def handle_update_policies(body: Dict, context: Any) -> Dict:
    """Update automation policies"""
    table_name = os.getenv('POLICIES_TABLE_NAME')
    table = dynamodb.Table(table_name)

    policy_id = body.get('policyId')
    policy_data = body.get('policyData')

    table.put_item(Item={
        'policyId': policy_id,
        **policy_data
    })

    return success_response({'message': 'Policy updated successfully'})

def success_response(data: Any) -> Dict:
    """Return success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data)
    }

def error_response(status_code: int, message: str) -> Dict:
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }
