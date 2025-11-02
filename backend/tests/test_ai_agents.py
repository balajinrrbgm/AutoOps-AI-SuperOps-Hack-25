"""
Test script for AI Agents Service
Demonstrates multi-agent capabilities with and without CrewAI
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_agents.agents_service import AIAgentsService
from integrations.bedrock_service import BedrockAIService

def test_agents():
    print("=" * 80)
    print("AutoOps AI Agents Service Test")
    print("=" * 80)
    
    # Initialize services
    print("\n1. Initializing services...")
    try:
        bedrock_service = BedrockAIService()
        print("   ✅ Bedrock service initialized")
    except Exception as e:
        print(f"   ⚠️ Bedrock service failed: {e}")
        bedrock_service = None
    
    try:
        ai_agents = AIAgentsService(bedrock_service=bedrock_service)
        print("   ✅ AI Agents service initialized")
    except Exception as e:
        print(f"   ❌ AI Agents service failed: {e}")
        return
    
    # Check status
    print("\n2. Checking AI Agents status...")
    status = ai_agents.get_agent_status()
    print(f"   Mode: {status['mode']}")
    print(f"   CrewAI Available: {status['crewai_available']}")
    print(f"   Agents Initialized: {status['agents_initialized']}")
    print(f"   Bedrock Service: {status['bedrock_service']}")
    
    # Test patch prioritization
    print("\n3. Testing Patch Prioritization Agent...")
    mock_patches = [
        {
            'id': 'patch-001',
            'title': 'Windows Security Update KB5001234',
            'severity': 'CRITICAL',
            'cvssScore': 9.8,
            'relatedCVEs': ['CVE-2024-1234', 'CVE-2024-5678'],
            'affectedDevices': ['device-1', 'device-2', 'device-3']
        },
        {
            'id': 'patch-002',
            'title': 'Office Update KB5005678',
            'severity': 'MEDIUM',
            'cvssScore': 5.5,
            'relatedCVEs': ['CVE-2024-9999'],
            'affectedDevices': ['device-4']
        },
        {
            'id': 'patch-003',
            'title': 'Chrome Browser Update',
            'severity': 'HIGH',
            'cvssScore': 7.2,
            'relatedCVEs': ['CVE-2024-1111', 'CVE-2024-2222'],
            'affectedDevices': ['device-1', 'device-2']
        }
    ]
    
    result = ai_agents.prioritize_patches(mock_patches, context={'environment': 'production'})
    print(f"   AI Generated: {result.get('ai_generated')}")
    print(f"   Model: {result.get('model')}")
    print(f"   Agent: {result.get('agent')}")
    print(f"   Prioritized {len(result.get('prioritized_patches', []))} patches")
    
    # Test alert correlation
    print("\n4. Testing Alert Correlation Agent...")
    mock_alerts = [
        {'id': 'alert-1', 'title': 'High CPU Usage', 'deviceId': 'device-1', 'deviceName': 'WEB-SERVER-01', 'severity': 'HIGH'},
        {'id': 'alert-2', 'title': 'Memory Leak Detected', 'deviceId': 'device-1', 'deviceName': 'WEB-SERVER-01', 'severity': 'MEDIUM'},
        {'id': 'alert-3', 'title': 'Disk Full', 'deviceId': 'device-2', 'deviceName': 'DB-SERVER-01', 'severity': 'CRITICAL'},
        {'id': 'alert-4', 'title': 'Connection Timeout', 'deviceId': 'device-1', 'deviceName': 'WEB-SERVER-01', 'severity': 'HIGH'}
    ]
    
    result = ai_agents.correlate_alerts(mock_alerts)
    print(f"   Total Alerts: {result.get('total_alerts')}")
    print(f"   Correlated Groups: {len(result.get('correlations', []))}")
    print(f"   AI Generated: {result.get('ai_generated')}")
    print(f"   Model: {result.get('model')}")
    
    # Test remediation decision
    print("\n5. Testing Remediation Decision Agent...")
    vulnerability = {
        'cveId': 'CVE-2024-1234',
        'description': 'Remote Code Execution in Windows SMB',
        'severity': 'CRITICAL',
        'cvssScore': 9.8
    }
    
    options = [
        {'name': 'Immediate Patch', 'description': 'Deploy patch immediately to all servers'},
        {'name': 'Scheduled Patch', 'description': 'Schedule for next maintenance window'},
        {'name': 'Workaround', 'description': 'Disable SMB service temporarily'}
    ]
    
    result = ai_agents.decide_remediation(vulnerability, options)
    decision = result.get('decision', {})
    print(f"   Recommended: {decision.get('recommended_option', {}).get('name')}")
    print(f"   Urgency: {decision.get('urgency')}")
    print(f"   Justification: {decision.get('justification')}")
    print(f"   AI Generated: {result.get('ai_generated')}")
    
    # Test learning agent
    print("\n6. Testing Learning & Optimization Agent...")
    action = {'type': 'patch_deployment', 'patch_id': 'patch-001', 'devices': 3}
    outcome = {'status': 'SUCCESS', 'devices_updated': 3, 'duration_minutes': 15}
    
    result = ai_agents.learn_from_outcome(action, outcome)
    print(f"   Learning Recorded: {result.get('learnings', {}).get('success', False)}")
    print(f"   AI Generated: {result.get('ai_generated')}")
    print(f"   Model: {result.get('model')}")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed successfully!")
    print("=" * 80)

if __name__ == '__main__':
    test_agents()
