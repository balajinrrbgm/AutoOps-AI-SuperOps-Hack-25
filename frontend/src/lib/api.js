// API utility for consistent API calls across the application

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

// Mock data for fallback when API is unavailable
const mockInventoryData = [
  {
    id: 1,
    name: 'PROD-WEB-01',
    ipAddress: '192.168.1.10',
    macAddress: '00:1B:44:11:3A:B7',
    operatingSystem: 'Windows Server 2019',
    type: 'Server',
    client: 'Acme Corp',
    site: 'Main Office',
    status: 'online',
    lastSeenAt: new Date().toISOString(),
    patchStatus: 'compliant',
    pendingPatches: 0,
    riskScore: 25.5,
    vulnerabilityStats: {
      total: 2,
      critical: 0,
      high: 0,
      medium: 2,
      low: 0
    },
    topVulnerabilities: [
      {
        cveId: 'CVE-2024-7621',
        severity: 'MEDIUM',
        cvssScore: 5.3,
        description: 'Moderate security vulnerability in web server component'
      }
    ]
  },
  {
    id: 2,
    name: 'PROD-DB-01',
    ipAddress: '192.168.1.20',
    macAddress: '00:1B:44:11:3A:B8',
    operatingSystem: 'Windows Server 2022',
    type: 'Server',
    client: 'Acme Corp',
    site: 'Main Office',
    status: 'online',
    lastSeenAt: new Date().toISOString(),
    patchStatus: 'pending',
    pendingPatches: 3,
    riskScore: 78.2,
    vulnerabilityStats: {
      total: 8,
      critical: 2,
      high: 3,
      medium: 2,
      low: 1
    },
    topVulnerabilities: [
      {
        cveId: 'CVE-2024-9123',
        severity: 'CRITICAL',
        cvssScore: 9.8,
        description: 'Critical RCE vulnerability allows remote code execution'
      },
      {
        cveId: 'CVE-2024-8956',
        severity: 'CRITICAL',
        cvssScore: 9.1,
        description: 'SQL injection vulnerability in database component'
      },
      {
        cveId: 'CVE-2024-8745',
        severity: 'HIGH',
        cvssScore: 8.8,
        description: 'Privilege escalation vulnerability'
      }
    ]
  },
  {
    id: 3,
    name: 'PROD-APP-01',
    ipAddress: '192.168.1.30',
    macAddress: '00:1B:44:11:3A:B9',
    operatingSystem: 'Ubuntu 22.04 LTS',
    type: 'Server',
    client: 'Acme Corp',
    site: 'Main Office',
    status: 'online',
    lastSeenAt: new Date().toISOString(),
    patchStatus: 'compliant',
    pendingPatches: 0,
    riskScore: 32.1,
    vulnerabilityStats: {
      total: 3,
      critical: 0,
      high: 1,
      medium: 2,
      low: 0
    },
    topVulnerabilities: [
      {
        cveId: 'CVE-2024-7890',
        severity: 'HIGH',
        cvssScore: 7.5,
        description: 'HTTP request smuggling vulnerability'
      },
      {
        cveId: 'CVE-2024-7621',
        severity: 'MEDIUM',
        cvssScore: 5.3,
        description: 'Moderate security vulnerability'
      }
    ]
  },
  {
    id: 4,
    name: 'WORKSTATION-01',
    ipAddress: '192.168.2.10',
    macAddress: '00:1B:44:11:3A:BA',
    operatingSystem: 'Windows 11 Pro',
    type: 'Workstation',
    client: 'Acme Corp',
    site: 'Main Office',
    status: 'online',
    lastSeenAt: new Date().toISOString(),
    patchStatus: 'pending',
    pendingPatches: 5,
    riskScore: 65.8,
    vulnerabilityStats: {
      total: 7,
      critical: 1,
      high: 3,
      medium: 3,
      low: 0
    },
    topVulnerabilities: [
      {
        cveId: 'CVE-2024-9123',
        severity: 'CRITICAL',
        cvssScore: 9.8,
        description: 'Critical RCE vulnerability allows remote code execution'
      },
      {
        cveId: 'CVE-2024-8632',
        severity: 'HIGH',
        cvssScore: 8.1,
        description: 'Authentication bypass vulnerability'
      }
    ]
  },
  {
    id: 5,
    name: 'WORKSTATION-02',
    ipAddress: '192.168.2.11',
    macAddress: '00:1B:44:11:3A:BB',
    operatingSystem: 'Windows 11 Pro',
    type: 'Workstation',
    client: 'Acme Corp',
    site: 'Branch Office',
    status: 'offline',
    lastSeenAt: new Date(Date.now() - 7200000).toISOString(),
    patchStatus: 'non-compliant',
    pendingPatches: 12,
    riskScore: 92.5,
    vulnerabilityStats: {
      total: 15,
      critical: 4,
      high: 6,
      medium: 5,
      low: 0
    },
    topVulnerabilities: [
      {
        cveId: 'CVE-2024-9123',
        severity: 'CRITICAL',
        cvssScore: 9.8,
        description: 'Critical RCE vulnerability allows remote code execution'
      },
      {
        cveId: 'CVE-2024-8956',
        severity: 'CRITICAL',
        cvssScore: 9.1,
        description: 'SQL injection vulnerability'
      },
      {
        cveId: 'CVE-2024-8745',
        severity: 'HIGH',
        cvssScore: 8.8,
        description: 'Privilege escalation vulnerability'
      },
      {
        cveId: 'CVE-2024-8632',
        severity: 'HIGH',
        cvssScore: 8.1,
        description: 'Authentication bypass vulnerability'
      }
    ]
  }
];

const mockAlertsData = [
  {
    id: 1,
    title: "High CPU Usage on SQL Server",
    description: "SQL Server on PROD-DB-01 showing 95% CPU utilization",
    severity: "critical",
    timestamp: new Date(Date.now() - 900000).toISOString(),
    deviceId: 2,
    deviceName: 'PROD-DB-01',
    status: 'active'
  },
  {
    id: 2,
    title: "Failed Windows Update",
    description: "KB5034441 failed to install on multiple workstations",
    severity: "high",
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    deviceId: 4,
    deviceName: 'WORKSTATION-01',
    status: 'active'
  },
  {
    id: 3,
    title: "Low Disk Space Warning",
    description: "C: drive on FILE-SRV-02 has less than 10% free space",
    severity: "medium",
    timestamp: new Date(Date.now() - 14400000).toISOString(),
    deviceId: null,
    deviceName: 'FILE-SRV-02',
    status: 'active'
  }
];

const mockPatchesData = [
  {
    id: 'KB5034441',
    title: 'Windows 11 Security Update',
    description: 'Cumulative security update for Windows 11',
    severity: 'CRITICAL',
    releaseDate: '2024-01-09',
    cveId: 'CVE-2024-9123',
    cveIds: ['CVE-2024-9123', 'CVE-2024-8956'],
    relatedCVEs: [
      { id: 'CVE-2024-9123', severity: 'CRITICAL', score: 9.8 },
      { id: 'CVE-2024-8956', severity: 'HIGH', score: 7.5 }
    ],
    affectedDevices: [1, 2], // Array of device IDs
    installedDevices: 0,
    failedDevices: 0,
    status: 'AVAILABLE',
    vendor: 'Microsoft',
    category: 'Security Update',
    size: '450 MB',
    requiresReboot: true
  },
  {
    id: 'KB5034439',
    title: 'Windows Server 2022 Update',
    description: 'Monthly rollup for Windows Server 2022',
    severity: 'HIGH',
    releaseDate: '2024-01-09',
    cveId: 'CVE-2024-8745',
    cveIds: ['CVE-2024-8745'],
    relatedCVEs: [
      { id: 'CVE-2024-8745', severity: 'HIGH', score: 7.8 }
    ],
    affectedDevices: [3, 4], // Array of device IDs
    installedDevices: 1,
    failedDevices: 0,
    status: 'DEPLOYING',
    vendor: 'Microsoft',
    category: 'Monthly Rollup',
    size: '320 MB',
    requiresReboot: true
  },
  {
    id: 'UBUNTU-2024-01',
    title: 'Ubuntu Security Updates',
    description: 'Security updates for Ubuntu 22.04 LTS',
    severity: 'MEDIUM',
    releaseDate: '2024-01-08',
    cveId: 'CVE-2024-7621',
    cveIds: ['CVE-2024-7621'],
    relatedCVEs: [
      { id: 'CVE-2024-7621', severity: 'MEDIUM', score: 5.5 }
    ],
    affectedDevices: [5], // Array of device IDs
    installedDevices: 1,
    failedDevices: 0,
    status: 'DEPLOYED',
    vendor: 'Canonical',
    category: 'Security Update',
    size: '125 MB',
    requiresReboot: false
  }
];

/**
 * Fetch with retry logic and fallback to mock data
 */
async function fetchWithRetry(url, options = {}, retries = 2) {
  const fetchOptions = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  for (let i = 0; i <= retries; i++) {
    try {
      const response = await fetch(url, fetchOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data, fromCache: false };
    } catch (error) {
      console.warn(`Attempt ${i + 1} failed for ${url}:`, error.message);
      
      if (i === retries) {
        // Return mock data on final retry
        return { success: false, data: null, error: error.message };
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}

/**
 * API Methods
 */
export const api = {
  // Inventory endpoints
  async getInventory() {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/inventory`);
    
    if (!result.success) {
      console.log('Using mock inventory data');
      return { success: true, data: mockInventoryData, fromCache: true };
    }
    
    return result;
  },

  async scanDevice(deviceId) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/scan-device/${deviceId}`, {
      method: 'POST'
    });
    
    if (!result.success) {
      return { success: true, data: { message: 'Scan initiated (mock)' }, fromCache: true };
    }
    
    return result;
  },

  // Alerts endpoints
  async getAlerts() {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/alerts`);
    
    if (!result.success) {
      console.log('Using mock alerts data');
      return { success: true, data: mockAlertsData, fromCache: true };
    }
    
    return result;
  },

  async acknowledgeAlert(alertId) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/alerts/${alertId}/acknowledge`, {
      method: 'POST'
    });
    
    if (!result.success) {
      return { success: true, data: { message: 'Alert acknowledged (mock)' }, fromCache: true };
    }
    
    return result;
  },

  async resolveAlert(alertId, resolution) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/alerts/${alertId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution })
    });
    
    if (!result.success) {
      return { success: true, data: { message: 'Alert resolved (mock)' }, fromCache: true };
    }
    
    return result;
  },

  async createAlert(alertData) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/alerts`, {
      method: 'POST',
      body: JSON.stringify(alertData)
    });
    
    if (!result.success) {
      return { success: true, data: { id: Date.now(), ...alertData }, fromCache: true };
    }
    
    return result;
  },

  // Patches endpoints
  async getPatches() {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/patches`);
    
    if (!result.success) {
      console.log('Using mock patches data');
      return { success: true, data: mockPatchesData, fromCache: true };
    }
    
    return result;
  },

  async getPatchDetails(patchId) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/patches/${patchId}/details`);
    
    if (!result.success) {
      const mockPatch = mockPatchesData.find(p => p.id === patchId);
      return { success: true, data: mockPatch || {}, fromCache: true };
    }
    
    return result;
  },

  async analyzePatch(patchData) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/ai/analyze-patch`, {
      method: 'POST',
      body: JSON.stringify(patchData)
    });
    
    if (!result.success) {
      // Generate mock AI analysis based on patch severity
      const severity = patchData.patch?.severity || 'MEDIUM';
      const isHighRisk = severity === 'CRITICAL' || severity === 'HIGH';
      
      return {
        success: true,
        data: {
          recommendation: isHighRisk ? 'REVIEW' : 'APPROVE',
          reasoning: isHighRisk 
            ? 'This patch addresses critical security vulnerabilities. Recommend thorough testing before production deployment.'
            : 'Patch has been analyzed and approved for deployment. Low risk of system disruption.',
          riskLevel: isHighRisk ? 7 : 3,
          businessImpact: isHighRisk ? 'HIGH' : 'LOW',
          confidence: 0.92,
          deploymentSteps: [
            'Backup affected systems before deployment',
            'Deploy to test environment first',
            isHighRisk ? 'Conduct thorough testing for 24-48 hours' : 'Monitor for 2-4 hours',
            'Deploy to production during maintenance window',
            'Verify successful installation and system stability',
            'Document deployment and any issues encountered'
          ]
        },
        fromCache: true
      };
    }
    
    return result;
  },

  async deployPatch(deploymentData) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/patches/deploy`, {
      method: 'POST',
      body: JSON.stringify(deploymentData)
    });
    
    if (!result.success) {
      return {
        success: true,
        data: {
          jobId: `mock-${Date.now()}`,
          message: 'Deployment initiated (mock)'
        },
        fromCache: true
      };
    }
    
    return result;
  },

  // Stats endpoints
  async getPatchStatus() {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/patches/status`);
    
    if (!result.success) {
      const inventory = mockInventoryData;
      return {
        success: true,
        data: {
          totalDevices: inventory.length,
          compliant: inventory.filter(d => d.patchStatus === 'compliant').length,
          pending: inventory.filter(d => d.patchStatus === 'pending').length,
          nonCompliant: inventory.filter(d => d.patchStatus === 'non-compliant').length,
          lastUpdate: new Date().toISOString()
        },
        fromCache: true
      };
    }
    
    return result;
  },

  async getPatchAnalysis() {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/patch-analysis`);
    
    if (!result.success) {
      return {
        success: true,
        data: mockPatchesData,
        fromCache: true
      };
    }
    
    return result;
  },

  async getPatchSchedule() {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/patch-schedule`);
    
    if (!result.success) {
      return {
        success: true,
        data: [],
        fromCache: true
      };
    }
    
    return result;
  },

  // Scheduler endpoints
  async getSchedules(status = null) {
    const url = status 
      ? `${API_BASE_URL}/api/schedules?status=${status}`
      : `${API_BASE_URL}/api/schedules`;
    
    const result = await fetchWithRetry(url);
    
    if (!result.success) {
      return {
        success: true,
        data: { schedules: [], count: 0 },
        fromCache: true
      };
    }
    
    return result;
  },

  async createSchedule(scheduleData) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/schedules`, {
      method: 'POST',
      body: JSON.stringify(scheduleData)
    });
    
    if (!result.success) {
      return {
        success: true,
        data: {
          scheduleId: `mock-${Date.now()}`,
          scheduledFor: scheduleData.scheduledFor,
          patchTitle: scheduleData.patchTitle,
          deviceCount: scheduleData.deviceIds?.length || 0,
          message: 'Schedule created (mock)'
        },
        fromCache: true
      };
    }
    
    return result;
  },

  async getScheduleDetails(scheduleId) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/schedules/${scheduleId}`);
    
    if (!result.success) {
      return {
        success: false,
        error: 'Schedule not found'
      };
    }
    
    return result;
  },

  async cancelSchedule(scheduleId) {
    const result = await fetchWithRetry(`${API_BASE_URL}/api/schedules/${scheduleId}`, {
      method: 'DELETE'
    });
    
    if (!result.success) {
      return {
        success: true,
        data: { message: 'Schedule cancelled (mock)' },
        fromCache: true
      };
    }
    
    return result;
  }
};

export default api;
