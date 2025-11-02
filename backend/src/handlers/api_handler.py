"""
Main API Handler for AutoOps AI
Handles incoming API requests and routes to appropriate services
"""
import json
import os
import logging
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
stepfunctions = boto3.client('stepfunctions')
s3 = boto3.client('s3')

class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert Decimal to int/float for JSON serialization"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    try:
        # Parse request
        http_method = event.get('httpMethod')
        raw_path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = json.loads(event.get('body') or '{}')

        # Normalize path - remove /api prefix if present and trailing slashes
        path = raw_path.replace('/api', '').rstrip('/') or '/'
        
        logger.info(f"Request: {http_method} {raw_path} -> {path}")
        logger.info(f"Path parameters: {path_parameters}")

        # Handle OPTIONS for CORS
        if http_method == 'OPTIONS':
            return cors_response()

        # Route to appropriate handler
        # Inventory endpoints
        if path == '/inventory' or path == '/api/inventory':
            return handle_inventory(event, context)
        elif path.startswith('/scan-device/') or path.startswith('/api/scan-device/'):
            device_id = path.split('/')[-1]
            return handle_scan_device(device_id, context)
        
        # Alerts endpoints
        elif path == '/alerts' or path == '/api/alerts':
            if http_method == 'POST':
                return handle_create_alert(body, context)
            else:
                return handle_get_alerts(event, context)
        elif path == '/alerts/active' or path == '/api/alerts/active':
            return handle_active_alerts(event, context)
        elif path == '/alerts/correlate' or path == '/api/alerts/correlate':
            return handle_alert_correlation(body, context)
        elif '/alerts/' in path and '/acknowledge' in path:
            alert_id = path.split('/alerts/')[-1].split('/')[0]
            return handle_acknowledge_alert(alert_id, context)
        elif '/alerts/' in path and '/resolve' in path:
            alert_id = path.split('/alerts/')[-1].split('/')[0]
            return handle_resolve_alert(alert_id, body, context)
        
        # Patches endpoints
        elif path == '/patches' or path == '/api/patches':
            return handle_get_patches(event, context)
        elif path == '/patches/status' or path == '/api/patches/status':
            return handle_patch_status(event, context)
        elif path == '/patches/deploy' or path == '/api/patches/deploy':
            return handle_patch_deployment(body, context)
        elif '/patches/' in path and '/details' in path:
            patch_id = path.split('/patches/')[-1].split('/')[0]
            return handle_patch_details(patch_id, context)
        
        # AI endpoints
        elif path == '/ai/analyze-patch' or path == '/api/ai/analyze-patch':
            return handle_ai_patch_analysis(body, context)
        
        # Dashboard stats endpoints
        elif path == '/dashboard/stats' or path == '/api/dashboard/stats':
            return handle_dashboard_stats(event, context)
        elif path == '/patch-analysis' or path == '/api/patch-analysis':
            return handle_patch_analysis(event, context)
        elif path == '/patch-schedule' or path == '/api/patch-schedule':
            return handle_get_schedules(event, context)
        
        # Actions and policies
        elif path == '/actions/recent':
            return handle_recent_actions(event, context)
        elif path == '/policies/get':
            return handle_get_policies(event, context)
        elif path == '/policies/update':
            return handle_update_policies(body, context)
        
        # Scheduler endpoints
        elif path == '/schedules' and http_method == 'GET':
            return handle_get_schedules(event, context)
        elif path == '/schedules' and http_method == 'POST':
            return handle_create_schedule(body, context)
        elif path.startswith('/schedules/') and http_method == 'DELETE':
            schedule_id = path.split('/')[-1]
            return handle_cancel_schedule(schedule_id, context)
        elif path.startswith('/schedules/') and http_method == 'GET':
            schedule_id = path.split('/')[-1]
            return handle_get_schedule(schedule_id, context)
        elif path == '/schedules/execute':
            return handle_execute_schedule(body, context)
        
        # Health check
        elif path == '/health' or path == '/':
            return success_response({
                'status': 'healthy',
                'service': 'AutoOps AI API',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'version': '2.0.0'
            })
        
        else:
            logger.warning(f"Endpoint not found: {http_method} {path}")
            return error_response(404, f'Endpoint not found: {path}')

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return error_response(500, str(e))

def cors_response() -> Dict:
    """Return CORS preflight response"""
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': ''
    }

def cors_response() -> Dict:
    """Return CORS preflight response"""
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': ''
    }

def handle_inventory(event: Dict, context: Any) -> Dict:
    """Get device inventory"""
    try:
        from integrations.superops_client import SuperOpsClient
        
        client = SuperOpsClient()
        devices = client.get_device_inventory()
        
        return success_response(devices)
    except Exception as e:
        logger.error(f"Error getting inventory: {e}", exc_info=True)
        # Return mock data
        mock_devices = [
            {
                'id': 1,
                'name': 'PROD-WEB-01',
                'ipAddress': '192.168.1.10',
                'operatingSystem': 'Windows Server 2019',
                'type': 'Server',
                'status': 'online',
                'patchStatus': 'compliant',
                'riskScore': 25.5,
                'vulnerabilityStats': {'total': 2, 'critical': 0, 'high': 0, 'medium': 2, 'low': 0},
                'topVulnerabilities': [{'cveId': 'CVE-2024-7621', 'severity': 'MEDIUM', 'cvssScore': 5.3}]
            },
            {
                'id': 2,
                'name': 'PROD-DB-01',
                'ipAddress': '192.168.1.20',
                'operatingSystem': 'Windows Server 2022',
                'type': 'Server',
                'status': 'online',
                'patchStatus': 'pending',
                'riskScore': 78.2,
                'vulnerabilityStats': {'total': 8, 'critical': 2, 'high': 3, 'medium': 2, 'low': 1},
                'topVulnerabilities': [{'cveId': 'CVE-2024-9123', 'severity': 'CRITICAL', 'cvssScore': 9.8}]
            }
        ]
        return success_response(mock_devices)

def handle_scan_device(device_id: str, context: Any) -> Dict:
    """Trigger device scan"""
    try:
        from integrations.superops_client import SuperOpsClient
        
        client = SuperOpsClient()
        result = client.scan_device(device_id)
        
        return success_response({'message': 'Scan initiated', 'deviceId': device_id, 'result': result})
    except Exception as e:
        logger.error(f"Error scanning device: {e}", exc_info=True)
        return success_response({'message': 'Scan initiated (mock)', 'deviceId': device_id})

def handle_get_alerts(event: Dict, context: Any) -> Dict:
    """Get all alerts"""
    try:
        from integrations.superops_client import SuperOpsClient
        
        client = SuperOpsClient()
        alerts = client.get_alerts()
        
        return success_response(alerts)
    except Exception as e:
        logger.error(f"Error getting alerts: {e}", exc_info=True)
        # Return mock alerts
        mock_alerts = [
            {
                'id': 1,
                'title': 'High CPU Usage',
                'severity': 'critical',
                'status': 'active',
                'deviceId': 2,
                'deviceName': 'PROD-DB-01',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        ]
        return success_response(mock_alerts)

def handle_create_alert(body: Dict, context: Any) -> Dict:
    """Create a new alert"""
    try:
        alerts_table = os.getenv('ALERTS_TABLE_NAME', 'AutoOps-Alerts')
        table = dynamodb.Table(alerts_table)
        
        alert_id = f"alert-{datetime.now(timezone.utc).timestamp()}"
        alert_record = {
            'alertId': alert_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'title': body.get('title'),
            'description': body.get('description'),
            'severity': body.get('severity', 'medium'),
            'deviceId': body.get('deviceId'),
            'status': 'active'
        }
        
        table.put_item(Item=alert_record)
        
        return success_response({'alertId': alert_id, **alert_record})
    except Exception as e:
        logger.error(f"Error creating alert: {e}", exc_info=True)
        return error_response(500, str(e))

def handle_acknowledge_alert(alert_id: str, context: Any) -> Dict:
    """Acknowledge an alert"""
    try:
        alerts_table = os.getenv('ALERTS_TABLE_NAME', 'AutoOps-Alerts')
        table = dynamodb.Table(alerts_table)
        
        table.update_item(
            Key={'alertId': alert_id},
            UpdateExpression='SET #status = :status, acknowledgedAt = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'acknowledged',
                ':timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
        
        return success_response({'message': 'Alert acknowledged', 'alertId': alert_id})
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}", exc_info=True)
        return success_response({'message': 'Alert acknowledged (mock)', 'alertId': alert_id})

def handle_resolve_alert(alert_id: str, body: Dict, context: Any) -> Dict:
    """Resolve an alert"""
    try:
        alerts_table = os.getenv('ALERTS_TABLE_NAME', 'AutoOps-Alerts')
        table = dynamodb.Table(alerts_table)
        
        table.update_item(
            Key={'alertId': alert_id},
            UpdateExpression='SET #status = :status, resolvedAt = :timestamp, resolution = :resolution',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'resolved',
                ':timestamp': datetime.now(timezone.utc).isoformat(),
                ':resolution': body.get('resolution', 'Resolved')
            }
        )
        
        return success_response({'message': 'Alert resolved', 'alertId': alert_id})
    except Exception as e:
        logger.error(f"Error resolving alert: {e}", exc_info=True)
        return success_response({'message': 'Alert resolved (mock)', 'alertId': alert_id})

def handle_get_patches(event: Dict, context: Any) -> Dict:
    """Get all available patches"""
    try:
        from integrations.superops_client import SuperOpsClient
        
        client = SuperOpsClient()
        patches = client.get_patch_status()
        
        # Auto-generate alerts for Critical/High patches
        generate_patch_alerts(patches)
        
        return success_response(patches)
    except Exception as e:
        logger.error(f"Error getting patches: {e}", exc_info=True)
        # Return mock patches
        mock_patches = [
            {
                'id': 'KB5034441',
                'title': 'Windows 11 Security Update',
                'description': 'Cumulative security update',
                'severity': 'CRITICAL',
                'releaseDate': '2024-01-09',
                'relatedCVEs': ['CVE-2024-9123', 'CVE-2024-8956'],
                'affectedDevices': [1, 2],
                'status': 'AVAILABLE',
                'vendor': 'Microsoft',
                'size': '450 MB',
                'requiresReboot': True
            },
            {
                'id': 'KB5034439',
                'title': 'Windows Server 2022 Update',
                'description': 'Monthly rollup',
                'severity': 'HIGH',
                'releaseDate': '2024-01-09',
                'relatedCVEs': ['CVE-2024-8745'],
                'affectedDevices': [3, 4],
                'status': 'AVAILABLE',
                'vendor': 'Microsoft',
                'size': '320 MB',
                'requiresReboot': True
            }
        ]
        
        # Generate alerts for mock patches too
        generate_patch_alerts(mock_patches)
        
        return success_response(mock_patches)

def generate_patch_alerts(patches: list) -> None:
    """Auto-generate alerts for Critical and High severity patches"""
    try:
        alerts_table = os.getenv('ALERTS_TABLE_NAME', 'AutoOps-Alerts')
        table = dynamodb.Table(alerts_table)
        
        # Filter for Critical and High patches that are AVAILABLE
        high_priority_patches = [
            p for p in patches 
            if p.get('severity') in ['CRITICAL', 'HIGH'] and p.get('status') == 'AVAILABLE'
        ]
        
        for patch in high_priority_patches:
            # Check if alert already exists for this patch
            try:
                response = table.scan(
                    FilterExpression='patchId = :patchId AND #status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':patchId': patch.get('id'),
                        ':status': 'active'
                    },
                    Limit=1
                )
                
                if response.get('Items'):
                    continue  # Alert already exists
            except Exception as scan_error:
                logger.warning(f"Error checking for existing alert: {scan_error}")
                continue
            
            # Create new alert
            alert_id = f"alert-patch-{patch.get('id')}-{int(datetime.now(timezone.utc).timestamp())}"
            severity = 'critical' if patch.get('severity') == 'CRITICAL' else 'high'
            
            alert_record = {
                'alertId': alert_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'title': f"{patch.get('severity')} Patch Available: {patch.get('title', 'Unknown')}",
                'description': f"A {patch.get('severity')} severity patch is available affecting {len(patch.get('affectedDevices', []))} devices. "
                              f"Related CVEs: {', '.join(patch.get('relatedCVEs', [])[:3])}. "
                              f"{patch.get('description', '')}",
                'severity': severity,
                'deviceId': patch.get('affectedDevices', [None])[0] if patch.get('affectedDevices') else None,
                'patchId': patch.get('id'),
                'patchTitle': patch.get('title'),
                'affectedDeviceCount': len(patch.get('affectedDevices', [])),
                'relatedCVEs': patch.get('relatedCVEs', []),
                'status': 'active',
                'source': 'auto-generated',
                'requiresAction': True
            }
            
            table.put_item(Item=alert_record)
            logger.info(f"Auto-generated alert for {severity} patch: {patch.get('id')}")
            
    except Exception as e:
        logger.error(f"Error generating patch alerts: {e}", exc_info=True)

def handle_patch_details(patch_id: str, context: Any) -> Dict:
    """Get detailed information about a specific patch"""
    try:
        from integrations.superops_client import SuperOpsClient
        
        client = SuperOpsClient()
        patches = client.get_patch_status()
        patch = next((p for p in patches if p.get('id') == patch_id), None)
        
        if patch:
            return success_response(patch)
        else:
            return error_response(404, f'Patch {patch_id} not found')
    except Exception as e:
        logger.error(f"Error getting patch details: {e}", exc_info=True)
        return error_response(500, str(e))

def handle_dashboard_stats(event: Dict, context: Any) -> Dict:
    """Get dashboard statistics"""
    try:
        from integrations.superops_client import SuperOpsClient
        
        client = SuperOpsClient()
        devices = client.get_device_inventory()
        patches = client.get_patch_status()
        alerts = client.get_alerts({'status': 'ACTIVE'})
        
        critical_vulns = sum(d.get('vulnerabilityStats', {}).get('critical', 0) for d in devices)
        
        return success_response({
            'totalDevices': len(devices),
            'criticalVulnerabilities': critical_vulns,
            'activeAlerts': len(alerts),
            'pendingPatches': len([p for p in patches if p.get('status') == 'AVAILABLE'])
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}", exc_info=True)
        return success_response({
            'totalDevices': 0,
            'criticalVulnerabilities': 0,
            'activeAlerts': 0,
            'pendingPatches': 0
        })

def handle_patch_analysis(event: Dict, context: Any) -> Dict:
    """Get patch analysis"""
    try:
        from integrations.superops_client import SuperOpsClient
        
        client = SuperOpsClient()
        patches = client.get_patch_status()
        
        return success_response(patches)
    except Exception as e:
        logger.error(f"Error getting patch analysis: {e}", exc_info=True)
        return success_response([])

def handle_patch_status(event: Dict, context: Any) -> Dict:
    """Get current patch status across all devices"""
    try:
        from integrations.superops_client import SuperOpsClient
        
        client = SuperOpsClient()
        
        # Get devices and patches from SuperOps
        devices = client.get_device_inventory()
        patches = client.get_patch_status()
        
        # Aggregate statistics
        total_devices = len(devices)
        
        # Calculate compliance based on device patch status
        compliant = sum(1 for p in patches if p.get('status') == 'DEPLOYED')
        pending = sum(1 for p in patches if p.get('status') == 'AVAILABLE')
        critical_patches = sum(1 for p in patches if p.get('severity') == 'CRITICAL')
        
        return success_response({
            'totalDevices': total_devices,
            'totalPatches': len(patches),
            'compliant': compliant,
            'pending': pending,
            'criticalPatches': critical_patches,
            'patches': patches,
            'devices': devices,
            'lastUpdate': datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Error in handle_patch_status: {e}", exc_info=True)
        # Return mock data on error
        return success_response({
            'totalDevices': 0,
            'totalPatches': 0,
            'compliant': 0,
            'pending': 0,
            'criticalPatches': 0,
            'patches': [],
            'devices': [],
            'lastUpdate': datetime.now(timezone.utc).isoformat(),
            'error': 'Using fallback data - SuperOps API unavailable'
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

def handle_ai_patch_analysis(body: Dict, context: Any) -> Dict:
    """Analyze patch using AI"""
    try:
        from services.ai_agent_service import get_ai_service
        
        patch_data = body.get('patch', {})
        devices = body.get('devices', [])
        vulnerabilities = body.get('vulnerabilities', [])
        
        # Get AI analysis
        ai_service = get_ai_service()
        analysis = ai_service.analyze_patch_risk(patch_data, devices, vulnerabilities)
        
        # Store analysis in DynamoDB for audit trail
        actions_table = os.getenv('ACTIONS_TABLE_NAME', 'AutoOps-Actions')
        table = dynamodb.Table(actions_table)
        
        action_record = {
            'actionId': f"patch-analysis-{datetime.now(timezone.utc).timestamp()}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': 'PATCH_ANALYSIS',
            'patchId': patch_data.get('id'),
            'patchTitle': patch_data.get('title'),
            'recommendation': analysis.get('recommendation'),
            'riskLevel': analysis.get('riskLevel'),
            'devicesAnalyzed': len(devices),
            'result': json.dumps(analysis),
            'status': 'COMPLETED'
        }
        
        table.put_item(Item=action_record)
        
        logger.info(f"AI patch analysis completed for {patch_data.get('id')}: {analysis.get('recommendation')}")
        
        return success_response(analysis)
        
    except Exception as e:
        logger.error(f"Error in AI patch analysis: {e}", exc_info=True)
        # Return fallback analysis
        from services.ai_agent_service import AIAgentService
        ai = AIAgentService()
        fallback = ai._generate_fallback_analysis(
            body.get('patch', {}),
            body.get('devices', []),
            body.get('vulnerabilities', [])
        )
        return success_response(fallback)

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
    """Trigger AI-based alert correlation using AWS Bedrock"""
    try:
        from integrations.superops_client import SuperOpsClient
        from services.ai_agent_service import get_ai_service
        
        alert_ids = body.get('alertIds', [])
        
        # Get alerts from SuperOps
        client = SuperOpsClient()
        all_alerts = client.get_alerts({'status': 'ACTIVE'})
        
        # Filter to requested alerts or use all if none specified
        if alert_ids:
            alerts_to_correlate = [a for a in all_alerts if a.get('id') in alert_ids]
        else:
            alerts_to_correlate = all_alerts
        
        # Use AI service for correlation
        ai_service = get_ai_service()
        correlation_result = ai_service.correlate_alerts(alerts_to_correlate)
        
        # Store correlation result in DynamoDB
        actions_table = os.getenv('ACTIONS_TABLE_NAME', 'AutoOps-Actions')
        table = dynamodb.Table(actions_table)
        
        action_record = {
            'actionId': f"correlation-{datetime.now(timezone.utc).timestamp()}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': 'ALERT_CORRELATION',
            'alertsAnalyzed': len(alerts_to_correlate),
            'groupsFound': len(correlation_result.get('correlationGroups', [])),
            'result': json.dumps(correlation_result),
            'status': 'COMPLETED'
        }
        
        table.put_item(Item=action_record)
        
        return success_response({
            'correlation': correlation_result,
            'alertsAnalyzed': len(alerts_to_correlate),
            'actionId': action_record['actionId'],
            'status': 'COMPLETED'
        })
        
    except Exception as e:
        logger.error(f"Error in alert correlation: {e}", exc_info=True)
        return error_response(500, f"Alert correlation failed: {str(e)}")

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

def handle_get_schedules(event: Dict, context: Any) -> Dict:
    """Get all scheduled patch deployments"""
    from handlers.patch_scheduler import get_scheduled_patches
    
    query_params = event.get('queryStringParameters', {}) or {}
    status = query_params.get('status')
    
    result = get_scheduled_patches(status)
    return success_response(result)

def handle_create_schedule(body: Dict, context: Any) -> Dict:
    """Create a new scheduled patch deployment"""
    from handlers.patch_scheduler import create_patch_schedule
    from services.ai_agent_service import get_ai_service
    
    # Get AI recommendation if not already provided
    ai_approved = body.get('aiApproved', False)
    
    if not ai_approved and body.get('enableAI', True):
        try:
            ai_service = get_ai_service()
            patch_data = {
                'id': body.get('patchId'),
                'title': body.get('patchTitle'),
                'severity': body.get('severity', 'MEDIUM')
            }
            
            analysis = ai_service.analyze_patch_risk(patch_data, [], [])
            
            # Auto-approve if risk level is low (< 4) and AI recommends APPROVE
            if analysis.get('riskLevel', 10) < 4 and analysis.get('recommendation') == 'APPROVE':
                logger.info(f"AI auto-approved patch {body.get('patchId')} - Risk: {analysis.get('riskLevel')}")
                body['aiApproved'] = True
                body['aiRiskLevel'] = analysis.get('riskLevel')
                body['aiRecommendation'] = analysis.get('recommendation')
            else:
                logger.info(f"AI requires review for patch {body.get('patchId')} - Risk: {analysis.get('riskLevel')}")
                body['aiApproved'] = False
                body['aiRiskLevel'] = analysis.get('riskLevel')
                body['aiRecommendation'] = analysis.get('recommendation')
        except Exception as ai_error:
            logger.warning(f"AI analysis failed, proceeding without approval: {ai_error}")
    
    result = create_patch_schedule(body)
    
    if result.get('success'):
        # Return the schedule count in the response for real-time UI updates
        from handlers.patch_scheduler import get_scheduled_patches
        schedule_stats = get_scheduled_patches('SCHEDULED')
        
        return success_response({
            **result,
            'scheduleCount': schedule_stats.get('count', 0),
            'schedules': schedule_stats.get('schedules', [])
        })
    else:
        return error_response(400, result.get('error', 'Failed to create schedule'))

def handle_cancel_schedule(schedule_id: str, context: Any) -> Dict:
    """Cancel a scheduled patch deployment"""
    from handlers.patch_scheduler import cancel_patch_schedule, get_scheduled_patches
    
    result = cancel_patch_schedule(schedule_id)
    
    if result.get('success'):
        # Return updated schedule count
        schedule_stats = get_scheduled_patches('SCHEDULED')
        
        return success_response({
            **result,
            'scheduleCount': schedule_stats.get('count', 0),
            'schedules': schedule_stats.get('schedules', [])
        })
    else:
        return error_response(400, result.get('error', 'Failed to cancel schedule'))

def handle_get_schedule(schedule_id: str, context: Any) -> Dict:
    """Get details of a specific schedule"""
    from handlers.patch_scheduler import get_schedule_details
    
    result = get_schedule_details(schedule_id)
    
    if result.get('success'):
        return success_response(result)
    else:
        return error_response(404, result.get('error', 'Schedule not found'))

def handle_execute_schedule(body: Dict, context: Any) -> Dict:
    """Execute a scheduled patch deployment (called by EventBridge)"""
    from handlers.patch_scheduler import execute_scheduled_patch
    
    schedule_id = body.get('scheduleId')
    patch_id = body.get('patchId')
    device_ids = body.get('deviceIds', [])
    
    result = execute_scheduled_patch(schedule_id, patch_id, device_ids)
    
    if result.get('success'):
        return success_response(result)
    else:
        return error_response(500, result.get('error', 'Failed to execute schedule'))

def success_response(data: Any) -> Dict:
    """Return success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data, cls=DecimalEncoder)
    }

def error_response(status_code: int, message: str) -> Dict:
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message}, cls=DecimalEncoder)
    }
