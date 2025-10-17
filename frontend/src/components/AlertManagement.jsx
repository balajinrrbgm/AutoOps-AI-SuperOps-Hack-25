'use client'

import React, { useState, useEffect } from 'react'

const AlertManagement = () => {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterSeverity, setFilterSeverity] = useState('all')
  const [newAlert, setNewAlert] = useState({
    title: '',
    description: '',
    severity: 'MEDIUM',
    deviceId: '',
    deviceName: ''
  })

  useEffect(() => {
    loadAlerts()
    const interval = setInterval(loadAlerts, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const loadAlerts = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/alerts')
      if (!response.ok) throw new Error('Failed to fetch alerts')
      const data = await response.json()
      setAlerts(data)
      setLoading(false)
    } catch (err) {
      console.error('Error loading alerts:', err)
      setError(err.message)
      setLoading(false)
    }
  }

  const createAlert = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:3001/api/alerts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAlert)
      })
      
      if (!response.ok) throw new Error('Failed to create alert')
      
      const createdAlert = await response.json()
      setAlerts([createdAlert, ...alerts])
      setShowCreateForm(false)
      setNewAlert({
        title: '',
        description: '',
        severity: 'MEDIUM',
        deviceId: '',
        deviceName: ''
      })
    } catch (err) {
      console.error('Error creating alert:', err)
      alert('Failed to create alert: ' + err.message)
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-200',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      LOW: 'bg-blue-100 text-blue-800 border-blue-200'
    }
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const getStatusColor = (status) => {
    const colors = {
      ACTIVE: 'bg-green-100 text-green-800 border-green-200',
      ACKNOWLEDGED: 'bg-blue-100 text-blue-800 border-blue-200',
      RESOLVED: 'bg-gray-100 text-gray-800 border-gray-200'
    }
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const filteredAlerts = alerts.filter(alert => {
    if (filterStatus !== 'all' && alert.status !== filterStatus) return false
    if (filterSeverity !== 'all' && alert.severity !== filterSeverity) return false
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading alerts...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error}</p>
        <button 
          onClick={loadAlerts}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Alert Management</h2>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            {showCreateForm ? 'Cancel' : '+ Create Alert'}
          </button>
        </div>

        {/* Create Alert Form */}
        {showCreateForm && (
          <form onSubmit={createAlert} className="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Create New Alert</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Alert Title *
                </label>
                <input
                  type="text"
                  required
                  value={newAlert.title}
                  onChange={(e) => setNewAlert({...newAlert, title: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Critical Security Issue"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Severity *
                </label>
                <select
                  required
                  value={newAlert.severity}
                  onChange={(e) => setNewAlert({...newAlert, severity: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Device ID
                </label>
                <input
                  type="text"
                  value={newAlert.deviceId}
                  onChange={(e) => setNewAlert({...newAlert, deviceId: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="dev-001"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Device Name
                </label>
                <input
                  type="text"
                  value={newAlert.deviceName}
                  onChange={(e) => setNewAlert({...newAlert, deviceName: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="WEB-SERVER-01"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  required
                  rows="3"
                  value={newAlert.description}
                  onChange={(e) => setNewAlert({...newAlert, description: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Detailed description of the alert..."
                />
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
              >
                Create Alert
              </button>
            </div>
          </form>
        )}

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Statuses</option>
              <option value="ACTIVE">Active</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Severity
            </label>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-sm text-gray-600">Total Alerts</p>
            <p className="text-2xl font-bold text-gray-900">{alerts.length}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-3">
            <p className="text-sm text-red-600">Critical</p>
            <p className="text-2xl font-bold text-red-600">
              {alerts.filter(a => a.severity === 'CRITICAL').length}
            </p>
          </div>
          <div className="bg-orange-50 rounded-lg p-3">
            <p className="text-sm text-orange-600">High</p>
            <p className="text-2xl font-bold text-orange-600">
              {alerts.filter(a => a.severity === 'HIGH').length}
            </p>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <p className="text-sm text-green-600">Active</p>
            <p className="text-2xl font-bold text-green-600">
              {alerts.filter(a => a.status === 'ACTIVE').length}
            </p>
          </div>
        </div>
      </div>

      {/* Alert List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200">
            <p className="text-gray-600">No alerts found matching your criteria.</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div 
              key={alert.id} 
              className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-bold text-gray-900">{alert.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(alert.status)}`}>
                        {alert.status}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-4">{alert.description}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                  <div>
                    <p className="text-gray-500">Device</p>
                    <p className="font-medium text-gray-900">{alert.deviceName || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Source</p>
                    <p className="font-medium text-gray-900">{alert.source}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Created</p>
                    <p className="font-medium text-gray-900">
                      {new Date(alert.createdAt).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Updated</p>
                    <p className="font-medium text-gray-900">
                      {new Date(alert.updatedAt).toLocaleString()}
                    </p>
                  </div>
                </div>

                {/* Vulnerability Context */}
                {alert.relatedVulnerabilities > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
                    <p className="text-sm font-semibold text-gray-700 mb-2">
                      Vulnerability Context
                    </p>
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <p className="text-2xl font-bold text-gray-900">{alert.relatedVulnerabilities}</p>
                        <p className="text-xs text-gray-600">Related CVEs</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-red-600">{alert.criticalVulnerabilities}</p>
                        <p className="text-xs text-red-600">Critical</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-orange-600">{alert.highVulnerabilities}</p>
                        <p className="text-xs text-orange-600">High</p>
                      </div>
                    </div>

                    {alert.vulnerabilityDetails && alert.vulnerabilityDetails.length > 0 && (
                      <div className="mt-4 space-y-2">
                        {alert.vulnerabilityDetails.map((vuln, idx) => (
                          <div 
                            key={idx}
                            className="bg-white rounded p-2 border border-gray-200"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-sm font-medium">{vuln.cveId}</span>
                                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getSeverityColor(vuln.severity)}`}>
                                  {vuln.severity}
                                </span>
                              </div>
                              <span className="text-sm font-bold">CVSS: {vuln.cvssScore}</span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">{vuln.description}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="bg-gray-50 px-6 py-3 border-t border-gray-200 flex justify-between items-center rounded-b-lg">
                <p className="text-sm text-gray-600">ID: {alert.id}</p>
                <div className="flex gap-2">
                  <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
                    Acknowledge
                  </button>
                  <button className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors">
                    Resolve
                  </button>
                  <button className="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors">
                    View Device
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AlertManagement
