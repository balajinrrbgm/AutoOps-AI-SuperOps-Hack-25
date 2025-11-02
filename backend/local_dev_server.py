"""
Local Development Server for AutoOps AI
Provides mock endpoints for testing frontend without full AWS deployment
Supports real SuperOps and NVD API integration when enabled
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from datetime import datetime, timedelta
import json
import random
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Feature flags from environment
USE_REAL_SUPEROPS = os.getenv('USE_REAL_SUPEROPS', 'false').lower() == 'true'
USE_REAL_AWS = os.getenv('USE_REAL_AWS', 'false').lower() == 'true'
USE_REAL_NVD = os.getenv('USE_REAL_NVD', 'true').lower() == 'true'

# Initialize services
bedrock_service = None
ai_agents_service = None
try:
    if USE_REAL_SUPEROPS:
        from src.integrations.superops_client import SuperOpsClient
        superops_client = SuperOpsClient()
        logger.info("✅ SuperOps client initialized with real API")
    else:
        superops_client = None
        logger.info("ℹ️ SuperOps using mock data")
        
    if USE_REAL_NVD:
        from src.integrations.nvd_client import NVDClient
        nvd_client = NVDClient()
        logger.info("✅ NVD client initialized with real API")
    else:
        nvd_client = None
        logger.info("ℹ️ NVD using mock data")
        
    # Try to import Bedrock service
    try:
        from src.integrations.bedrock_service import BedrockAIService
        bedrock_service = BedrockAIService()
        logger.info("✅ Bedrock AI service initialized")
    except ImportError as ie:
        logger.warning(f"Bedrock service unavailable (boto3 not installed): {ie}")
        bedrock_service = None
    except Exception as be:
        logger.warning(f"Bedrock service initialization failed: {be}")
        bedrock_service = None
    
    # Try to import AI Agents service (works with or without CrewAI)
    try:
        from src.ai_agents.agents_service import AIAgentsService
        ai_agents_service = AIAgentsService(bedrock_service=bedrock_service)
        logger.info("✅ AI Agents service initialized")
    except Exception as ae:
        logger.warning(f"AI Agents service unavailable: {ae}")
        ai_agents_service = None
        
    if USE_REAL_AWS:
        try:
            from src.services.patch_management_service import PatchManagementService
            patch_service = PatchManagementService()
            logger.info("✅ AWS services initialized")
        except Exception as e:
            logger.warning(f"AWS services unavailable: {e}")
            patch_service = None
    else:
        patch_service = None
        logger.info("ℹ️ AWS services using mock data")
        
    has_real_services = USE_REAL_SUPEROPS or USE_REAL_NVD or USE_REAL_AWS
except Exception as e:
    logger.warning(f"Could not initialize some services: {e}. Using mock data.")
    superops_client = None
    nvd_client = None
    bedrock_service = None
    ai_agents_service = None
    patch_service = None
    has_real_services = False


# ==================== MOCK DATA ====================

MOCK_DEVICES = [
    {
        'id': 'device-001',
        'name': 'WEB-SERVER-01',
        'type': 'Server',
        'ipAddress': '192.168.1.10',
        'operatingSystem': 'Windows Server 2019',
        'riskScore': 8.5,
        'vulnerabilityCount': {'critical': 3, 'high': 5, 'medium': 12, 'low': 8},
        'lastScan': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        'status': 'ONLINE',
        'location': 'Data Center 1'
    },
    {
        'id': 'device-002',
        'name': 'DB-SERVER-01',
        'type': 'Database Server',
        'ipAddress': '192.168.1.20',
        'operatingSystem': 'Ubuntu 20.04 LTS',
        'riskScore': 9.2,
        'vulnerabilityCount': {'critical': 5, 'high': 8, 'medium': 15, 'low': 10},
        'lastScan': (datetime.utcnow() - timedelta(hours=4)).isoformat(),
        'status': 'ONLINE',
        'location': 'Data Center 1'
    },
    {
        'id': 'device-003',
        'name': 'APP-SERVER-01',
        'type': 'Application Server',
        'ipAddress': '192.168.1.30',
        'operatingSystem': 'CentOS 8',
        'riskScore': 6.5,
        'vulnerabilityCount': {'critical': 1, 'high': 3, 'medium': 8, 'low': 15},
        'lastScan': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        'status': 'ONLINE',
        'location': 'Data Center 2'
    }
]

MOCK_PATCHES = [
    {
        'id': 'patch-001',
        'title': 'Critical Security Update for Windows Server',
        'description': 'Addresses remote code execution vulnerability in Windows RPC. This patch fixes a critical vulnerability that could allow an unauthenticated attacker to execute arbitrary code remotely.',
        'severity': 'CRITICAL',
        'releaseDate': (datetime.utcnow() - timedelta(days=2)).isoformat(),
        'status': 'AVAILABLE',
        'cveId': 'CVE-2024-12345',
        'relatedCVEs': ['CVE-2024-12345', 'CVE-2024-12346'],
        'affectedDevices': ['device-001'],
        'size': '125 MB',
        'vendor': 'Microsoft',
        'requiresReboot': True,
        'installTime': '15-20 minutes',
        'supersededBy': None,
        'supersedes': ['KB5001234', 'KB5001235']
    },
    {
        'id': 'patch-002',
        'title': 'Linux Kernel Security Patch',
        'description': 'Fixes privilege escalation vulnerability in kernel. This update addresses a local privilege escalation flaw that could allow a malicious user to gain root access.',
        'severity': 'HIGH',
        'releaseDate': (datetime.utcnow() - timedelta(days=5)).isoformat(),
        'status': 'AVAILABLE',
        'cveId': 'CVE-2024-23456',
        'relatedCVEs': ['CVE-2024-23456'],
        'affectedDevices': ['device-002', 'device-003'],
        'size': '45 MB',
        'vendor': 'Canonical',
        'requiresReboot': True,
        'installTime': '10-15 minutes',
        'supersededBy': None,
        'supersedes': []
    },
    {
        'id': 'patch-003',
        'title': 'Apache Web Server Security Update',
        'description': 'Security update for Apache HTTP Server addressing multiple vulnerabilities including request smuggling and denial of service issues.',
        'severity': 'MEDIUM',
        'releaseDate': (datetime.utcnow() - timedelta(days=10)).isoformat(),
        'status': 'DEPLOYED',
        'cveId': 'CVE-2024-34567',
        'relatedCVEs': ['CVE-2024-34567', 'CVE-2024-34568'],
        'affectedDevices': ['device-001', 'device-003'],
        'size': '20 MB',
        'vendor': 'Apache Foundation',
        'requiresReboot': False,
        'installTime': '5-10 minutes',
        'supersededBy': None,
        'supersedes': ['v2.4.54']
    },
    {
        'id': 'patch-004',
        'title': 'OpenSSL Security Hotfix',
        'description': 'Critical OpenSSL update addressing remote code execution vulnerability (Heartbleed-like). Immediate deployment recommended.',
        'severity': 'CRITICAL',
        'releaseDate': (datetime.utcnow() - timedelta(days=1)).isoformat(),
        'status': 'AVAILABLE',
        'cveId': 'CVE-2024-45678',
        'relatedCVEs': ['CVE-2024-45678'],
        'affectedDevices': ['device-002', 'device-003'],
        'size': '8 MB',
        'vendor': 'OpenSSL Project',
        'requiresReboot': False,
        'installTime': '2-5 minutes',
        'supersededBy': None,
        'supersedes': ['OpenSSL 3.0.11']
    },
    {
        'id': 'patch-005',
        'title': 'Windows Defender Definition Update',
        'description': 'Latest virus and spyware definitions for Windows Defender. Includes detection for recent malware campaigns.',
        'severity': 'LOW',
        'releaseDate': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
        'status': 'SCHEDULED',
        'cveId': None,
        'relatedCVEs': [],
        'affectedDevices': ['device-001'],
        'size': '150 MB',
        'vendor': 'Microsoft',
        'requiresReboot': False,
        'installTime': '5 minutes',
        'supersededBy': None,
        'supersedes': []
    }
]

MOCK_ALERTS = [
    {
        'id': 'alert-001',
        'title': 'Critical Vulnerability Detected',
        'description': 'CVE-2024-12345 detected on WEB-SERVER-01',
        'severity': 'CRITICAL',
        'status': 'ACTIVE',
        'deviceId': 'device-001',
        'deviceName': 'WEB-SERVER-01',
        'cveId': 'CVE-2024-12345',
        'createdAt': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        'acknowledgedAt': None
    },
    {
        'id': 'alert-002',
        'title': 'Multiple High Severity Vulnerabilities',
        'description': 'Database server requires immediate patching',
        'severity': 'HIGH',
        'status': 'ACTIVE',
        'deviceId': 'device-002',
        'deviceName': 'DB-SERVER-01',
        'cveId': 'CVE-2024-23456',
        'createdAt': (datetime.utcnow() - timedelta(hours=5)).isoformat(),
        'acknowledgedAt': None
    }
]

MOCK_VULNERABILITIES = [
    {
        'cveId': 'CVE-2024-12345',
        'description': 'Remote Code Execution in Windows RPC',
        'severity': 'CRITICAL',
        'cvssScore': 9.8,
        'publishedDate': (datetime.utcnow() - timedelta(days=3)).isoformat(),
        'affectedProducts': ['Windows Server 2019', 'Windows Server 2022'],
        'references': ['https://msrc.microsoft.com/update-guide']
    },
    {
        'cveId': 'CVE-2024-23456',
        'description': 'Linux Kernel Privilege Escalation',
        'severity': 'HIGH',
        'cvssScore': 7.8,
        'publishedDate': (datetime.utcnow() - timedelta(days=6)).isoformat(),
        'affectedProducts': ['Linux Kernel 5.x'],
        'references': ['https://ubuntu.com/security/notices']
    }
]


# ==================== INVENTORY ENDPOINTS ====================

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get device inventory with vulnerability correlation"""
    try:
        if USE_REAL_SUPEROPS and superops_client:
            logger.info("Fetching real device inventory from SuperOps...")
            devices = superops_client.get_device_inventory()
            
            # Enrich with vulnerability data
            enriched_devices = []
            for device in devices:
                enriched_device = {
                    'id': device.get('id'),
                    'name': device.get('name'),
                    'type': device.get('type', 'Unknown'),
                    'ipAddress': device.get('ipAddress'),
                    'operatingSystem': device.get('operatingSystem', 'Unknown'),
                    'status': 'ONLINE',  # Could be derived from lastSeenAt
                    'location': device.get('site', {}).get('name', 'Unknown'),
                    'client': device.get('client', {}).get('name', 'Unknown'),
                    'lastScan': device.get('lastSeenAt', datetime.utcnow().isoformat()),
                    'riskScore': random.uniform(5.0, 9.5),  # TODO: Calculate from vulnerabilities
                    'vulnerabilityCount': {
                        'critical': random.randint(0, 5),
                        'high': random.randint(3, 10),
                        'medium': random.randint(5, 15),
                        'low': random.randint(10, 20)
                    }
                }
                enriched_devices.append(enriched_device)
            
            logger.info(f"✅ Retrieved {len(enriched_devices)} devices from SuperOps")
            return jsonify(enriched_devices)
        else:
            logger.info("Using mock device inventory")
            return jsonify(MOCK_DEVICES)
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        return jsonify(MOCK_DEVICES)


@app.route('/api/scan-device/<device_id>', methods=['POST'])
def scan_device(device_id):
    """Trigger vulnerability scan for a specific device"""
    try:
        logger.info(f"Starting scan for device {device_id}")
        
        # Simulate scan delay
        import time
        time.sleep(1)
        
        # Update device last scan time
        for device in MOCK_DEVICES:
            if device['id'] == device_id:
                device['lastScan'] = datetime.utcnow().isoformat()
                # Randomly update vulnerability counts
                device['vulnerabilityCount']['critical'] = random.randint(0, 5)
                device['vulnerabilityCount']['high'] = random.randint(3, 10)
                device['riskScore'] = round(random.uniform(5.0, 9.5), 1)
                
                return jsonify({
                    'success': True,
                    'device': device,
                    'message': f'Scan completed for {device["name"]}'
                })
        
        return jsonify({'error': 'Device not found'}), 404
        
    except Exception as e:
        logger.error(f"Error scanning device: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ALERT ENDPOINTS ====================

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    try:
        status_filter = request.args.get('status', 'ACTIVE')
        
        if USE_REAL_SUPEROPS and superops_client:
            logger.info("Fetching real alerts from SuperOps...")
            alerts = superops_client.get_alerts()
            
            # Filter by status
            if status_filter != 'ALL':
                alerts = [a for a in alerts if a.get('status') == status_filter]
            
            logger.info(f"✅ Retrieved {len(alerts)} alerts from SuperOps")
            return jsonify(alerts)
        else:
            logger.info("Using mock alerts")
            filtered_alerts = [a for a in MOCK_ALERTS if a['status'] == status_filter or status_filter == 'ALL']
            return jsonify(filtered_alerts)
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify([]), 500


@app.route('/api/alerts/<alert_id>/acknowledge', methods=['PATCH'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        logger.info(f"Acknowledging alert {alert_id}")
        
        for alert in MOCK_ALERTS:
            if alert['id'] == alert_id:
                alert['status'] = 'ACKNOWLEDGED'
                alert['acknowledgedAt'] = datetime.utcnow().isoformat()
                
                return jsonify({
                    'success': True,
                    'alert': alert,
                    'message': f'Alert {alert_id} acknowledged'
                })
        
        return jsonify({'error': 'Alert not found'}), 404
        
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/<alert_id>/resolve', methods=['PATCH'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        logger.info(f"Resolving alert {alert_id}")
        
        for alert in MOCK_ALERTS:
            if alert['id'] == alert_id:
                alert['status'] = 'RESOLVED'
                alert['resolvedAt'] = datetime.utcnow().isoformat()
                
                return jsonify({
                    'success': True,
                    'alert': alert,
                    'message': f'Alert {alert_id} resolved'
                })
        
        return jsonify({'error': 'Alert not found'}), 404
        
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/active', methods=['GET'])
def get_active_alerts():
    """Get active alerts (compatibility endpoint for frontend)"""
    try:
        if USE_REAL_SUPEROPS and superops_client:
            logger.info("Fetching real active alerts from SuperOps...")
            alerts = superops_client.get_alerts()
            
            # Filter for active alerts only
            active_alerts = [a for a in alerts if a.get('status') == 'ACTIVE']
            
            logger.info(f"✅ Retrieved {len(active_alerts)} active alerts from SuperOps")
            return jsonify(active_alerts)
        else:
            logger.info("Using mock active alerts")
            active_alerts = [a for a in MOCK_ALERTS if a['status'] == 'ACTIVE']
            return jsonify(active_alerts)
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}")
        # Return mock data on error
        return jsonify([a for a in MOCK_ALERTS if a['status'] == 'ACTIVE'])


# ==================== PATCH MANAGEMENT ENDPOINTS ====================

@app.route('/api/patches', methods=['GET'])
def get_patches():
    """Get all available patches"""
    try:
        if USE_REAL_SUPEROPS and superops_client:
            logger.info("Fetching real patch data from SuperOps...")
            patches = superops_client.get_patch_status()
            logger.info(f"✅ Retrieved {len(patches)} patches from SuperOps")
            return jsonify(patches)
        else:
            logger.info("Using mock patch data")
            return jsonify(MOCK_PATCHES)
    except Exception as e:
        logger.error(f"Error getting patches: {e}")
        return jsonify(MOCK_PATCHES)


@app.route('/api/patches/<patch_id>/details', methods=['GET'])
def get_patch_details(patch_id):
    """Get detailed information for a specific patch from SuperOps"""
    try:
        logger.info(f"Fetching details for patch {patch_id}")
        
        # Find the patch
        patch = next((p for p in MOCK_PATCHES if p['id'] == patch_id), None)
        
        if not patch:
            return jsonify({'error': 'Patch not found'}), 404
        
        # Return extended details (in real scenario, this would fetch from SuperOps API)
        details = {
            'installTime': patch.get('installTime', 'Unknown'),
            'requiresReboot': patch.get('requiresReboot', False),
            'supersedes': patch.get('supersedes', []),
            'supersededBy': patch.get('supersededBy'),
            'knowledgeBaseUrl': f"https://support.vendor.com/kb/{patch_id}",
            'deploymentNotes': 'Test in non-production environment before deploying to production servers.',
            'rollbackAvailable': True,
            'compatibilityIssues': [],
            'estimatedDowntime': '2-5 minutes' if not patch.get('requiresReboot') else '10-15 minutes',
            'successRate': 98.5,
            'totalDeployments': random.randint(100, 5000),
            'failedDeployments': random.randint(0, 50)
        }
        
        return jsonify(details)
        
    except Exception as e:
        logger.error(f"Error getting patch details: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/patch-analysis', methods=['GET'])
def get_patch_analysis():
    """Get patch analysis summary"""
    try:
        critical_count = len([p for p in MOCK_PATCHES if p['severity'] == 'CRITICAL' and p['status'] == 'AVAILABLE'])
        total_affected = sum([len(p['affectedDevices']) for p in MOCK_PATCHES if p['status'] == 'AVAILABLE'])
        deployed_count = len([p for p in MOCK_PATCHES if p['status'] == 'DEPLOYED'])
        
        # Calculate patch coverage metrics
        total_devices = len(MOCK_DEVICES)
        fully_patched = len([d for d in MOCK_DEVICES if d['vulnerabilityCount']['critical'] == 0])
        partially_patched = len([d for d in MOCK_DEVICES if 0 < d['vulnerabilityCount']['critical'] < 3])
        unpatched = total_devices - fully_patched - partially_patched
        
        coverage_rate = (fully_patched / total_devices * 100) if total_devices > 0 else 0
        
        return jsonify({
            'criticalPending': critical_count,
            'totalAffectedDevices': total_affected,
            'complianceRate': coverage_rate,
            'coverageRate': coverage_rate,
            'fullyPatched': fully_patched,
            'partiallyPatched': partially_patched,
            'unpatched': unpatched,
            'totalPatches': len(MOCK_PATCHES),
            'availablePatches': len([p for p in MOCK_PATCHES if p['status'] == 'AVAILABLE']),
            'deployedPatches': deployed_count,
            'lastAnalysis': datetime.utcnow().isoformat(),
            'averageDeploymentTime': '12 minutes',
            'successRate': 97.8
        })
    except Exception as e:
        logger.error(f"Error getting patch analysis: {e}")
        return jsonify({}), 500


@app.route('/api/patch-schedule', methods=['GET'])
def get_patch_schedule():
    """Get scheduled patch deployments"""
    try:
        scheduled = [
            {
                'id': 'schedule-001',
                'patchTitle': 'Critical Security Update for Windows Server',
                'scheduledFor': (datetime.utcnow() + timedelta(days=1)).isoformat(),
                'deviceCount': 1
            },
            {
                'id': 'schedule-002',
                'patchTitle': 'Linux Kernel Security Patch',
                'scheduledFor': (datetime.utcnow() + timedelta(days=2)).isoformat(),
                'deviceCount': 2
            }
        ]
        
        if has_real_services:
            scheduled = patch_service.get_deployment_schedule()
        
        return jsonify(scheduled)
    except Exception as e:
        logger.error(f"Error getting patch schedule: {e}")
        return jsonify([])


@app.route('/api/ai/analyze-patch', methods=['POST'])
def analyze_patch():
    """AI-powered patch analysis using AWS Bedrock"""
    try:
        data = request.json
        patch = data.get('patch', {})
        devices = data.get('devices', [])
        vulnerabilities = data.get('vulnerabilities', [])
        
        logger.info(f"AI analyzing patch: {patch.get('id')}")
        
        # Use Bedrock AI service if available
        if bedrock_service:
            logger.info("Using Bedrock AI for patch analysis")
            analysis = bedrock_service.analyze_patch(patch)
            
            # Add mock data for compatibility
            analysis['recommendation'] = analysis.get('deployment_recommendation', 'SCHEDULED')
            analysis['reasoning'] = analysis.get('recommended_action', '')
            analysis['riskLevel'] = analysis.get('priority_score', 5)
            analysis['businessImpact'] = analysis.get('risk_assessment', {}).get('business_impact', 'MEDIUM')
            analysis['confidence'] = 0.90 if analysis.get('ai_generated') else 0.75
            analysis['automationRecommendation'] = 'MANUAL' if analysis.get('risk_assessment', {}).get('deployment_risk') == 'HIGH' else 'AUTO'
            analysis['suggestedTestingSteps'] = [
                analysis.get('testing_requirements', 'Test in development environment')
            ]
            analysis['rollbackProcedure'] = analysis.get('rollback_plan', 'Standard rollback procedure')
            analysis['estimatedDowntime'] = analysis.get('estimated_downtime', '< 5 minutes')
            analysis['affectedServices'] = [device.get('name') for device in devices[:5]]
            
            return jsonify(analysis)
        
        # Fallback mock AI analysis
        severity = patch.get('severity', 'MEDIUM')
        
        if severity == 'CRITICAL':
            recommendation = 'IMMEDIATE'
            risk_level = 9
            business_impact = 'CRITICAL'
            confidence = 0.95
            reasoning = 'Critical security vulnerability requires immediate patching. Risk of exploitation is high.'
        elif severity == 'HIGH':
            recommendation = 'SCHEDULED'
            risk_level = 7
            business_impact = 'MODERATE'
            confidence = 0.85
            reasoning = 'High priority patch. Recommend testing in non-production environment first.'
        else:
            recommendation = 'DEFERRED'
            risk_level = 5
            business_impact = 'MINIMAL'
            confidence = 0.75
            reasoning = 'Medium priority patch. Can be scheduled during next maintenance window.'
        
        analysis = {
            'recommendation': recommendation,
            'reasoning': reasoning,
            'riskLevel': risk_level,
            'businessImpact': business_impact,
            'confidence': confidence,
            'deploymentSteps': [
                'Create snapshot/backup of affected systems',
                'Verify patch compatibility with current configuration',
                'Deploy to test environment and monitor for 24 hours',
                'Schedule production deployment during maintenance window',
                'Deploy to production with monitoring enabled',
                'Verify successful installation on all devices',
                'Monitor systems for 48 hours post-deployment',
                'Document any issues and rollback if necessary'
            ],
            'rollbackPlan': 'Restore from snapshot if critical issues detected within 4 hours',
            'estimatedDuration': '2-4 hours',
            'maintenanceWindow': (datetime.utcnow() + timedelta(days=2)).replace(hour=2, minute=0).isoformat(),
            'affectedServices': ['Web Service', 'API Gateway'] if 'WEB' in patch.get('title', '') else ['Database Service'],
            'prerequisites': [
                'Valid system backups',
                'Change approval ticket',
                'Notification sent to stakeholders'
            ]
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing patch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/patches/deploy', methods=['POST'])
def deploy_patch():
    """Deploy patch to devices via SuperOps or manual deployment"""
    try:
        data = request.json
        patch_id = data.get('patchId')
        device_ids = data.get('deviceIds', [])
        schedule = data.get('schedule')
        ai_approved = data.get('aiApproved', False)
        
        logger.info(f"Deploying patch {patch_id} to {len(device_ids)} devices")
        
        # Try SuperOps deployment if enabled
        if USE_REAL_SUPEROPS and superops_client:
            try:
                logger.info("Deploying via SuperOps API...")
                result = superops_client.deploy_patch(
                    device_ids=device_ids,
                    patch_ids=[patch_id],
                    schedule=schedule
                )
                
                deployment = {
                    'deploymentId': result.get('deploymentId', f"deploy-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"),
                    'patchId': patch_id,
                    'deviceIds': device_ids,
                    'status': result.get('status', 'SCHEDULED' if schedule else 'IN_PROGRESS'),
                    'scheduledFor': result.get('scheduledFor') or (schedule.get('scheduledFor') if schedule else None),
                    'initiatedAt': datetime.utcnow().isoformat(),
                    'aiApproved': ai_approved,
                    'estimatedCompletion': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                    'message': result.get('message', 'Deployment initiated via SuperOps'),
                    'deploymentMethod': 'SuperOps'
                }
                
                logger.info(f"✅ Patch deployed via SuperOps: {deployment['deploymentId']}")
                return jsonify(deployment)
                
            except Exception as e:
                logger.error(f"SuperOps deployment failed: {e}. Falling back to mock deployment.")
        
        # Mock deployment (fallback or when SuperOps not enabled)
        deployment = {
            'deploymentId': f"deploy-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'patchId': patch_id,
            'deviceIds': device_ids,
            'status': 'SCHEDULED' if schedule else 'IN_PROGRESS',
            'scheduledFor': schedule.get('scheduledFor') if schedule else None,
            'initiatedAt': datetime.utcnow().isoformat(),
            'aiApproved': ai_approved,
            'estimatedCompletion': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'message': 'Deployment initiated (mock mode)',
            'deploymentMethod': 'Mock'
        }
        
        # Update patch status in mock data
        for patch in MOCK_PATCHES:
            if patch['id'] == patch_id:
                patch['status'] = 'SCHEDULED' if schedule else 'DEPLOYING'
        
        logger.info(f"✅ Mock patch deployment created: {deployment['deploymentId']}")
        return jsonify(deployment)
        
    except Exception as e:
        logger.error(f"Error deploying patch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/patches/schedule', methods=['POST'])
def schedule_patch_deployment():
    """Schedule a patch deployment for a specific date/time"""
    try:
        data = request.json
        patch_id = data.get('patchId')
        device_ids = data.get('deviceIds', [])
        scheduled_for = data.get('scheduledFor')  # ISO datetime string
        maintenance_window = data.get('maintenanceWindow')  # Optional: start/end times
        notes = data.get('notes', '')
        
        logger.info(f"Scheduling patch {patch_id} for {scheduled_for}")
        
        # Create schedule object
        schedule = {
            'scheduleId': f"sched-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'patchId': patch_id,
            'deviceIds': device_ids,
            'scheduledFor': scheduled_for,
            'maintenanceWindow': maintenance_window,
            'status': 'SCHEDULED',
            'createdAt': datetime.utcnow().isoformat(),
            'notes': notes,
            'estimatedDuration': '30 minutes',
            'autoApprove': data.get('autoApprove', False)
        }
        
        # If SuperOps is enabled, use it
        if USE_REAL_SUPEROPS and superops_client:
            try:
                result = superops_client.deploy_patch(
                    device_ids=device_ids,
                    patch_ids=[patch_id],
                    schedule={'scheduledFor': scheduled_for}
                )
                schedule['deploymentId'] = result.get('deploymentId')
                schedule['message'] = result.get('message', 'Scheduled via SuperOps')
                logger.info(f"✅ Patch scheduled via SuperOps: {schedule['scheduleId']}")
            except Exception as e:
                logger.error(f"SuperOps scheduling failed: {e}. Saved locally.")
                schedule['message'] = 'Scheduled locally (SuperOps unavailable)'
        else:
            schedule['message'] = 'Scheduled locally (mock mode)'
        
        # Update patch status
        for patch in MOCK_PATCHES:
            if patch['id'] == patch_id:
                patch['status'] = 'SCHEDULED'
        
        return jsonify(schedule)
        
    except Exception as e:
        logger.error(f"Error scheduling patch: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== NVD ENDPOINTS ====================

@app.route('/api/nvd/recent', methods=['GET'])
def get_recent_vulnerabilities():
    """Get recent vulnerabilities from NVD"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        if has_real_services:
            vulns = nvd_client.get_recent_cves(limit=limit)
            return jsonify(vulns)
        
        return jsonify(MOCK_VULNERABILITIES)
    except Exception as e:
        logger.error(f"Error getting NVD data: {e}")
        return jsonify(MOCK_VULNERABILITIES)


@app.route('/api/nvd/search', methods=['GET'])
def search_vulnerabilities():
    """Search NVD for specific CVEs"""
    try:
        cve_id = request.args.get('cveId')
        keyword = request.args.get('keyword')
        
        if has_real_services and cve_id:
            vuln = nvd_client.get_cve_details(cve_id)
            return jsonify(vuln)
        
        # Mock search
        results = [v for v in MOCK_VULNERABILITIES if cve_id in v.get('cveId', '') or keyword in v.get('description', '')]
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error searching NVD: {e}")
        return jsonify([])


# ==================== AI AGENTS ENDPOINTS ====================

@app.route('/api/ai/agents/status', methods=['GET'])
def get_agents_status():
    """Get AI agents status"""
    try:
        if ai_agents_service:
            status = ai_agents_service.get_agent_status()
            return jsonify(status)
        
        return jsonify({
            'crewai_available': False,
            'agents_initialized': False,
            'bedrock_service': bedrock_service is not None,
            'agents': {},
            'mode': 'Offline'
        })
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/agents/prioritize', methods=['POST'])
def prioritize_patches_ai():
    """Use AI agents to prioritize patches"""
    try:
        data = request.get_json()
        patches = data.get('patches', MOCK_PATCHES)
        context = data.get('context', {})
        
        if ai_agents_service:
            result = ai_agents_service.prioritize_patches(patches, context)
            return jsonify(result)
        
        # Fallback to simple prioritization
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        sorted_patches = sorted(
            patches,
            key=lambda p: (severity_order.get(p.get('severity', 'MEDIUM'), 0), -len(p.get('affectedDevices', []))),
            reverse=True
        )
        
        return jsonify({
            'prioritized_patches': sorted_patches,
            'ai_generated': False,
            'model': 'Fallback',
            'agent': 'None'
        })
    except Exception as e:
        logger.error(f"Error prioritizing patches with AI: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/agents/correlate-alerts', methods=['POST'])
def correlate_alerts_ai():
    """Use AI agents to correlate alerts"""
    try:
        data = request.get_json()
        alerts = data.get('alerts', MOCK_ALERTS)
        
        if ai_agents_service:
            result = ai_agents_service.correlate_alerts(alerts)
            return jsonify(result)
        
        # Fallback to simple grouping
        correlations = {}
        for alert in alerts:
            device_id = alert.get('deviceId', 'unknown')
            key = device_id
            if key not in correlations:
                correlations[key] = {
                    'device': alert.get('deviceName', device_id),
                    'alerts': [],
                    'count': 0
                }
            correlations[key]['alerts'].append(alert)
            correlations[key]['count'] += 1
        
        return jsonify({
            'correlations': list(correlations.values()),
            'total_alerts': len(alerts),
            'ai_generated': False,
            'model': 'Fallback'
        })
    except Exception as e:
        logger.error(f"Error correlating alerts with AI: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/agents/decide-remediation', methods=['POST'])
def decide_remediation_ai():
    """Use AI agents to decide remediation strategy"""
    try:
        data = request.get_json()
        vulnerability = data.get('vulnerability', {})
        options = data.get('options', [
            {'name': 'Immediate Patch', 'description': 'Deploy patch immediately'},
            {'name': 'Scheduled Patch', 'description': 'Schedule for maintenance window'},
            {'name': 'Workaround', 'description': 'Apply temporary workaround'},
            {'name': 'Accept Risk', 'description': 'Document and accept the risk'}
        ])
        
        if ai_agents_service:
            result = ai_agents_service.decide_remediation(vulnerability, options)
            return jsonify(result)
        
        # Fallback to severity-based decision
        severity = vulnerability.get('severity', 'MEDIUM')
        if severity in ['CRITICAL', 'HIGH']:
            recommended = options[0]
            urgency = 'IMMEDIATE'
        else:
            recommended = options[1]
            urgency = 'SCHEDULED'
        
        return jsonify({
            'decision': {
                'recommended_option': recommended,
                'urgency': urgency,
                'justification': f'Based on {severity} severity',
                'confidence': 0.5
            },
            'ai_generated': False,
            'model': 'Fallback'
        })
    except Exception as e:
        logger.error(f"Error deciding remediation with AI: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/agents/learn', methods=['POST'])
def learn_from_outcome():
    """AI agents learn from deployment outcomes"""
    try:
        data = request.get_json()
        action = data.get('action', {})
        outcome = data.get('outcome', {})
        
        if ai_agents_service:
            result = ai_agents_service.learn_from_outcome(action, outcome)
            return jsonify(result)
        
        # Fallback to simple logging
        return jsonify({
            'learnings': {
                'recorded': True,
                'timestamp': datetime.utcnow().isoformat(),
                'action_type': action.get('type'),
                'outcome_status': outcome.get('status')
            },
            'ai_generated': False,
            'model': 'Fallback'
        })
    except Exception as e:
        logger.error(f"Error learning from outcome: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== DASHBOARD STATS ====================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            'totalDevices': len(MOCK_DEVICES),
            'criticalVulnerabilities': sum(d['vulnerabilityCount']['critical'] for d in MOCK_DEVICES),
            'activeAlerts': len([a for a in MOCK_ALERTS if a['status'] == 'ACTIVE']),
            'pendingPatches': len([p for p in MOCK_PATCHES if p['status'] in ['AVAILABLE', 'PENDING']]),
            'complianceRate': 75.5,
            'averageRiskScore': round(sum(d['riskScore'] for d in MOCK_DEVICES) / len(MOCK_DEVICES), 1),
            'lastUpdated': datetime.utcnow().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({}), 500


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'superops': superops_client is not None,
            'nvd': nvd_client is not None,
            'bedrock': bedrock_service is not None,
            'ai_agents': ai_agents_service is not None,
            'ai_agents_mode': ai_agents_service.get_agent_status()['mode'] if ai_agents_service else 'Offline'
        }
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║              AutoOps AI - Development Server             ║
╠══════════════════════════════════════════════════════════╣
║  Server running on: http://localhost:{port}               ║
║  Real services enabled: {has_real_services}                          ║
║  Debug mode: {debug}                                        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
