# AutoOps AI - Architecture Documentation

## System Architecture Overview

AutoOps AI is built on a serverless, event-driven architecture leveraging AWS services and AI orchestration.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│                    (React + TailwindCSS)                         │
│                     Hosted on AWS Amplify                        │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│              (REST API with Lambda Integration)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Lambda     │ │   Lambda     │ │   Lambda     │
│  Functions   │ │  Functions   │ │  Functions   │
│              │ │              │ │              │
│ - API Handler│ │ - AI Agents  │ │ - Workflows  │
│ - SuperOps   │ │ - CrewAI     │ │ - Step Fns   │
│   Integration│ │ - Bedrock    │ │   Handlers   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  DynamoDB    │ │      S3      │ │  OpenSearch  │
│              │ │              │ │              │
│ - Policies   │ │ - Playbooks  │ │ - Vectors    │
│ - Actions    │ │ - Logs       │ │ - Context    │
│ - Executions │ │ - Reports    │ │ - Learning   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Component Details

### 1. Frontend (React + TailwindCSS)
- **Dashboard**: Real-time monitoring of patches, alerts, and AI actions
- **Policy Manager**: Configure automation policies
- **Alert Management**: View and manage correlated alerts
- **Approval Interface**: Approve/reject AI-recommended actions

### 2. API Gateway
- RESTful API endpoints
- Request validation and throttling
- CORS configuration
- CloudWatch logging

### 3. Lambda Functions

#### API Handler
- Routes incoming requests
- Integrates with SuperOps.ai
- Manages CRUD operations

#### AI Risk Assessment
- Evaluates patch criticality
- Assesses deployment risk
- Determines approval requirements

#### Patch Deployment
- Executes patch deployments via SuperOps
- Monitors deployment progress
- Handles rollbacks

#### Alert Processing
- Fetches alerts from SuperOps
- Triggers AI correlation
- Updates alert status

#### Slack Bot
- Processes slash commands
- Handles interactive components
- Sends notifications

### 4. AI Orchestration (AWS Bedrock + CrewAI)

#### Agents
1. **Patch Prioritization Agent**
   - Analyzes CVE data from NVD
   - Prioritizes based on CVSS, exploitability, business impact
   - Recommends deployment schedule

2. **Alert Correlation Agent**
   - Groups related alerts
   - Identifies duplicate/redundant alerts
   - Reduces alert noise

3. **Root Cause Analysis Agent**
   - Investigates incident origins
   - Analyzes logs and metrics
   - Identifies systemic issues

4. **Remediation Decision Agent**
   - Determines safe actions
   - Operates within policy guardrails
   - Plans rollback procedures

5. **Learning Agent**
   - Incorporates human feedback
   - Improves decision quality
   - Identifies patterns

### 5. Workflow Orchestration (Step Functions)

#### Patch Deployment Workflow
1. Get patch details
2. AI risk assessment
3. Check approval requirement
4. (Optional) Request approval with timeout
5. Deploy patches
6. Monitor deployment
7. Verify success
8. Update metrics
9. (On failure) Initiate rollback

#### Alert Processing Workflow
1. Fetch alerts
2. AI correlation
3. Root cause analysis
4. Determine remediation
5. Execute or request approval
6. Update alert status
7. Learn from outcome

### 6. Data Stores

#### DynamoDB Tables
- **Policies**: Automation policies and guardrails
- **Actions**: Audit trail of AI decisions
- **Executions**: Workflow execution logs
- TTL enabled for automatic cleanup

#### S3 Buckets
- **Playbooks**: Remediation scripts with versioning
- **Logs**: CloudWatch log exports
- Lifecycle policies for cost optimization

#### OpenSearch
- Vector database for AI context
- Historical incident data
- Learning from past decisions

### 7. External Integrations

#### SuperOps.ai
- Device inventory
- Patch management
- Alert management
- Script execution
- GraphQL API

#### NVD CVE API
- Vulnerability data
- CVSS scores
- CPE matching
- Rate-limited requests

#### Slack/Teams
- Command interface
- Approval workflows
- Notifications
- Interactive components

## Security Architecture

### Authentication & Authorization
- API Gateway with IAM authorization
- Secrets Manager for credentials
- Least privilege IAM roles
- Token-based authentication

### Data Security
- Encryption at rest (S3, DynamoDB)
- Encryption in transit (TLS 1.2+)
- VPC endpoints for AWS services
- Security groups and NACLs

### Audit & Compliance
- CloudTrail for API logging
- CloudWatch for monitoring
- Action audit trail in DynamoDB
- Immutable logs in S3

## Scalability & Reliability

### Horizontal Scaling
- Lambda auto-scaling
- DynamoDB on-demand capacity
- API Gateway throttling
- Multi-AZ deployment

### Fault Tolerance
- Retry logic in Step Functions
- Dead letter queues
- Circuit breaker pattern
- Graceful degradation

### Monitoring & Alerting
- CloudWatch metrics and alarms
- X-Ray tracing
- Custom dashboards
- SNS notifications

## Cost Optimization

### Strategies
- Lambda reserved concurrency
- DynamoDB on-demand vs provisioned
- S3 lifecycle policies
- CloudWatch log retention
- Bedrock prompt optimization

### Estimated Costs
See DEPLOYMENT.md for detailed cost breakdown

## Deployment Architecture

### CI/CD Pipeline
- GitHub Actions / CodePipeline
- Automated testing
- Blue-green deployments
- Rollback capability

### Environments
- Development (dev)
- Staging (staging)
- Production (prod)

## Future Enhancements

1. **Multi-Region Deployment**: Active-active for higher availability
2. **Advanced ML Models**: Custom models for specific MSP needs
3. **Additional Integrations**: More RMM/PSA platforms
4. **Enhanced Visualization**: Real-time charts and analytics
5. **Mobile App**: iOS/Android for on-the-go management
