param(
    [Parameter(Mandatory)][string]$Cad,
    [Parameter(Mandatory)][string]$Out,
    [string]$Matlab = 'C:/Program Files/MATLAB/R2026b/bin/matlab.exe',
    [string]$Nx = 'C:/Program Files/Siemens/NX 12.0/NXBIN/run_journal.exe',
    [string]$Mechanical = 'C:/Program Files/ANSYS Inc/v241/aisol/Bin/winx64/AnsysWBU.exe',
    [switch]$MatlabOnly
)
$ErrorActionPreference = 'Stop'
$Cad = (Resolve-Path -LiteralPath $Cad).Path.Replace('\','/')
$Out = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Out).Replace('\','/')
$src = $PSScriptRoot.Replace('\','/')
$mlOut = $Out.Replace("'","''")
$mlCad = $Cad.Replace("'","''")
$mlSrc = $src.Replace("'","''")
Push-Location (Join-Path $PSScriptRoot '../../..')
try {
    & python "$src/prepare_local.py" $Out $Cad
    if ($LASTEXITCODE) { throw 'Preparing the pinned Argon baseline failed' }
    & $Matlab -batch "addpath('$mlOut/baseline/animation'); solve_ep02_v3_motion('$mlOut/baseline')" -logfile "$Out/baseline_execution.log"
    if ($LASTEXITCODE) { throw 'Baseline replay failed' }
    & $Matlab -batch "addpath('$mlSrc'); run_validation('$mlOut','$mlCad')" -logfile "$Out/matlab_execution.log"
    if ($LASTEXITCODE) { throw 'MATLAB validation failed' }
    & python "$src/chamber_geometry.py" "$Out/matlab"
    if ($LASTEXITCODE) { throw 'Chamber geometry validation failed' }
    if ($MatlabOnly) { return }

    $env:CAPY_FIT_INPUT = $Cad
    $env:CAPY_FIT_AUDIT_OUT = "$Out/nx_verify"
    $env:CAPY_VALIDATION_CAD = $Cad
    $env:CAPY_VALIDATION_OUT = $Out
    New-Item -ItemType Directory -Path $env:CAPY_FIT_AUDIT_OUT | Out-Null
    & $Nx "$Cad/nx_fit_check.py" *> "$Out/nx_verify/execution.log"
    if ($LASTEXITCODE) { throw 'NX interference audit failed' }
    & $Nx "$src/nx_extract_pin.py" *> "$Out/ansys/nx_extract.log"
    if ($LASTEXITCODE) { throw 'NX STEP export failed' }
    foreach ($case in @('coarse','medium','fine','sensitivity')) {
        $env:CAPY_PIN_CASE = $case
        $proc = Start-Process -FilePath $Mechanical -WindowStyle Hidden -Wait -PassThru `
            -ArgumentList @('-DSApplet','-AppModeMech','-b','-script',('"' + $src + '/solve_pin_mechanical.py"'))
        if ($proc.ExitCode -or -not (Test-Path -LiteralPath "$Out/ansys/$case/case.json")) {
            throw "Mechanical did not complete case $case. Check its recorded execution error and license status."
        }
    }
    & python "$src/check_pin_results.py" "$Out/ansys"
    if ($LASTEXITCODE) { throw 'Ansys result validation failed' }
}
finally {
    Pop-Location
}
