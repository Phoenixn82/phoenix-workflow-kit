# cloakscrape.ps1 - PowerShell wrapper around cloakscrape.py
# Routes to the dedicated CloakBrowser venv so other Python installs stay clean.
#
# Examples:
#   .\cloakscrape.ps1 https://target.com
#   .\cloakscrape.ps1 https://job-board.com --humanize --wait-for ".job-title"
#   .\cloakscrape.ps1 https://logged-in-site.com --profile linkedin
#   .\cloakscrape.ps1 https://target.com --out C:\tmp\page.html

$venvPython = 'C:\Users\<you>\external-tools\cloakbrowser-venv\Scripts\python.exe'
$script     = 'C:\Users\<you>\.claude\scripts\cloakscrape.py'

if (-not (Test-Path $venvPython)) {
  Write-Error "CloakBrowser venv missing at $venvPython. Reinstall: see project_cloakbrowser_install_2026_05_26.md"
  exit 1
}

& $venvPython $script @args
