#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
require("source-map-support/register");
const cdk = require("aws-cdk-lib");
const autoops_stack_1 = require("../lib/autoops-stack");
const app = new cdk.App();
new autoops_stack_1.AutoOpsStack(app, 'AutoOpsAIStack', {
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiaW5mcmFzdHJ1Y3R1cmUuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyJpbmZyYXN0cnVjdHVyZS50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7QUFDQSx1Q0FBcUM7QUFDckMsbUNBQW1DO0FBQ25DLHdEQUFvRDtBQUVwRCxNQUFNLEdBQUcsR0FBRyxJQUFJLEdBQUcsQ0FBQyxHQUFHLEVBQUUsQ0FBQztBQUUxQixJQUFJLDRCQUFZLENBQUMsR0FBRyxFQUFFLGdCQUFnQixFQUFFO0lBQ3RDLEdBQUcsRUFBRTtRQUNILE9BQU8sRUFBRSxPQUFPLENBQUMsR0FBRyxDQUFDLG1CQUFtQixJQUFJLGNBQWM7UUFDMUQsTUFBTSxFQUFFLE9BQU8sQ0FBQyxHQUFHLENBQUMsa0JBQWtCLElBQUksV0FBVztLQUN0RDtJQUNELFdBQVcsRUFBRSx3RUFBd0U7SUFDckYsSUFBSSxFQUFFO1FBQ0osT0FBTyxFQUFFLFlBQVk7UUFDckIsV0FBVyxFQUFFLFlBQVk7UUFDekIsU0FBUyxFQUFFLFNBQVM7S0FDckI7Q0FDRixDQUFDLENBQUMiLCJzb3VyY2VzQ29udGVudCI6WyIjIS91c3IvYmluL2VudiBub2RlXHJcbmltcG9ydCAnc291cmNlLW1hcC1zdXBwb3J0L3JlZ2lzdGVyJztcclxuaW1wb3J0ICogYXMgY2RrIGZyb20gJ2F3cy1jZGstbGliJztcclxuaW1wb3J0IHsgQXV0b09wc1N0YWNrIH0gZnJvbSAnLi4vbGliL2F1dG9vcHMtc3RhY2snO1xyXG5cclxuY29uc3QgYXBwID0gbmV3IGNkay5BcHAoKTtcclxuXHJcbm5ldyBBdXRvT3BzU3RhY2soYXBwLCAnQXV0b09wc0FJU3RhY2snLCB7XHJcbiAgZW52OiB7XHJcbiAgICBhY2NvdW50OiBwcm9jZXNzLmVudi5DREtfREVGQVVMVF9BQ0NPVU5UIHx8ICczNTgyNjI2NjEzNDQnLFxyXG4gICAgcmVnaW9uOiBwcm9jZXNzLmVudi5DREtfREVGQVVMVF9SRUdJT04gfHwgJ3VzLWVhc3QtMicsXHJcbiAgfSxcclxuICBkZXNjcmlwdGlvbjogJ0F1dG9PcHMgQUkgLSBJbnRlbGxpZ2VudCBQYXRjaCBNYW5hZ2VtZW50IFBsYXRmb3JtIHdpdGggTXVsdGktQWdlbnQgQUknLFxyXG4gIHRhZ3M6IHtcclxuICAgIFByb2plY3Q6ICdBdXRvT3BzLUFJJyxcclxuICAgIEVudmlyb25tZW50OiAnUHJvZHVjdGlvbicsXHJcbiAgICBNYW5hZ2VkQnk6ICdBV1MtQ0RLJyxcclxuICB9LFxyXG59KTtcclxuIl19