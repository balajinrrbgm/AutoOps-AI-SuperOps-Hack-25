'use client'

import React, { useState, useEffect } from 'react'
import { Shield, Server, Clock, CheckCircle, AlertTriangle, Calendar, Download, RefreshCw, Eye, Play, Search, Filter, TrendingUp, Activity } from 'lucide-react'
import api from '../lib/api'

const PatchManagementSystem = () => {
  const [patches, setPatches] = useState([])
  const [devices, setDevices] = useState([])
  const [patchAnalysis, setPatchAnalysis] = useState(null)
  const [patchDetails, setPatchDetails] = useState({}) // Store detailed patch info from SuperOps
  const [loading, setLoading] = useState(true)
  const [activeView, setActiveView] = useState('overview') // overview, patches, devices, schedule, compliance
  const [selectedPatch, setSelectedPatch] = useState(null)
  const [showDeployModal, setShowDeployModal] = useState(false)
  const [showPatchDetailsModal, setShowPatchDetailsModal] = useState(false)
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [deploymentSchedule, setDeploymentSchedule] = useState([])
  const [autoApproveEnabled, setAutoApproveEnabled] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [severityFilter, setSeverityFilter] = useState('ALL')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [usingMockData, setUsingMockData] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadPatchData()
    loadSchedules()
    const interval = setInterval(() => {
      loadPatchData()
      loadSchedules()
    }, 60000) // Refresh every minute
    return () => clearInterval(interval)
  }, [])

  const loadPatchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load patches from API
      const patchesResult = await api.getPatches()
      if (patchesResult.success) {
        const patchData = Array.isArray(patchesResult.data) ? patchesResult.data : []
        setPatches(patchData)
        setUsingMockData(patchesResult.fromCache || false)
      } else {
        throw new Error('Failed to load patches')
      }

      // Load devices with patch status
      const devicesResult = await api.getInventory()
      if (devicesResult.success) {
        const deviceData = Array.isArray(devicesResult.data) ? devicesResult.data : []
        setDevices(deviceData)
      }

      // For mock data, generate simple analysis
      if (patchesResult.fromCache || !patchesResult.success) {
        const patchData = Array.isArray(patchesResult.data) ? patchesResult.data : []
        const deviceData = Array.isArray(devicesResult.data) ? devicesResult.data : []
        const totalDevices = deviceData.length
        const patchedDevices = deviceData.filter(d => d.patchStatus === 'compliant').length
        
        setPatchAnalysis({
          totalPatches: patchData.length,
          criticalPatches: patchData.filter(p => p.severity === 'CRITICAL').length,
          pendingDeployments: patchData.filter(p => p.status === 'AVAILABLE').length,
          coverageRate: totalDevices > 0 ? (patchedDevices / totalDevices) * 100 : 0,
          fullyPatched: patchedDevices,
          partiallyPatched: totalDevices > 0 ? Math.max(0, totalDevices - patchedDevices - 1) : 0,
          unpatched: totalDevices > 0 ? Math.max(0, totalDevices - patchedDevices) : 0,
          criticalExposure: deviceData.filter(d => 
            d.vulnerabilityStats?.critical > 0
          ).map(d => ({
            deviceName: d.name,
            cveId: d.topVulnerabilities?.[0]?.cveId || 'N/A',
            cvssScore: d.topVulnerabilities?.[0]?.cvssScore || 0
          }))
        })
        setPatchDetails({})
      }

      setLoading(false)
    } catch (err) {
      console.error('Error loading patch data:', err)
      setError(err.message || 'Failed to load patch data')
      setLoading(false)
      // Set empty arrays to prevent crashes
      if (!patches || patches.length === 0) {
        setPatches([])
      }
      if (!devices || devices.length === 0) {
        setDevices([])
      }
    }
  }

  const loadSchedules = async () => {
    try {
      const result = await api.getSchedules('SCHEDULED')
      if (result.success) {
        const schedules = result.data.schedules || []
        
        // If no schedules exist, seed with sample data for demonstration
        if (schedules.length === 0 && patches.length > 0) {
          const sampleSchedules = [
            {
              scheduleId: `sample-${Date.now()}-1`,
              patchId: patches[0]?.id || 'KB5034441',
              patchTitle: patches[0]?.title || 'Windows Security Update',
              severity: patches[0]?.severity || 'CRITICAL',
              deviceCount: patches[0]?.affectedDevices?.length || 2,
              scheduledFor: new Date(Date.now() + 7200000).toISOString(), // 2 hours from now
              status: 'SCHEDULED',
              requestedBy: 'admin'
            },
            {
              scheduleId: `sample-${Date.now()}-2`,
              patchId: patches[1]?.id || 'KB5034439',
              patchTitle: patches[1]?.title || 'Windows Server Update',
              severity: patches[1]?.severity || 'HIGH',
              deviceCount: patches[1]?.affectedDevices?.length || 3,
              scheduledFor: new Date(Date.now() + 86400000).toISOString(), // 24 hours from now
              status: 'SCHEDULED',
              requestedBy: 'admin'
            },
            {
              scheduleId: `sample-${Date.now()}-3`,
              patchId: patches[2]?.id || 'UBUNTU-2024-01',
              patchTitle: patches[2]?.title || 'Ubuntu Security Update',
              severity: patches[2]?.severity || 'MEDIUM',
              deviceCount: patches[2]?.affectedDevices?.length || 1,
              scheduledFor: new Date(Date.now() + 172800000).toISOString(), // 48 hours from now
              status: 'SCHEDULED',
              requestedBy: 'system'
            }
          ]
          setDeploymentSchedule(sampleSchedules)
        } else {
          setDeploymentSchedule(schedules)
        }
      }
    } catch (err) {
      console.error('Error loading schedules:', err)
      // Set empty array on error
      setDeploymentSchedule([])
    }
  }

  const requestAIAnalysis = async (patch) => {
    try {
      const result = await api.analyzePatch({
        patch: patch,
        devices: devices.filter(d => patch.affectedDevices?.includes(d.id)),
        vulnerabilities: patch.relatedCVEs
      })
      
      if (result.success) {
        setAiAnalysis(result.data)
        setSelectedPatch(patch)
        setShowDeployModal(true)
      } else {
        throw new Error('Analysis failed')
      }
    } catch (err) {
      console.error('AI analysis error:', err)
      alert('Failed to get AI analysis: ' + err.message)
    }
  }

  const deployPatch = async (patch, schedule = null) => {
    try {
      if (schedule) {
        // Create schedule using API
        const result = await api.createSchedule({
          patchId: patch.id,
          patchTitle: patch.title,
          deviceIds: patch.affectedDevices || [],
          scheduledFor: schedule.scheduledFor || Date.now() + 86400000,
          severity: patch.severity,
          requestedBy: 'admin',
          enableAI: true  // Enable AI auto-approval for low-risk patches
        })
        
        if (result.success) {
          // Update deployment schedule with the response data
          if (result.data.schedules) {
            setDeploymentSchedule(result.data.schedules)
          }
          
          alert(`✅ Patch scheduled successfully for ${new Date(schedule.scheduledFor || Date.now() + 86400000).toLocaleString()}!\n\n` +
                `Schedule Count: ${result.data.scheduleCount || 0} active schedules\n` +
                (result.data.aiApproved ? `🤖 AI Auto-Approved (Risk: ${result.data.aiRiskLevel}/10)` : 
                 result.data.aiRecommendation ? `⚠️ AI Recommendation: ${result.data.aiRecommendation}` : ''))
          
          setShowDeployModal(false)
          setAiAnalysis(null)
          
          // Refresh all data to update counts
          loadPatchData()
          loadSchedules()
        } else {
          throw new Error(result.error || 'Failed to create schedule')
        }
      } else {
        // Immediate deployment
        const result = await api.deployPatch({
          patchId: patch.id,
          deviceIds: patch.affectedDevices,
          aiApproved: aiAnalysis?.recommendation === 'APPROVE'
        })
        
        if (result.success) {
          alert('✅ Patch deployment initiated successfully!')
          setShowDeployModal(false)
          setAiAnalysis(null)
          loadPatchData()
          loadSchedules()
        } else {
          throw new Error('Deployment failed')
        }
      }
    } catch (err) {
      console.error('Deploy error:', err)
      alert('❌ Failed to deploy patch: ' + err.message)
    }
  }

  const viewPatchDetails = (patch) => {
    setSelectedPatch(patch)
    setShowPatchDetailsModal(true)
  }

  const getFilteredPatches = () => {
    if (!patches || !Array.isArray(patches)) return []
    
    return patches.filter(patch => {
      const matchesSearch = patch.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           patch.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           patch.cveId?.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesSeverity = severityFilter === 'ALL' || patch.severity === severityFilter
      const matchesStatus = statusFilter === 'ALL' || patch.status === statusFilter
      return matchesSearch && matchesSeverity && matchesStatus
    })
  }

  const getSeverityBadge = (severity) => {
    const colors = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-300',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      LOW: 'bg-blue-100 text-blue-800 border-blue-300'
    }
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  const getStatusBadge = (status) => {
    const colors = {
      AVAILABLE: 'bg-green-100 text-green-800 border-green-300',
      PENDING: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      DEPLOYING: 'bg-blue-100 text-blue-800 border-blue-300',
      DEPLOYED: 'bg-gray-100 text-gray-800 border-gray-300',
      FAILED: 'bg-red-100 text-red-800 border-red-300',
      SCHEDULED: 'bg-purple-100 text-purple-800 border-purple-300'
    }
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading patch management system...</p>
        </div>
      </div>
    )
  }

  // Error state display
  if (error && !patches.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center max-w-md">
          <div className="text-red-600 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-xl font-bold text-gray-900 mb-2">Error Loading Data</p>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => {
              setError(null)
              loadPatchData()
              loadSchedules()
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
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
                ⚠️ Using demo data - API unavailable. Showing sample patches for demonstration.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">🛡️ World-Class Patch Management</h2>
            <p className="text-sm text-gray-600 mt-1">AI-Powered Intelligent Patch Deployment System</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-green-50 px-4 py-2 rounded-lg border border-green-200">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm font-medium text-green-800">AI Active</span>
            </div>
            <button
              onClick={loadPatchData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* View Tabs */}
        <div className="flex space-x-2 border-b border-gray-200">
          {['overview', 'patches', 'devices', 'schedule', 'compliance'].map((view) => (
            <button
              key={view}
              onClick={() => setActiveView(view)}
              className={`px-6 py-3 font-medium capitalize transition-all duration-200 border-b-2 ${
                activeView === view
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {view}
            </button>
          ))}
        </div>
      </div>

      {/* Overview View */}
      {activeView === 'overview' && (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium opacity-90">Total Patches</h3>
                <span className="text-3xl">📦</span>
              </div>
              <p className="text-4xl font-bold">{patches?.length || 0}</p>
              <p className="text-sm opacity-80 mt-2">{patches?.filter(p => p.status === 'AVAILABLE').length || 0} available</p>
            </div>

            <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium opacity-90">Critical Patches</h3>
                <span className="text-3xl">🔥</span>
              </div>
              <p className="text-4xl font-bold">{patches?.filter(p => p.severity === 'CRITICAL').length || 0}</p>
              <p className="text-sm opacity-80 mt-2">Requires immediate action</p>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium opacity-90">Deployed</h3>
                <span className="text-3xl">✅</span>
              </div>
              <p className="text-4xl font-bold">{patches?.filter(p => p.status === 'DEPLOYED').length || 0}</p>
              <p className="text-sm opacity-80 mt-2">Successfully applied</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium opacity-90">Scheduled</h3>
                <span className="text-3xl">📅</span>
              </div>
              <p className="text-4xl font-bold">{deploymentSchedule?.length || 0}</p>
              <p className="text-sm opacity-80 mt-2">Upcoming deployments</p>
            </div>
          </div>

          {/* Patch Analysis Summary */}
          {patchAnalysis && patchAnalysis.coverageRate !== undefined && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">📊 Patch Coverage Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="relative inline-flex items-center justify-center w-32 h-32">
                    <svg className="w-32 h-32 transform -rotate-90">
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-gray-200"
                      />
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 56}`}
                        strokeDashoffset={`${2 * Math.PI * 56 * (1 - (patchAnalysis.coverageRate || 0) / 100)}`}
                        className="text-green-500"
                      />
                    </svg>
                    <span className="absolute text-2xl font-bold">{(patchAnalysis.coverageRate || 0).toFixed(1)}%</span>
                  </div>
                  <p className="text-sm font-medium text-gray-700 mt-2">Coverage Rate</p>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Fully Patched</span>
                    <span className="font-bold text-green-600">{patchAnalysis.fullyPatched || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Partially Patched</span>
                    <span className="font-bold text-yellow-600">{patchAnalysis.partiallyPatched || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Unpatched</span>
                    <span className="font-bold text-red-600">{patchAnalysis.unpatched || 0}</span>
                  </div>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-red-800 mb-2">Critical Exposure</p>
                  <p className="text-3xl font-bold text-red-600">{patchAnalysis.criticalExposure?.length || 0}</p>
                  <p className="text-xs text-red-600 mt-1">Devices with critical vulnerabilities</p>
                </div>
              </div>
            </div>
          )}

          {/* AI Recommendations */}
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg border border-indigo-200 p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">🤖</span>
              <div>
                <h3 className="text-lg font-bold text-gray-900">AI-Powered Recommendations</h3>
                <p className="text-sm text-gray-600">Intelligent deployment suggestions</p>
              </div>
            </div>
            <div className="space-y-3">
              {patches?.filter(p => p.severity === 'CRITICAL' && p.status === 'AVAILABLE').slice(0, 3).map((patch) => (
                <div key={patch.id} className="bg-white rounded-lg p-4 border border-indigo-200">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900">{patch.title}</p>
                      <p className="text-sm text-gray-600 mt-1">{patch.affectedDevices?.length || 0} devices affected</p>
                    </div>
                    <button
                      onClick={() => requestAIAnalysis(patch)}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                    >
                      Analyze & Deploy
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Patches View */}
      {activeView === 'patches' && (
        <div className="space-y-4">
          {/* Search and Filter Bar */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    placeholder="Search patches by title, CVE, or description..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Severity Filter */}
              <div>
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="ALL">All Severities</option>
                  <option value="CRITICAL">Critical</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                </select>
              </div>

              {/* Status Filter */}
              <div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="ALL">All Status</option>
                  <option value="AVAILABLE">Available</option>
                  <option value="PENDING">Pending</option>
                  <option value="DEPLOYING">Deploying</option>
                  <option value="DEPLOYED">Deployed</option>
                  <option value="FAILED">Failed</option>
                  <option value="SCHEDULED">Scheduled</option>
                </select>
              </div>
            </div>

            {/* Results Count */}
            <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
              <span>Showing {getFilteredPatches().length} of {patches.length} patches</span>
              <button
                onClick={loadPatchData}
                className="flex items-center gap-2 px-3 py-1 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>
          </div>

          {/* Patches List */}
          {getFilteredPatches().length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200">
              <Shield className="mx-auto mb-4 text-gray-400" size={48} />
              <p className="text-gray-600 font-medium mb-2">No patches found</p>
              <p className="text-sm text-gray-500">Try adjusting your search or filters</p>
            </div>
          ) : (
            getFilteredPatches().map((patch) => (
              <div key={patch.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-all">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Shield className="text-blue-600" size={20} />
                        <h3 className="text-lg font-bold text-gray-900">{patch.title}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getSeverityBadge(patch.severity)}`}>
                          {patch.severity}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStatusBadge(patch.status)}`}>
                          {patch.status}
                        </span>
                      </div>
                      <p className="text-gray-700 mb-3">{patch.description}</p>
                      
                      {/* Metadata */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <Calendar className="text-gray-400" size={16} />
                          <div>
                            <p className="text-gray-500 text-xs">Released</p>
                            <p className="font-medium text-gray-900">{new Date(patch.releaseDate).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Server className="text-gray-400" size={16} />
                          <div>
                            <p className="text-gray-500 text-xs">Affected Devices</p>
                            <p className="font-medium text-gray-900">{patch.affectedDevices?.length || 0} devices</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Download className="text-gray-400" size={16} />
                          <div>
                            <p className="text-gray-500 text-xs">Size</p>
                            <p className="font-medium text-gray-900">{patch.size || 'Unknown'}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Activity className="text-gray-400" size={16} />
                          <div>
                            <p className="text-gray-500 text-xs">Vendor</p>
                            <p className="font-medium text-gray-900">{patch.vendor || 'Unknown'}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Related CVEs */}
                  {patch.relatedCVEs && patch.relatedCVEs.length > 0 && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="text-red-600" size={16} />
                        <p className="text-sm font-semibold text-red-800">Related Vulnerabilities</p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {patch.relatedCVEs.map((cve, idx) => (
                          <span key={idx} className="px-2 py-1 bg-white text-red-800 rounded text-xs font-mono border border-red-200 hover:bg-red-100 transition-colors cursor-pointer">
                            {cve}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Additional Information */}
                  {patchDetails[patch.id] && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                      <p className="text-sm font-semibold text-blue-800 mb-2">Patch Details</p>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        {patchDetails[patch.id].requiresReboot !== undefined && (
                          <div className="flex items-center gap-2">
                            <span className="text-blue-600">🔄</span>
                            <span className="text-gray-700">
                              Reboot: {patchDetails[patch.id].requiresReboot ? 'Required' : 'Not Required'}
                            </span>
                          </div>
                        )}
                        {patchDetails[patch.id].installTime && (
                          <div className="flex items-center gap-2">
                            <Clock className="text-blue-600" size={14} />
                            <span className="text-gray-700">Install Time: {patchDetails[patch.id].installTime}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-4 border-t border-gray-200 flex-wrap">
                    <button
                      onClick={() => viewPatchDetails(patch)}
                      className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                    >
                      <Eye size={16} />
                      View Details
                    </button>
                    
                    {patch.status === 'AVAILABLE' && (
                      <>
                        <button
                          onClick={() => requestAIAnalysis(patch)}
                          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all text-sm font-medium shadow-md"
                        >
                          <TrendingUp size={16} />
                          AI Analysis & Deploy
                        </button>
                        <button
                          onClick={() => {
                            // Quick schedule without AI analysis
                            deployPatch(patch, { scheduledFor: Date.now() + 86400000 })
                          }}
                          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                        >
                          <Calendar size={16} />
                          Schedule for Later
                        </button>
                        <button
                          onClick={() => {
                            setSelectedPatch(patch)
                            setAiAnalysis(null)
                            setShowDeployModal(true)
                          }}
                          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                        >
                          <Play size={16} />
                          Deploy Now
                        </button>
                      </>
                    )}
                    
                    {patch.status === 'DEPLOYED' && (
                      <button className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium cursor-default">
                        <CheckCircle size={16} />
                        Deployed
                      </button>
                    )}
                    
                    {patch.status === 'SCHEDULED' && (
                      <button className="flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg text-sm font-medium cursor-default">
                        <Calendar size={16} />
                        Scheduled
                      </button>
                    )}
                    
                    {patch.status === 'DEPLOYING' && (
                      <button className="flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg text-sm font-medium cursor-default">
                        <RefreshCw className="animate-spin" size={16} />
                        Deploying...
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Devices View */}
      {activeView === 'devices' && (
        <div className="space-y-4">
          {devices?.map((device) => {
            const devicePatches = patches?.filter(p => p.affectedDevices?.includes(device.id)) || []
            const pendingPatches = devicePatches.filter(p => p.status === 'AVAILABLE')
            
            return (
              <div key={device.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900">{device.name}</h3>
                    <p className="text-sm text-gray-600">{device.operatingSystem}</p>
                    <div className="mt-4 grid grid-cols-3 gap-4">
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-sm text-gray-600">Total Patches</p>
                        <p className="text-2xl font-bold text-gray-900">{devicePatches.length}</p>
                      </div>
                      <div className="bg-yellow-50 rounded-lg p-3">
                        <p className="text-sm text-yellow-600">Pending</p>
                        <p className="text-2xl font-bold text-yellow-600">{pendingPatches.length}</p>
                      </div>
                      <div className="bg-red-50 rounded-lg p-3">
                        <p className="text-sm text-red-600">Vulnerabilities</p>
                        <p className="text-2xl font-bold text-red-600">{device.vulnerabilityStats?.total || 0}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Schedule View - Enhanced */}
      {activeView === 'schedule' && (
        <div className="space-y-6">
          {/* Schedule Metrics Dashboard */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <Calendar size={28} />
                <span className="text-3xl font-bold">{deploymentSchedule?.length || 0}</span>
              </div>
              <p className="text-purple-100 text-sm font-medium">Total Scheduled</p>
              <p className="text-purple-200 text-xs mt-1">Active patch schedules</p>
            </div>

            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <Clock size={28} />
                <span className="text-3xl font-bold">
                  {deploymentSchedule?.filter(s => new Date(s.scheduledFor) < new Date(Date.now() + 86400000)).length || 0}
                </span>
              </div>
              <p className="text-blue-100 text-sm font-medium">Next 24 Hours</p>
              <p className="text-blue-200 text-xs mt-1">Upcoming deployments</p>
            </div>

            <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <AlertTriangle size={28} />
                <span className="text-3xl font-bold">
                  {deploymentSchedule?.filter(s => s.severity === 'CRITICAL').length || 0}
                </span>
              </div>
              <p className="text-red-100 text-sm font-medium">Critical Patches</p>
              <p className="text-red-200 text-xs mt-1">High priority items</p>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <Server size={28} />
                <span className="text-3xl font-bold">
                  {deploymentSchedule?.reduce((sum, s) => sum + (s.deviceCount || 0), 0) || 0}
                </span>
              </div>
              <p className="text-green-100 text-sm font-medium">Total Devices</p>
              <p className="text-green-200 text-xs mt-1">Affected endpoints</p>
            </div>
          </div>

          {/* Schedule Status Distribution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <TrendingUp size={20} className="text-blue-600" />
              Schedule Distribution by Severity
            </h3>
            <div className="grid grid-cols-4 gap-4">
              {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(severity => {
                const count = deploymentSchedule?.filter(s => s.severity === severity).length || 0
                const total = deploymentSchedule?.length || 1
                const percentage = ((count / total) * 100).toFixed(0)
                
                return (
                  <div key={severity} className="text-center">
                    <div className={`relative pt-1 ${
                      severity === 'CRITICAL' ? 'text-red-600' :
                      severity === 'HIGH' ? 'text-orange-600' :
                      severity === 'MEDIUM' ? 'text-yellow-600' :
                      'text-blue-600'
                    }`}>
                      <div className="flex mb-2 items-center justify-center">
                        <span className="text-3xl font-bold">{count}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                        <div 
                          className={`h-2 rounded-full ${
                            severity === 'CRITICAL' ? 'bg-red-600' :
                            severity === 'HIGH' ? 'bg-orange-600' :
                            severity === 'MEDIUM' ? 'bg-yellow-600' :
                            'bg-blue-600'
                          }`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-semibold uppercase">{severity}</span>
                      <p className="text-xs text-gray-500 mt-1">{percentage}% of total</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Schedule Timeline View */}
          {deploymentSchedule && deploymentSchedule.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Activity size={20} className="text-blue-600" />
                Deployment Timeline
              </h3>
              <div className="space-y-3">
                {deploymentSchedule
                  .sort((a, b) => new Date(a.scheduledFor) - new Date(b.scheduledFor))
                  .slice(0, 5)
                  .map((schedule, idx) => {
                    const scheduleDate = new Date(schedule.scheduledFor)
                    const now = new Date()
                    const hoursUntil = ((scheduleDate - now) / (1000 * 60 * 60)).toFixed(1)
                    const isPast = scheduleDate < now
                    
                    return (
                      <div key={idx} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                        <div className="flex-shrink-0 w-20 text-center">
                          <div className={`text-2xl font-bold ${isPast ? 'text-red-600' : 'text-blue-600'}`}>
                            {scheduleDate.getDate()}
                          </div>
                          <div className="text-xs text-gray-600">
                            {scheduleDate.toLocaleDateString('en-US', { month: 'short' })}
                          </div>
                          <div className="text-xs text-gray-500">
                            {scheduleDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${getSeverityBadge(schedule.severity)}`}>
                              {schedule.severity}
                            </span>
                            <span className="font-semibold text-gray-900">{schedule.patchTitle}</span>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <span className="flex items-center gap-1">
                              <Server size={14} />
                              {schedule.deviceCount} devices
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock size={14} />
                              {isPast ? 'Overdue' : `In ${hoursUntil}h`}
                            </span>
                            {schedule.requestedBy && (
                              <span className="flex items-center gap-1">
                                👤 {schedule.requestedBy}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            </div>
          )}

          {/* Detailed Schedule Table */}
          {!deploymentSchedule || deploymentSchedule.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-gray-200">
              <Calendar size={64} className="mx-auto text-gray-300 mb-4" />
              <p className="text-xl font-bold text-gray-700 mb-2">No Scheduled Deployments</p>
              <p className="text-gray-500 mb-6">Get started by scheduling patches from the Patches tab</p>
              <button 
                onClick={() => setActiveView('patches')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium inline-flex items-center gap-2"
              >
                <Shield size={18} />
                View Available Patches
              </button>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <Calendar size={20} className="text-blue-600" />
                  All Scheduled Deployments ({deploymentSchedule.length})
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patch</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scheduled For</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Devices</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {deploymentSchedule.map((schedule, idx) => {
                      const scheduleDate = new Date(schedule.scheduledFor)
                      const status = schedule.status || 'SCHEDULED'
                      
                      return (
                        <tr key={idx} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{schedule.patchTitle || schedule.patchId}</div>
                            {schedule.patchId && (
                              <div className="text-xs text-gray-500">ID: {schedule.patchId}</div>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${getSeverityBadge(schedule.severity)}`}>
                              {schedule.severity}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{scheduleDate.toLocaleDateString()}</div>
                            <div className="text-xs text-gray-500">{scheduleDate.toLocaleTimeString()}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-1 text-sm text-gray-900">
                              <Server size={14} className="text-gray-500" />
                              {schedule.deviceCount || 0}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusBadge(status)}`}>
                              {status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => {
                                  if (schedule.scheduleId) {
                                    api.cancelSchedule(schedule.scheduleId).then((result) => {
                                      if (result.success) {
                                        // Update deployment schedule with the response data
                                        if (result.data.schedules) {
                                          setDeploymentSchedule(result.data.schedules)
                                        }
                                        alert(`✅ Schedule cancelled successfully!\n\nRemaining schedules: ${result.data.scheduleCount || 0}`)
                                        // Refresh all data
                                        loadSchedules()
                                        loadPatchData()
                                      }
                                    }).catch(err => {
                                      console.error('Cancel error:', err)
                                      alert('❌ Failed to cancel schedule')
                                    })
                                  } else {
                                    setDeploymentSchedule(deploymentSchedule.filter((_, i) => i !== idx))
                                    alert('Schedule removed from list')
                                  }
                                }}
                                className="px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 transition-colors font-medium"
                              >
                                Cancel
                              </button>
                              {schedule.scheduleId && (
                                <button
                                  onClick={() => {
                                    api.getScheduleDetails(schedule.scheduleId).then(result => {
                                      if (result.success) {
                                        alert(JSON.stringify(result.schedule, null, 2))
                                      }
                                    })
                                  }}
                                  className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors font-medium"
                                >
                                  Details
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Compliance View */}
      {activeView === 'compliance' && (
        <div className="space-y-6">
          {patchAnalysis && patchAnalysis.coverageRate !== undefined ? (
            <>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Compliance Status</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                    <span className="font-medium text-gray-700">Overall Patch Compliance</span>
                    <span className={`text-2xl font-bold ${
                      patchAnalysis.coverageRate >= 90 ? 'text-green-600' : 
                      patchAnalysis.coverageRate >= 70 ? 'text-yellow-600' : 
                      'text-red-600'
                    }`}>
                      {patchAnalysis.coverageRate.toFixed(1)}%
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-green-50 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-green-600">{patchAnalysis.fullyPatched || 0}</p>
                      <p className="text-sm text-green-700 mt-1">Fully Patched</p>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-yellow-600">{patchAnalysis.partiallyPatched || 0}</p>
                      <p className="text-sm text-yellow-700 mt-1">Partially Patched</p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-red-600">{patchAnalysis.unpatched || 0}</p>
                      <p className="text-sm text-red-700 mt-1">Unpatched</p>
                    </div>
                  </div>
                  
                  {patchAnalysis.criticalExposure && patchAnalysis.criticalExposure.length > 0 && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
                      <h4 className="font-semibold text-red-800 mb-3 flex items-center gap-2">
                        <AlertTriangle size={20} />
                        Critical Compliance Issues ({patchAnalysis.criticalExposure.length})
                      </h4>
                      <div className="space-y-2">
                        {patchAnalysis.criticalExposure.map((exposure, idx) => (
                          <div key={idx} className="bg-white rounded p-3 border border-red-200">
                            <p className="font-medium text-gray-900">{exposure.deviceName}</p>
                            <p className="text-sm text-red-600">{exposure.cveId} - CVSS {exposure.cvssScore}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200">
              <Shield size={48} className="mx-auto text-gray-400 mb-3" />
              <p className="text-gray-600 font-medium">Compliance data not available</p>
              <p className="text-sm text-gray-500 mt-2">Patch analysis is currently unavailable. Try refreshing the data.</p>
            </div>
          )}
        </div>
      )}

      {/* Patch Details Modal */}
      {showPatchDetailsModal && selectedPatch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 sticky top-0 z-10">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <Shield size={28} />
                    <h2 className="text-2xl font-bold">{selectedPatch.title}</h2>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${getSeverityBadge(selectedPatch.severity)} bg-white bg-opacity-90`}>
                      {selectedPatch.severity}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusBadge(selectedPatch.status)} bg-white bg-opacity-90`}>
                      {selectedPatch.status}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setShowPatchDetailsModal(false)}
                  className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Description */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 flex items-center gap-2">
                  <Activity size={20} className="text-blue-600" />
                  Description
                </h3>
                <p className="text-gray-700 leading-relaxed">{selectedPatch.description}</p>
              </div>

              {/* Key Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Calendar size={18} className="text-gray-600" />
                    <h4 className="font-semibold text-gray-900">Release Information</h4>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Release Date:</span>
                      <span className="font-medium text-gray-900">{new Date(selectedPatch.releaseDate).toLocaleDateString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Vendor:</span>
                      <span className="font-medium text-gray-900">{selectedPatch.vendor || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Patch Size:</span>
                      <span className="font-medium text-gray-900">{selectedPatch.size || 'Unknown'}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Server size={18} className="text-gray-600" />
                    <h4 className="font-semibold text-gray-900">Deployment Information</h4>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Affected Devices:</span>
                      <span className="font-medium text-gray-900">{selectedPatch.affectedDevices?.length || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Requires Reboot:</span>
                      <span className="font-medium text-gray-900">{selectedPatch.requiresReboot ? 'Yes' : 'No'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Current Status:</span>
                      <span className="font-medium text-gray-900">{selectedPatch.status}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Related CVEs */}
              {selectedPatch.relatedCVEs && selectedPatch.relatedCVEs.length > 0 && (
                <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle size={20} className="text-red-600" />
                    <h3 className="text-lg font-bold text-red-800">Related Vulnerabilities</h3>
                  </div>
                  <div className="space-y-3">
                    {selectedPatch.relatedCVEs.map((cve, idx) => (
                      <div key={idx} className="bg-white rounded-lg p-3 border border-red-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-mono font-bold text-red-800">{cve}</span>
                          <a
                            href={`https://nvd.nist.gov/vuln/detail/${cve}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            View on NVD →
                          </a>
                        </div>
                        <p className="text-sm text-gray-600">Click to view full CVE details on NVD database</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Affected Devices List */}
              {selectedPatch.affectedDevices && selectedPatch.affectedDevices.length > 0 && (
                <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Server size={20} className="text-blue-600" />
                    <h3 className="text-lg font-bold text-blue-800">Affected Devices</h3>
                  </div>
                  <div className="space-y-2">
                    {selectedPatch.affectedDevices.map((deviceId) => {
                      const device = devices.find(d => d.id === deviceId)
                      return device ? (
                        <div key={deviceId} className="bg-white rounded-lg p-3 border border-blue-200 flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-gray-900">{device.name}</p>
                            <p className="text-sm text-gray-600">{device.operatingSystem} • {device.ipAddress}</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                            device.riskScore >= 8 ? 'bg-red-100 text-red-800' :
                            device.riskScore >= 6 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            Risk: {device.riskScore}
                          </span>
                        </div>
                      ) : (
                        <div key={deviceId} className="bg-white rounded-lg p-3 border border-blue-200">
                          <p className="text-gray-600">Device ID: {deviceId}</p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t-2 border-gray-200">
                {selectedPatch.status === 'AVAILABLE' && (
                  <>
                    <button
                      onClick={() => {
                        setShowPatchDetailsModal(false)
                        requestAIAnalysis(selectedPatch)
                      }}
                      className="flex-1 flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-bold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md"
                    >
                      <TrendingUp size={20} />
                      AI Analysis & Deploy
                    </button>
                    <button
                      onClick={() => {
                        setShowPatchDetailsModal(false)
                        setAiAnalysis(null)
                        setShowDeployModal(true)
                      }}
                      className="flex-1 flex items-center justify-center gap-2 py-3 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 transition-colors"
                    >
                      <Play size={20} />
                      Manual Deploy
                    </button>
                  </>
                )}
                <button
                  onClick={() => setShowPatchDetailsModal(false)}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-bold hover:bg-gray-300 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Deploy Modal with AI Analysis */}
      {showDeployModal && selectedPatch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">Deploy Patch: {selectedPatch.title}</h2>
                <p className="text-sm opacity-90">AI-Powered Deployment Analysis</p>
              </div>
              <button
                onClick={() => {
                  setShowDeployModal(false)
                  setAiAnalysis(null)
                }}
                className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-6 space-y-6">
              {aiAnalysis ? (
                <>
                  {/* AI Recommendation */}
                  <div className={`rounded-lg p-4 border-2 ${
                    aiAnalysis.recommendation === 'APPROVE' 
                      ? 'bg-green-50 border-green-300' 
                      : aiAnalysis.recommendation === 'REVIEW'
                      ? 'bg-yellow-50 border-yellow-300'
                      : 'bg-red-50 border-red-300'
                  }`}>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-3xl">
                        {aiAnalysis.recommendation === 'APPROVE' ? '✅' : aiAnalysis.recommendation === 'REVIEW' ? '⚠️' : '❌'}
                      </span>
                      <div>
                        <p className="font-bold text-lg">AI Recommendation: {aiAnalysis.recommendation}</p>
                        <p className="text-sm opacity-80">{aiAnalysis.reasoning}</p>
                      </div>
                    </div>
                  </div>

                  {/* Risk Assessment */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-bold text-gray-900 mb-3">Risk Assessment</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-700">Deployment Risk:</span>
                        <span className="font-bold">{aiAnalysis.riskLevel}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Business Impact:</span>
                        <span className="font-bold">{aiAnalysis.businessImpact}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Confidence Score:</span>
                        <span className="font-bold">{(aiAnalysis.confidence * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Deployment Plan */}
                  <div>
                    <h3 className="font-bold text-gray-900 mb-3">Recommended Deployment Plan</h3>
                    <ol className="space-y-2">
                      {aiAnalysis.deploymentSteps?.map((step, idx) => (
                        <li key={idx} className="flex gap-3">
                          <span className="font-bold text-indigo-600">{idx + 1}.</span>
                          <span className="text-gray-700">{step}</span>
                        </li>
                      ))}
                    </ol>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => deployPatch(selectedPatch)}
                      className="flex-1 py-3 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700 transition-colors"
                    >
                      Deploy Now
                    </button>
                    <button
                      onClick={() => deployPatch(selectedPatch, { scheduledFor: Date.now() + 86400000 })}
                      className="flex-1 py-3 bg-purple-600 text-white rounded-lg font-bold hover:bg-purple-700 transition-colors"
                    >
                      Schedule for Later
                    </button>
                    <button
                      onClick={() => {
                        setShowDeployModal(false)
                        setAiAnalysis(null)
                      }}
                      className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-bold hover:bg-gray-300 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">AI is analyzing the patch deployment...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PatchManagementSystem
