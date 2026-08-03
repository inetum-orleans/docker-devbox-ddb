# Run the frozen binary against a throwaway project.
#
# The test suite imports ddb as a package, so nothing else exercises what pyinstaller bundles: two startup bugs
# (missing binaryornot data files, missing cookiecutter VERSION.txt) already shipped unnoticed this way.
param([Parameter(Mandatory = $true)][string]$Binary)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

$ddb = (Resolve-Path $Binary).Path
$project = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
New-Item -ItemType Directory -Path $project | Out-Null

# Reaches api.github.com, which covers the certificate bundle pyinstaller has to ship.
& $ddb --version
& $ddb features

Push-Location $project
try {
	@'
core:
  project:
    name: smoke
  check_updates: false
'@ | Set-Content -Path ddb.yml

	& $ddb configure
	& $ddb config | Out-Null
	& $ddb download

	if (-not (Test-Path .gitignore)) {
		throw "ddb configure did not generate .gitignore"
	}
}
finally {
	Pop-Location
}

Write-Output "Smoke test passed: $ddb"
