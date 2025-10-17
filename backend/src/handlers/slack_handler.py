"""
Slack Bot Handler for AutoOps AI
Processes Slack commands and interactions
"""
import json
import os
import hmac
import hashlib
import time
import boto3
from typing import Dict, Any
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stepfunctions = boto3.client('stepfunctions')
secretsmanager = boto3.client('secretsmanager')

def verify_slack_signature(event: Dict) -> bool:
    """Verify request is from Slack"""
    slack_signature = event['headers'].get('X-Slack-Signature', '')
    slack_timestamp = event['headers'].get('X-Slack-Request-Timestamp', '')

    # Prevent replay attacks
    if abs(time.time() - int(slack_timestamp)) > 60 * 5:
        return False

    # Get signing secret
    secret_arn = os.getenv('SLACK_SECRET_ARN')
    secret = secretsmanager.get_secret_value(SecretId=secret_arn)
    credentials = json.loads(secret['SecretString'])
    signing_secret = credentials['signingSecret']

    # Compute signature
    sig_basestring = f"v0:{slack_timestamp}:{event['body']}"
    my_signature = 'v0=' + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, slack_signature)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Slack commands and interactions"""
    try:
        # Verify signature
        if not verify_slack_signature(event):
            return {'statusCode': 401, 'body': 'Invalid signature'}

        # Parse request
        if event.get('path') == '/slack/commands':
            return handle_slash_command(event)
        elif event.get('path') == '/slack/interactions':
            return handle_interaction(event)
        else:
            return {'statusCode': 404, 'body': 'Not found'}

    except Exception as e:
        logger.error(f"Error processing Slack request: {e}", exc_info=True)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'text': f'Error processing request: {str(e)}',
                'response_type': 'ephemeral'
            })
        }

def handle_slash_command(event: Dict) -> Dict:
    """Handle /autoops slash command"""
    from urllib.parse import parse_qs

    body = parse_qs(event['body'])
    command = body.get('command', [''])[0]
    text = body.get('text', [''])[0]
    user_id = body.get('user_id', [''])[0]

    logger.info(f"Command: {command}, Text: {text}, User: {user_id}")

    # Parse subcommand
    parts = text.split()
    subcommand = parts[0] if parts else 'help'

    if subcommand == 'status':
        return get_system_status()
    elif subcommand == 'patch':
        if len(parts) > 1 and parts[1] == 'review':
            return get_patch_review()
        else:
            return show_patch_menu()
    elif subcommand == 'alert':
        if len(parts) > 1 and parts[1] == 'summary':
            return get_alert_summary()
        else:
            return show_alert_menu()
    elif subcommand == 'approve':
        if len(parts) > 1:
            action_id = parts[1]
            return approve_action(action_id, user_id)
        else:
            return error_response('Please provide action ID to approve')
    elif subcommand == 'help':
        return show_help()
    else:
        return error_response(f'Unknown command: {subcommand}')

def handle_interaction(event: Dict) -> Dict:
    """Handle button clicks and other interactions"""
    from urllib.parse import parse_qs

    body = parse_qs(event['body'])
    payload = json.loads(body.get('payload', ['{}'])[0])

    action_type = payload.get('type')

    if action_type == 'block_actions':
        actions = payload.get('actions', [])
        for action in actions:
            action_id = action.get('action_id')
            value = action.get('value')

            if action_id.startswith('approve_'):
                return process_approval(value, payload.get('user', {}))
            elif action_id.startswith('reject_'):
                return process_rejection(value, payload.get('user', {}))

    return {'statusCode': 200}

def get_system_status() -> Dict:
    """Get and format system status"""
    # This would call your backend API
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response_type': 'in_channel',
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '*AutoOps AI System Status* 🤖\n\n'
                               '✅ All systems operational\n'
                               '📊 Monitoring 150 devices\n'
                               '🔄 3 patches pending approval\n'
                               '🚨 2 active alerts'
                    }
                }
            ]
        })
    }

def get_patch_review() -> Dict:
    """Get pending patches for review"""
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response_type': 'ephemeral',
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '*Patches Pending Review* 📋'
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '*CVE-2024-12345* - Critical\n'
                               'Windows Server 2022 Security Update\n'
                               'Affects: 15 devices\n'
                               'CVSS: 9.8'
                    },
                    'accessory': {
                        'type': 'button',
                        'text': {
                            'type': 'plain_text',
                            'text': 'Approve'
                        },
                        'action_id': 'approve_patch_1',
                        'value': 'patch_1',
                        'style': 'primary'
                    }
                }
            ]
        })
    }

def show_help() -> Dict:
    """Show help message"""
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response_type': 'ephemeral',
            'text': '''*AutoOps AI Commands* 🤖

`/autoops status` - View system status
`/autoops patch review` - Review pending patches
`/autoops alert summary` - Get alert summary
`/autoops approve [action-id]` - Approve pending action
`/autoops help` - Show this help message'''
        })
    }

def error_response(message: str) -> Dict:
    """Return error response"""
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response_type': 'ephemeral',
            'text': f'❌ {message}'
        })
    }

def approve_action(action_id: str, user_id: str) -> Dict:
    """Approve a pending action"""
    # Send approval to Step Functions
    # This is simplified - would need task token lookup
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response_type': 'in_channel',
            'text': f'✅ Action {action_id} approved by <@{user_id}>'
        })
    }
