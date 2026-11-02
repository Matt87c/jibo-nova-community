param(
    [string] $CheckoutPath = (Join-Path (Get-Location).Path 'jibo-nova-community-public-checkout'),
    [switch] $Publish
)
$ErrorActionPreference = 'Stop'
$source = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$repo = 'Matt87c/jibo-nova-community'
$url = 'https://github.com/Matt87c/jibo-nova-community.git'
$target = [System.IO.Path]::GetFullPath($CheckoutPath)

Write-Host "Public repository: $repo"
Write-Host "Audited source:    $source"
Write-Host "Public checkout:   $target"
Write-Host 'Your private jibo-nova repository will not be cloned, changed, or published.'

if (Test-Path (Join-Path $source '.git')) {
    throw 'Refusing to use a source folder with .git history. Extract a clean source snapshot.'
}
foreach ($tool in @('git','python')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "Required command is missing: $tool"
    }
}
& python (Join-Path $source 'scripts/validate_all.py')
if ($LASTEXITCODE -ne 0) { throw 'Source validation failed. No publishing permitted.' }

if (-not $Publish) {
    Write-Host 'DRY RUN: no clone/copy/commit/push performed.'
    Write-Host 'Review the source, then rerun with -Publish to create a public commit.'
    return
}

if (-not (Test-Path $target)) {
    & git clone $url $target
    if ($LASTEXITCODE -ne 0) { throw 'Cannot clone the public repository.' }
}
$actual = (& git -C $target remote get-url origin)
if ($LASTEXITCODE -ne 0 -or $actual -notmatch '^(https://github\.com/|git@github\.com:)Matt87c/jibo-nova-community(\.git)?$') {
    throw "Refusing: target git origin does not exactly match the public repo: $actual"
}
$branch = (& git -C $target branch --show-current)
if ($branch -ne 'main') { throw "Refusing to modify branch '$branch'. Use main." }
$status = (& git -C $target status --porcelain)
if ($status) { throw 'Refusing: checkout contains uncommitted changes. Review them first.' }

# Robocopy performs a copy (NOT mirror), so unrelated public files are not deleted.
# Exclude the root LICENSE to preserve the one already created on GitHub.
& robocopy $source $target /E /XD .git __pycache__ .pytest_cache release-assets /XF LICENSE | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Robocopy failed with status $LASTEXITCODE" }
# Retain theme-local licenses while preserving the root GitHub license.
Get-ChildItem (Join-Path $source 'themes') -Directory | ForEach-Object {
    $p = Join-Path $_.FullName 'LICENSE'
    if (Test-Path $p) {
        $destDir = Join-Path (Join-Path $target 'themes') $_.Name
        Copy-Item -LiteralPath $p -Destination (Join-Path $destDir 'LICENSE') -Force
    }
}

& git -C $target add -A
if ($LASTEXITCODE -ne 0) { throw 'git add failed' }
& git -C $target diff --cached --check
if ($LASTEXITCODE -ne 0) { throw 'Whitespace conflict detected in staged files' }
Write-Host 'Files staged for public publishing:'
& git -C $target diff --cached --stat
$staged = @(& git -C $target diff --cached --name-only)
if ($staged | Where-Object { $_ -match '(^|/)(\.env|\.git/|secrets?\.json|credentials?\.json)|\.(pem|key|p12|pfx|sqlite|db|log)$' }) {
    throw 'Refusing to commit files with sensitive names/extensions.'
}
if (-not $staged -or $staged.Count -eq 0) {
    Write-Host 'No changes to publish.'
    return
}
& git -C $target commit -m 'Add validated public BEacon themes and release automation'
if ($LASTEXITCODE -ne 0) { throw 'Commit failed' }
& git -C $target push origin main
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
Write-Host 'Public files pushed. Check GitHub Actions before creating a prerelease.'
