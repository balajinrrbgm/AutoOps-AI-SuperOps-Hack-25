"""
Patch Scheduler Handler
Manages scheduled patch deployments using AWS EventBridge Scheduler
"""
import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import boto3
from botocore.exceptions import ClientError
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
scheduler_client = boto3.client('scheduler')
lambda_client = boto3.client('lambda')

SCHEDULED_PATCHES_TABLE = os.getenv('SCHEDULED_PATCHES_TABLE', 'AutoOps-ScheduledPatches')
SCHEDULER_ROLE_ARN = os.getenv('SCHEDULER_ROLE_ARN')
SCHEDULE_GROUP_NAME = os.getenv('SCHEDULE_GROUP_NAME', 'autoops-patch-schedules')
LAMBDA_FUNCTION_ARN = os.getenv('AWS_LAMBDA_FUNCTION_NAME')


def create_patch_schedule(patch_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a scheduled patch deployment
    
    Args:
        patch_data: {
            'patchId': str,
            'patchTitle': str,
            'deviceIds': List[str],
            'scheduledFor': str (ISO timestamp),
            'severity': str,
            'requestedBy': str
        }
    
    Returns:
        Dict with schedule details
    """
    try:
        schedule_id = str(uuid.uuid4())
        scheduled_for = patch_data.get('scheduledFor')
        
        # Parse scheduled time
        if isinstance(scheduled_for, int):
            # Unix timestamp in milliseconds
            scheduled_dt = datetime.fromtimestamp(scheduled_for / 1000, tz=timezone.utc)
        else:
            # ISO format string
            scheduled_dt = datetime.fromisoformat(scheduled_for.replace('Z', '+00:00'))
        
        scheduled_iso = scheduled_dt.isoformat()
        
        # Store in DynamoDB
        table = dynamodb.Table(SCHEDULED_PATCHES_TABLE)
        
        schedule_item = {
            'scheduleId': schedule_id,
            'scheduledFor': scheduled_iso,
            'patchId': patch_data.get('patchId'),
            'patchTitle': patch_data.get('patchTitle'),
            'deviceIds': patch_data.get('deviceIds', []),
            'deviceCount': len(patch_data.get('deviceIds', [])),
            'severity': patch_data.get('severity', 'MEDIUM'),
            'status': 'SCHEDULED',
            'requestedBy': patch_data.get('requestedBy', 'system'),
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat()
        }
        
        table.put_item(Item=schedule_item)
        logger.info(f"Created schedule {schedule_id} in DynamoDB")
        
        # Create EventBridge Schedule
        schedule_expression = f"at({scheduled_dt.strftime('%Y-%m-%dT%H:%M:%S')})"
        
        target_input = {
            'action': 'execute_scheduled_patch',
            'scheduleId': schedule_id,
            'patchId': patch_data.get('patchId'),
            'deviceIds': patch_data.get('deviceIds', [])
        }
        
        try:
            scheduler_client.create_schedule(
                Name=f"patch-{schedule_id}",
                GroupName=SCHEDULE_GROUP_NAME,
                ScheduleExpression=schedule_expression,
                Target={
                    'Arn': f"arn:aws:lambda:{os.getenv('AWS_REGION')}:{os.getenv('AWS_ACCOUNT_ID')}:function:{os.getenv('AWS_LAMBDA_FUNCTION_NAME')}",
                    'RoleArn': SCHEDULER_ROLE_ARN,
                    'Input': json.dumps(target_input)
                },
                FlexibleTimeWindow={'Mode': 'OFF'},
                Description=f"Scheduled deployment for {patch_data.get('patchTitle')}"
            )
            logger.info(f"Created EventBridge schedule patch-{schedule_id}")
        except ClientError as e:
            logger.error(f"Failed to create EventBridge schedule: {e}")
            # Continue - schedule is still in DynamoDB for manual execution
        
        return {
            'success': True,
            'scheduleId': schedule_id,
            'scheduledFor': scheduled_iso,
            'patchTitle': patch_data.get('patchTitle'),
            'deviceCount': len(patch_data.get('deviceIds', [])),
            'message': 'Patch deployment scheduled successfully'
        }
        
    except Exception as e:
        logger.error(f"Error creating patch schedule: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def get_scheduled_patches(status: str = None) -> Dict[str, Any]:
    """
    Get all scheduled patches, optionally filtered by status
    
    Args:
        status: Optional status filter (SCHEDULED, COMPLETED, CANCELLED, FAILED)
    
    Returns:
        List of scheduled patches
    """
    try:
        table = dynamodb.Table(SCHEDULED_PATCHES_TABLE)
        
        if status:
            # Query by status using GSI
            response = table.query(
                IndexName='StatusIndex',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status}
            )
        else:
            # Scan all schedules
            response = table.scan()
        
        schedules = response.get('Items', [])
        
        # Sort by scheduled time
        schedules.sort(key=lambda x: x.get('scheduledFor', ''), reverse=False)
        
        return {
            'success': True,
            'schedules': schedules,
            'count': len(schedules)
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduled patches: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'schedules': []
        }


def cancel_patch_schedule(schedule_id: str) -> Dict[str, Any]:
    """
    Cancel a scheduled patch deployment
    
    Args:
        schedule_id: The schedule ID to cancel
    
    Returns:
        Success/failure status
    """
    try:
        table = dynamodb.Table(SCHEDULED_PATCHES_TABLE)
        
        # Update status in DynamoDB
        response = table.update_item(
            Key={'scheduleId': schedule_id},
            UpdateExpression='SET #status = :status, updatedAt = :updated',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'CANCELLED',
                ':updated': datetime.now(timezone.utc).isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        
        # Delete EventBridge schedule
        try:
            scheduler_client.delete_schedule(
                Name=f"patch-{schedule_id}",
                GroupName=SCHEDULE_GROUP_NAME
            )
            logger.info(f"Deleted EventBridge schedule patch-{schedule_id}")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                logger.error(f"Failed to delete EventBridge schedule: {e}")
        
        return {
            'success': True,
            'message': 'Schedule cancelled successfully',
            'schedule': response.get('Attributes', {})
        }
        
    except Exception as e:
        logger.error(f"Error cancelling schedule: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def execute_scheduled_patch(schedule_id: str, patch_id: str, device_ids: List[str]) -> Dict[str, Any]:
    """
    Execute a scheduled patch deployment
    
    This is called by EventBridge Scheduler at the scheduled time
    
    Args:
        schedule_id: The schedule ID
        patch_id: The patch ID to deploy
        device_ids: List of device IDs
    
    Returns:
        Deployment status
    """
    try:
        table = dynamodb.Table(SCHEDULED_PATCHES_TABLE)
        
        # Update status to EXECUTING
        table.update_item(
            Key={'scheduleId': schedule_id},
            UpdateExpression='SET #status = :status, updatedAt = :updated, executionStarted = :started',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'EXECUTING',
                ':updated': datetime.now(timezone.utc).isoformat(),
                ':started': datetime.now(timezone.utc).isoformat()
            }
        )
        
        logger.info(f"Executing scheduled patch deployment: {schedule_id}")
        
        # Import deployment handler
        from .patch_deployment_handler import deploy_patches
        
        # Execute patch deployment
        result = deploy_patches({
            'patchIds': [patch_id],
            'deviceIds': device_ids,
            'scheduleId': schedule_id,
            'source': 'scheduled'
        })
        
        # Update final status
        final_status = 'COMPLETED' if result.get('success') else 'FAILED'
        
        table.update_item(
            Key={'scheduleId': schedule_id},
            UpdateExpression='SET #status = :status, updatedAt = :updated, executionCompleted = :completed, result = :result',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': final_status,
                ':updated': datetime.now(timezone.utc).isoformat(),
                ':completed': datetime.now(timezone.utc).isoformat(),
                ':result': json.dumps(result)
            }
        )
        
        return {
            'success': True,
            'scheduleId': schedule_id,
            'status': final_status,
            'deploymentResult': result
        }
        
    except Exception as e:
        logger.error(f"Error executing scheduled patch: {e}", exc_info=True)
        
        # Update status to FAILED
        try:
            table.update_item(
                Key={'scheduleId': schedule_id},
                UpdateExpression='SET #status = :status, updatedAt = :updated, error = :error',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'FAILED',
                    ':updated': datetime.now(timezone.utc).isoformat(),
                    ':error': str(e)
                }
            )
        except:
            pass
        
        return {
            'success': False,
            'error': str(e)
        }


def get_schedule_details(schedule_id: str) -> Dict[str, Any]:
    """
    Get details of a specific schedule
    
    Args:
        schedule_id: The schedule ID
    
    Returns:
        Schedule details
    """
    try:
        table = dynamodb.Table(SCHEDULED_PATCHES_TABLE)
        
        response = table.get_item(Key={'scheduleId': schedule_id})
        
        if 'Item' not in response:
            return {
                'success': False,
                'error': 'Schedule not found'
            }
        
        return {
            'success': True,
            'schedule': response['Item']
        }
        
    except Exception as e:
        logger.error(f"Error getting schedule details: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def cleanup_old_schedules(days: int = 30) -> Dict[str, Any]:
    """
    Clean up completed/cancelled schedules older than specified days
    
    Args:
        days: Number of days to keep
    
    Returns:
        Cleanup summary
    """
    try:
        table = dynamodb.Table(SCHEDULED_PATCHES_TABLE)
        cutoff_date = datetime.now(timezone.utc).timestamp() - (days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff_date, tz=timezone.utc).isoformat()
        
        # Scan for old completed/cancelled schedules
        response = table.scan(
            FilterExpression='#status IN (:completed, :cancelled) AND scheduledFor < :cutoff',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':completed': 'COMPLETED',
                ':cancelled': 'CANCELLED',
                ':cutoff': cutoff_iso
            }
        )
        
        deleted_count = 0
        for item in response.get('Items', []):
            table.delete_item(Key={'scheduleId': item['scheduleId']})
            deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old schedules")
        
        return {
            'success': True,
            'deletedCount': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up schedules: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }
