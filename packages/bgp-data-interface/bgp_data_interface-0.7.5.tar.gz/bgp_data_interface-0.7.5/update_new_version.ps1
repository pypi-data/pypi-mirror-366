
# Delete old distributions
Remove-Item -Path "dist" -Recurse

# Build a new distribution
py -m build

# Upload the new distribution to PyPI
$token = Get-Content "pypi_token.txt" | Select-Object -First 1
$env:TWINE_PASSWORD = $token

py -m twine upload -u __token__ dist/*
