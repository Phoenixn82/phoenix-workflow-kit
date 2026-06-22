# UserPromptSubmit hook — github-publish-nudge
# When the user signals he's making/adding/publishing a GitHub repo PUBLIC,
# inject a reminder so Claude proactively runs the repo doc-standard check.
# Injects context only; never asks permission; silent (no output) when no match.
$ErrorActionPreference = 'SilentlyContinue'
try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }

    $prompt = ''
    try { $prompt = ($raw | ConvertFrom-Json).prompt } catch { $prompt = $raw }
    if (-not $prompt) { exit 0 }

    $patterns = @(
        'mak\w*\s+.{0,25}\bpublic\b',
        '\bgo(?:ing)?\s+public\b',
        '\bpublic(?:ly|ize|ise)?\b.{0,30}\b(?:repo|repository|github)\b',
        '\b(?:repo|repository|github)\b.{0,30}\bpublic\b',
        '\b(?:publish\w*|open[-\s]?sourc\w*)\b.{0,30}\b(?:repo|repository|project|github|it|this)\b',
        '\bnew\s+public\s+repo\b'
    )

    $hit = $false
    foreach ($p in $patterns) { if ($prompt -imatch $p) { $hit = $true; break } }
    if (-not $hit) { exit 0 }

    $msg = 'the user may be taking a GitHub repo public. Per his standing request, proactively offer/run the repo doc-standard check as part of this work: README has an H1 title + a one-line description + a Getting-started (or Install+Run) section + a screenshot-or-code-example + a License section; a LICENSE file exists at root; the repo description equals the README one-liner; 5-8 relevant topics; and run a privacy/secret scan against the publishing denylist. Standard + checklist: _system/second-brain/Reference/github-repo-doc-standard.md . Visually vet any screenshot for private data BEFORE it lands on a public repo. NEVER flip repo visibility yourself - Approach-C: the human does the public flip.'

    $out = @{ hookSpecificOutput = @{ hookEventName = 'UserPromptSubmit'; additionalContext = $msg } } | ConvertTo-Json -Compress -Depth 5
    Write-Output $out
} catch { }
exit 0
