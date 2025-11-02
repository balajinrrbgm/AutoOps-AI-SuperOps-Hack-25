# AWS Integration & Real-Time Features Guide

## Overview
AutoOps AI integrates AWS services for real-time vulnerability monitoring, alerting, and patch management automation. This guide explains how to set up and use these features.

## AWS Services Used

### 1. Amazon DynamoDB
**Purpose**: Store vulnerability assessments, device-CVE mappings, and alert history

**Table Structure**:
```
Table Name: AutoOps-Vulnerabilities

Primary Key:
  - PK (Partition Key): String - Device ID or Alert ID
  - SK (Sort Key): String - CVE ID + Timestamp

Attributes:
  - deviceId: String
  - deviceName: String
  - cveId: String
  - cvssScore: Number
  - severity: String (CRITICAL, HIGH, MEDIUM, LOW)
  - description: String
  - analyzedAt: String (ISO timestamp)
  - ttl: Number (Unix timestamp for auto-deletion)
```

**Setup**:
```bash
aws dynamodb create-table \
  --table-name AutoOps-Vulnerabilities \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2. Amazon SNS (Simple Notification Service)
**Purpose**: Send real-time alerts for critical vulnerabilities

**Topic Structure**:
```
Topic Name: AutoOps-CriticalAlerts
ARN: arn:aws:sns:us-east-1:ACCOUNT_ID:AutoOps-CriticalAlerts

Message Attributes:
  - severity: String (CRITICAL, HIGH, MEDIUM, LOW)
  - deviceId: String
  - cveId: String
```

**Setup**:
```bash
# Create SNS Topic
aws sns create-topic --name AutoOps-CriticalAlerts --region us-east-1

# Subscribe to email notifications
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:AutoOps-CriticalAlerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Subscribe to SMS notifications
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:AutoOps-CriticalAlerts \
  --protocol sms \
  --notification-endpoint +1234567890
```

### 3. Amazon EventBridge
**Purpose**: Route vulnerability events to automated remediation workflows

**Event Pattern**:
```json
{
  "source": ["autoops.vulnerability.analyzer"],
  "detail-type": ["Vulnerability Alert"],
  "detail": {
    "severity": ["CRITICAL"],
    "cvssScore": [{"numeric": [">=", 9.0]}]
  }
}
```

**Setup**:
```bash
# Create EventBridge Rule for Critical Vulnerabilities
aws events put-rule \
  --name AutoOps-CriticalVulnerabilities \
  --event-pattern '{"source":["autoops.vulnerability.analyzer"],"detail-type":["Vulnerability Alert"],"detail":{"severity":["CRITICAL"]}}' \
  --region us-east-1

# Add Lambda target for automated patching
aws events put-targets \
  --rule AutoOps-CriticalVulnerabilities \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT_ID:function:AutoOps-AutoPatch"
```

## Configuration

### Environment Variables
Add these to your `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# DynamoDB
VULNERABILITY_TABLE=AutoOps-Vulnerabilities

# SNS
ALERT_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:AutoOps-CriticalAlerts

# SuperOps & NVD (already configured)
SUPEROPS_API_TOKEN=your-token
SUPEROPS_SUBDOMAIN=your-subdomain
SUPEROPS_DATA_CENTER=us
NVD_API_KEY=your-nvd-key
```

## Features

### 1. Device Inventory with Vulnerability Mapping
**Endpoint**: `GET /api/inventory`

**Description**: Retrieves all devices from SuperOps MSP and cross-references them with NVD vulnerabilities

**Response**:
```json
[
  {
    "id": "dev-001",
    "name": "WEB-SERVER-PROD-01",
    "operatingSystem": "Windows Server 2019 Build 17763",
    "ipAddress": "192.168.1.10",
    "vulnerabilityStats": {
      "total": 8,
      "critical": 2,
      "high": 3,
      "medium": 3
    },
    "topVulnerabilities": [
      {
        "cveId": "CVE-2024-38063",
        "cvssScore": 9.8,
        "severity": "CRITICAL"
      }
    ],
    "riskScore": 87.5
  }
]
```

### 2. Vulnerability Analysis
**Endpoint**: `GET /api/vulnerability-analysis?deviceId=dev-001`

**Description**: Analyzes NVD CVEs against specific device OS/software versions

**How it works**:
1. Fetches device inventory from SuperOps
2. Retrieves recent CVEs from NVD (last 30 days)
3. Matches CVEs to devices based on OS version and software
4. Calculates risk scores
5. Stores results in DynamoDB
6. Sends SNS alerts for critical vulnerabilities (CVSS >= 9.0)

### 3. Patch Coverage Analysis
**Endpoint**: `GET /api/patch-analysis`

**Description**: Compares available patches from SuperOps with known vulnerabilities

**Response**:
```json
{
  "totalDevices": 147,
  "fullyPatched": 98,
  "partiallyPatched": 35,
  "unpatched": 14,
  "coverageRate": 66.7,
  "criticalExposure": [
    {
      "deviceId": "dev-004",
      "deviceName": "FILE-SERVER-01",
      "cveId": "CVE-2024-38063",
      "cvssScore": 9.8
    }
  ],
  "patchRecommendations": [...]
}
```

### 4. Alert Management
**Endpoints**: 
- `GET /api/alerts` - Get all alerts with vulnerability context
- `POST /api/alerts` - Create new alert

**Description**: Enriches SuperOps alerts with NVD vulnerability data

**Alert Creation Flow**:
1. User creates alert (manual) or system detects vulnerability (automatic)
2. Alert stored in DynamoDB
3. SNS notification sent to subscribers
4. EventBridge event published for automation
5. Frontend displays alert with vulnerability context

### 5. Real-Time Monitoring
**Implementation**: 
- Frontend polls `/api/inventory` and `/api/alerts` every 30 seconds
- Backend sends EventBridge events for immediate processing
- SNS sends push notifications for critical alerts

## Usage Examples

### Python Backend Service
```python
from backend.src.services.vulnerability_analyzer import VulnerabilityAnalyzer

# Initialize analyzer
analyzer = VulnerabilityAnalyzer()

# Analyze all devices
vulnerabilities = analyzer.analyze_device_vulnerabilities()
# Returns: List of vulnerabilities found across all devices
# Side effects: Stores in DynamoDB, sends SNS alerts for critical CVEs

# Get device inventory with vulnerability stats
inventory = analyzer.get_device_inventory_with_vulnerabilities()
# Returns: List of devices with vulnerability counts and risk scores

# Analyze patch coverage
analysis = analyzer.analyze_patch_coverage()
# Returns: Patch statistics and recommendations

# Get enriched alerts
alerts = analyzer.get_alerts_with_context()
# Returns: SuperOps alerts + vulnerability context

# Create custom alert
alert = analyzer.create_alert({
    'title': 'Critical CVE Detected',
    'description': 'CVE-2024-38063 found on production server',
    'severity': 'CRITICAL',
    'deviceId': 'dev-001',
    'deviceName': 'WEB-SERVER-PROD-01',
    'cveIds': ['CVE-2024-38063']
})
# Side effects: Stores in DynamoDB, sends SNS, publishes EventBridge event
```

### Frontend Components

#### Inventory List
```jsx
import InventoryList from '../src/components/InventoryList'

// Displays:
// - Searchable device list
// - Risk scores and vulnerability counts
// - Top CVEs per device
// - Sort by risk/vulnerabilities/name
// - Filter by severity
```

#### Alert Management
```jsx
import AlertManagement from '../src/components/AlertManagement'

// Features:
// - View all alerts with vulnerability context
// - Create new alerts
// - Filter by status/severity
// - Shows related CVEs for each alert
// - Acknowledge/Resolve alerts
```

## AWS IAM Permissions Required

Create an IAM role with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/AutoOps-Vulnerabilities"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:us-east-1:*:AutoOps-CriticalAlerts"
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents"
      ],
      "Resource": "arn:aws:events:us-east-1:*:event-bus/default"
    }
  ]
}
```

## Automation Workflows

### Critical Vulnerability Detected
1. NVD CVE matched to device → VulnerabilityAnalyzer
2. CVSS >= 9.0 → Store in DynamoDB + Send SNS alert
3. SNS → Email/SMS to security team
4. EventBridge event → Lambda function
5. Lambda → Deploy emergency patch via SuperOps API

### Daily Vulnerability Scan
1. Scheduled Lambda (CloudWatch Events)
2. Calls `analyze_device_vulnerabilities()`
3. Generates daily report
4. Sends summary via SNS
5. Updates DynamoDB with latest scan results

### Patch Compliance Check
1. Scheduled every 6 hours
2. Calls `analyze_patch_coverage()`
3. Identifies non-compliant devices
4. Creates alerts for devices with critical exposure
5. Generates patch deployment recommendations

## Testing

### Local Development
The local dev server (`local_dev_server.py`) provides mock data for all endpoints. AWS services are optional for local testing.

### Production
1. Ensure AWS credentials are configured
2. Create DynamoDB table and SNS topic
3. Set environment variables
4. Deploy Lambda functions (optional)
5. Configure EventBridge rules (optional)

## Monitoring & Logs

### CloudWatch Logs
- Lambda execution logs
- DynamoDB throughput metrics
- SNS delivery status

### Application Logs
```python
import logging
logger = logging.getLogger(__name__)

# Logs stored in:
# - Backend: stdout (captured by CloudWatch in Lambda)
# - Local: console output
```

## Cost Estimation

**Assumptions**: 150 devices, 1 scan/hour, 10 critical alerts/day

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| DynamoDB | 720 scans × 150 devices = 108K writes, 10K reads | ~$13 |
| SNS | 300 notifications/month | <$1 |
| EventBridge | 300 events/month | Free tier |
| Lambda | 720 invocations, 512MB, 30s avg | ~$2 |
| **Total** | | **~$16/month** |

## Troubleshooting

### DynamoDB Connection Issues
```bash
# Test DynamoDB access
aws dynamodb describe-table --table-name AutoOps-Vulnerabilities

# Check IAM permissions
aws sts get-caller-identity
```

### SNS Not Sending
```bash
# Verify topic exists
aws sns list-topics

# Check subscriptions
aws sns list-subscriptions-by-topic --topic-arn YOUR_TOPIC_ARN

# Test publish
aws sns publish --topic-arn YOUR_TOPIC_ARN --message "Test alert"
```

### EventBridge Events Not Triggering
```bash
# List rules
aws events list-rules

# Check targets
aws events list-targets-by-rule --rule AutoOps-CriticalVulnerabilities
```

## Security Best Practices

1. **Encrypt DynamoDB**: Enable encryption at rest
2. **SNS Access Control**: Use topic policies to restrict publishers
3. **IAM Least Privilege**: Only grant required permissions
4. **Secrets Management**: Use AWS Secrets Manager for API keys
5. **VPC Endpoints**: Use for DynamoDB/SNS in private subnets

## Next Steps

1. ✅ Set up AWS credentials
2. ✅ Create DynamoDB table
3. ✅ Create SNS topic and subscribe
4. ✅ Configure environment variables
5. ✅ Test with local dev server
6. ⬜ Deploy to AWS Lambda (optional)
7. ⬜ Set up CloudWatch alarms
8. ⬜ Configure automated patch deployment

## Support

For issues or questions:
- Check CloudWatch Logs for errors
- Review IAM permissions
- Verify network connectivity to AWS
- Check `.env` file configuration
