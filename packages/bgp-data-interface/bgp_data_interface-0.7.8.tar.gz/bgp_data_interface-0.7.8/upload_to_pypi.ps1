# upload_to_pypi script
# This script updates the version in pyproject.toml,
# commits and pushes to gitlab,
# builds a new distribution,
# and uploads it to PyPI
#
# Usage: .\update_new_version.ps1 -NewVersion "0.7.5"
#

# Updates the new version in pyproject.toml
param (
    [string]$NewVersion
)

if (-not $NewVersion) {
    Write-Error "You must provide a version e.g. -NewVersion `"0.1.2`""
    exit 1
}

$tomlPath = "pyproject.toml"
$content = Get-Content $tomlPath

# Replace the line that starts with 'version ='
$content = $content | ForEach-Object {
    if ($_ -match '^\s*version\s*=\s*".*"') {
        "version = `"$NewVersion`""
    } else {
        $_
    }
}

# Write the updated content back to the file
Set-Content -Path $tomlPath -Value $content
Write-Output "Updated version in $tomlPath to $NewVersion "






# Commit and push to git
git add .
git commit -m "Update version to $NewVersion"
git push origin main






# Delete old distributions
if (Test-Path "dist") {
    Remove-Item -Path "dist" -Recurse
}

# Build a new distribution
py -m build

# Ensure the PyPI token is set in the environment variable
$token = Get-Content "../pypi_token.txt" | Select-Object -First 1
$env:TWINE_PASSWORD = $token

# Upload the new distribution to PyPI
py -m twine upload -u __token__ dist/*
