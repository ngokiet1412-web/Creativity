# CAPY BK: inspect owner-supplied assets ZIP and extract to a local Creativity clone.
# This script DOES NOT commit or push files; have Codex review first.
param(
 [Parameter(Mandatory=$true)][string]$ZipPath,
 [string]$RepoRoot = (Get-Location).Path
)
$ErrorActionPreference = "Stop"
if (!(Test-Path -LiteralPath $ZipPath)) { throw "ZIP missing: $ZipPath" }
if (!(Test-Path -LiteralPath (Join-Path $RepoRoot ".git"))) { throw "RepoRoot is not a git worktree: $RepoRoot" }
$expectedZip = "db936bc60b1c173cce32491c43f9725ac9cedc4b67550209f1184508d83d4be5"
$actualZip = (Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualZip -ne $expectedZip) { throw "ZIP checksum mismatch: $actualZip" }
$staging = Join-Path $env:TEMP ("capybk_assets_" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $staging | Out-Null
try {
 Expand-Archive -LiteralPath $ZipPath -DestinationPath $staging -Force
 $manifest = Get-Content -LiteralPath (Join-Path $staging "ASSET_SHA256.json") -Raw | ConvertFrom-Json
 foreach ($item in $manifest) {
  $relative = $item.destination -replace '/', [IO.Path]::DirectorySeparatorChar
  $src = Join-Path $staging $relative
  $actual = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $item.sha256.ToLowerInvariant()) { throw "File hash mismatch: $relative" }
  $target = Join-Path $RepoRoot $relative
  if (Test-Path -LiteralPath $target) {
   $existing = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
   if ($existing -ne $actual) { throw "Existing asset differs, refusing overwrite: $target" }
   Write-Host "Already present: $relative"
   continue
  }
  New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null
  Copy-Item -LiteralPath $src -Destination $target
  Write-Host "Imported: $relative"
 }
 Write-Host "Verified package and copied approved files. Review 'git status' and create a PR; no commit/push performed."
}
finally { Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction SilentlyContinue }
