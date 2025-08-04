# PowerShell version of PyPI deployment script

Write-Host "🚀 AceFlow MCP Server - Deploy to PyPI" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check if we're in the correct directory
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "❌ Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Pre-deployment checklist:" -ForegroundColor Yellow
Write-Host "1. ✅ PyPI account registered?"
Write-Host "2. ✅ API Token obtained?"
Write-Host "3. ✅ Code functionality tested?"
Write-Host ""

$proceed = Read-Host "Confirm all above completed, continue deployment? (y/N)"

if ($proceed -notmatch "^[Yy]$") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🚀 Starting deployment process..." -ForegroundColor Green

# Step 1: Environment preparation
Write-Host "📦 Step 1: Preparing environment..." -ForegroundColor Cyan
Write-Host "🐍 Checking Python version..."
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not properly installed" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Installing/updating required packages..."
pip install --upgrade pip build twine pytest wheel setuptools
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 2: Configure authentication (if not configured)
if (-not (Test-Path "~/.pypirc")) {
    Write-Host "🔐 Step 2: Configuring PyPI authentication..." -ForegroundColor Cyan
    $apiToken = Read-Host "Please enter your PyPI API Token (pypi-xxxxxxx)"
    
    if ([string]::IsNullOrEmpty($apiToken)) {
        Write-Host "❌ API Token cannot be empty" -ForegroundColor Red
        exit 1
    }
    
    $pypircContent = @"
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = $apiToken
"@
    
    $pypircContent | Out-File -FilePath "~/.pypirc" -Encoding UTF8
    Write-Host "✅ PyPI authentication configured!" -ForegroundColor Green
} else {
    Write-Host "✅ PyPI authentication already configured" -ForegroundColor Green
}

# Step 3: Run tests
Write-Host "🧪 Step 3: Running tests..." -ForegroundColor Cyan
python -m pytest tests/
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed, deployment aborted" -ForegroundColor Red
    exit 1
}

# Step 4: Build and publish
Write-Host "📦 Step 4: Building and publishing..." -ForegroundColor Cyan

# Clean previous builds
Write-Host "🧹 Cleaning previous build files..."
Remove-Item -Path "dist", "build", "*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue

# Build package
Write-Host "📦 Building Python package..."
python -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Package build failed" -ForegroundColor Red
    exit 1
}

# Verify package
Write-Host "🔍 Verifying package integrity..."
python -m twine check dist/*
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Package verification failed" -ForegroundColor Red
    exit 1
}

# Show build results
Write-Host ""
Write-Host "📦 Build completed! Found the following files:" -ForegroundColor Green
Get-ChildItem dist/

Write-Host ""
$confirm = Read-Host "Confirm publish to PyPI? (y/N)"

if ($confirm -match "^[Yy]$") {
    Write-Host "🚀 Publishing to PyPI..." -ForegroundColor Green
    python -m twine upload dist/*
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Publication successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Next steps:" -ForegroundColor Yellow
        Write-Host "1. Visit https://pypi.org/project/aceflow-mcp-server/ to confirm successful publication"
        Write-Host "2. Test installation: pip install aceflow-mcp-server"
        Write-Host "3. Test uvx: uvx aceflow-mcp-server"
        Write-Host "4. Update documentation and README installation instructions"
    } else {
        Write-Host "❌ Publication failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "📦 Build completed, package ready in dist/ directory" -ForegroundColor Green
    Write-Host "💡 Manual publish command: twine upload dist/*" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Deployment process completed!" -ForegroundColor Green