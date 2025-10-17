'use client'

import React, { useState, useEffect } from 'react'

const InventoryList = () => {
  const [inventory, setInventory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sortBy, setSortBy] = useState('riskScore')
  const [filterSeverity, setFilterSeverity] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadInventory()
    const interval = setInterval(loadInventory, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const loadInventory = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/inventory')
      if (!response.ok) throw new Error('Failed to fetch inventory')
      const data = await response.json()
      setInventory(data)
      setLoading(false)
    } catch (err) {
      console.error('Error loading inventory:', err)
      setError(err.message)
      setLoading(false)
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
                  <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
                    View Details
                  </button>
                  <button className="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors">
                    Scan Now
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

export default InventoryList
