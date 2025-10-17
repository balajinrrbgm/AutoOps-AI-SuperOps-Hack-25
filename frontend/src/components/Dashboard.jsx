import React, { useState, useEffect } from 'react';
import { fetchAuthSession } from 'aws-amplify/auth';
import axios from 'axios';

const Dashboard = () => {
  const [patchStatus, setPatchStatus] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [aiActions, setAiActions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
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
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
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
