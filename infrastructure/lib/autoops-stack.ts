import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as stepfunctions from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as opensearch from 'aws-cdk-lib/aws-opensearchservice';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export class AutoOpsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ============================================
    // DynamoDB Tables
    // ============================================

    // Policies Table
    const policiesTable = new dynamodb.Table(this, 'PoliciesTable', {
      partitionKey: { name: 'policyId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
    });

    // Actions Audit Table
    const actionsTable = new dynamodb.Table(this, 'ActionsTable', {
      partitionKey: { name: 'actionId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
    });

    // Execution Logs Table
    const executionLogsTable = new dynamodb.Table(this, 'ExecutionLogsTable', {
      partitionKey: { name: 'executionId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      timeToLiveAttribute: 'ttl',
    });

    // ============================================
    // S3 Buckets
    // ============================================

    // Playbooks Repository
    const playbooksBucket = new s3.Bucket(this, 'PlaybooksBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Logs and Reports
    const logsBucket = new s3.Bucket(this, 'LogsBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      lifecycleRules: [
        {
          expiration: cdk.Duration.days(90),
          transitions: [
            {
              storageClass: s3.StorageClass.INFREQUENT_ACCESS,
              transitionAfter: cdk.Duration.days(30),
            },
          ],
        },
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // ============================================
    // Secrets Manager
    // ============================================

    const superopsSecret = new secretsmanager.Secret(this, 'SuperOpsCredentials', {
      secretName: 'autoops/superops-credentials',
      description: 'SuperOps.ai API credentials',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ subdomain: '' }),
        generateStringKey: 'apiToken',
      },
    });

    const slackSecret = new secretsmanager.Secret(this, 'SlackCredentials', {
      secretName: 'autoops/slack-credentials',
      description: 'Slack Bot credentials',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ signingSecret: '' }),
        generateStringKey: 'botToken',
      },
    });

    // ============================================
    // Lambda Layer for Dependencies
    // ============================================

    const dependenciesLayer = new lambda.LayerVersion(this, 'DependenciesLayer', {
      code: lambda.Code.fromAsset('../backend/layers/dependencies'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
      description: 'Common dependencies for AutoOps AI',
    });

    // ============================================
    // Lambda Functions
    // ============================================

    // Common Lambda props
    const commonLambdaProps = {
      runtime: lambda.Runtime.PYTHON_3_11,
      timeout: cdk.Duration.seconds(30),
      layers: [dependenciesLayer],
      environment: {
        POLICIES_TABLE_NAME: policiesTable.tableName,
        ACTIONS_TABLE_NAME: actionsTable.tableName,
        PLAYBOOKS_BUCKET_NAME: playbooksBucket.bucketName,
        BEDROCK_MODEL: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        SUPEROPS_SECRET_ARN: superopsSecret.secretArn,
        SLACK_SECRET_ARN: slackSecret.secretArn,
      },
    };

    // Main API Handler
    const apiHandler = new lambda.Function(this, 'APIHandler', {
      ...commonLambdaProps,
      functionName: 'autoops-api-handler',
      code: lambda.Code.fromAsset('../backend/src'),
      handler: 'handlers.api_handler.lambda_handler',
      timeout: cdk.Duration.seconds(60),
    });

    // AI Risk Assessment Function
    const aiRiskFunction = new lambda.Function(this, 'AIRiskFunction', {
      ...commonLambdaProps,
      functionName: 'autoops-ai-risk-assessment',
      code: lambda.Code.fromAsset('../backend/src'),
      handler: 'handlers.ai_risk_handler.lambda_handler',
      timeout: cdk.Duration.seconds(120),
      memorySize: 1024,
    });

    // AI Agents Service Function (NEW - Multi-Agent AI)
    const aiAgentsFunction = new lambda.Function(this, 'AIAgentsFunction', {
      ...commonLambdaProps,
      functionName: 'autoops-ai-agents',
      code: lambda.Code.fromAsset('../backend/src'),
      handler: 'handlers.ai_agents_handler.lambda_handler',
      timeout: cdk.Duration.seconds(180),
      memorySize: 2048, // CrewAI needs more memory
      environment: {
        ...commonLambdaProps.environment,
        USE_CREWAI: 'true',
      },
    });

    // Patch Deployment Function
    const patchDeployFunction = new lambda.Function(this, 'PatchDeployFunction', {
      ...commonLambdaProps,
      functionName: 'autoops-patch-deploy',
      code: lambda.Code.fromAsset('../backend/src'),
      handler: 'handlers.patch_handler.lambda_handler',
    });

    // Slack Bot Handler
    const slackBotFunction = new lambda.Function(this, 'SlackBotFunction', {
      ...commonLambdaProps,
      functionName: 'autoops-slack-bot',
      code: lambda.Code.fromAsset('../backend/src'),
      handler: 'handlers.slack_handler.lambda_handler',
    });

    // Grant permissions
    policiesTable.grantReadWriteData(apiHandler);
    actionsTable.grantReadWriteData(apiHandler);
    playbooksBucket.grantRead(apiHandler);
    superopsSecret.grantRead(apiHandler);

    aiRiskFunction.addToRolePolicy(new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      resources: ['*'],
    }));

    aiAgentsFunction.addToRolePolicy(new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      resources: ['*'],
    }));

    policiesTable.grantReadWriteData(aiAgentsFunction);
    actionsTable.grantReadWriteData(aiAgentsFunction);

    // ============================================
    // API Gateway
    // ============================================

    const api = new apigateway.RestApi(this, 'AutoOpsAPI', {
      restApiName: 'AutoOps AI API',
      description: 'API for AutoOps AI Platform',
      deployOptions: {
        stageName: 'prod',
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    const apiIntegration = new apigateway.LambdaIntegration(apiHandler);

    api.root.addResource('patches').addResource('status').addMethod('GET', apiIntegration);
    api.root.addResource('alerts').addResource('active').addMethod('GET', apiIntegration);
    api.root.addResource('actions').addResource('recent').addMethod('GET', apiIntegration);

    // AI Agents endpoints
    const aiAgentsIntegration = new apigateway.LambdaIntegration(aiAgentsFunction);
    const aiResource = api.root.addResource('ai').addResource('agents');
    aiResource.addResource('status').addMethod('GET', aiAgentsIntegration);
    aiResource.addResource('prioritize').addMethod('POST', aiAgentsIntegration);
    aiResource.addResource('correlate-alerts').addMethod('POST', aiAgentsIntegration);
    aiResource.addResource('decide-remediation').addMethod('POST', aiAgentsIntegration);
    aiResource.addResource('learn').addMethod('POST', aiAgentsIntegration);

    // ============================================
    // Outputs
    // ============================================

    new cdk.CfnOutput(this, 'APIEndpoint', {
      value: api.url,
      description: 'API Gateway endpoint URL',
    });

    new cdk.CfnOutput(this, 'PoliciesTableName', {
      value: policiesTable.tableName,
    });

    new cdk.CfnOutput(this, 'PlaybooksBucketName', {
      value: playbooksBucket.bucketName,
    });
  }
}
