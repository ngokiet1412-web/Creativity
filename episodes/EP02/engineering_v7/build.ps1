param(
    [Parameter(Mandatory)] [string] $Out,
    [Parameter(Mandatory)] [string] $Capy,
    [Parameter(Mandatory)] [string] $FFmpeg,
    [string] $Blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe',
    [string] $Matlab = 'C:\Program Files\MATLAB\R2026b\bin\matlab.exe',
    [string] $BaseBlend,
    [switch] $IncludeNX,
    [switch] $PreviewOnly
)

$ErrorActionPreference = 'Stop'
$Out = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Out)
$Capy = (Resolve-Path -LiteralPath $Capy).Path
$FFmpeg = (Resolve-Path -LiteralPath $FFmpeg).Path
$Blender = (Resolve-Path -LiteralPath $Blender).Path
$Matlab = (Resolve-Path -LiteralPath $Matlab).Path
New-Item -ItemType Directory -Force $Out | Out-Null

function Invoke-Program {
    param([string] $Executable, [string[]] $Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Executable exited with code $LASTEXITCODE"
    }
}

$env:PYTHONDONTWRITEBYTECODE = '1'
$env:CAPY_V7_SCRIPT = $PSScriptRoot
$env:CAPY_V7_OUT = $Out
Invoke-Program $Matlab @('-wait','-batch',
    "addpath(getenv('CAPY_V7_SCRIPT')); export_motion(getenv('CAPY_V7_OUT'));")

if ($IncludeNX) {
    $env:CAPY_NX_CALIBRATION_OUT = $Out
    $journal = Join-Path $PSScriptRoot 'nx_calibration.vb'
    Push-Location $Out
    try {
        Invoke-Program "$env:UGII_BASE_DIR\NXBIN\run_journal.exe" @($journal)
    } finally {
        Pop-Location
    }
    Invoke-Program $Blender @('-b','--factory-startup','--python-exit-code','7','--python',
        (Join-Path $PSScriptRoot 'render_scene.py'),'--','--out',$Out,'--nx-units')
}

if (!$BaseBlend) {
    $seed = Join-Path $Out 'base'
    Invoke-Program $Blender @('-b','--factory-startup','--python-exit-code','7','--python',
        (Join-Path $PSScriptRoot '../blender_pc200/build_shot.py'),'--','--out',$seed)
    $BaseBlend = Join-Path $seed 'EP02_PC200_BLENDER_DRAFT.blend'
}
$BaseBlend = (Resolve-Path -LiteralPath $BaseBlend).Path
Invoke-Program $Blender @('-b',$BaseBlend,'--python-exit-code','7','--python',
    (Join-Path $PSScriptRoot 'render_scene.py'),'--','--out',$Out,'--capy',$Capy,
    '--preview','52','118','272','464')
if ($PreviewOnly) { return }

$frames = Join-Path $Out 'frames'
New-Item -ItemType Directory -Force $frames | Out-Null
Invoke-Program $Blender @('-b',(Join-Path $Out 'EP02_hero.blend'),'-o',
    (Join-Path $frames 'hr_'),'-F','PNG','-a')
$video = Join-Path $Out 'EP02_V7_HYDRAULIC_REVEAL_DRAFT.mp4'
Invoke-Program $FFmpeg @('-hide_banner','-v','error','-y','-framerate','30','-start_number','1',
    '-i',(Join-Path $frames 'hr_%04d.png'),'-frames:v','510','-c:v','libx264','-crf','17',
    '-pix_fmt','yuv420p','-movflags','+faststart',$video)
Invoke-Program $FFmpeg @('-hide_banner','-v','error','-xerror','-i',$video,'-f','null','NUL')
