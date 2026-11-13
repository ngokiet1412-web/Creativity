# Verify the approved EP01 package before copying anything into the checkout.
[CmdletBinding(DefaultParameterSetName = 'Verify')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Zip')][string]$ZipPath,
    [Parameter(Mandatory, ParameterSetName = 'Extracted')][string]$ExtractedPath,
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$expectedZip = 'db936bc60b1c173cce32491c43f9725ac9cedc4b67550209f1184508d83d4be5'
$expectedManifest = 'e0af9dc3ff81c4877b4341903fcffebbf521951b4a319eb6f6109bd6edd1f7ff'
$manifestTarget = Join-Path $RepoRoot 'assets/ASSET_SHA256.json'

function Assert-Hash($Path, $Hash) {
    if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash -ne $Hash) {
        throw "SHA-256 mismatch: $Path"
    }
}

function Assert-Asset($Path, $Entry) {
    if ((Get-Item -LiteralPath $Path).Length -ne $Entry.bytes) {
        throw "Size mismatch: $Path"
    }
    Assert-Hash $Path $Entry.sha256
}

if (!(Test-Path -LiteralPath (Join-Path $RepoRoot '.git'))) {
    throw "RepoRoot is not a git worktree: $RepoRoot"
}

$staging = $null
try {
    if ($ZipPath) {
        Assert-Hash $ZipPath $expectedZip
        $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
        $staging = Join-Path $tempRoot ("capybk_assets_" + [Guid]::NewGuid().ToString('N'))
        Expand-Archive -LiteralPath $ZipPath -DestinationPath $staging
        $ExtractedPath = $staging
    }

    $manifestPath = $manifestTarget
    if ($ExtractedPath) { $manifestPath = Join-Path $ExtractedPath 'ASSET_SHA256.json' }
    Assert-Hash $manifestPath $expectedManifest
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $pending = @()
    foreach ($entry in $manifest) {
        $relative = $entry.destination
        if ($relative -eq 'scripts/build_capy_bk_ep01_animatic_PROTOTYPE.py') {
            # main already has a different revision of this script.
            $relative = 'assets/prototypes/source/build_capy_bk_ep01_animatic_PROTOTYPE.py'
        }
        $target = Join-Path $RepoRoot $relative
        if ($ExtractedPath) {
            $source = Join-Path $ExtractedPath $entry.destination
            Assert-Asset $source $entry
        }
        if ((Test-Path -LiteralPath $target) -or !$ExtractedPath) {
            Assert-Asset $target $entry
        } else {
            $pending += [pscustomobject]@{ Source = $source; Target = $target }
        }
        Write-Host "Verified: $relative"
    }

    $gif = Join-Path $RepoRoot 'assets/approved/capy_bk_master.gif'
    if ($ExtractedPath) { $gif = Join-Path $ExtractedPath 'assets/approved/capy_bk_master.gif' }
    $stream = [IO.File]::OpenRead((Resolve-Path -LiteralPath $gif).Path)
    try {
        $header = [byte[]]::new(6)
        $count = $stream.Read($header, 0, $header.Length)
        if ($count -ne 6 -or [Text.Encoding]::ASCII.GetString($header) -cne 'GIF89a') {
            throw 'Canonical mascot does not have the expected GIF89a signature.'
        }
    } finally { $stream.Dispose() }

    if ($ExtractedPath) {
        if (Test-Path -LiteralPath $manifestTarget) {
            Assert-Hash $manifestTarget $expectedManifest
        } else {
            $pending += [pscustomobject]@{ Source = $manifestPath; Target = $manifestTarget }
        }
        foreach ($item in $pending) {
            New-Item -ItemType Directory -Path (Split-Path -Parent $item.Target) -Force | Out-Null
            # The two-argument overload refuses an existing destination.
            [IO.File]::Copy((Resolve-Path -LiteralPath $item.Source).Path, $item.Target)
        }
    }
    Write-Host "Verified $($manifest.Count) files and GIF89a signature. Copied $($pending.Count) files."
} finally {
    if ($staging -and (Test-Path -LiteralPath $staging)) {
        $resolved = (Resolve-Path -LiteralPath $staging).Path
        if ((Split-Path -Parent $resolved) -eq $tempRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) -and
            (Split-Path -Leaf $resolved) -match '^capybk_assets_[0-9a-f]{32}$') {
            Remove-Item -LiteralPath $resolved -Recurse -Force
        }
    }
}
