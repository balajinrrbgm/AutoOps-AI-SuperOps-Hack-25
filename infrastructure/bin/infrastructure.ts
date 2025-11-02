#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AutoOpsStack } from '../lib/autoops-stack';

const app = new cdk.App();

new AutoOpsStack(app, 'AutoOpsAIStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT || '358262661344',
    region: process.env.CDK_DEFAULT_REGION || 'us-east-2',
  },
  description: 'AutoOps AI - Intelligent Patch Management Platform with Multi-Agent AI',
  tags: {
    Project: 'AutoOps-AI',
    Environment: 'Production',
    ManagedBy: 'AWS-CDK',
  },
});
