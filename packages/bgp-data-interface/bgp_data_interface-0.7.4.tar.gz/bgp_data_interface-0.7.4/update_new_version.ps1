
# Delete old distributions
Remove-Item -Path "dist" -Recurse

# Build a new distribution
py -m build

# Upload the new distribution to PyPI
$env:TWINE_PASSWORD = "pypi-AgEIcHlwaS5vcmcCJDVkZTBmMjcxLTYxZWEtNDJiMC1hYzZhLWVmNzM4MzIyNTc5MQACKlszLCI1MDdiOThkNi05ZGFhLTQ0NzEtOTk1NS1iN2ZhMzQ2MTU1YmQiXQAABiDaRLZ0_UnvgNP37qnnqrs2W0xORMwWPzF6kBDuhCP8eg"

py -m twine upload -u __token__ dist/*
