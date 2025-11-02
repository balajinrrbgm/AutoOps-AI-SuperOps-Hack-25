#!/usr/bin/env python3
"""
Local development server for AutoOps AI
Simulates the Lambda API endpoints for local testing
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Mock data
MOCK_PATCH_STATUS = {
    "totalDevices": 150,
    "compliant": 128,
    "pending": 22,
    "lastUpdate": datetime.now().isoformat()
}

MOCK_ALERTS = [
    {
        "id": 1,
        "title": "High CPU Usage on SQL Server",
        "description": "SQL Server on PROD-DB-01 showing 95% CPU utilization",
        "severity": "critical",
        "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "source": "SuperOps"
    },
    {
        "id": 2,
        "title": "Failed Windows Update",
        "description": "KB5034441 failed to install on multiple workstations",
        "severity": "high",
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        "source": "WSUS"
    },
    {
        "id": 3,
        "title": "Low Disk Space Warning",
        "description": "C: drive on FILE-SRV-02 has less than 10% free space",
        "severity": "medium",
        "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
        "source": "Monitoring"
    }
]

MOCK_ACTIONS = [
    {
        "id": 1,
        "type": "Patch Deployment",
        "description": "Deployed security updates to 25 workstations",
        "status": "completed",
        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
        "agent": "AI-Patch-Agent"
    },
    {
        "id": 2,
        "type": "Alert Correlation",
        "description": "Correlated 5 disk space alerts into single incident",
        "status": "completed",
        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
        "agent": "AI-Alert-Agent"
    },
    {
        "id": 3,
        "type": "Risk Assessment",
        "description": "Analyzing impact of pending CVE-2024-1234 patches",
        "status": "pending",
        "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "agent": "AI-Risk-Agent"
    }
]

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AutoOps AI Local Dev Server"
    })

@app.route('/patches/status', methods=['GET'])
def get_patch_status():
    """Get patch management status"""
    # Add some randomness to simulate real data changes
    status = MOCK_PATCH_STATUS.copy()
    status["pending"] = random.randint(15, 30)
    status["compliant"] = status["totalDevices"] - status["pending"]
    status["lastUpdate"] = datetime.now().isoformat()
    
    return jsonify(status)

@app.route('/alerts/active', methods=['GET'])
def get_active_alerts():
    """Get active alerts"""
    # Simulate some alerts aging out or new ones appearing
    active_alerts = MOCK_ALERTS.copy()
    
    # Sometimes add a new alert
    if random.random() < 0.3:
        new_alert = {
            "id": len(active_alerts) + 1,
            "title": "New Network Connectivity Issue",
            "description": f"Switch SW-{random.randint(10,99)} showing intermittent connectivity",
            "severity": random.choice(["low", "medium", "high"]),
            "timestamp": datetime.now().isoformat(),
            "source": "Network Monitoring"
        }
        active_alerts.append(new_alert)
    
    return jsonify(active_alerts)

@app.route('/actions/recent', methods=['GET'])
def get_recent_actions():
    """Get recent AI actions"""
    return jsonify(MOCK_ACTIONS)

@app.route('/devices/inventory', methods=['GET'])
def get_device_inventory():
    """Get device inventory from SuperOps"""
    inventory = []
    for i in range(1, 21):  # Mock 20 devices
        device = {
            "id": f"device-{i:03d}",
            "name": f"WS-{i:03d}" if i <= 15 else f"SRV-{i-15:02d}",
            "type": "workstation" if i <= 15 else "server",
            "os": "Windows 11" if i <= 10 else "Windows Server 2022" if i > 15 else "Windows 10",
            "lastSeen": (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat(),
            "patchStatus": random.choice(["compliant", "pending", "failed"]),
            "pendingPatches": random.randint(0, 15) if random.random() < 0.4 else 0
        }
        inventory.append(device)
    
    return jsonify(inventory)

@app.route('/ai/risk-assessment', methods=['POST'])
def ai_risk_assessment():
    """AI risk assessment endpoint"""
    data = request.get_json()
    
    # Mock AI response
    assessment = {
        "riskScore": random.randint(1, 10),
        "recommendation": "Deploy during maintenance window",
        "impactAnalysis": "Low risk - affects non-critical systems only",
        "confidence": random.uniform(0.8, 0.99),
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(assessment)

@app.route('/workflow/execute', methods=['POST'])
def execute_workflow():
    """Execute automation workflow"""
    data = request.get_json()
    
    # Mock workflow execution
    result = {
        "workflowId": f"wf-{random.randint(1000, 9999)}",
        "status": "initiated",
        "estimatedCompletion": (datetime.now() + timedelta(minutes=30)).isoformat(),
        "steps": [
            {"name": "Validate", "status": "completed"},
            {"name": "Risk Assessment", "status": "completed"},
            {"name": "Deploy", "status": "running"},
            {"name": "Verify", "status": "pending"}
        ]
    }
    
    return jsonify(result)

@app.route('/nvd/top-cves', methods=['GET'])
def get_top_cves():
    """Get top 10 critical CVEs"""
    # Mock top CVEs data
    top_cves = [
        {
            "id": "CVE-2024-9123",
            "cvssScore": 9.8,
            "severity": "CRITICAL",
            "description": "Critical RCE vulnerability in Apache HTTP Server allows attackers to execute arbitrary code",
            "published": "2024-10-15T00:00:00",
            "affectedSystems": 45,
            "patchAvailable": True
        },
        {
            "id": "CVE-2024-8956",
            "cvssScore": 9.4,
            "severity": "CRITICAL",
            "description": "Windows Kernel elevation of privilege vulnerability",
            "published": "2024-10-12T00:00:00",
            "affectedSystems": 89,
            "patchAvailable": True
        },
        {
            "id": "CVE-2024-8743",
            "cvssScore": 9.1,
            "severity": "CRITICAL",
            "description": "SQL Server remote code execution vulnerability allows unauthenticated attackers",
            "published": "2024-10-10T00:00:00",
            "affectedSystems": 23,
            "patchAvailable": True
        },
        {
            "id": "CVE-2024-8521",
            "cvssScore": 8.8,
            "severity": "HIGH",
            "description": "OpenSSL buffer overflow vulnerability in TLS handshake processing",
            "published": "2024-10-08T00:00:00",
            "affectedSystems": 156,
            "patchAvailable": True
        },
        {
            "id": "CVE-2024-8234",
            "cvssScore": 8.6,
            "severity": "HIGH",
            "description": "Chrome V8 type confusion vulnerability allows remote code execution",
            "published": "2024-10-05T00:00:00",
            "affectedSystems": 67,
            "patchAvailable": True
        },
        {
            "id": "CVE-2024-7912",
            "cvssScore": 8.4,
            "severity": "HIGH",
            "description": "VMware ESXi heap overflow vulnerability in USB service",
            "published": "2024-10-03T00:00:00",
            "affectedSystems": 12,
            "patchAvailable": False
        },
        {
            "id": "CVE-2024-7654",
            "cvssScore": 8.1,
            "severity": "HIGH",
            "description": "Linux Kernel use-after-free vulnerability in netfilter subsystem",
            "published": "2024-10-01T00:00:00",
            "affectedSystems": 34,
            "patchAvailable": True
        },
        {
            "id": "CVE-2024-7432",
            "cvssScore": 7.8,
            "severity": "HIGH",
            "description": "Microsoft Exchange Server privilege escalation vulnerability",
            "published": "2024-09-28T00:00:00",
            "affectedSystems": 28,
            "patchAvailable": True
        },
        {
            "id": "CVE-2024-7123",
            "cvssScore": 7.5,
            "severity": "HIGH",
            "description": "Jenkins arbitrary file read vulnerability through crafted requests",
            "published": "2024-09-25T00:00:00",
            "affectedSystems": 8,
            "patchAvailable": True
        },
        {
            "id": "CVE-2024-6890",
            "cvssScore": 7.2,
            "severity": "HIGH",
            "description": "Docker Engine privilege escalation through container escape",
            "published": "2024-09-22T00:00:00",
            "affectedSystems": 19,
            "patchAvailable": True
        }
    ]
    
    return jsonify(top_cves)

@app.route('/stats/overview', methods=['GET'])
def get_stats_overview():
    """Get comprehensive stats for dashboard"""
    stats = {
        "vulnerabilities": {
            "critical": random.randint(8, 15),
            "high": random.randint(20, 35),
            "medium": random.randint(40, 60),
            "low": random.randint(15, 25),
            "total": random.randint(100, 150)
        },
        "patches": {
            "deployed": random.randint(80, 95),
            "pending": random.randint(10, 25),
            "failed": random.randint(2, 8)
        },
        "devices": {
            "total": 150,
            "online": random.randint(140, 148),
            "offline": random.randint(2, 10),
            "critical": random.randint(0, 3)
        },
        "automation": {
            "tasksCompleted": random.randint(500, 800),
            "tasksRunning": random.randint(5, 15),
            "successRate": random.uniform(94.5, 99.5)
        }
    }
    
    return jsonify(stats)

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get SuperOps device inventory with vulnerability data"""
    # Mock comprehensive inventory data
    inventory = [
        {
            'id': 'dev-001',
            'name': 'WEB-SERVER-PROD-01',
            'type': 'Windows Server',
            'operatingSystem': 'Windows Server 2019 Build 17763',
            'ipAddress': '192.168.1.10',
            'macAddress': '00:0C:29:A1:B2:C3',
            'lastSeenAt': datetime.now().isoformat(),
            'client': 'Acme Corporation',
            'site': 'Data Center East',
            'vulnerabilityStats': {
                'total': 8,
                'critical': 2,
                'high': 3,
                'medium': 3
            },
            'topVulnerabilities': [
                {'cveId': 'CVE-2024-38063', 'cvssScore': 9.8, 'severity': 'CRITICAL'},
                {'cveId': 'CVE-2024-43491', 'cvssScore': 9.0, 'severity': 'CRITICAL'}
            ],
            'riskScore': 87.5
        },
        {
            'id': 'dev-002',
            'name': 'DB-SERVER-PROD-01',
            'type': 'Linux Server',
            'operatingSystem': 'Ubuntu 22.04.3 LTS',
            'ipAddress': '192.168.1.20',
            'macAddress': '00:0C:29:D4:E5:F6',
            'lastSeenAt': datetime.now().isoformat(),
            'client': 'Acme Corporation',
            'site': 'Data Center East',
            'vulnerabilityStats': {
                'total': 5,
                'critical': 1,
                'high': 2,
                'medium': 2
            },
            'topVulnerabilities': [
                {'cveId': 'CVE-2024-26130', 'cvssScore': 9.1, 'severity': 'CRITICAL'}
            ],
            'riskScore': 72.3
        },
        {
            'id': 'dev-003',
            'name': 'APP-SERVER-PROD-01',
            'type': 'Windows Server',
            'operatingSystem': 'Windows Server 2022 Build 20348',
            'ipAddress': '192.168.1.30',
            'macAddress': '00:0C:29:G7:H8:I9',
            'lastSeenAt': datetime.now().isoformat(),
            'client': 'TechStart Inc',
            'site': 'Data Center West',
            'vulnerabilityStats': {
                'total': 12,
                'critical': 3,
                'high': 5,
                'medium': 4
            },
            'topVulnerabilities': [
                {'cveId': 'CVE-2024-38063', 'cvssScore': 9.8, 'severity': 'CRITICAL'},
                {'cveId': 'CVE-2024-43491', 'cvssScore': 9.0, 'severity': 'CRITICAL'}
            ],
            'riskScore': 92.1
        },
        {
            'id': 'dev-004',
            'name': 'FILE-SERVER-01',
            'type': 'Windows Server',
            'operatingSystem': 'Windows Server 2016 Build 14393',
            'ipAddress': '192.168.1.40',
            'macAddress': '00:0C:29:J1:K2:L3',
            'lastSeenAt': (datetime.now() - timedelta(hours=2)).isoformat(),
            'client': 'Global Enterprises',
            'site': 'Branch Office',
            'vulnerabilityStats': {
                'total': 15,
                'critical': 5,
                'high': 6,
                'medium': 4
            },
            'topVulnerabilities': [
                {'cveId': 'CVE-2024-38063', 'cvssScore': 9.8, 'severity': 'CRITICAL'},
                {'cveId': 'CVE-2024-43491', 'cvssScore': 9.0, 'severity': 'CRITICAL'}
            ],
            'riskScore': 95.7
        },
        {
            'id': 'dev-005',
            'name': 'WORKSTATION-HR-05',
            'type': 'Workstation',
            'operatingSystem': 'Windows 11 Pro Build 22621',
            'ipAddress': '192.168.2.15',
            'macAddress': '00:0C:29:M4:N5:O6',
            'lastSeenAt': datetime.now().isoformat(),
            'client': 'Acme Corporation',
            'site': 'Headquarters',
            'vulnerabilityStats': {
                'total': 3,
                'critical': 0,
                'high': 1,
                'medium': 2
            },
            'topVulnerabilities': [
                {'cveId': 'CVE-2024-38200', 'cvssScore': 7.5, 'severity': 'HIGH'}
            ],
            'riskScore': 35.2
        }
    ]
    return jsonify(inventory)

@app.route('/api/alerts', methods=['GET'])
def get_enriched_alerts():
    """Get alerts enriched with vulnerability context"""
    alerts = [
        {
            'id': 'alert-001',
            'title': 'Critical Vulnerability Detected',
            'description': 'CVE-2024-38063 detected on WEB-SERVER-PROD-01',
            'severity': 'CRITICAL',
            'status': 'ACTIVE',
            'source': 'NVD Scanner',
            'deviceId': 'dev-001',
            'deviceName': 'WEB-SERVER-PROD-01',
            'createdAt': (datetime.now() - timedelta(hours=2)).isoformat(),
            'updatedAt': (datetime.now() - timedelta(hours=1)).isoformat(),
            'relatedVulnerabilities': 8,
            'criticalVulnerabilities': 2,
            'highVulnerabilities': 3,
            'vulnerabilityDetails': [
                {
                    'cveId': 'CVE-2024-38063',
                    'cvssScore': 9.8,
                    'severity': 'CRITICAL',
                    'description': 'Windows TCP/IP Remote Code Execution Vulnerability'
                }
            ]
        },
        {
            'id': 'alert-002',
            'title': 'Multiple High Severity Vulnerabilities',
            'description': 'Multiple vulnerabilities detected on APP-SERVER-PROD-01',
            'severity': 'HIGH',
            'status': 'ACTIVE',
            'source': 'Vulnerability Analyzer',
            'deviceId': 'dev-003',
            'deviceName': 'APP-SERVER-PROD-01',
            'createdAt': (datetime.now() - timedelta(hours=5)).isoformat(),
            'updatedAt': (datetime.now() - timedelta(hours=3)).isoformat(),
            'relatedVulnerabilities': 12,
            'criticalVulnerabilities': 3,
            'highVulnerabilities': 5,
            'vulnerabilityDetails': [
                {
                    'cveId': 'CVE-2024-38063',
                    'cvssScore': 9.8,
                    'severity': 'CRITICAL',
                    'description': 'Windows TCP/IP Remote Code Execution Vulnerability'
                },
                {
                    'cveId': 'CVE-2024-43491',
                    'cvssScore': 9.0,
                    'severity': 'CRITICAL',
                    'description': 'Windows Update Remote Code Execution Vulnerability'
                }
            ]
        },
        {
            'id': 'alert-003',
            'title': 'Outdated OS Version Detected',
            'description': 'Windows Server 2016 requires security updates',
            'severity': 'HIGH',
            'status': 'ACKNOWLEDGED',
            'source': 'Compliance Scanner',
            'deviceId': 'dev-004',
            'deviceName': 'FILE-SERVER-01',
            'createdAt': (datetime.now() - timedelta(days=1)).isoformat(),
            'updatedAt': (datetime.now() - timedelta(hours=6)).isoformat(),
            'relatedVulnerabilities': 15,
            'criticalVulnerabilities': 5,
            'highVulnerabilities': 6,
            'vulnerabilityDetails': [
                {
                    'cveId': 'CVE-2024-38063',
                    'cvssScore': 9.8,
                    'severity': 'CRITICAL',
                    'description': 'Windows TCP/IP Remote Code Execution Vulnerability'
                }
            ]
        },
        {
            'id': 'alert-004',
            'title': 'Patch Deployment Required',
            'description': 'Security patches pending for DB-SERVER-PROD-01',
            'severity': 'MEDIUM',
            'status': 'ACTIVE',
            'source': 'Patch Manager',
            'deviceId': 'dev-002',
            'deviceName': 'DB-SERVER-PROD-01',
            'createdAt': (datetime.now() - timedelta(hours=8)).isoformat(),
            'updatedAt': (datetime.now() - timedelta(hours=8)).isoformat(),
            'relatedVulnerabilities': 5,
            'criticalVulnerabilities': 1,
            'highVulnerabilities': 2,
            'vulnerabilityDetails': []
        }
    ]
    return jsonify(alerts)

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """Create a new alert"""
    data = request.get_json()
    
    alert = {
        'alertId': f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'title': data.get('title', 'New Alert'),
        'description': data.get('description', ''),
        'severity': data.get('severity', 'MEDIUM'),
        'deviceId': data.get('deviceId'),
        'deviceName': data.get('deviceName'),
        'createdAt': datetime.now().isoformat(),
        'status': 'ACTIVE'
    }
    
    return jsonify(alert), 201

@app.route('/api/patch-analysis', methods=['GET'])
def get_patch_analysis():
    """Get patch coverage analysis"""
    analysis = {
        'totalDevices': 147,
        'fullyPatched': 98,
        'partiallyPatched': 35,
        'unpatched': 14,
        'coverageRate': 66.7,
        'criticalExposure': [
            {
                'deviceId': 'dev-004',
                'deviceName': 'FILE-SERVER-01',
                'cveId': 'CVE-2024-38063',
                'cvssScore': 9.8
            },
            {
                'deviceId': 'dev-003',
                'deviceName': 'APP-SERVER-PROD-01',
                'cveId': 'CVE-2024-38063',
                'cvssScore': 9.8
            }
        ],
        'patchRecommendations': [
            {
                'deviceId': 'dev-001',
                'deviceName': 'WEB-SERVER-PROD-01',
                'criticalPatches': 2,
                'patches': [
                    {
                        'id': 'KB5043083',
                        'title': 'Security Update for Windows Server 2019',
                        'severity': 'Critical',
                        'cveId': 'CVE-2024-38063'
                    }
                ]
            },
            {
                'deviceId': 'dev-004',
                'deviceName': 'FILE-SERVER-01',
                'criticalPatches': 5,
                'patches': [
                    {
                        'id': 'KB5043064',
                        'title': 'Security Update for Windows Server 2016',
                        'severity': 'Critical',
                        'cveId': 'CVE-2024-38063'
                    }
                ]
            }
        ]
    }
    return jsonify(analysis)

@app.route('/api/vulnerability-analysis', methods=['GET'])
def get_vulnerability_analysis():
    """Analyze vulnerabilities across all devices"""
    device_id = request.args.get('deviceId')
    
    # Mock vulnerability analysis data
    vulnerabilities = [
        {
            'deviceId': 'dev-001',
            'deviceName': 'WEB-SERVER-PROD-01',
            'cveId': 'CVE-2024-38063',
            'cvssScore': 9.8,
            'severity': 'CRITICAL',
            'description': 'Windows TCP/IP Remote Code Execution Vulnerability',
            'publishedDate': '2024-08-13',
            'patchAvailable': True,
            'affectedSoftware': ['Windows Server 2019']
        },
        {
            'deviceId': 'dev-002',
            'deviceName': 'DB-SERVER-PROD-01',
            'cveId': 'CVE-2024-26130',
            'cvssScore': 9.1,
            'severity': 'CRITICAL',
            'description': 'Linux Kernel Use After Free Vulnerability',
            'publishedDate': '2024-07-22',
            'patchAvailable': True,
            'affectedSoftware': ['Ubuntu 22.04']
        }
    ]
    
    if device_id:
        vulnerabilities = [v for v in vulnerabilities if v['deviceId'] == device_id]
    
    return jsonify(vulnerabilities)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    print(f"🚀 AutoOps AI Local Dev Server starting on port {port}")
    print(f"📊 Dashboard available at: http://localhost:3000")
    print(f"🔧 API endpoints available at: http://localhost:{port}")
    print("\n📍 Available endpoints:")
    print("  GET  /health")
    print("  GET  /patches/status")
    print("  GET  /alerts/active")
    print("  GET  /actions/recent")
    print("  GET  /devices/inventory")
    print("  GET  /nvd/top-cves")
    print("  GET  /stats/overview")
    print("  GET  /api/inventory               - Device inventory with vulnerabilities")
    print("  GET  /api/alerts                  - Alerts with vulnerability context")
    print("  POST /api/alerts                  - Create new alert")
    print("  GET  /api/patch-analysis          - Patch coverage analysis")
    print("  GET  /api/vulnerability-analysis  - Vulnerability analysis")
    print("  POST /ai/risk-assessment")
    print("  POST /workflow/execute")
    
    app.run(host='0.0.0.0', port=port, debug=True)