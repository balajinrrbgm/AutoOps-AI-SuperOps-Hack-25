"""
AWS AI Agentic Service
Integrates AWS Bedrock with CrewAI for intelligent patch management
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-2'))
BEDROCK_MODEL = os.getenv('BEDROCK_MODEL', 'anthropic.claude-3-5-sonnet-20241022-v2:0')


class AIAgentService:
    """AI Agent Service for patch analysis and decision making"""
    
    def __init__(self):
        self.model_id = BEDROCK_MODEL
        
    def analyze_patch_risk(self, patch_data: Dict, devices: List[Dict], vulnerabilities: List[Dict]) -> Dict:
        """
        Analyze patch deployment risk using AWS Bedrock
        
        Args:
            patch_data: Patch information
            devices: Affected devices
            vulnerabilities: Related CVEs
            
        Returns:
            AI analysis with recommendation, risk level, and deployment steps
        """
        try:
            # Prepare context for AI
            context = {
                'patch': {
                    'id': patch_data.get('id'),
                    'title': patch_data.get('title'),
                    'description': patch_data.get('description'),
                    'severity': patch_data.get('severity'),
                    'releaseDate': patch_data.get('releaseDate'),
                    'vendor': patch_data.get('vendor', 'Unknown')
                },
                'devices': [{
                    'name': d.get('name'),
                    'type': d.get('type'),
                    'os': d.get('operatingSystem'),
                    'criticality': self._assess_device_criticality(d)
                } for d in devices[:10]],  # Limit to 10 for token efficiency
                'vulnerabilities': vulnerabilities,
                'deviceCount': len(devices)
            }
            
            # Create AI prompt
            prompt = f"""You are an expert IT operations analyst specializing in patch management and cybersecurity risk assessment.

Analyze the following patch deployment scenario and provide a comprehensive risk assessment:

PATCH INFORMATION:
- Title: {context['patch']['title']}
- Severity: {context['patch']['severity']}
- Vendor: {context['patch']['vendor']}
- Description: {context['patch']['description']}

AFFECTED SYSTEMS:
- Total Devices: {context['deviceCount']}
- Sample Devices: {json.dumps(context['devices'], indent=2)}

RELATED VULNERABILITIES:
{json.dumps(context['vulnerabilities'], indent=2)}

Provide your analysis in the following JSON format:
{{
    "recommendation": "APPROVE|REVIEW|REJECT",
    "reasoning": "Detailed explanation of your recommendation",
    "riskLevel": 1-10 (1=lowest, 10=highest),
    "businessImpact": "LOW|MEDIUM|HIGH|CRITICAL",
    "confidence": 0.0-1.0,
    "deploymentSteps": [
        "Step 1: ...",
        "Step 2: ...",
        "Step 3: ..."
    ],
    "mitigationStrategies": [
        "Strategy 1: ...",
        "Strategy 2: ..."
    ],
    "rollbackPlan": "Description of rollback procedure",
    "estimatedDuration": "Expected deployment time",
    "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
    "postDeploymentValidation": ["Validation step 1", "Validation step 2"]
}}

Consider:
1. Severity of vulnerabilities being patched
2. Criticality of affected systems
3. Potential system disruption
4. Rollback complexity
5. Vendor patch quality history
6. Testing recommendations
7. Deployment window recommendations

Respond ONLY with valid JSON."""

            # Call Bedrock API
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response.get('body').read())
            ai_response = response_body.get('content', [{}])[0].get('text', '{}')
            
            # Parse AI response
            try:
                analysis = json.loads(ai_response)
            except json.JSONDecodeError:
                # If AI doesn't return valid JSON, extract it
                import re
                json_match = re.search(r'\{[\s\S]*\}', ai_response)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    raise ValueError("AI response is not valid JSON")
            
            # Add metadata
            analysis['timestamp'] = datetime.now(timezone.utc).isoformat()
            analysis['modelUsed'] = self.model_id
            analysis['analyzedDevices'] = len(devices)
            
            logger.info(f"AI patch analysis completed: {analysis.get('recommendation')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI patch analysis: {e}", exc_info=True)
            # Return fallback analysis
            return self._generate_fallback_analysis(patch_data, devices, vulnerabilities)
    
    def correlate_alerts(self, alerts: List[Dict]) -> Dict:
        """
        Correlate related alerts using AI pattern recognition
        
        Args:
            alerts: List of alerts to correlate
            
        Returns:
            Correlation analysis with grouped alerts and root cause
        """
        try:
            # Prepare alert context
            alert_summary = [{
                'id': a.get('id'),
                'title': a.get('title'),
                'description': a.get('description'),
                'severity': a.get('severity'),
                'deviceName': a.get('deviceName'),
                'timestamp': a.get('createdAt')
            } for a in alerts[:20]]  # Limit for token efficiency
            
            prompt = f"""You are an expert IT operations analyst specializing in alert correlation and root cause analysis.

Analyze these alerts and identify patterns, relationships, and potential root causes:

ALERTS:
{json.dumps(alert_summary, indent=2)}

Provide your analysis in JSON format:
{{
    "correlationGroups": [
        {{
            "groupId": "unique-id",
            "alertIds": ["alert-1", "alert-2"],
            "commonPattern": "Description of pattern",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "likelyRootCause": "Description"
        }}
    ],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ],
    "priorityActions": [
        {{
            "action": "Action description",
            "urgency": "IMMEDIATE|HIGH|MEDIUM|LOW",
            "affectedSystems": ["system-1", "system-2"]
        }}
    ]
}}

Respond ONLY with valid JSON."""

            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1500,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            })
            
            response = bedrock_runtime.invoke_model(modelId=self.model_id, body=body)
            response_body = json.loads(response.get('body').read())
            ai_response = response_body.get('content', [{}])[0].get('text', '{}')
            
            # Parse response
            import re
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                correlation = json.loads(json_match.group())
            else:
                correlation = json.loads(ai_response)
            
            correlation['timestamp'] = datetime.now(timezone.utc).isoformat()
            correlation['totalAlertsAnalyzed'] = len(alerts)
            
            logger.info(f"Alert correlation completed: {len(correlation.get('correlationGroups', []))} groups")
            return correlation
            
        except Exception as e:
            logger.error(f"Error in alert correlation: {e}", exc_info=True)
            return {
                'correlationGroups': [],
                'recommendations': ['Alert correlation unavailable - manual review required'],
                'priorityActions': [],
                'error': str(e)
            }
    
    def recommend_remediation(self, issue_description: str, context: Dict) -> Dict:
        """
        Get AI-powered remediation recommendations
        
        Args:
            issue_description: Description of the issue
            context: Additional context (devices, logs, etc.)
            
        Returns:
            Remediation recommendations
        """
        try:
            prompt = f"""You are an expert IT operations engineer specializing in automated remediation.

ISSUE: {issue_description}

CONTEXT:
{json.dumps(context, indent=2)}

Provide step-by-step remediation instructions in JSON format:
{{
    "remediationSteps": [
        {{
            "step": 1,
            "action": "Action description",
            "command": "Command to execute (if applicable)",
            "validation": "How to validate success",
            "rollback": "How to rollback if needed"
        }}
    ],
    "estimatedTime": "Duration",
    "riskLevel": "LOW|MEDIUM|HIGH",
    "requiresApproval": true/false,
    "affectedSystems": ["system-1"],
    "prerequisites": ["Prerequisite 1"]
}}

Respond ONLY with valid JSON."""

            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1500,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            })
            
            response = bedrock_runtime.invoke_model(modelId=self.model_id, body=body)
            response_body = json.loads(response.get('body').read())
            ai_response = response_body.get('content', [{}])[0].get('text', '{}')
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            remediation = json.loads(json_match.group() if json_match else ai_response)
            
            remediation['timestamp'] = datetime.now(timezone.utc).isoformat()
            return remediation
            
        except Exception as e:
            logger.error(f"Error in remediation recommendation: {e}", exc_info=True)
            return {
                'remediationSteps': [],
                'error': str(e),
                'estimatedTime': 'Unknown',
                'riskLevel': 'HIGH',
                'requiresApproval': True
            }
    
    def _assess_device_criticality(self, device: Dict) -> str:
        """Assess device criticality based on type and role"""
        device_type = device.get('type', '').lower()
        device_name = device.get('name', '').lower()
        
        if any(x in device_name for x in ['prod', 'production', 'db', 'database', 'web']):
            return 'HIGH'
        elif 'server' in device_type or 'srv' in device_name:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_fallback_analysis(self, patch_data: Dict, devices: List[Dict], vulnerabilities: List[Dict]) -> Dict:
        """Generate fallback analysis when AI is unavailable"""
        severity = patch_data.get('severity', 'MEDIUM')
        is_critical = severity in ['CRITICAL', 'HIGH']
        
        return {
            'recommendation': 'REVIEW' if is_critical else 'APPROVE',
            'reasoning': f'Automated analysis based on {severity} severity. {"Critical patch requires manual review." if is_critical else "Patch approved for deployment."}',
            'riskLevel': 8 if severity == 'CRITICAL' else 6 if severity == 'HIGH' else 4,
            'businessImpact': severity,
            'confidence': 0.7,
            'deploymentSteps': [
                'Create backup of affected systems',
                'Deploy to test environment first',
                'Monitor for 4 hours minimum',
                'Deploy to production during maintenance window',
                'Verify system stability post-deployment'
            ],
            'mitigationStrategies': ['Have rollback plan ready', 'Monitor system metrics'],
            'rollbackPlan': 'Use system restore points or previous patch version',
            'estimatedDuration': '2-4 hours',
            'prerequisites': ['System backups', 'Change approval'],
            'postDeploymentValidation': ['Check system logs', 'Verify service availability'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'modelUsed': 'fallback',
            'analyzedDevices': len(devices),
            'note': 'AI service unavailable - using rule-based analysis'
        }


# Singleton instance
_ai_service = None

def get_ai_service() -> AIAgentService:
    """Get singleton AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIAgentService()
    return _ai_service
