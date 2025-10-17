'use client';

import React, { useState, useEffect } from 'react';

const EnhancedDashboard = () => {
  const [patchStatus, setPatchStatus] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [aiActions, setAiActions] = useState([]);
  const [topCVEs, setTopCVEs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(() => {
      setRefreshing(true);
      loadDashboardData();
      setTimeout(() => setRefreshing(false), 500);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
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
          severity: "critical",
          timestamp: new Date(Date.now() - 900000).toISOString()
        },
        {
          id: 2,
          title: "Failed Windows Update",
          description: "KB5034441 failed to install on multiple workstations",
          severity: "high",
          timestamp: new Date(Date.now() - 7200000).toISOString()
        },
        {
          id: 3,
          title: "Low Disk Space Warning",
          description: "C: drive on FILE-SRV-02 has less than 10% free space",
          severity: "medium",
          timestamp: new Date(Date.now() - 14400000).toISOString()
        }
      ]);
      
      setAiActions([
        {
          id: 1,
          type: "Patch Deployment",
          description: "Deployed security updates to 25 workstations",
          status: "completed",
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          agent: "AI-Patch-Agent"
        },
        {
          id: 2,
          type: "Alert Correlation",
          description: "Correlated 5 disk space alerts into single incident",
          status: "completed",
          timestamp: new Date(Date.now() - 10800000).toISOString(),
          agent: "AI-Alert-Agent"
        },
        {
          id: 3,
          type: "Risk Assessment",
          description: "Analyzing impact of pending CVE-2024-1234 patches",
          status: "pending",
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          agent: "AI-Risk-Agent"
        }
      ]);

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
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'from-red-600 to-red-700',
      HIGH: 'from-orange-500 to-orange-600',
      MEDIUM: 'from-yellow-500 to-yellow-600',
      LOW: 'from-green-500 to-green-600',
      critical: 'from-red-600 to-red-700',
      high: 'from-orange-500 to-orange-600',
      medium: 'from-yellow-500 to-yellow-600',
      low: 'from-green-500 to-green-600'
    };
    return colors[severity] || 'from-gray-500 to-gray-600';
  };

  const getSeverityBadge = (severity) => {
    const colors = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-300',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      LOW: 'bg-green-100 text-green-800 border-green-300',
      critical: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-green-100 text-green-800 border-green-300'
    };
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const then = new Date(timestamp);
    const seconds = Math.floor((now - then) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center">
          <div 
            data-testid="loading-spinner"
            className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600 mx-auto mb-4"
          ></div>
          <p className="text-gray-600 font-medium">Loading AutoOps AI Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-xl">🤖</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">AutoOps AI Dashboard</h1>
                  <p className="text-sm text-gray-500">Powered by NVD & SuperOps.ai</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg ${refreshing ? 'bg-blue-100' : 'bg-green-100'}`}>
                <div className={`w-2 h-2 rounded-full ${refreshing ? 'bg-blue-600 animate-pulse' : 'bg-green-600'}`}></div>
                <span className="text-xs font-medium text-gray-700">
                  {refreshing ? 'Refreshing...' : 'Live'}
                </span>
              </div>
              <button 
                onClick={loadDashboardData}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm transition-all duration-200 hover:shadow-md"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
          
          {/* Tabs */}
          <div className="flex space-x-1 border-b border-gray-200">
            {['overview', 'vulnerabilities', 'patches', 'alerts'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-3 font-medium capitalize transition-all duration-200 border-b-2 ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        {activeTab === 'overview' && stats && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Devices"
                value={patchStatus.totalDevices || 0}
                icon="💻"
                gradient="from-blue-500 to-cyan-500"
                subtitle={`${stats.devices.online} online`}
              />
              <StatCard
                title="Compliant"
                value={patchStatus.compliant || 0}
                icon="✅"
                gradient="from-green-500 to-emerald-500"
                subtitle={`${Math.round((patchStatus.compliant / patchStatus.totalDevices) * 100)}% compliance`}
              />
              <StatCard
                title="Pending Patches"
                value={patchStatus.pending || 0}
                icon="⏳"
                gradient="from-yellow-500 to-orange-500"
                subtitle={`${stats.patches.failed} failed`}
              />
              <StatCard
                title="Critical CVEs"
                value={topCVEs.filter(c => c.severity === 'CRITICAL').length}
                icon="🚨"
                gradient="from-red-500 to-pink-500"
                subtitle={`${topCVEs.length} total vulnerabilities`}
              />
            </div>

            {/* Quick Stats Bar */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">System Health</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <QuickStat label="Automation Success" value={`${stats.automation.successRate}%`} trend="up" />
                <QuickStat label="Tasks Completed" value={stats.automation.tasksCompleted} trend="up" />
                <QuickStat label="Active Tasks" value={stats.automation.tasksRunning} trend="stable" />
                <QuickStat label="Critical Devices" value={stats.devices.critical} trend="down" />
              </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Top CVEs */}
              <div className="lg:col-span-2">
                <CVEList cves={topCVEs.slice(0, 5)} getSeverityColor={getSeverityColor} getSeverityBadge={getSeverityBadge} formatTimeAgo={formatTimeAgo} />
              </div>

              {/* Alerts & Actions Sidebar */}
              <div className="space-y-6">
                <AlertsWidget alerts={alerts} getSeverityBadge={getSeverityBadge} formatTimeAgo={formatTimeAgo} />
                <AIActionsWidget actions={aiActions} formatTimeAgo={formatTimeAgo} />
              </div>
            </div>
          </>
        )}

        {/* Vulnerabilities Tab */}
        {activeTab === 'vulnerabilities' && (
          <div>
            <CVEList cves={topCVEs} getSeverityColor={getSeverityColor} getSeverityBadge={getSeverityBadge} formatTimeAgo={formatTimeAgo} full />
          </div>
        )}

        {/* Patches Tab */}
        {activeTab === 'patches' && (
          <PatchManagement patchStatus={patchStatus} stats={stats} />
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <AlertsManagement alerts={alerts} getSeverityBadge={getSeverityBadge} formatTimeAgo={formatTimeAgo} />
        )}
      </div>
    </div>
  );
};

// StatCard Component
const StatCard = ({ title, value, icon, gradient, subtitle }) => (
  <div className={`bg-gradient-to-br ${gradient} rounded-xl p-6 text-white shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl`}>
    <div className="flex items-center justify-between mb-3">
      <h3 className="text-sm font-medium opacity-90">{title}</h3>
      <span className="text-3xl">{icon}</span>
    </div>
    <p className="text-4xl font-bold mb-2">{value}</p>
    {subtitle && <p className="text-sm opacity-80">{subtitle}</p>}
  </div>
);

// QuickStat Component
const QuickStat = ({ label, value, trend }) => {
  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    stable: 'text-gray-600'
  };
  const trendIcons = {
    up: '↗',
    down: '↘',
    stable: '→'
  };
  
  return (
    <div className="text-center">
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-600 mt-1">{label}</p>
      <span className={`text-xs font-medium ${trendColors[trend]}`}>
        {trendIcons[trend]}
      </span>
    </div>
  );
};

// CVE List Component
const CVEList = ({ cves, getSeverityColor, getSeverityBadge, formatTimeAgo, full = false }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200">
    <div className="p-6 border-b border-gray-200">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">🔒 Top Critical Vulnerabilities (NVD)</h2>
        <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold">
          {cves.filter(c => c.severity === 'CRITICAL').length} Critical
        </span>
      </div>
      <p className="text-sm text-gray-600 mt-1">Latest CVEs from National Vulnerability Database</p>
    </div>
    <div className="divide-y divide-gray-100">
      {cves.map((cve, index) => (
        <div key={cve.id} className="p-5 hover:bg-gray-50 transition-colors duration-150">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <span className="font-mono font-bold text-blue-600">{cve.id}</span>
                <span className={`px-2 py-1 rounded-full text-xs font-semibold border ${getSeverityBadge(cve.severity)}`}>
                  {cve.severity}
                </span>
                {cve.patchAvailable && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                    Patch Available
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-700 mb-2">{cve.description}</p>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <span>📅 {formatTimeAgo(cve.published)}</span>
                <span>🖥️ {cve.affectedSystems} systems affected</span>
              </div>
            </div>
            <div className="ml-4 text-right">
              <div className={`w-16 h-16 bg-gradient-to-br ${getSeverityColor(cve.severity)} rounded-lg flex items-center justify-center shadow-lg`}>
                <span className="text-white font-bold text-xl">{cve.cvssScore}</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">CVSS Score</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Alerts Widget
const AlertsWidget = ({ alerts, getSeverityBadge, formatTimeAgo }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200">
    <div className="p-4 border-b border-gray-200">
      <h3 className="font-bold text-gray-900">⚠️ Active Alerts</h3>
    </div>
    <div className="divide-y divide-gray-100">
      {alerts.map(alert => (
        <div key={alert.id} className="p-4 hover:bg-gray-50 transition-colors duration-150">
          <div className="flex items-start justify-between mb-2">
            <h4 className="font-semibold text-gray-900 text-sm">{alert.title}</h4>
            <span className={`px-2 py-1 rounded-full text-xs font-semibold border ${getSeverityBadge(alert.severity)}`}>
              {alert.severity}
            </span>
          </div>
          <p className="text-xs text-gray-600 mb-2">{alert.description}</p>
          <p className="text-xs text-gray-500">{formatTimeAgo(alert.timestamp)}</p>
        </div>
      ))}
    </div>
  </div>
);

// AI Actions Widget
const AIActionsWidget = ({ actions, formatTimeAgo }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200">
    <div className="p-4 border-b border-gray-200">
      <h3 className="font-bold text-gray-900">🤖 AI Actions</h3>
    </div>
    <div className="divide-y divide-gray-100">
      {actions.map(action => (
        <div key={action.id} className="p-4 hover:bg-gray-50 transition-colors duration-150">
          <div className="flex items-start justify-between mb-2">
            <h4 className="font-semibold text-gray-900 text-sm">{action.type}</h4>
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
              action.status === 'completed' ? 'bg-green-100 text-green-700' :
              action.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {action.status}
            </span>
          </div>
          <p className="text-xs text-gray-600 mb-2">{action.description}</p>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{action.agent}</span>
            <span>{formatTimeAgo(action.timestamp)}</span>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Patch Management Tab
const PatchManagement = ({ patchStatus, stats }) => (
  <div className="space-y-6">
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Patch Management Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="text-center p-6 bg-green-50 rounded-lg border border-green-200">
          <p className="text-4xl font-bold text-green-600">{stats.patches.deployed}</p>
          <p className="text-sm text-gray-600 mt-2">Deployed Successfully</p>
        </div>
        <div className="text-center p-6 bg-yellow-50 rounded-lg border border-yellow-200">
          <p className="text-4xl font-bold text-yellow-600">{stats.patches.pending}</p>
          <p className="text-sm text-gray-600 mt-2">Pending Deployment</p>
        </div>
        <div className="text-center p-6 bg-red-50 rounded-lg border border-red-200">
          <p className="text-4xl font-bold text-red-600">{stats.patches.failed}</p>
          <p className="text-sm text-gray-600 mt-2">Failed Deployments</p>
        </div>
      </div>
    </div>
  </div>
);

// Alerts Management Tab
const AlertsManagement = ({ alerts, getSeverityBadge, formatTimeAgo }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200">
    <div className="p-6 border-b border-gray-200">
      <h2 className="text-2xl font-bold text-gray-900">Alert Management</h2>
    </div>
    <div className="divide-y divide-gray-100">
      {alerts.map(alert => (
        <div key={alert.id} className="p-6 hover:bg-gray-50 transition-colors duration-150">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">{alert.title}</h3>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getSeverityBadge(alert.severity)}`}>
              {alert.severity}
            </span>
          </div>
          <p className="text-gray-700 mb-3">{alert.description}</p>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <span>⏰ {formatTimeAgo(alert.timestamp)}</span>
            <button className="text-blue-600 hover:text-blue-700 font-medium">Investigate →</button>
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default EnhancedDashboard;
