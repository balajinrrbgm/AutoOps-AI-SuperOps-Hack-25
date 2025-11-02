'use client';

import React, { useState, useEffect } from 'react';
import { fetchAuthSession } from 'aws-amplify/auth';
import axios from 'axios';

const Dashboard = () => {
  const [patchStatus, setPatchStatus] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [aiActions, setAiActions] = useState([]);
  const [topCVEs, setTopCVEs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      // For local development, use mock data instead of API calls
      if (process.env.NODE_ENV === 'development') {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setPatchStatus({
          totalDevices: 150,
          compliant: 128,
          pending: 22,
          lastUpdate: new Date().toISOString()
        });
        
        setAlerts([
          {
            id: 1,
            title: "High CPU Usage on SQL Server",
            description: "SQL Server on PROD-DB-01 showing 95% CPU utilization",
            severity: "critical"
          },
          {
            id: 2,
            title: "Failed Windows Update",
            description: "KB5034441 failed to install on multiple workstations",
            severity: "high"
          },
          {
            id: 3,
            title: "Low Disk Space Warning",
            description: "C: drive on FILE-SRV-02 has less than 10% free space",
            severity: "medium"
          }
        ]);
        
        setAiActions([
          {
            id: 1,
            type: "Patch Deployment",
            description: "Deployed security updates to 25 workstations",
            status: "completed",
            timestamp: new Date(Date.now() - 3600000).toISOString()
          },
          {
            id: 2,
            type: "Alert Correlation",
            description: "Correlated 5 disk space alerts into single incident",
            status: "completed",
            timestamp: new Date(Date.now() - 10800000).toISOString()
          },
          {
            id: 3,
            type: "Risk Assessment",
            description: "Analyzing impact of pending CVE-2024-1234 patches",
            status: "pending",
            timestamp: new Date(Date.now() - 1800000).toISOString()
          }
        ]);

        // Mock Top CVEs data
        setTopCVEs([
          {
            id: "CVE-2024-9123",
            cvssScore: 9.8,
            severity: "CRITICAL",
            description: "Critical RCE vulnerability in Apache HTTP Server allows attackers to execute arbitrary code",
            published: "2024-10-15T00:00:00",
            affectedSystems: 45,
            patchAvailable: true
          },
          {
            id: "CVE-2024-8956",
            cvssScore: 9.4,
            severity: "CRITICAL",
            description: "Windows Kernel elevation of privilege vulnerability",
            published: "2024-10-12T00:00:00",
            affectedSystems: 89,
            patchAvailable: true
          },
          {
            id: "CVE-2024-8743",
            cvssScore: 9.1,
            severity: "CRITICAL",
            description: "SQL Server remote code execution vulnerability allows unauthenticated attackers",
            published: "2024-10-10T00:00:00",
            affectedSystems: 23,
            patchAvailable: true
          },
          {
            id: "CVE-2024-8521",
            cvssScore: 8.8,
            severity: "HIGH",
            description: "OpenSSL buffer overflow vulnerability in TLS handshake processing",
            published: "2024-10-08T00:00:00",
            affectedSystems: 156,
            patchAvailable: true
          },
          {
            id: "CVE-2024-8234",
            cvssScore: 8.6,
            severity: "HIGH",
            description: "Chrome V8 type confusion vulnerability allows remote code execution",
            published: "2024-10-05T00:00:00",
            affectedSystems: 67,
            patchAvailable: true
          },
          {
            id: "CVE-2024-7912",
            cvssScore: 8.4,
            severity: "HIGH",
            description: "VMware ESXi heap overflow vulnerability in USB service",
            published: "2024-10-03T00:00:00",
            affectedSystems: 12,
            patchAvailable: false
          },
          {
            id: "CVE-2024-7654",
            cvssScore: 8.1,
            severity: "HIGH",
            description: "Linux Kernel use-after-free vulnerability in netfilter subsystem",
            published: "2024-10-01T00:00:00",
            affectedSystems: 34,
            patchAvailable: true
          },
          {
            id: "CVE-2024-7432",
            cvssScore: 7.8,
            severity: "HIGH",
            description: "Microsoft Exchange Server privilege escalation vulnerability",
            published: "2024-09-28T00:00:00",
            affectedSystems: 28,
            patchAvailable: true
          },
          {
            id: "CVE-2024-7123",
            cvssScore: 7.5,
            severity: "HIGH",
            description: "Jenkins arbitrary file read vulnerability through crafted requests",
            published: "2024-09-25T00:00:00",
            affectedSystems: 8,
            patchAvailable: true
          },
          {
            id: "CVE-2024-6890",
            cvssScore: 7.2,
            severity: "HIGH",
            description: "Docker Engine privilege escalation through container escape",
            published: "2024-09-22T00:00:00",
            affectedSystems: 19,
            patchAvailable: true
          }
        ]);

        // Mock comprehensive stats
        setStats({
          vulnerabilities: {
            critical: 12,
            high: 28,
            medium: 45,
            low: 18,
            total: 103
          },
          patches: {
            deployed: 128,
            pending: 22,
            failed: 5
          },
          devices: {
            total: 150,
            online: 145,
            offline: 5,
            critical: 2
          },
          automation: {
            tasksCompleted: 687,
            tasksRunning: 8,
            successRate: 97.2
          }
        });
      } else {
        // Production API calls
        const session = await fetchAuthSession();
        const token = session.tokens.idToken.toString();

        const apiUrl = process.env.NEXT_PUBLIC_API_URL;

        const [patchRes, alertsRes, actionsRes] = await Promise.all([
          axios.get(`${apiUrl}/patches/status`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${apiUrl}/alerts/active`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${apiUrl}/actions/recent`, {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        setPatchStatus(patchRes.data);
        setAlerts(alertsRes.data);
        setAiActions(actionsRes.data);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
      // Fallback to mock data on error
      setPatchStatus({ totalDevices: 0, compliant: 0, pending: 0 });
      setAlerts([]);
      setAiActions([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div 
          data-testid="loading-spinner"
          className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
        ></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">AutoOps AI Dashboard</h1>

        {/* Patch Status */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Devices"
            value={patchStatus.totalDevices || 0}
            icon="🖥️"
            color="blue"
          />
          <StatCard
            title="Compliant"
            value={patchStatus.compliant || 0}
            icon="✅"
            color="green"
          />
          <StatCard
            title="Pending Patches"
            value={patchStatus.pending || 0}
            icon="⏳"
            color="yellow"
          />
          <StatCard
            title="Critical Alerts"
            value={alerts.filter(a => a.severity === 'critical').length}
            icon="🚨"
            color="red"
          />
        </div>

        {/* Active Alerts */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Active Alerts</h2>
          <div className="space-y-3">
            {alerts.slice(0, 5).map(alert => (
              <AlertItem key={alert.id} alert={alert} />
            ))}
          </div>
        </div>

        {/* Recent AI Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Recent AI Actions</h2>
          <div className="space-y-3">
            {aiActions.slice(0, 5).map(action => (
              <ActionItem key={action.id} action={action} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }) => {
  const colors = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-green-50 text-green-700',
    yellow: 'bg-yellow-50 text-yellow-700',
    red: 'bg-red-50 text-red-700'
  };

  return (
    <div className={`rounded-lg p-6 ${colors[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-75">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );
};

const AlertItem = ({ alert }) => (
  <div className="border-l-4 border-red-500 bg-red-50 p-4 rounded">
    <div className="flex items-center justify-between">
      <div>
        <h3 className="font-semibold text-gray-900">{alert.title}</h3>
        <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
      </div>
      <span className="px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
        {alert.severity}
      </span>
    </div>
  </div>
);

const ActionItem = ({ action }) => (
  <div className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
    <div className="flex items-center justify-between">
      <div>
        <h3 className="font-semibold text-gray-900">{action.type}</h3>
        <p className="text-sm text-gray-600 mt-1">{action.description}</p>
        <p className="text-xs text-gray-500 mt-1">{new Date(action.timestamp).toLocaleString()}</p>
      </div>
      <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
        action.status === 'completed' ? 'bg-green-100 text-green-800' :
        action.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
        'bg-gray-100 text-gray-800'
      }`}>
        {action.status}
      </span>
    </div>
  </div>
);

export default Dashboard;
