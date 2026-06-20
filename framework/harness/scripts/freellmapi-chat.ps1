[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Prompt,

  [ValidateSet('auto', 'code', 'agent', 'fast', 'long', 'reason', 'creative', 'multilingual', 'cheap')]
  [string]$Task = 'auto',

  [string]$Model,
  [string]$System,
  [int]$MaxTokens = 1200,
  [double]$Temperature = 0.2,
  [switch]$Raw
)

$ErrorActionPreference = 'Stop'

$base = if ($env:FREELLMAPI_BASE_URL) {
  $env:FREELLMAPI_BASE_URL.TrimEnd('/')
} else {
  'http://127.0.0.1:3001'
}

$taskModels = @{
  auto = 'auto'
  code = 'qwen/qwen3-coder-480b-a35b-instruct'
  agent = 'moonshotai/kimi-k2.6'
  fast = 'openai/gpt-oss-120b'
  long = 'gemini-2.5-flash'
  reason = 'magistral-medium-latest'
  creative = 'minimaxai/minimax-m2.7'
  multilingual = 'mistral-large-latest'
  cheap = 'gemini-2.5-flash-lite'
}

$chosenModel = if ($Model) { $Model } else { $taskModels[$Task] }

try {
  $keyResponse = Invoke-RestMethod -Uri "$base/api/settings/api-key" -Method Get
  $unifiedKey = $keyResponse.apiKey
} catch {
  throw "FreeLLMAPI is not reachable at $base. Start it with: node server/dist/index.js"
}

if (-not $unifiedKey) {
  throw 'FreeLLMAPI did not return a unified API key.'
}

$messages = @()
if ($System) {
  $messages += @{ role = 'system'; content = $System }
}
$messages += @{ role = 'user'; content = $Prompt }

$payload = @{
  model = $chosenModel
  messages = $messages
  max_tokens = $MaxTokens
  temperature = $Temperature
}

$body = $payload | ConvertTo-Json -Depth 12

try {
  $response = Invoke-WebRequest `
    -Uri "$base/v1/chat/completions" `
    -Method Post `
    -UseBasicParsing `
    -Headers @{ Authorization = "Bearer $unifiedKey" } `
    -ContentType 'application/json' `
    -Body $body
} catch {
  $detail = $_.Exception.Message
  if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
    $detail = $_.ErrorDetails.Message
  }
  throw "FreeLLMAPI request failed: $detail"
}

if ($Raw) {
  $response.Content
  return
}

$json = $response.Content | ConvertFrom-Json
$routedVia = $response.Headers['X-Routed-Via']
if ($routedVia -is [array]) {
  $routedVia = $routedVia -join ','
}

[pscustomobject]@{
  task = $Task
  requestedModel = $chosenModel
  routedVia = $routedVia
  content = $json.choices[0].message.content
}
