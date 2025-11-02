'use client'

import React, { useState, useEffect } from 'react'
import api from '../lib/api'

const InventoryList = () => {
  const [inventory, setInventory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [usingMockData, setUsingMockData] = useState(false)
  const [sortBy, setSortBy] = useState('riskScore')
  const [filterSeverity, setFilterSeverity] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [scanning, setScanning] = useState({})

  useEffect(() => {
    loadInventory()
    const interval = setInterval(loadInventory, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const loadInventory = async () => {
    try {
      setError(null)
      const result = await api.getInventory()
      
      if (result.success) {
        setInventory(result.data)
        setUsingMockData(result.fromCache || false)
      } else {
        setError(result.error || 'Failed to fetch inventory')
      }
    } catch (err) {
      console.error('Error loading inventory:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetails = (device) => {
    setSelectedDevice(device)
    setShowDetailsModal(true)
  }

  const handleScanNow = async (deviceId) => {
    setScanning(prev => ({ ...prev, [deviceId]: true }))
    
    try {
      const result = await api.scanDevice(deviceId)
      
      if (result.success) {
        alert(`Scan initiated successfully for device ${deviceId}. ${result.data.message || ''}`)
        // Reload inventory after scan
        setTimeout(() => loadInventory(), 2000)
      } else {
        alert('Failed to initiate scan: ' + result.error)
      }
    } catch (err) {
      console.error('Scan error:', err)
      alert('Failed to initiate scan: ' + err.message)
    } finally {
      setScanning(prev => ({ ...prev, [deviceId]: false }))
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'text-red-600 bg-red-50',
      HIGH: 'text-orange-600 bg-orange-50',
      MEDIUM: 'text-yellow-600 bg-yellow-50',
      LOW: 'text-blue-600 bg-blue-50'
    }
    return colors[severity] || 'text-gray-600 bg-gray-50'
  }

  const getRiskColor = (score) => {
    if (score >= 80) return 'text-red-600 font-bold'
    if (score >= 60) return 'text-orange-600 font-semibold'
    if (score >= 40) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getRiskBadge = (score) => {
    if (score >= 80) return 'bg-red-100 text-red-800 border-red-200'
    if (score >= 60) return 'bg-orange-100 text-orange-800 border-orange-200'
    if (score >= 40) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-green-100 text-green-800 border-green-200'
  }

  const filteredAndSortedInventory = inventory
    .filter(device => {
      // Filter by severity
      if (filterSeverity !== 'all') {
        const hasSeverity = device.topVulnerabilities?.some(v => v.severity === filterSeverity)
        if (!hasSeverity) return false
      }
      
      // Filter by search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        return (
          device.name?.toLowerCase().includes(query) ||
          device.operatingSystem?.toLowerCase().includes(query) ||
          device.ipAddress?.toLowerCase().includes(query) ||
          device.client?.toLowerCase().includes(query)
        )
      }
      
      return true
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'riskScore':
          return (b.riskScore || 0) - (a.riskScore || 0)
        case 'vulnerabilities':
          return (b.vulnerabilityStats?.total || 0) - (a.vulnerabilityStats?.total || 0)
        case 'name':
          return (a.name || '').localeCompare(b.name || '')
        default:
          return 0
      }
    })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading inventory...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error}</p>
        <button 
          onClick={loadInventory}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Mock Data Banner */}
      {usingMockData && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <span className="text-yellow-600">⚠️</span>
            <p className="text-yellow-800 font-medium">
              Using demo data - API unavailable. Showing sample devices for demonstration.
            </p>
          </div>
        </div>
      )}
      
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Device Inventory</h2>
        
        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Devices
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Name, IP, OS, Client..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="riskScore">Risk Score (High to Low)</option>
              <option value="vulnerabilities">Vulnerabilities (Most First)</option>
              <option value="name">Device Name (A-Z)</option>
            </select>
          </div>

          {/* Filter by Severity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Severity
            </label>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Devices</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH">High Only</option>
              <option value="MEDIUM">Medium Only</option>
            </select>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-sm text-gray-600">Total Devices</p>
            <p className="text-2xl font-bold text-gray-900">{inventory.length}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-3">
            <p className="text-sm text-red-600">High Risk</p>
            <p className="text-2xl font-bold text-red-600">
              {inventory.filter(d => d.riskScore >= 80).length}
            </p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-3">
            <p className="text-sm text-yellow-600">Medium Risk</p>
            <p className="text-2xl font-bold text-yellow-600">
              {inventory.filter(d => d.riskScore >= 40 && d.riskScore < 80).length}
            </p>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <p className="text-sm text-green-600">Low Risk</p>
            <p className="text-2xl font-bold text-green-600">
              {inventory.filter(d => d.riskScore < 40).length}
            </p>
          </div>
        </div>
      </div>

      {/* Device List */}
      <div className="space-y-4">
        {filteredAndSortedInventory.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200">
            <p className="text-gray-600">No devices found matching your criteria.</p>
          </div>
        ) : (
          filteredAndSortedInventory.map((device) => (
            <div 
              key={device.id} 
              className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">{device.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getRiskBadge(device.riskScore)}`}>
                        Risk: {device.riskScore.toFixed(1)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                      <div>
                        <p className="text-gray-500">Type</p>
                        <p className="font-medium text-gray-900">{device.type}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">IP Address</p>
                        <p className="font-medium text-gray-900">{device.ipAddress}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Client</p>
                        <p className="font-medium text-gray-900">{device.client}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Site</p>
                        <p className="font-medium text-gray-900">{device.site}</p>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-3 mb-4">
                      <p className="text-sm text-gray-600 mb-1">Operating System</p>
                      <p className="font-medium text-gray-900">{device.operatingSystem}</p>
                    </div>

                    {/* Vulnerability Stats */}
                    <div className="grid grid-cols-4 gap-3 mb-4">
                      <div className="bg-white border border-gray-200 rounded-lg p-3 text-center">
                        <p className="text-2xl font-bold text-gray-900">
                          {device.vulnerabilityStats?.total || 0}
                        </p>
                        <p className="text-xs text-gray-600">Total</p>
                      </div>
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
                        <p className="text-2xl font-bold text-red-600">
                          {device.vulnerabilityStats?.critical || 0}
                        </p>
                        <p className="text-xs text-red-600">Critical</p>
                      </div>
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-center">
                        <p className="text-2xl font-bold text-orange-600">
                          {device.vulnerabilityStats?.high || 0}
                        </p>
                        <p className="text-xs text-orange-600">High</p>
                      </div>
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
                        <p className="text-2xl font-bold text-yellow-600">
                          {device.vulnerabilityStats?.medium || 0}
                        </p>
                        <p className="text-xs text-yellow-600">Medium</p>
                      </div>
                    </div>

                    {/* Top Vulnerabilities */}
                    {device.topVulnerabilities && device.topVulnerabilities.length > 0 && (
                      <div>
                        <p className="text-sm font-semibold text-gray-700 mb-2">
                          Top Vulnerabilities
                        </p>
                        <div className="space-y-2">
                          {device.topVulnerabilities.slice(0, 3).map((vuln, idx) => (
                            <div 
                              key={idx}
                              className="flex items-center justify-between bg-gray-50 rounded-lg p-2 border border-gray-200"
                            >
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-sm font-medium text-gray-900">
                                  {vuln.cveId}
                                </span>
                                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getSeverityColor(vuln.severity)}`}>
                                  {vuln.severity}
                                </span>
                              </div>
                              <span className="text-sm font-bold text-gray-900">
                                CVSS: {vuln.cvssScore}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="bg-gray-50 px-6 py-3 border-t border-gray-200 flex items-center justify-between rounded-b-lg">
                <p className="text-sm text-gray-600">
                  Last Seen: {new Date(device.lastSeenAt).toLocaleString()}
                </p>
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleViewDetails(device)}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View Details
                  </button>
                  <button 
                    onClick={() => handleScanNow(device.id)}
                    disabled={scanning[device.id]}
                    className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                      scanning[device.id]
                        ? 'bg-gray-400 text-white cursor-not-allowed'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {scanning[device.id] ? 'Scanning...' : 'Scan Now'}
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Device Details Modal */}
      {showDetailsModal && selectedDevice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">{selectedDevice.name}</h2>
                <p className="text-sm opacity-90">Device ID: {selectedDevice.id}</p>
              </div>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              {/* Risk Score */}
              <div className={`rounded-lg p-4 border-2 ${getRiskBadge(selectedDevice.riskScore)}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium opacity-80">Overall Risk Score</p>
                    <p className="text-3xl font-bold">{selectedDevice.riskScore.toFixed(1)}/100</p>
                  </div>
                  <div className="text-5xl">
                    {selectedDevice.riskScore >= 80 ? '🔴' : selectedDevice.riskScore >= 60 ? '🟠' : selectedDevice.riskScore >= 40 ? '🟡' : '🟢'}
                  </div>
                </div>
              </div>

              {/* Device Information */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Type</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.type}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">IP Address</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.ipAddress}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">MAC Address</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.macAddress}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Last Seen</p>
                  <p className="font-semibold text-gray-900">{new Date(selectedDevice.lastSeenAt).toLocaleString()}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Client</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.client}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Site</p>
                  <p className="font-semibold text-gray-900">{selectedDevice.site}</p>
                </div>
              </div>

              {/* Operating System */}
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <p className="text-sm text-blue-600 font-medium mb-2">Operating System</p>
                <p className="text-lg font-semibold text-gray-900">{selectedDevice.operatingSystem}</p>
              </div>

              {/* Vulnerability Statistics */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">Vulnerability Statistics</h3>
                <div className="grid grid-cols-4 gap-3">
                  <div className="bg-white border-2 border-gray-200 rounded-lg p-4 text-center">
                    <p className="text-3xl font-bold text-gray-900">{selectedDevice.vulnerabilityStats?.total || 0}</p>
                    <p className="text-sm text-gray-600 mt-1">Total</p>
                  </div>
                  <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 text-center">
                    <p className="text-3xl font-bold text-red-600">{selectedDevice.vulnerabilityStats?.critical || 0}</p>
                    <p className="text-sm text-red-600 mt-1">Critical</p>
                  </div>
                  <div className="bg-orange-50 border-2 border-orange-200 rounded-lg p-4 text-center">
                    <p className="text-3xl font-bold text-orange-600">{selectedDevice.vulnerabilityStats?.high || 0}</p>
                    <p className="text-sm text-orange-600 mt-1">High</p>
                  </div>
                  <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4 text-center">
                    <p className="text-3xl font-bold text-yellow-600">{selectedDevice.vulnerabilityStats?.medium || 0}</p>
                    <p className="text-sm text-yellow-600 mt-1">Medium</p>
                  </div>
                </div>
              </div>

              {/* All Vulnerabilities */}
              {selectedDevice.topVulnerabilities && selectedDevice.topVulnerabilities.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-3">All Vulnerabilities</h3>
                  <div className="space-y-2">
                    {selectedDevice.topVulnerabilities.map((vuln, idx) => (
                      <div 
                        key={idx}
                        className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <span className="font-mono text-lg font-bold text-gray-900">{vuln.cveId}</span>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${getSeverityColor(vuln.severity)}`}>
                              {vuln.severity}
                            </span>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-gray-600">CVSS Score</p>
                            <p className="text-2xl font-bold text-gray-900">{vuln.cvssScore}</p>
                          </div>
                        </div>
                        {vuln.description && (
                          <p className="text-sm text-gray-700 mt-2">{vuln.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleScanNow(selectedDevice.id)}
                  disabled={scanning[selectedDevice.id]}
                  className={`flex-1 py-3 rounded-lg font-semibold transition-colors ${
                    scanning[selectedDevice.id]
                      ? 'bg-gray-400 text-white cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {scanning[selectedDevice.id] ? 'Scanning...' : '🔍 Rescan Device'}
                </button>
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="flex-1 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InventoryList
