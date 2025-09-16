# Security Scanner for investByYourself Codebase
# Scans for hardcoded credentials, secrets, and other security issues.

param(
    [string]$Directory = ".",
    [string]$OutputFile = "",
    [switch]$CheckGit
)

Write-Host "🔍 Security Scanner for investByYourself Codebase" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Patterns to detect secrets and credentials
$SecretPatterns = @{
    "password" = "password\s*[=:]\s*['""][^'""]+['""]"
    "secret" = "secret\s*[=:]\s*['""][^'""]+['""]"
    "api_key" = "api_key\s*[=:]\s*['""][^'""]+['""]"
    "token" = "token\s*[=:]\s*['""][^'""]+['""]"
    "credential" = "credential\s*[=:]\s*['""][^'""]+['""]"
    "private_key" = "private_key\s*[=:]\s*['""][^'""]+['""]"
    "access_key" = "access_key\s*[=:]\s*['""][^'""]+['""]"
    "secret_key" = "secret_key\s*[=:]\s*['""][^'""]+['""]"
    "auth" = "auth\s*[=:]\s*['""][^'""]+['""]"
    "login" = "login\s*[=:]\s*['""][^'""]+['""]"
}

# File extensions to scan
$ScannableExtensions = @('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.yml', '.yaml', '.json', '.xml', '.html', '.css', '.sh', '.bash', '.env', '.conf', '.config', '.ini', '.toml')

# Directories to exclude
$ExcludeDirs = @('__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules', '.pytest_cache', '.mypy_cache', 'build', 'dist', 'target')

# Files to exclude
$ExcludeFiles = @('.gitignore', '.env.example', 'docker.env.example', 'env.template', 'docker.env.example', 'test.env', 'test_env_config.env')

$Issues = @()
$TotalFiles = 0
$ScannedFiles = 0

function Test-EnvironmentVariableUsage {
    param([string]$Line)

    $EnvPatterns = @(
        "os\.getenv\(",
        "os\.environ\[",
        "os\.environ\.get\(",
        "load_dotenv\(",
        "\$\{.*\}",
        "process\.env\.",
        "System\.getenv\(",
        "getenv\("
    )

    foreach ($pattern in $EnvPatterns) {
        if ($Line -match $pattern) {
            return $true
        }
    }
    return $false
}

function Scan-File {
    param([string]$FilePath)

    $FileIssues = @()

    try {
        $Content = Get-Content -Path $FilePath -Encoding UTF8 -ErrorAction Stop
        $Lines = $Content -split "`n"

        for ($i = 0; $i -lt $Lines.Count; $i++) {
            $Line = $Lines[$i]
            $LineNumber = $i + 1

            foreach ($PatternName in $SecretPatterns.Keys) {
                $Pattern = $SecretPatterns[$PatternName]
                if ($Line -match $Pattern) {
                    # Check if it's a false positive (environment variable usage)
                    if (Test-EnvironmentVariableUsage -Line $Line) {
                        continue
                    }

                    $FileIssues += [PSCustomObject]@{
                        File = $FilePath
                        Line = $LineNumber
                        Pattern = $PatternName
                        Content = $Line.Trim()
                        Match = $matches[0]
                        Severity = "HIGH"
                    }
                }
            }
        }

        # Check for hardcoded URLs with credentials
        $UrlPattern = "https?://[^:\s]+:[^@\s]+@[^\s]+"
        if ($Content -match $UrlPattern) {
            $FileIssues += [PSCustomObject]@{
                File = $FilePath
                Line = 0
                Pattern = "hardcoded_url_with_credentials"
                Content = $matches[0]
                Match = $matches[0]
                Severity = "CRITICAL"
            }
        }

    } catch {
        $FileIssues += [PSCustomObject]@{
            File = $FilePath
            Line = 0
            Pattern = "file_read_error"
            Content = "Error reading file: $($_.Exception.Message)"
            Match = ""
            Severity = "LOW"
        }
    }

    return $FileIssues
}

function Scan-Directory {
    param([string]$RootDir)

    Write-Host "🔍 Scanning directory: $RootDir" -ForegroundColor Yellow

    $Files = Get-ChildItem -Path $RootDir -Recurse -File | Where-Object {
        $_.Extension -in $ScannableExtensions -and
        $_.Directory.Name -notin $ExcludeDirs -and
        $_.Name -notin $ExcludeFiles
    }

    $TotalFiles = $Files.Count

    foreach ($File in $Files) {
        $TotalFiles++
        $FileIssues = Scan-File -FilePath $File.FullName
        $Issues += $FileIssues
        $ScannedFiles++

        if ($FileIssues.Count -gt 0) {
            Write-Host "⚠️  Found $($FileIssues.Count) issues in $($File.Name)" -ForegroundColor Red
        }
    }

    Write-Host "`n📊 Scan Summary:" -ForegroundColor Green
    Write-Host "  Total files: $TotalFiles" -ForegroundColor White
    Write-Host "  Scanned files: $ScannedFiles" -ForegroundColor White
    Write-Host "  Issues found: $($Issues.Count)" -ForegroundColor White
}

function Generate-Report {
    if ($Issues.Count -eq 0) {
        $Report = "✅ No security issues found! Your codebase appears to be secure."
        Write-Host $Report -ForegroundColor Green
        return $Report
    }

    # Group issues by severity
    $IssuesBySeverity = @{}
    foreach ($Issue in $Issues) {
        $Severity = $Issue.Severity
        if (-not $IssuesBySeverity.ContainsKey($Severity)) {
            $IssuesBySeverity[$Severity] = @()
        }
        $IssuesBySeverity[$Severity] += $Issue
    }

    # Generate report
    $ReportLines = @(
        "🚨 Security Scan Report",
        "=" * 60,
        "Total Issues Found: $($Issues.Count)",
        ""
    )

    foreach ($Severity in @("CRITICAL", "HIGH", "MEDIUM", "LOW")) {
        if ($IssuesBySeverity.ContainsKey($Severity)) {
            $SeverityIssues = $IssuesBySeverity[$Severity]
            $ReportLines += @(
                "🔴 $Severity Issues ($($SeverityIssues.Count)):",
                "-" * 40
            )

            foreach ($Issue in $SeverityIssues) {
                $ReportLines += @(
                    "File: $($Issue.File)",
                    "Line: $($Issue.Line)",
                    "Pattern: $($Issue.Pattern)",
                    "Content: $($Issue.Content)",
                    "Match: $($Issue.Match)",
                    ""
                )
            }
        }
    }

    # Recommendations
    $ReportLines += @(
        "💡 Recommendations:",
        "-" * 40,
        "1. Replace hardcoded credentials with environment variables",
        "2. Use configuration files that are not committed to version control",
        "3. Implement proper secret management (e.g., AWS Secrets Manager, HashiCorp Vault)",
        "4. Use pre-commit hooks to prevent committing secrets",
        "5. Regularly rotate credentials and API keys",
        "6. Consider using GitGuardian or similar tools for continuous monitoring",
        ""
    )

    $Report = $ReportLines -join "`n"

    # Save to file if specified
    if ($OutputFile) {
        $Report | Out-File -FilePath $OutputFile -Encoding UTF8
        Write-Host "📄 Report saved to: $OutputFile" -ForegroundColor Green
    }

    Write-Host $Report -ForegroundColor White
    return $Report
}

function Check-GitHistory {
    Write-Host "`n🔍 Checking git history for potential secrets..." -ForegroundColor Yellow

    try {
        $GitLog = git log --all --full-history -- "*.py" "*.yml" "*.yaml" "*.env*" 2>$null

        if ($LASTEXITCODE -eq 0) {
            $GitIssues = @()

            # Look for potential secrets in commit messages
            $CommitPatterns = @(
                "password.*=.*['""][^'""]+['""]",
                "secret.*=.*['""][^'""]+['""]",
                "api_key.*=.*['""][^'""]+['""]"
            )

            foreach ($Line in $GitLog -split "`n") {
                foreach ($Pattern in $CommitPatterns) {
                    if ($Line -match $Pattern) {
                        $GitIssues += [PSCustomObject]@{
                            Type = "git_history"
                            Content = $Line.Trim()
                            Severity = "MEDIUM"
                        }
                    }
                }
            }

            if ($GitIssues.Count -gt 0) {
                Write-Host "⚠️  Found $($GitIssues.Count) potential issues in git history" -ForegroundColor Red
                $Issues += $GitIssues
            } else {
                Write-Host "✅ No obvious secrets found in git history" -ForegroundColor Green
            }
        } else {
            Write-Host "⚠️  Could not check git history" -ForegroundColor Yellow
        }

    } catch {
        Write-Host "⚠️  Error checking git history: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main execution
try {
    # Scan directory
    Scan-Directory -RootDir $Directory

    # Check git history if requested
    if ($CheckGit) {
        Check-GitHistory
    }

    # Generate report
    Generate-Report

    # Exit with appropriate code
    if ($Issues.Count -gt 0) {
        Write-Host "`n❌ Security scan completed with $($Issues.Count) issues found!" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "`n✅ Security scan completed successfully!" -ForegroundColor Green
        exit 0
    }

} catch {
    Write-Host "❌ Error during security scan: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
