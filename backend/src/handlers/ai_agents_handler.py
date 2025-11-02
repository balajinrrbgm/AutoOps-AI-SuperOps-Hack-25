"""
AWS Lambda Handler for AI Agents Service
Provides multi-agent AI capabilities via API Gateway
"""
import json
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_agents.agents_service import AIAgentsService
from integrations.bedrock_service import BedrockAIService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services (reuse across warm Lambda invocations)
bedrock_service = None
ai_agents_service = None

def initialize_services():
    """Initialize AI services on cold start"""
    global bedrock_service, ai_agents_service
    
    if bedrock_service is None:
        try:
            bedrock_service = BedrockAIService()
            logger.info("✅ Bedrock service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock: {e}")
            bedrock_service = None
    
    if ai_agents_service is None:
        try:
            ai_agents_service = AIAgentsService(bedrock_service=bedrock_service)
            logger.info("✅ AI Agents service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AI Agents: {e}")
            ai_agents_service = None


def lambda_handler(event, context):
    """
    AWS Lambda handler for AI Agents endpoints
    
    Routes:
    - GET /ai/agents/status
    - POST /ai/agents/prioritize
    - POST /ai/agents/correlate-alerts
    - POST /ai/agents/decide-remediation
    - POST /ai/agents/learn
    """
    try:
        # Initialize services on cold start
        initialize_services()
        
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        logger.info(f"Processing {http_method} {path}")
        
        # Route to appropriate handler
        if path.endswith('/status'):
            response = handle_status()
        elif path.endswith('/prioritize'):
            response = handle_prioritize(body)
        elif path.endswith('/correlate-alerts'):
            response = handle_correlate_alerts(body)
        elif path.endswith('/decide-remediation'):
            response = handle_decide_remediation(body)
        elif path.endswith('/learn'):
            response = handle_learn(body)
        else:
            response = {
                'statusCode': 404,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
        
        # Add CORS headers
        response['headers'] = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }


def handle_status():
    """Get AI agents status"""
    try:
        if ai_agents_service:
            status = ai_agents_service.get_agent_status()
        else:
            status = {
                'crewai_available': False,
                'agents_initialized': False,
                'bedrock_service': bedrock_service is not None,
                'mode': 'Service Unavailable'
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(status)
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def handle_prioritize(body):
    """AI-powered patch prioritization"""
    try:
        patches = body.get('patches', [])
        context = body.get('context', {})
        
        if not patches:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'patches array is required'})
            }
        
        if ai_agents_service:
            result = ai_agents_service.prioritize_patches(patches, context)
        else:
            # Fallback to simple prioritization
            severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            sorted_patches = sorted(
                patches,
                key=lambda p: (severity_order.get(p.get('severity', 'MEDIUM'), 0), -len(p.get('affectedDevices', []))),
                reverse=True
            )
            result = {
                'prioritized_patches': sorted_patches,
                'ai_generated': False,
                'model': 'Fallback',
                'agent': 'Service Unavailable'
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Error prioritizing patches: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def handle_correlate_alerts(body):
    """AI-powered alert correlation"""
    try:
        alerts = body.get('alerts', [])
        
        if not alerts:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'alerts array is required'})
            }
        
        if ai_agents_service:
            result = ai_agents_service.correlate_alerts(alerts)
        else:
            # Simple fallback grouping
            correlations = {}
            for alert in alerts:
                device_id = alert.get('deviceId', 'unknown')
                if device_id not in correlations:
                    correlations[device_id] = {
                        'device': alert.get('deviceName', device_id),
                        'alerts': [],
                        'count': 0
                    }
                correlations[device_id]['alerts'].append(alert)
                correlations[device_id]['count'] += 1
            
            result = {
                'correlations': list(correlations.values()),
                'total_alerts': len(alerts),
                'ai_generated': False,
                'model': 'Fallback'
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Error correlating alerts: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def handle_decide_remediation(body):
    """AI-powered remediation decision"""
    try:
        vulnerability = body.get('vulnerability', {})
        options = body.get('options', [
            {'name': 'Immediate Patch', 'description': 'Deploy patch immediately'},
            {'name': 'Scheduled Patch', 'description': 'Schedule for maintenance window'},
            {'name': 'Workaround', 'description': 'Apply temporary workaround'}
        ])
        
        if not vulnerability:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'vulnerability object is required'})
            }
        
        if ai_agents_service:
            result = ai_agents_service.decide_remediation(vulnerability, options)
        else:
            # Simple severity-based fallback
            severity = vulnerability.get('severity', 'MEDIUM')
            cvss_score = vulnerability.get('cvssScore', 5.0)
            
            if cvss_score >= 9.0 or severity == 'CRITICAL':
                recommended = options[0] if options else {'name': 'Immediate Patch'}
                urgency = 'IMMEDIATE'
            elif cvss_score >= 7.0 or severity == 'HIGH':
                recommended = options[0] if options else {'name': 'Scheduled Patch'}
                urgency = 'URGENT'
            else:
                recommended = options[-1] if options else {'name': 'Next maintenance window'}
                urgency = 'NORMAL'
            
            result = {
                'decision': {
                    'recommended_option': recommended,
                    'urgency': urgency,
                    'justification': f'Based on CVSS score of {cvss_score} and {severity} severity',
                    'confidence': 0.5
                },
                'ai_generated': False,
                'model': 'Fallback'
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Error deciding remediation: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def handle_learn(body):
    """AI learning from outcomes"""
    try:
        action = body.get('action', {})
        outcome = body.get('outcome', {})
        
        if not action or not outcome:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'action and outcome objects are required'})
            }
        
        if ai_agents_service:
            result = ai_agents_service.learn_from_outcome(action, outcome)
        else:
            # Simple logging fallback
            result = {
                'learnings': {
                    'recorded': True,
                    'timestamp': datetime.utcnow().isoformat(),
                    'action_type': action.get('type'),
                    'outcome_status': outcome.get('status')
                },
                'ai_generated': False,
                'model': 'Fallback'
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Error learning from outcome: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
