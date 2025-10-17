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
    print("  POST /ai/risk-assessment")
    print("  POST /workflow/execute")
    
    app.run(host='0.0.0.0', port=port, debug=True)