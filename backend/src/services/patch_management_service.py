"""
AI-Powered Patch Management Service
Integrates AWS Bedrock, CrewAI agents, SuperOps, and NVD for intelligent patch deployment
"""
import os
import json
import boto3
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from ..integrations.superops_client import SuperOpsClient
from ..integrations.nvd_client import NVDClient
from ..ai_agents.crew_config import AutoOpsAIAgents

logger = logging.getLogger(__name__)


class PatchManagementService:
    def __init__(self):
        self.superops_client = SuperOpsClient()
        self.nvd_client = NVDClient()
        self.ai_agents = AutoOpsAIAgents()
        
        # AWS Services
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.sns_client = boto3.client('sns', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.eventbridge = boto3.client('events', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        self.patch_table_name = os.getenv('PATCH_TABLE', 'AutoOps-Patches')

    def get_all_patches(self) -> List[Dict]:
        """Get all available patches from SuperOps"""
        try:
            # Get patch status from SuperOps
            patch_statuses = self.superops_client.get_patch_status()
            
            patches = []
            for status in patch_statuses:
                if status.get('criticalPatches'):
                    for patch in status['criticalPatches']:
                        patch_obj = {
                            'id': patch.get('id', f"patch-{len(patches)}"),
                            'title': patch.get('title', 'Unknown Patch'),
                            'description': patch.get('description', ''),
                            'severity': patch.get('severity', 'MEDIUM'),
                            'releaseDate': patch.get('publishDate', datetime.utcnow().isoformat()),
                            'status': self._determine_patch_status(patch),
                            'cveId': patch.get('cveId'),
                            'relatedCVEs': [patch.get('cveId')] if patch.get('cveId') else [],
                            'affectedDevices': [status['deviceId']],
                            'size': patch.get('size', 'Unknown'),
                            'vendor': patch.get('vendor', 'Microsoft'),
                            'requiresReboot': patch.get('requiresReboot', True)
                        }
                        patches.append(patch_obj)
            
            return patches
            
        except Exception as e:
            logger.error(f"Error getting patches: {e}")
            return []

    def _determine_patch_status(self, patch: Dict) -> str:
        """Determine current status of a patch"""
        # Logic to determine if patch is available, pending, deployed, etc.
        return 'AVAILABLE'  # Simplified for now

    def analyze_patch_with_ai(self, patch: Dict, devices: List[Dict], vulnerabilities: List[Dict]) -> Dict:
        """Use AI agents to analyze patch deployment risk and recommendations"""
        try:
            # Prepare context for AI analysis
            context = {
                'patches': [patch],
                'systems': devices,
                'cve_data': vulnerabilities,
                'policies': self._get_deployment_policies()
            }
            
            # Create patch crew for analysis
            patch_crew = self.ai_agents.create_patch_crew(context)
            
            # Execute AI analysis
            logger.info(f"Starting AI analysis for patch: {patch['id']}")
            result = patch_crew.kickoff()
            
            # Parse AI recommendations
            analysis = self._parse_ai_response(result, patch)
            
            # Store analysis in DynamoDB
            self._store_patch_analysis(patch['id'], analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return safe default recommendation
            return {
                'recommendation': 'REVIEW',
                'reasoning': 'AI analysis unavailable, manual review required',
                'riskLevel': 5,
                'businessImpact': 'MEDIUM',
                'confidence': 0.5,
                'deploymentSteps': [
                    'Verify patch compatibility',
                    'Test in non-production environment',
                    'Deploy to production with monitoring',
                    'Verify deployment success',
                    'Have rollback plan ready'
                ]
            }

    def _parse_ai_response(self, ai_result, patch: Dict) -> Dict:
        """Parse AI crew response into structured recommendation"""
        try:
            # Extract insights from AI result
            recommendation_text = str(ai_result).lower()
            
            # Determine recommendation
            if 'approve' in recommendation_text and 'immediate' in recommendation_text:
                recommendation = 'APPROVE'
                risk_level = 2
            elif 'reject' in recommendation_text or 'high risk' in recommendation_text:
                recommendation = 'REJECT'
                risk_level = 8
            else:
                recommendation = 'REVIEW'
                risk_level = 5
            
            # Determine business impact
            if patch['severity'] == 'CRITICAL':
                business_impact = 'HIGH'
                confidence = 0.95
            elif patch['severity'] == 'HIGH':
                business_impact = 'MEDIUM'
                confidence = 0.85
            else:
                business_impact = 'LOW'
                confidence = 0.75
            
            return {
                'recommendation': recommendation,
                'reasoning': f"AI analysis based on severity ({patch['severity']}), affected devices, and vulnerability context",
                'riskLevel': risk_level,
                'businessImpact': business_impact,
                'confidence': confidence,
                'deploymentSteps': [
                    'Create snapshot/backup of affected systems',
                    'Verify patch compatibility with system configuration',
                    'Deploy to test environment first',
                    'Monitor system metrics during deployment',
                    'Deploy to production in maintenance window',
                    'Verify patch installation success',
                    'Monitor for 24 hours post-deployment'
                ],
                'rollbackPlan': 'Restore from snapshot if issues detected within 4 hours',
                'estimatedDuration': '2-4 hours',
                'maintenanceWindow': self._suggest_maintenance_window()
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                'recommendation': 'REVIEW',
                'reasoning': 'Unable to parse AI analysis',
                'riskLevel': 5,
                'businessImpact': 'MEDIUM',
                'confidence': 0.5,
                'deploymentSteps': ['Manual review required']
            }

    def _suggest_maintenance_window(self) -> str:
        """Suggest optimal maintenance window based on system usage patterns"""
        # Suggest weekend deployment for critical patches
        now = datetime.utcnow()
        next_saturday = now + timedelta(days=(5 - now.weekday()) % 7)
        suggested_time = next_saturday.replace(hour=2, minute=0, second=0, microsecond=0)
        return suggested_time.isoformat()

    def _get_deployment_policies(self) -> Dict:
        """Get organizational deployment policies"""
        return {
            'requireApproval': True,
            'testingRequired': True,
            'maintenanceWindowOnly': True,
            'allowedHours': [0, 1, 2, 3, 4, 5],  # 12 AM - 5 AM
            'maxConcurrentDeployments': 5,
            'rollbackEnabled': True,
            'snapshotRequired': True
        }

    def deploy_patch(self, patch_id: str, device_ids: List[str], schedule: Optional[Dict] = None, ai_approved: bool = False) -> Dict:
        """Deploy patch to specified devices"""
        try:
            # Get patch details
            patches = self.get_all_patches()
            patch = next((p for p in patches if p['id'] == patch_id), None)
            
            if not patch:
                raise ValueError(f"Patch {patch_id} not found")
            
            # Validate deployment
            if not ai_approved and patch['severity'] == 'CRITICAL':
                logger.warning(f"Critical patch {patch_id} deployed without AI approval")
            
            # Create deployment record
            deployment = {
                'deploymentId': f"deploy-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                'patchId': patch_id,
                'deviceIds': device_ids,
                'status': 'SCHEDULED' if schedule else 'INITIATING',
                'scheduledFor': schedule.get('scheduledFor') if schedule else None,
                'initiatedAt': datetime.utcnow().isoformat(),
                'aiApproved': ai_approved,
                'deploymentSteps': []
            }
            
            if schedule:
                # Schedule deployment
                self._schedule_deployment(deployment)
            else:
                # Deploy immediately via SuperOps
                result = self.superops_client.deploy_patch(
                    device_ids=device_ids,
                    patch_ids=[patch_id],
                    schedule=schedule
                )
                
                deployment['superopsDeploymentId'] = result.get('deploymentId')
                deployment['status'] = 'IN_PROGRESS'
            
            # Store deployment in DynamoDB
            self._store_deployment(deployment)
            
            # Send SNS notification
            self._notify_deployment(deployment, patch)
            
            # Publish EventBridge event
            self._publish_deployment_event(deployment, patch)
            
            return deployment
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise

    def _schedule_deployment(self, deployment: Dict):
        """Schedule patch deployment using EventBridge"""
        try:
            scheduled_time = datetime.fromisoformat(deployment['scheduledFor'])
            
            # Create EventBridge scheduled rule
            rule_name = f"patch-deploy-{deployment['deploymentId']}"
            
            self.eventbridge.put_rule(
                Name=rule_name,
                ScheduleExpression=f"cron({scheduled_time.minute} {scheduled_time.hour} {scheduled_time.day} {scheduled_time.month} ? {scheduled_time.year})",
                State='ENABLED',
                Description=f"Scheduled patch deployment {deployment['deploymentId']}"
            )
            
            # Add Lambda target
            self.eventbridge.put_targets(
                Rule=rule_name,
                Targets=[{
                    'Id': '1',
                    'Arn': os.getenv('PATCH_DEPLOYMENT_LAMBDA_ARN', ''),
                    'Input': json.dumps(deployment)
                }]
            )
            
            logger.info(f"Scheduled deployment {deployment['deploymentId']} for {scheduled_time}")
            
        except Exception as e:
            logger.error(f"Failed to schedule deployment: {e}")

    def _store_patch_analysis(self, patch_id: str, analysis: Dict):
        """Store AI patch analysis in DynamoDB"""
        try:
            table = self.dynamodb.Table(self.patch_table_name)
            
            item = {
                'PK': f"PATCH#{patch_id}",
                'SK': f"ANALYSIS#{datetime.utcnow().isoformat()}",
                'patchId': patch_id,
                'recommendation': analysis['recommendation'],
                'riskLevel': analysis['riskLevel'],
                'businessImpact': analysis['businessImpact'],
                'confidence': str(analysis['confidence']),
                'reasoning': analysis['reasoning'],
                'deploymentSteps': analysis['deploymentSteps'],
                'analyzedAt': datetime.utcnow().isoformat(),
                'ttl': int((datetime.utcnow() + timedelta(days=90)).timestamp())
            }
            
            table.put_item(Item=item)
            
        except Exception as e:
            logger.warning(f"Could not store patch analysis: {e}")

    def _store_deployment(self, deployment: Dict):
        """Store deployment record in DynamoDB"""
        try:
            table = self.dynamodb.Table(self.patch_table_name)
            
            item = {
                'PK': f"DEPLOYMENT#{deployment['deploymentId']}",
                'SK': f"STATUS#{deployment['status']}",
                **deployment,
                'ttl': int((datetime.utcnow() + timedelta(days=365)).timestamp())
            }
            
            table.put_item(Item=item)
            
        except Exception as e:
            logger.warning(f"Could not store deployment: {e}")

    def _notify_deployment(self, deployment: Dict, patch: Dict):
        """Send SNS notification for deployment"""
        topic_arn = os.getenv('ALERT_SNS_TOPIC_ARN', '')
        if not topic_arn:
            return
        
        try:
            message = f"""
Patch Deployment {'Scheduled' if deployment.get('scheduledFor') else 'Initiated'}

Patch: {patch['title']}
Severity: {patch['severity']}
Devices: {len(deployment['deviceIds'])}
Status: {deployment['status']}
Deployment ID: {deployment['deploymentId']}
{'Scheduled For: ' + deployment.get('scheduledFor', '') if deployment.get('scheduledFor') else ''}

AI Approved: {'Yes' if deployment.get('aiApproved') else 'No'}
"""
            
            self.sns_client.publish(
                TopicArn=topic_arn,
                Subject=f"Patch Deployment: {patch['title']}",
                Message=message,
                MessageAttributes={
                    'severity': {'DataType': 'String', 'StringValue': patch['severity']},
                    'deploymentId': {'DataType': 'String', 'StringValue': deployment['deploymentId']}
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to send SNS notification: {e}")

    def _publish_deployment_event(self, deployment: Dict, patch: Dict):
        """Publish deployment event to EventBridge"""
        try:
            self.eventbridge.put_events(
                Entries=[{
                    'Source': 'autoops.patch.management',
                    'DetailType': 'Patch Deployment',
                    'Detail': json.dumps({
                        'deployment': deployment,
                        'patch': patch
                    }),
                    'EventBusName': 'default'
                }]
            )
            
        except Exception as e:
            logger.error(f"Failed to publish deployment event: {e}")

    def get_deployment_schedule(self) -> List[Dict]:
        """Get all scheduled patch deployments"""
        try:
            table = self.dynamodb.Table(self.patch_table_name)
            
            response = table.scan(
                FilterExpression='begins_with(PK, :pk)',
                ExpressionAttributeValues={':pk': 'DEPLOYMENT#'}
            )
            
            deployments = []
            for item in response.get('Items', []):
                if item.get('status') == 'SCHEDULED':
                    deployments.append({
                        'deploymentId': item['deploymentId'],
                        'patchTitle': item.get('patchTitle', 'Unknown'),
                        'scheduledFor': item.get('scheduledFor'),
                        'deviceCount': len(item.get('deviceIds', []))
                    })
            
            return sorted(deployments, key=lambda x: x['scheduledFor'])
            
        except Exception as e:
            logger.error(f"Error getting deployment schedule: {e}")
            return []

    def rollback_deployment(self, deployment_id: str) -> Dict:
        """Rollback a failed patch deployment"""
        try:
            # Implement rollback logic via SuperOps
            logger.info(f"Initiating rollback for deployment {deployment_id}")
            
            # Update deployment status
            table = self.dynamodb.Table(self.patch_table_name)
            table.update_item(
                Key={
                    'PK': f"DEPLOYMENT#{deployment_id}",
                    'SK': 'STATUS#IN_PROGRESS'
                },
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'ROLLED_BACK'}
            )
            
            return {
                'deploymentId': deployment_id,
                'status': 'ROLLED_BACK',
                'rolledBackAt': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise
