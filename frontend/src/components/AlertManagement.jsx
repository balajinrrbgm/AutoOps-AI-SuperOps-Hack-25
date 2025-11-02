'use client'

import React, { useState, useEffect } from 'react'
import api from '../lib/api'

const AlertManagement = () => {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterSeverity, setFilterSeverity] = useState('all')
  const [processingAlert, setProcessingAlert] = useState({})
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [showDeviceModal, setShowDeviceModal] = useState(false)
  const [usingMockData, setUsingMockData] = useState(false)
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
      const result = await api.getAlerts()
      if (result.success) {
        setAlerts(result.data)
        setUsingMockData(result.fromCache || false)
        setError(null)
      } else {
        setError('Failed to load alerts')
      }
      setLoading(false)
    } catch (err) {
      console.error('Error loading alerts:', err)
      setError(err.message)
      setLoading(false)
    }
  }

  const handleAcknowledge = async (alertId) => {
    setProcessingAlert(prev => ({ ...prev, [alertId]: 'acknowledging' }))
    
    try {
      const result = await api.acknowledgeAlert(alertId)
      
      if (result.success) {
        // Update local state
        setAlerts(alerts.map(alert => 
          alert.id === alertId ? { ...alert, status: 'ACKNOWLEDGED', updatedAt: new Date().toISOString() } : alert
        ))
        alert(`Alert ${alertId} acknowledged successfully`)
      } else {
        throw new Error('Failed to acknowledge alert')
      }
    } catch (err) {
      console.error('Acknowledge error:', err)
      alert('Failed to acknowledge alert: ' + err.message)
    } finally {
      setProcessingAlert(prev => ({ ...prev, [alertId]: null }))
    }
  }

  const handleResolve = async (alertId) => {
    setProcessingAlert(prev => ({ ...prev, [alertId]: 'resolving' }))
    
    try {
      const result = await api.resolveAlert(alertId, 'Manually resolved')
      
      if (result.success) {
        // Update local state
        setAlerts(alerts.map(alert => 
          alert.id === alertId ? { ...alert, status: 'RESOLVED', updatedAt: new Date().toISOString() } : alert
        ))
        alert(`Alert ${alertId} resolved successfully`)
      } else {
        throw new Error('Failed to resolve alert')
      }
    } catch (err) {
      console.error('Resolve error:', err)
      alert('Failed to resolve alert: ' + err.message)
    } finally {
      setProcessingAlert(prev => ({ ...prev, [alertId]: null }))
    }
  }

  const handleViewDevice = async (deviceId, deviceName) => {
    try {
      const result = await api.getInventory()
      
      if (result.success) {
        const device = result.data.find(d => d.id === deviceId)
        
        if (device) {
          setSelectedDevice(device)
          setShowDeviceModal(true)
        } else {
          alert(`Device ${deviceName} not found in inventory`)
        }
      } else {
        throw new Error('Failed to fetch device')
      }
    } catch (err) {
      console.error('View device error:', err)
      alert('Failed to load device details: ' + err.message)
    }
  }

  const createAlert = async (e) => {
    e.preventDefault()
    try {
      const result = await api.createAlert(newAlert)
      
      if (result.success) {
        setAlerts([result.data, ...alerts])
        setShowCreateForm(false)
        setNewAlert({
          title: '',
          description: '',
          severity: 'MEDIUM',
          deviceId: '',
          deviceName: ''
        })
      } else {
        throw new Error('Failed to create alert')
      }
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
      {/* Demo Data Banner */}
      {usingMockData && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                ⚠️ Using demo data - API unavailable. Showing sample alerts for demonstration.
              </p>
            </div>
          </div>
        </div>
      )}

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
                  <button 
                    onClick={() => handleAcknowledge(alert.id)}
                    disabled={alert.status === 'ACKNOWLEDGED' || alert.status === 'RESOLVED' || processingAlert[alert.id] === 'acknowledging'}
                    className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                      alert.status === 'ACKNOWLEDGED' || alert.status === 'RESOLVED'
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : processingAlert[alert.id] === 'acknowledging'
                        ? 'bg-blue-400 text-white cursor-wait'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {processingAlert[alert.id] === 'acknowledging' ? 'Acknowledging...' : 
                     alert.status === 'ACKNOWLEDGED' ? 'Acknowledged' : 'Acknowledge'}
                  </button>
                  <button 
                    onClick={() => handleResolve(alert.id)}
                    disabled={alert.status === 'RESOLVED' || processingAlert[alert.id] === 'resolving'}
                    className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                      alert.status === 'RESOLVED'
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : processingAlert[alert.id] === 'resolving'
                        ? 'bg-green-400 text-white cursor-wait'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {processingAlert[alert.id] === 'resolving' ? 'Resolving...' : 
                     alert.status === 'RESOLVED' ? 'Resolved' : 'Resolve'}
                  </button>
                  <button 
                    onClick={() => handleViewDevice(alert.deviceId, alert.deviceName)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    View Device
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Device Details Modal */}
      {showDeviceModal && selectedDevice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">{selectedDevice.name}</h2>
                <p className="text-sm opacity-90">Device from Alert</p>
              </div>
              <button
                onClick={() => setShowDeviceModal(false)}
                className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm text-gray-600">Type</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.type}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm text-gray-600">IP Address</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.ipAddress}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm text-gray-600">Operating System</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.operatingSystem}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm text-gray-600">Risk Score</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.riskScore.toFixed(1)}/100</p>
                </div>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm font-semibold text-red-800 mb-2">Critical Vulnerabilities</p>
                <p className="text-3xl font-bold text-red-600">{selectedDevice.vulnerabilityStats?.critical || 0}</p>
              </div>

              <button
                onClick={() => setShowDeviceModal(false)}
                className="w-full py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AlertManagement
