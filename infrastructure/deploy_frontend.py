#!/usr/bin/env python3
"""
Deploy Frontend to S3
"""

import boto3
import os
from pathlib import Path
import mimetypes

REGION = 'us-east-2'
ACCOUNT_ID = '358262661344'
BUCKET_NAME = f'autoops-frontend-{ACCOUNT_ID}'
API_ENDPOINT = 'https://83d0wk5nj8.execute-api.us-east-2.amazonaws.com/prod'

print("="*80)
print("AutoOps AI - Frontend Deployment")
print("="*80)
print(f"Bucket: {BUCKET_NAME}")
print(f"API Endpoint: {API_ENDPOINT}")
print("="*80)

s3 = boto3.client('s3', region_name=REGION)

# Create a simple index.html for demo
print("\n[1/2] Creating demo frontend...")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoOps AI - Intelligent Patch Management</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.2em;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        
        .status {{
            padding: 10px 20px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }}
        
        .status.success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status.info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .status.warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
            transition: all 0.3s;
        }}
        
        .btn:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .endpoint-list {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        
        .endpoint {{
            padding: 8px;
            margin: 5px 0;
            background: white;
            border-left: 4px solid #667eea;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        
        .metric {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        
        #response {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AutoOps AI</h1>
            <p class="subtitle">Intelligent Patch Management with Multi-Agent AI</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>System Status</h2>
                <div class="status success">✓ Infrastructure Deployed</div>
                <div class="status success">✓ Lambda Functions Active</div>
                <div class="status success">✓ API Gateway Ready</div>
                <div class="status info">ℹ AI Agents: Simplified Mode</div>
            </div>
            
            <div class="card">
                <h2>Deployment Metrics</h2>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">4</div>
                        <div class="metric-label">DynamoDB Tables</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">3</div>
                        <div class="metric-label">S3 Buckets</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">5</div>
                        <div class="metric-label">AI Agents</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>API Endpoints</h2>
                <div class="endpoint-list">
                    <div class="endpoint">/ai/agents/status</div>
                    <div class="endpoint">/ai/agents/prioritize</div>
                    <div class="endpoint">/ai/agents/correlate-alerts</div>
                    <div class="endpoint">/ai/agents/decide-remediation</div>
                    <div class="endpoint">/ai/agents/learn</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Test AI Agents</h2>
            <button class="btn" onclick="testStatus()">Check Status</button>
            <button class="btn" onclick="testPrioritize()">Test Prioritization</button>
            <button class="btn" onclick="testCorrelate()">Test Alert Correlation</button>
            <div id="response"></div>
        </div>
    </div>
    
    <script>
        const API_BASE = '{API_ENDPOINT}';
        
        async function makeRequest(endpoint, method = 'GET', body = null) {{
            const responseDiv = document.getElementById('response');
            responseDiv.innerHTML = '<div class="loading"></div> Loading...';
            
            try {{
                const options = {{
                    method: method,
                    headers: {{
                        'Content-Type': 'application/json'
                    }}
                }};
                
                if (body) {{
                    options.body = JSON.stringify(body);
                }}
                
                const response = await fetch(API_BASE + endpoint, options);
                const data = await response.json();
                
                responseDiv.innerHTML = JSON.stringify(data, null, 2);
            }} catch (error) {{
                responseDiv.innerHTML = 'Error: ' + error.message;
            }}
        }}
        
        function testStatus() {{
            makeRequest('/ai/agents/status');
        }}
        
        function testPrioritize() {{
            const testData = {{
                patches: [
                    {{
                        id: 'KB5012345',
                        title: 'Security Update for Windows',
                        severity: 'CRITICAL',
                        cvssScore: 9.8,
                        affectedDevices: 150
                    }},
                    {{
                        id: 'KB5012346',
                        title: 'Feature Update',
                        severity: 'LOW',
                        cvssScore: 3.2,
                        affectedDevices: 50
                    }}
                ]
            }};
            makeRequest('/ai/agents/prioritize', 'POST', testData);
        }}
        
        function testCorrelate() {{
            const testData = {{
                alerts: [
                    {{
                        id: 'alert-001',
                        type: 'security',
                        message: 'High CPU usage detected',
                        deviceId: 'server-01'
                    }},
                    {{
                        id: 'alert-002',
                        type: 'security',
                        message: 'Patch installation failed',
                        deviceId: 'server-01'
                    }}
                ]
            }};
            makeRequest('/ai/agents/correlate-alerts', 'POST', testData);
        }}
        
        // Auto-load status on page load
        window.onload = testStatus;
    </script>
</body>
</html>
"""

# Save to temp file
frontend_dir = Path('../frontend/dist')
frontend_dir.mkdir(exist_ok=True, parents=True)
index_path = frontend_dir / 'index.html'

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("  ✓ Created index.html")

# Upload to S3
print("\n[2/2] Uploading to S3...")

try:
    s3.upload_file(
        str(index_path),
        BUCKET_NAME,
        'index.html',
        ExtraArgs={
            'ContentType': 'text/html',
            'CacheControl': 'no-cache'
        }
    )
    print(f"  ✓ Uploaded index.html to {BUCKET_NAME}")
    
    # Get website URL (using bucket website endpoint)
    website_url = f"http://{BUCKET_NAME}.s3-website.{REGION}.amazonaws.com"
    direct_url = f"https://s3.{REGION}.amazonaws.com/{BUCKET_NAME}/index.html"
    
    print("\n" + "="*80)
    print("✅ Frontend deployment complete!")
    print("="*80)
    print(f"\nDirect S3 URL: {direct_url}")
    print(f"API Endpoint: {API_ENDPOINT}")
    print("\nNote: For production, configure CloudFront distribution")
    print("      Or use the AWS Console to access the S3 object directly")
    print("\nFeatures:")
    print("  ✓ Interactive dashboard")
    print("  ✓ Live API testing")
    print("  ✓ System status monitoring")
    print("  ✓ AI agent demonstrations")
    print("="*80)
    
except Exception as e:
    print(f"  ❌ Failed to upload: {e}")
    import traceback
    traceback.print_exc()
