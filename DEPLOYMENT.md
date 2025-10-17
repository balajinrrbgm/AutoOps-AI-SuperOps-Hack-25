# AutoOps AI - Deployment Guide

## Prerequisites

### AWS Account Setup
1. AWS Account with admin access
2. AWS CLI configured
3. AWS CDK installed: `npm install -g aws-cdk`
4. Node.js 18+ and Python 3.11+

### External Services
1. **SuperOps.ai Account**
   - API Token
   - Subdomain name
   - Data center location (US/EU)

2. **Slack/Teams** (Optional)
   - Bot token
   - Signing secret
   - Workspace ID

3. **NVD API Key** (Optional but recommended)
   - Register at: https://nvd.nist.gov/developers/request-an-api-key

## Step-by-Step Deployment

### 1. Clone and Setup Repository

```bash
git clone <repository-url>
cd autoops-ai
```

### 2. Configure Environment Variables

Create `.env` file in root directory:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your_account_id

# SuperOps Configuration
SUPEROPS_API_TOKEN=your_superops_token
SUPEROPS_SUBDOMAIN=your_subdomain
SUPEROPS_DATA_CENTER=us  # or eu

# AWS Bedrock
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0

# Slack (Optional)
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your_signing_secret
SLACK_CHANNEL_ID=your_channel_id

# NVD API (Optional)
NVD_API_KEY=your_nvd_api_key
```

### 3. Install Dependencies

#### Backend
```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### Frontend
```bash
cd frontend
npm install
cd ..
```

#### Infrastructure
```bash
cd infrastructure
npm install
cd ..
```

### 4. Build Lambda Layers

```bash
cd backend
mkdir -p layers/dependencies/python
pip install -r requirements.txt -t layers/dependencies/python/
cd ..
```

### 5. Bootstrap CDK (First time only)

```bash
cd infrastructure
cdk bootstrap aws://ACCOUNT_ID/REGION
```

### 6. Deploy Infrastructure

```bash
cd infrastructure
cdk synth  # Verify CloudFormation template
cdk deploy --all --require-approval never
```

This will create:
- Lambda functions
- API Gateway
- DynamoDB tables
- S3 buckets
- Step Functions state machines
- IAM roles and policies
- CloudWatch logs

**Deployment takes approximately 10-15 minutes**

### 7. Store Secrets in AWS Secrets Manager

```bash
aws secretsmanager put-secret-value \
  --secret-id autoops/superops-credentials \
  --secret-string '{
    "apiToken": "your_superops_token",
    "subdomain": "your_subdomain",
    "dataCenter": "us"
  }'

aws secretsmanager put-secret-value \
  --secret-id autoops/slack-credentials \
  --secret-string '{
    "botToken": "xoxb-your-token",
    "signingSecret": "your_signing_secret"
  }'
```

### 8. Upload Initial Playbooks to S3

```bash
aws s3 sync playbooks/ s3://YOUR_PLAYBOOKS_BUCKET/
```

### 9. Initialize Default Policies

```bash
python scripts/init_policies.py
```

### 10. Deploy Frontend to AWS Amplify

#### Option A: Using Amplify Console (Recommended)

1. Go to AWS Amplify Console
2. Choose "Host web app"
3. Connect your Git repository
4. Configure build settings:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm install
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/.next
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

5. Set environment variables in Amplify Console:
   - `NEXT_PUBLIC_API_URL`: Your API Gateway URL
   - `NEXT_PUBLIC_REGION`: Your AWS region

#### Option B: Using Amplify CLI

```bash
cd frontend
amplify init
amplify add hosting
amplify publish
```

### 11. Configure Slack Integration (Optional)

1. Create Slack App at https://api.slack.com/apps
2. Enable following Bot Token Scopes:
   - `chat:write`
   - `commands`
   - `im:write`
3. Install app to workspace
4. Configure Slash Commands:
   - Command: `/autoops`
   - Request URL: `YOUR_API_GATEWAY_URL/slack/commands`
5. Enable Interactive Components:
   - Request URL: `YOUR_API_GATEWAY_URL/slack/interactions`

### 12. Test Deployment

```bash
# Test API endpoint
curl -X GET YOUR_API_GATEWAY_URL/patches/status

# Test frontend
open YOUR_AMPLIFY_URL
```

### 13. Enable Monitoring

CloudWatch dashboards are automatically created. Access them at:
- AWS Console > CloudWatch > Dashboards > AutoOps-Dashboard

### 14. Configure Alerts

```bash
aws sns create-topic --name autoops-alerts
aws sns subscribe \
  --topic-arn arn:aws:sns:REGION:ACCOUNT:autoops-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

## Post-Deployment Configuration

### 1. Configure Patch Policies

```bash
# Edit policies via API or UI
curl -X POST YOUR_API_GATEWAY_URL/policies/update \
  -H "Content-Type: application/json" \
  -d @policies/patch_policy.json
```

### 2. Setup Scheduled Scans

Configure EventBridge rules for automated scanning:

```bash
aws events put-rule \
  --name autoops-daily-scan \
  --schedule-expression "cron(0 2 * * ? *)"
```

### 3. Enable Step Functions Logging

All Step Functions executions are logged to CloudWatch Logs automatically.

## Troubleshooting

### Lambda Function Failures

Check CloudWatch Logs:
```bash
aws logs tail /aws/lambda/autoops-api-handler --follow
```

### API Gateway Errors

Enable detailed CloudWatch logging in API Gateway stage settings.

### Permission Issues

Ensure Lambda execution roles have:
- DynamoDB access
- S3 access
- Bedrock access
- Secrets Manager access

### Frontend Not Loading

1. Check Amplify build logs
2. Verify environment variables
3. Check API Gateway CORS configuration

## Updating the Deployment

### Update Backend

```bash
cd infrastructure
cdk deploy
```

### Update Frontend

```bash
cd frontend
amplify publish
```

### Update Lambda Code Only

```bash
aws lambda update-function-code \
  --function-name autoops-api-handler \
  --zip-file fileb://function.zip
```

## Rollback Procedure

```bash
# Rollback infrastructure
cd infrastructure
cdk deploy --rollback

# Rollback Step Functions execution
aws stepfunctions stop-execution \
  --execution-arn YOUR_EXECUTION_ARN \
  --cause "Manual rollback"
```

## Cost Estimation

Monthly costs for moderate usage (100 devices):

- Lambda: $20-30
- DynamoDB: $10-20
- S3: $5-10
- API Gateway: $10-15
- Bedrock: $100-150
- Step Functions: $10-15
- CloudWatch: $10-20
- Amplify: $5-10

**Total: ~$170-270/month**

## Security Best Practices

1. Enable MFA for AWS account
2. Use least privilege IAM roles
3. Encrypt all data at rest and in transit
4. Rotate secrets regularly
5. Enable CloudTrail for audit logging
6. Use VPC endpoints for AWS services
7. Implement rate limiting on APIs
8. Regular security audits

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [documentation-url]
- Email: support@autoops-ai.com
