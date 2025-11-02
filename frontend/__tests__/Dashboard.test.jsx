import { render, screen } from '@testing-library/react'
import Dashboard from '../src/components/Dashboard'

// Mock aws-amplify/auth since it requires authentication setup
jest.mock('aws-amplify/auth', () => ({
  fetchAuthSession: jest.fn(() => Promise.resolve({
    tokens: {
      idToken: {
        toString: () => 'mock-token'
      }
    }
  }))
}))

// Mock axios to return arrays for the dashboard data
jest.mock('axios', () => ({
  get: jest.fn((url) => {
    if (url.includes('/patches/status')) {
      return Promise.resolve({ 
        data: {
          totalDevices: 100,
          compliant: 85,
          pending: 15
        }
      })
    }
    if (url.includes('/alerts/active')) {
      return Promise.resolve({ 
        data: [
          { id: 1, title: 'Test Alert', severity: 'critical', description: 'Test alert description' }
        ]
      })
    }
    if (url.includes('/actions/recent')) {
      return Promise.resolve({ 
        data: [
          { id: 1, type: 'Patch', status: 'completed', description: 'Test action', timestamp: new Date().toISOString() }
        ]
      })
    }
    return Promise.resolve({ data: [] })
  })
}))

describe('Dashboard', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks()
  })

  it('renders loading spinner initially', () => {
    render(<Dashboard />)
    const loadingElement = screen.getByTestId('loading-spinner')
    expect(loadingElement).toBeInTheDocument()
  })

  it('component renders without crashing', () => {
    // This test just ensures the component can be rendered without throwing an error
    const { container } = render(<Dashboard />)
    expect(container).toBeInTheDocument()
  })
})