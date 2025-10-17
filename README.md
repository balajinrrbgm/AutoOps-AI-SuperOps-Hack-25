# AutoOps AI - Agentic AI-Powered IT Operations Platform

## Overview
AutoOps AI is an Agentic AI-powered platform designed to make IT operations self-driving for MSPs and IT teams. It intelligently handles patch management, alert management, and routine IT administrative tasks through autonomous AI agents.

## Architecture
- **Frontend**: React + TailwindCSS (AWS Amplify)
- **Backend**: AWS Lambda + API Gateway
- **AI Orchestration**: AWS Bedrock + CrewAI
- **Workflow**: AWS Step Functions
- **Storage**: DynamoDB, S3, Amazon OpenSearch
- **Integration**: SuperOps.ai APIs
- **Monitoring**: CloudWatch + CloudTrail

## Key Features
1. **Patch Management**: Automated discovery, prioritization, and safe deployment
2. **Alert Management**: Intelligent correlation and root cause analysis
3. **Automated Remediation**: Policy-driven autonomous actions
4. **ChatOps Interface**: Slack/Teams integration
5. **Continuous Learning**: AI adapts from feedback

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
```
SUPEROPS_API_TOKEN=your_token_here
SUPEROPS_SUBDOMAIN=your_subdomain
AWS_REGION=us-east-1
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0
SLACK_BOT_TOKEN=your_slack_token
SLACK_SIGNING_SECRET=your_signing_secret
```

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
