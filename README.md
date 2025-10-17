# AutoOps AI - Agentic AI-Powered IT Operations Platform

## Overview
AutoOps AI is an Agentic AI-powered platform designed to make IT operations self-driving for MSPs and IT teams. It intelligently handles patch management, alert management, vulnerability scanning, and routine IT administrative tasks through autonomous AI agents with real-time AWS services integration.

## 🆕 Latest Features
- **NVD Vulnerability Integration**: Real-time CVE scanning and correlation with device inventory
- **SuperOps MSP Device Inventory**: Complete visibility into all managed devices with vulnerability status
- **AWS Real-Time Alerting**: SNS notifications for critical vulnerabilities
- **DynamoDB Vulnerability Tracking**: Historical vulnerability data and trend analysis
- **EventBridge Automation**: Event-driven patch deployment and remediation
- **Enhanced Dashboard**: Modern UI with inventory management and alert creation

## Architecture
- **Frontend**: Next.js 14 + React 18 + TailwindCSS (AWS Amplify)
- **Backend**: AWS Lambda + API Gateway + Flask (Local Dev)
- **AI Orchestration**: AWS Bedrock + CrewAI
- **Workflow**: AWS Step Functions + EventBridge
- **Storage**: DynamoDB, S3, Amazon OpenSearch
- **Alerting**: Amazon SNS + EventBridge
- **Integration**: SuperOps.ai APIs + NVD API
- **Monitoring**: CloudWatch + CloudTrail

## Key Features
1. **Vulnerability Management**: 
   - Real-time NVD CVE scanning
   - Device-to-vulnerability correlation
   - Risk scoring and prioritization
   - Top 10 critical CVE dashboard

2. **Patch Management**: 
   - Automated discovery and prioritization
   - Patch coverage analysis
   - Safe deployment with rollback
   - Compliance reporting

3. **Device Inventory Management**:
   - Real-time SuperOps device synchronization
   - Vulnerability status per device
   - Risk-based sorting and filtering
   - OS and software inventory

4. **Alert Management**: 
   - Intelligent correlation and root cause analysis
   - Vulnerability-enriched alerts
   - Manual and automated alert creation
   - AWS SNS real-time notifications

5. **Automated Remediation**: 
   - Policy-driven autonomous actions
   - EventBridge-triggered workflows
   - Emergency patch deployment
   - Compliance enforcement

6. **ChatOps Interface**: Slack/Teams integration
7. **Continuous Learning**: AI adapts from feedback

## Project Structure
```
autoops-ai/
├── frontend/               # React frontend
├── backend/               # Lambda functions
├── infrastructure/        # AWS CDK/CloudFormation
├── ai-agents/            # CrewAI agents
├── workflows/            # Step Functions definitions
├── playbooks/            # Remediation scripts
└── tests/                # Test suites
```

## Prerequisites
- AWS Account with appropriate permissions
- SuperOps.ai account and API token
- Node.js 18+
- Python 3.11+
- AWS CLI configured
- AWS CDK installed

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd autoops-ai
```

### 2. Install Dependencies
```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt

# Infrastructure
cd ../infrastructure
npm install
```

### 3. Configure Environment
Copy `.env.example` to `.env` and fill in:
```bash
# SuperOps Configuration
SUPEROPS_API_TOKEN=your_token_here
SUPEROPS_SUBDOMAIN=your_subdomain
SUPEROPS_DATA_CENTER=us

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0

# DynamoDB
VULNERABILITY_TABLE=AutoOps-Vulnerabilities

# SNS
ALERT_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:AutoOps-CriticalAlerts

# NVD API
NVD_API_KEY=your_nvd_api_key

# Slack Integration (Optional)
SLACK_BOT_TOKEN=your_slack_token
SLACK_SIGNING_SECRET=your_signing_secret
```

## Quick Start (Local Development)

1. **Start Backend Server**:
```bash
# Terminal 1
cd backend
python ../local_dev_server.py
# Server starts on http://localhost:3001
```

2. **Start Frontend**:
```bash
# Terminal 2
cd frontend
npm run dev
# Dashboard opens on http://localhost:3000
```

3. **Access Features**:
- **Overview Tab**: Dashboard statistics and top 10 CVEs
- **Vulnerabilities Tab**: Detailed CVE analysis
- **Inventory Tab**: SuperOps device list with vulnerability status
- **Alerts Tab**: Create and manage security alerts
- **Patches Tab**: Patch management and compliance

## API Endpoints

### Device & Vulnerability Endpoints
- `GET /api/inventory` - Device inventory with vulnerability stats
- `GET /api/vulnerability-analysis?deviceId=<id>` - Analyze device vulnerabilities
- `GET /api/patch-analysis` - Patch coverage analysis

### Alert Endpoints
- `GET /api/alerts` - Get alerts with vulnerability context
- `POST /api/alerts` - Create new alert

### NVD Integration
- `GET /nvd/top-cves` - Top 10 critical CVEs

### Statistics
- `GET /stats/overview` - Dashboard statistics

See [AWS_INTEGRATION.md](./AWS_INTEGRATION.md) for detailed AWS setup and real-time features.

### 4. Deploy Infrastructure
```bash
cd infrastructure
cdk deploy --all
```

### 5. Deploy Frontend
```bash
cd frontend
amplify init
amplify push
```

## Deployment to AWS

### Using AWS CDK (Recommended)
```bash
cd infrastructure
cdk bootstrap
cdk deploy AutoOpsAIStack
```

### Manual Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for step-by-step instructions.

## Usage

### Dashboard Access
Navigate to your Amplify URL to access the dashboard.

### ChatOps Commands
In Slack/Teams:
- `/autoops status` - View system status
- `/autoops patch review` - Review pending patches
- `/autoops alert summary` - Get alert summary
- `/autoops approve [action-id]` - Approve pending action

## Configuration

### Policy Configuration
Define automation policies in `policies/` directory:
```yaml
patch_policy:
  auto_approve_severity: ["low", "medium"]
  approval_required: ["high", "critical"]
  rollback_on_failure: true

alert_policy:
  auto_correlate: true
  suppress_duplicates: true
  escalation_threshold: 3
```

## Development

### Running Locally
```bash
# Frontend
cd frontend && npm run dev

# Backend (using SAM)
cd backend && sam local start-api
```

### Running Tests
```bash
# Frontend
cd frontend && npm test

# Backend
cd backend && pytest
```

## Architecture Diagrams
See [ARCHITECTURE.md](./ARCHITECTURE.md)

## API Documentation
See [API.md](./API.md)

## Contributing
See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License
MIT License - See [LICENSE](./LICENSE)

## Support
For issues and questions, please open a GitHub issue.
