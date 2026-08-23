param(
    [string]$Version = "0.1.0-beta.3"
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$DistRoot = Join-Path $ProjectDir "dist\$Version"
$BuildRoot = Join-Path $ProjectDir "build\$Version"
$OutputDir = Join-Path $DistRoot "DouyinLiveRecorderBeta"
$ReleaseDir = Join-Path $ProjectDir "release"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Missing build environment: $Python"
}

& $Python -m PyInstaller --noconfirm --clean --distpath $DistRoot --workpath $BuildRoot `
    (Join-Path $ProjectDir "DouyinLiveRecorderBeta.spec")
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

$Ffmpeg = Get-Command ffmpeg -ErrorAction Stop
$Ffprobe = Get-Command ffprobe -ErrorAction Stop
$Node = Get-Command node -ErrorAction Stop

New-Item -ItemType Directory -Force -Path (Join-Path $OutputDir "ffmpeg") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $OutputDir "node") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $OutputDir "THIRD_PARTY_LICENSES") | Out-Null
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

Copy-Item -LiteralPath $Ffmpeg.Source -Destination (Join-Path $OutputDir "ffmpeg\ffmpeg.exe") -Force
Copy-Item -LiteralPath $Ffprobe.Source -Destination (Join-Path $OutputDir "ffmpeg\ffprobe.exe") -Force
Copy-Item -LiteralPath $Node.Source -Destination (Join-Path $OutputDir "node\node.exe") -Force
$FfmpegRoot = Split-Path (Split-Path $Ffmpeg.Source -Parent) -Parent
Copy-Item -LiteralPath (Join-Path $FfmpegRoot "LICENSE") -Destination (Join-Path $OutputDir "THIRD_PARTY_LICENSES\FFMPEG-LICENSE.txt") -Force
Copy-Item -LiteralPath (Join-Path $ProjectDir "licenses\NODEJS-LICENSE.txt") -Destination (Join-Path $OutputDir "THIRD_PARTY_LICENSES\NODEJS-LICENSE.txt") -Force
Copy-Item -LiteralPath (Join-Path $ProjectDir "LICENSE") -Destination $OutputDir -Force
Copy-Item -LiteralPath (Join-Path $ProjectDir "README_BETA.vi.md") -Destination $OutputDir -Force
Copy-Item -LiteralPath (Join-Path $ProjectDir "THIRD_PARTY_NOTICES.md") -Destination $OutputDir -Force

$SelfTest = Start-Process -FilePath (Join-Path $OutputDir "DouyinLiveRecorderBeta.exe") -ArgumentList "--self-test" -WorkingDirectory $OutputDir -Wait -PassThru
if ($SelfTest.ExitCode -ne 0) {
    throw "Packaged self-test failed with exit code $($SelfTest.ExitCode)"
}
$SelfTestReport = Get-Content -Raw -LiteralPath (Join-Path $OutputDir "logs\self-test.json") | ConvertFrom-Json
if (-not $SelfTestReport.passed) {
    throw "Packaged self-test report did not pass"
}
if ($SelfTestReport.version -ne $Version) {
    throw "Packaged version $($SelfTestReport.version) does not match requested version $Version"
}
Copy-Item -LiteralPath (Join-Path $OutputDir "logs\self-test.json") `
    -Destination (Join-Path $ReleaseDir "DouyinLiveRecorderBeta-$Version-self-test.json") -Force
Write-Host "Packaged self-test passed"

Remove-Item -LiteralPath (Join-Path $OutputDir "config\config.ini") -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $OutputDir "config\URL_config.ini") -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $OutputDir "logs") -Recurse -Force -ErrorAction SilentlyContinue

$ZipPath = Join-Path $ReleaseDir "DouyinLiveRecorderBeta-$Version-win-x64.zip"
if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
$Compressed = $false
for ($Attempt = 1; $Attempt -le 3; $Attempt++) {
    try {
        if (Test-Path -LiteralPath $ZipPath) {
            Remove-Item -LiteralPath $ZipPath -Force
        }
        Compress-Archive -Path (Join-Path $OutputDir "*") -DestinationPath $ZipPath -CompressionLevel Optimal
        $Compressed = $true
        break
    } catch {
        if ($Attempt -eq 3) {
            throw
        }
        Start-Sleep -Seconds 2
    }
}
if (-not $Compressed) {
    throw "Release archive was not created"
}
$FileHash = Get-FileHash -Algorithm SHA256 -LiteralPath $ZipPath
$ChecksumPath = Join-Path $ReleaseDir "SHA256SUMS.txt"
"$($FileHash.Hash)  $([IO.Path]::GetFileName($ZipPath))" | Set-Content -LiteralPath $ChecksumPath -Encoding ascii
$FileHash | Format-List
