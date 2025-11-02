# AWS Credentials Setup Script
# Run this in PowerShell to fix the corrupted credentials file

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "AWS Credentials Setup for AutoOps AI" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Check if .aws directory exists
$awsDir = "$env:USERPROFILE\.aws"
if (!(Test-Path $awsDir)) {
    Write-Host "`nCreating .aws directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $awsDir -Force | Out-Null
}

# Backup corrupted credentials if exists
$credsFile = "$awsDir\credentials"
if (Test-Path $credsFile) {
    Write-Host "`nBacking up existing credentials to credentials.backup..." -ForegroundColor Yellow
    Copy-Item $credsFile "$awsDir\credentials.backup" -Force
    Remove-Item $credsFile -Force
}

Write-Host "`n" + "=" * 80 -ForegroundColor Green
Write-Host "Please enter your AWS credentials:" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green

# Prompt for credentials
$accessKey = Read-Host -Prompt "`nAWS Access Key ID"
$secretKey = Read-Host -Prompt "AWS Secret Access Key" -AsSecureString
$secretKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretKey))

# Ask if using temporary credentials
$useTemp = Read-Host "`nAre you using temporary credentials (SSO)? (y/n)"

$sessionToken = ""
if ($useTemp -eq 'y' -or $useTemp -eq 'Y') {
    $sessionTokenSecure = Read-Host -Prompt "AWS Session Token" -AsSecureString
    $sessionToken = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sessionTokenSecure))
}

# Create credentials file
Write-Host "`nCreating credentials file..." -ForegroundColor Yellow

$credentialsContent = @"
[default]
aws_access_key_id = $accessKey
aws_secret_access_key = $secretKeyPlain
"@

if ($sessionToken) {
    $credentialsContent += "`naws_session_token = $sessionToken"
}

$credentialsContent | Out-File -FilePath $credsFile -Encoding ASCII -Force

# Create config file
Write-Host "Creating config file..." -ForegroundColor Yellow

$configFile = "$awsDir\config"
$configContent = @"
[default]
region = us-east-2
output = json
"@

$configContent | Out-File -FilePath $configFile -Encoding ASCII -Force

# Test credentials
Write-Host "`n" + "=" * 80 -ForegroundColor Green
Write-Host "Testing AWS credentials..." -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green

try {
    $result = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ SUCCESS! AWS credentials are working!" -ForegroundColor Green
        Write-Host $result
        
        Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "=" * 80 -ForegroundColor Cyan
        Write-Host "1. Deploy infrastructure:" -ForegroundColor White
        Write-Host "   cd backend" -ForegroundColor Gray
        Write-Host "   python ..\infrastructure\deploy_infrastructure.py" -ForegroundColor Gray
        Write-Host "`n2. Or use AWS CDK:" -ForegroundColor White
        Write-Host "   cd infrastructure" -ForegroundColor Gray
        Write-Host "   cdk bootstrap" -ForegroundColor Gray
        Write-Host "   cdk deploy" -ForegroundColor Gray
        Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ Error: Credentials test failed" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        Write-Host "`nPlease check your credentials and try again." -ForegroundColor Yellow
    }
} catch {
    Write-Host "`n⚠️  Could not test credentials (aws CLI may not be installed)" -ForegroundColor Yellow
    Write-Host "Credentials file created. Try deploying manually." -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
