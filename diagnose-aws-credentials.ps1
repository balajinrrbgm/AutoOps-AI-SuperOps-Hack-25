# AWS Credentials Diagnostic Tool
# Identifies issues with AWS credentials

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AWS Credentials Troubleshooting" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Check Environment Variables
Write-Host "`n[1] Checking Environment Variables..." -ForegroundColor Yellow
$envAccessKey = $env:AWS_ACCESS_KEY_ID
$envSessionToken = $env:AWS_SESSION_TOKEN

if ($envAccessKey) {
    $maskedKey = $envAccessKey.Substring(0, 4) + "****" + $envAccessKey.Substring($envAccessKey.Length - 4)
    Write-Host "   AWS_ACCESS_KEY_ID: $maskedKey" -ForegroundColor White
    
    if ($envAccessKey.StartsWith("ASIA")) {
        Write-Host "   Type: TEMPORARY credentials (expires in hours)" -ForegroundColor Yellow
        
        if (!$envSessionToken) {
            Write-Host "   ERROR: Missing AWS_SESSION_TOKEN!" -ForegroundColor Red
            Write-Host "   Temporary credentials MUST have session token" -ForegroundColor Red
        }
    } elseif ($envAccessKey.StartsWith("AKIA")) {
        Write-Host "   Type: PERMANENT credentials (long-term)" -ForegroundColor Green
    }
} else {
    Write-Host "   No AWS_ACCESS_KEY_ID in environment" -ForegroundColor Gray
}

if ($envSessionToken) {
    Write-Host "   AWS_SESSION_TOKEN: Present" -ForegroundColor White
}

# Check Credentials File
Write-Host "`n[2] Checking Credentials File..." -ForegroundColor Yellow
$credsFile = "$env:USERPROFILE\.aws\credentials"
if (Test-Path $credsFile) {
    Write-Host "   File: $credsFile" -ForegroundColor White
    try {
        $content = Get-Content $credsFile -Raw
        if ($content -match "aws_access_key_id\s*=\s*(AKIA\w+|ASIA\w+)") {
            $fileKey = $matches[1]
            $maskedFileKey = $fileKey.Substring(0, 4) + "****" + $fileKey.Substring($fileKey.Length - 4)
            Write-Host "   Access Key: $maskedFileKey" -ForegroundColor White
            
            if ($fileKey.StartsWith("ASIA") -and $content -notmatch "aws_session_token") {
                Write-Host "   ERROR: Temporary credentials missing session token!" -ForegroundColor Red
            }
        }
    } catch {
        Write-Host "   ERROR: Cannot read file (corrupted)" -ForegroundColor Red
    }
} else {
    Write-Host "   File does not exist" -ForegroundColor Gray
}

# Test AWS Connection
Write-Host "`n[3] Testing AWS Connection..." -ForegroundColor Yellow
try {
    $result = aws sts get-caller-identity --output json 2>&1
    if ($LASTEXITCODE -eq 0) {
        $identity = $result | ConvertFrom-Json
        Write-Host "   SUCCESS!" -ForegroundColor Green
        Write-Host "   Account: $($identity.Account)" -ForegroundColor White
        Write-Host "   UserId: $($identity.UserId)" -ForegroundColor White
    } else {
        Write-Host "   FAILED" -ForegroundColor Red
        Write-Host "   $result" -ForegroundColor Red
        
        if ($result -match "InvalidClientTokenId") {
            Write-Host "`n   Reason: Access Key ID is invalid or deleted" -ForegroundColor Yellow
        } elseif ($result -match "ExpiredToken") {
            Write-Host "`n   Reason: Temporary credentials expired" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   AWS CLI error: $_" -ForegroundColor Yellow
}

# Recommendations
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "SOLUTIONS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`nYour credentials are INVALID or EXPIRED. Here's how to fix:" -ForegroundColor Yellow

Write-Host "`nSOLUTION 1: Create IAM User Access Key (Recommended)" -ForegroundColor Green
Write-Host "  1. Go to: https://console.aws.amazon.com/iam/home#/users" -ForegroundColor White
Write-Host "  2. Select your IAM user" -ForegroundColor White
Write-Host "  3. Security credentials tab" -ForegroundColor White
Write-Host "  4. Create access key -> CLI/SDK" -ForegroundColor White
Write-Host "  5. Download CSV or copy both keys" -ForegroundColor White
Write-Host "  6. Keys will start with AKIA (permanent, no session token needed)" -ForegroundColor White

Write-Host "`nSOLUTION 2: Use AWS SSO (If configured)" -ForegroundColor Green
Write-Host "  Run: aws sso login" -ForegroundColor White
Write-Host "  (Opens browser for authentication)" -ForegroundColor White

Write-Host "`nSOLUTION 3: Get from AWS CloudShell" -ForegroundColor Green
Write-Host "  1. Open AWS Console -> CloudShell" -ForegroundColor White
Write-Host "  2. Run: cat ~/.aws/credentials" -ForegroundColor White
Write-Host "  3. Copy the credentials shown" -ForegroundColor White

# Clean environment
Write-Host "`n================================================================================" -ForegroundColor Cyan
if ($envAccessKey) {
    $clean = Read-Host "`nClear expired credentials from environment? (y/n)"
    if ($clean -eq 'y') {
        $env:AWS_ACCESS_KEY_ID = $null
        $env:AWS_SECRET_ACCESS_KEY = $null
        $env:AWS_SESSION_TOKEN = $null
        Write-Host "Environment variables cleared for this session" -ForegroundColor Green
    }
}

Write-Host "`nNext: After getting fresh credentials, run:" -ForegroundColor Yellow
Write-Host "  .\setup-aws-credentials.ps1" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
