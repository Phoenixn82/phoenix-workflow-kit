<#
  secret.ps1  -  DPAPI-encrypted secret store (per Windows user, CurrentUser scope)

  Secrets are encrypted at rest under C:\Users\<you>\.secrets\<scope>.json
  (each value DPAPI-protected, base64). Only THIS Windows login can decrypt.
  No plaintext ever touches disk. The Claude secret-firewall blocks the AI
  from running the decrypt verbs (get/run/show), so this is a YOU tool.

  Usage:
    secret set         <scope> <name> [value]   # value omitted => secure prompt (no echo)
    secret set-from-env<scope> <name> <ENVVAR> [User|Machine|Process]
    secret get         <scope> <name>           # prints the plaintext (for you)
    secret list        [scope]                  # names only, never values
    secret rm          <scope> <name>
    secret import-json <scope> <jsonfile>       # {"NAME":"value",...} -> encrypted
    secret run         <scope> -- <command...>  # inject scope as env, run child

  Examples:
    pwsh -File secret.ps1 set freellmapi GROQ_API_KEY
    pwsh -File secret.ps1 run example_app -- npm run dev
#>
[CmdletBinding()]
param(
  [Parameter(Position=0)][string]$Action,
  [Parameter(Position=1)][string]$Scope,
  [Parameter(Position=2)][string]$Name,
  [Parameter(Position=3, ValueFromRemainingArguments=$true)][string[]]$Rest
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Security
$DPScope = [System.Security.Cryptography.DataProtectionScope]::CurrentUser
$Root = 'C:\Users\<you>\.secrets'

function Ensure-Root { if (-not (Test-Path $Root)) { New-Item -ItemType Directory -Force -Path $Root | Out-Null } }
function Store-Path([string]$s) { Join-Path $Root ($s + '.json') }

function Protect-Str([string]$plain) {
  $b = [System.Text.Encoding]::UTF8.GetBytes($plain)
  $e = [System.Security.Cryptography.ProtectedData]::Protect($b, $null, $DPScope)
  [Convert]::ToBase64String($e)
}
function Unprotect-Str([string]$b64) {
  $e = [Convert]::FromBase64String($b64)
  $b = [System.Security.Cryptography.ProtectedData]::Unprotect($e, $null, $DPScope)
  [System.Text.Encoding]::UTF8.GetString($b)
}
function Load-Scope([string]$s) {
  $p = Store-Path $s
  if (Test-Path $p) {
    $o = Get-Content $p -Raw | ConvertFrom-Json
    $h = @{}; foreach ($pr in $o.PSObject.Properties) { $h[$pr.Name] = $pr.Value }
    return $h
  }
  return @{}
}
function Save-Scope([string]$s, [hashtable]$h) {
  Ensure-Root
  ($h | ConvertTo-Json -Depth 5) | Out-File -FilePath (Store-Path $s) -Encoding utf8 -Force
}
function Mask([string]$v) { $n=$v.Length; if($n -le 6){('*'*$n)+" ($n)"} else {"$($v.Substring(0,4))...$($v.Substring($n-2)) ($n)"} }

switch ($Action) {
  'set' {
    if (-not $Scope -or -not $Name) { throw "usage: secret set <scope> <name> [value]" }
    if ($Rest -and $Rest.Count -gt 0) { $val = ($Rest -join ' ') }
    else { $sec = Read-Host "Value for $Scope/$Name" -AsSecureString
           $val = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)) }
    $h = Load-Scope $Scope; $h[$Name] = Protect-Str $val; Save-Scope $Scope $h
    Write-Output "stored $Scope/$Name  [$(Mask $val)]"
  }
  'set-from-env' {
    if (-not $Scope -or -not $Name) { throw "usage: secret set-from-env <scope> <name> <ENVVAR> [User|Machine|Process]" }
    $envName = if ($Rest.Count -ge 1) { $Rest[0] } else { $Name }
    $target  = if ($Rest.Count -ge 2) { $Rest[1] } else { 'User' }
    $val = [Environment]::GetEnvironmentVariable($envName, $target)
    if ([string]::IsNullOrEmpty($val)) { throw "env var '$envName' ($target) is empty/missing" }
    $h = Load-Scope $Scope; $h[$Name] = Protect-Str $val; Save-Scope $Scope $h
    Write-Output "stored $Scope/$Name from `$env:$envName ($target)  [$(Mask $val)]"
  }
  'get' {
    if (-not $Scope -or -not $Name) { throw "usage: secret get <scope> <name>" }
    $h = Load-Scope $Scope; if (-not $h.ContainsKey($Name)) { throw "no such secret $Scope/$Name" }
    Write-Output (Unprotect-Str $h[$Name])
  }
  'list' {
    if ($Scope) { (Load-Scope $Scope).Keys | Sort-Object | ForEach-Object { Write-Output $_ } }
    else { if (Test-Path $Root) { Get-ChildItem $Root -Filter *.json | ForEach-Object { Write-Output ($_.BaseName) } } }
  }
  'rm' {
    if (-not $Scope -or -not $Name) { throw "usage: secret rm <scope> <name>" }
    $h = Load-Scope $Scope; if ($h.ContainsKey($Name)) { $h.Remove($Name); Save-Scope $Scope $h; Write-Output "removed $Scope/$Name" } else { Write-Output "not found" }
  }
  'import-json' {
    if (-not $Scope -or -not $Name) { throw "usage: secret import-json <scope> <jsonfile>" }
    $src = Get-Content $Name -Raw | ConvertFrom-Json
    $h = Load-Scope $Scope; $c = 0
    foreach ($pr in $src.PSObject.Properties) { $h[$pr.Name] = Protect-Str ([string]$pr.Value); $c++ }
    Save-Scope $Scope $h
    Write-Output "imported $c secrets into scope '$Scope'"
  }
  'run' {
    if (-not $Scope) { throw "usage: secret run <scope> -- <command...>" }
    $cmd = @(); if ($Name) { $cmd += $Name }; if ($Rest) { $cmd += $Rest }
    $cmd = $cmd | Where-Object { $_ -ne '--' }
    if ($cmd.Count -eq 0) { throw "no command given after scope" }
    $h = Load-Scope $Scope
    foreach ($k in $h.Keys) { Set-Item -Path ("Env:" + $k) -Value (Unprotect-Str $h[$k]) }
    & $cmd[0] @($cmd[1..($cmd.Count-1)])
  }
  default {
    Write-Output "secret.ps1 - DPAPI secret store"
    Write-Output "  set | set-from-env | get | list | rm | import-json | run"
    Write-Output "  store: $Root  (CurrentUser DPAPI, no plaintext at rest)"
  }
}
