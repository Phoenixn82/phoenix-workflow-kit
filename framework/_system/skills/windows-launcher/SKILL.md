---
name: windows-launcher
description: >-
  Use when building or fixing a Windows desktop launcher, startup script, or
  multi-process launch system for any of the user's projects. Covers: killing
  stale processes before start, reliable port management, process hiding (no
  CMD windows), startup health-check detection, browser/Chrome launching by
  window handle, PowerShell window suppression, and desktop shortcut creation
  with custom icons. Trigger phrases: "build a launcher", "launch script",
  "desktop launcher", "desktop icon", "give it an icon on my desktop",
  "make it launchable from the desktop", "the launcher crashes",
  "it won't start", "port already in use", "hide the CMD window",
  "window snapping", "launch Claude + browser + editor",
  "startup script for Windows".
---

# Windows Launcher — Reliable Multi-Process Launch on Windows

Based on patterns learned from Apex (example-scraper) and Project Dashboard launchers. These patterns exist because Windows process management is genuinely hard — apply them upfront to avoid the fix chain.

> **This skill owns Pillar B (launch robustness) of the Reliability Standard** (`RELIABILITY_STANDARD.md` at the root of AI_Projects, AGENTS.md hard rule #12). The reference implementation is **reference-app** — `desktop_app.py` (WebView2, readiness-gated subprocess boot), `reference-app-start.ps1` (browser app-mode, idempotent, "safe to double-click repeatedly"), `launch-windows.ps1` (self-bootstrapping installer). A launcher is not "done" until it satisfies the seven checks below. The goal is the thing the user keeps asking for: **opens every time, on the first double-click, even after a week.**

## The seven non-negotiables (a launcher that works every time)

1. **Idempotent** — check "is the port already up?" before spawning; if it is, attach to the running instance instead of killing + respawning. Safe to double-click repeatedly, no "port already in use," no duplicate processes. (Freeing the port — Problem 1 — is the fallback when you *must* take it over; idempotent reuse is gentler and preferred for a user-facing launcher.)
2. **Readiness-gated** — poll the port/health endpoint until it actually answers (with a timeout) BEFORE opening the window. Never show a window pointed at a not-yet-ready server — that's the blank-window failure. (Problem 2.)
3. **Self-healing** — create missing dirs / DB / `.env` / log folder on launch (`New-Item -Force`, `os.makedirs(exist_ok=True)`). Missing state is created, never a crash.
4. **Self-contained** — run from the bundled runtime (the project's own `venv`/frozen exe), not system Python or a global tool. The launcher lives in the project; the shortcut points into it.
5. **Hardened against platform gotchas** — force `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8` (cp1252 crashes), fix PATH order, no CMD-window flashes (Problem 3).
6. **Fails loud with a map** — tee every subprocess's stdout/stderr to `logs\`; on failure, print the exact log path ("Server didn't come up — check logs\server-boot.err.log") and keep the window open (`Read-Host "Press Enter to exit"`) so the message is readable.
7. **Clean shutdown** — terminate child processes when the window closes, so orphans don't fight the next launch for the port.

The mechanics below implement these. Use them; don't reinvent.

---

## The Core Problems (and their solutions)

### Problem 1: Port already in use on restart

**Symptom:** `uvicorn` or `node` fails to start because port 8000/8001/3000 is occupied by a stale process from the last session.

**Solution — always free the port before starting:**

```powershell
# PowerShell: kill whatever is on a port before starting
function Free-Port($port) {
    $proc = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess
    if ($proc) {
        Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
}

Free-Port 8001
Free-Port 3000
```

```python
# Python: kill whatever is on a port before starting
import socket, subprocess, sys

def free_port(port):
    """Kill whatever process is using this port."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if f":{port} " in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                subprocess.run(["taskkill", "/F", "/PID", pid],
                               capture_output=True)
    except Exception:
        pass
```

---

### Problem 2: Not knowing if the server actually started

**Symptom:** The launcher opens Chrome before the backend is ready, user sees a connection error, has to manually refresh.

**Solution — health-check loop before launching the frontend:**

```python
import time, requests

def wait_for_server(url, timeout=30):
    """Poll the health endpoint until the server responds."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

# Use it:
if not wait_for_server("http://localhost:8001/health"):
    print("Backend failed to start within 30s — check the log")
    sys.exit(1)
```

```powershell
# PowerShell version
function Wait-ForServer($url, $timeoutSec = 30) {
    $deadline = (Get-Date).AddSeconds($timeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($r.StatusCode -lt 500) { return $true }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    return $false
}
```

---

### Problem 3: CMD windows popping up

**Symptom:** Every spawned subprocess opens a visible black CMD/PowerShell window. Looks broken.

**Solution — hide the window via `CREATE_NO_WINDOW` flag (Python) or `-WindowStyle Hidden` (PowerShell):**

```python
import subprocess

CREATE_NO_WINDOW = 0x08000000

proc = subprocess.Popen(
    ["python", "backend/main.py"],
    creationflags=CREATE_NO_WINDOW,
    stdout=open("logs/backend.log", "w"),
    stderr=subprocess.STDOUT,
)
```

```powershell
# PowerShell: hide the spawned window
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "python"
$psi.Arguments = "backend\main.py"
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$psi.CreateNoWindow = $true
$proc = [System.Diagnostics.Process]::Start($psi)
```

**For the launcher .vbs wrapper (to hide the PowerShell window that runs the launcher itself):**
```vbs
' launch.vbs — run launch.ps1 invisibly
Set WShell = CreateObject("WScript.Shell")
WShell.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & _
    CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & _
    "\launch.ps1""", 0, False
```

---

### Problem 4: Launching Chrome / detecting the browser window

**Symptom:** `Start-Process chrome` works, but you can't get a handle to the window for snapping or focus management.

**Solution — launch Chrome and find its window by process ID or window title:**

```powershell
# Launch Chrome and get the process
$chrome = Start-Process "chrome" -ArgumentList "http://localhost:3000" -PassThru
Start-Sleep -Seconds 2  # Let Chrome open

# Find the Chrome window (main window)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

# Find by process — get the main window handle
$chromeProc = Get-Process -Name "chrome" | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if ($chromeProc) {
    [Win32]::SetForegroundWindow($chromeProc.MainWindowHandle)
}
```

---

### Problem 5: Window snapping / split-screen layout

**Symptom:** Windows arranged manually after launch, or `SetWindowPos` fails silently.

**Solution — position windows directly via the Win32 `MoveWindow` API.** (Do NOT use `SendKeys` for Win+Arrow snapping: `System.Windows.Forms.SendKeys` has no Win-key modifier — `^%(LEFT)` is Ctrl+Alt+Left and `^{LEFT}` is Ctrl+Left, neither snaps a window. The `MoveWindow` approach below is the only reliable path.)

```powershell
Add-Type -AssemblyName System.Windows.Forms
# Get screen dimensions
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$halfWidth = [int]($screen.Width / 2)

# Snap a process window to left half
function Snap-WindowLeft($processName) {
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class WinSnap {
        [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);
        [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    }
"@
    $proc = Get-Process -Name $processName -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if ($proc) {
        $h = $proc.MainWindowHandle
        [WinSnap]::SetForegroundWindow($h)
        [WinSnap]::MoveWindow($h, $screen.Left, $screen.Top, $halfWidth, $screen.Height, $true)
    }
}
```

---

### Problem 6: Adding a custom desktop icon

**Symptom:** the user wants the launcher to look like a real app on the Desktop, not a generic .bat file with the default script icon. Asks: "give it an icon on my desktop", "make it launchable from the desktop", "put it on my desktop with an icon".

**Why .bat alone can't do this:** Windows `.bat` / `.cmd` files do NOT support a custom icon attribute. They always render with the shell's default script icon. To get a custom icon you MUST create a `.lnk` shortcut that targets the .bat and set the shortcut's `IconLocation`.

**Convention — the user's preferred layout:**
1. The `.bat` lives **inside the project** (e.g., `<project>/launch.bat`), not on the Desktop. Keeps Desktop clean, keeps the launcher versioned with the code.
2. A `.lnk` shortcut on the Desktop (`<App Name>.lnk`) points to the in-project `.bat` with a custom icon.
3. If a stale `.bat` already lives on the Desktop from an earlier attempt, **move** it into the project, don't copy — leaving a duplicate at the Desktop creates two paths to the same launcher and the user can't tell them apart.

**Picking an icon source (in order of preference):**
1. **Project's own favicon** — most Next.js projects have `app/favicon.ico` or `public/favicon.ico`. Use it directly. No conversion needed. Matches the in-browser tab icon for visual continuity.
2. **Existing `.ico` in the repo** — `assets/icon.ico`, `branding/logo.ico`, etc. Same direct-reference treatment.
3. **Generate from PNG/SVG** — if the project only has a PNG/SVG logo, convert it. Prefer ImageMagick (`magick logo.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico`) if available, else use the favicon as-is even if it's low-res.
4. **System icon fallback** — for pure-utility launchers with no brand, point at a Windows system icon: `IconLocation = "C:\Windows\System32\imageres.dll,109"` (gear), `,15` (folder), `,168` (terminal). Browse via `Get-ChildItem C:\Windows\System32\*.dll | % { ... }` or just pick from the well-known indexes.

**CRITICAL — hardcode the real Desktop, never trust redirected Desktop APIs blindly:**

The user's shell-folder registry can point at a stale synced Desktop path. BOTH `$env:USERPROFILE\Desktop` and `[Environment]::GetFolderPath('Desktop')` may return a dead redirected Desktop path; shortcuts placed there are invisible because that folder no longer holds the live Desktop. Hardcode the real root:
```powershell
$desktop = 'C:\Users\<you>\Desktop'
```
Same rule for Documents (`C:\Users\<you>\Documents`) and Pictures (`C:\Users\<you>\Pictures`). Never call `GetFolderPath` for these three.

**The PowerShell snippet (use this verbatim — the COM API is the only reliable way on Windows):**

```powershell
$desktop = 'C:\Users\<you>\Desktop'
$shortcutPath = "$desktop\<App Name>.lnk"
$targetBat    = "<absolute path to project>\launch.bat"
$workDir      = "<absolute path to project>"
$iconFile     = "<absolute path to .ico>"   # e.g., "<project>\app\favicon.ico"

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($shortcutPath)
$lnk.TargetPath       = $targetBat
$lnk.WorkingDirectory = $workDir
$lnk.IconLocation     = "$iconFile,0"   # ,0 = first icon in the .ico
$lnk.Description      = "<one-line tooltip>"
$lnk.WindowStyle      = 1               # 1=normal, 7=minimized, 3=maximized
$lnk.Save()
```

`IconLocation` syntax is `<path>,<index>`. For a single-icon `.ico` always use `,0`. For multi-icon `.dll`/`.exe` containers (like `imageres.dll`) the index selects which icon.

**Verification — confirm the shortcut landed AND the icon resolves:**

```powershell
# Test 1: shortcut file exists
Test-Path "$desktop\<App Name>.lnk"

# Test 2: icon path on the shortcut resolves to a real file
$s = (New-Object -ComObject WScript.Shell).CreateShortcut("$desktop\<App Name>.lnk")
$iconPath = ($s.IconLocation -split ',')[0]
Test-Path $iconPath   # must be True — if False, Explorer falls back to the default .bat icon
```

If `Test-Path $iconPath` returns `False`, Explorer silently falls back to the default script icon and you'll think the code didn't work. Always verify the icon file exists at the path you set.

**Refresh the Desktop if the icon doesn't appear:**

Windows caches icons aggressively. If a new shortcut shows the wrong icon (cached generic .bat icon), force a refresh:

```powershell
# Refresh the Desktop without logging out
ie4uinit.exe -show
# Nuclear option: clear the icon cache
Stop-Process -Name explorer -Force; Start-Process explorer
```

**Do NOT pin to taskbar by default** — the user didn't ask for that. The Desktop .lnk is enough. Pinning is a separate request.

**When the user says "update the icon"** — you only need to re-set `IconLocation` on the existing shortcut (no need to delete + recreate). Same COM snippet, skip `TargetPath` / `WorkingDirectory` lines if they're unchanged.

---

## Canonical Launcher Structure

For any project that needs a desktop launcher:

```
project/
├── launch.vbs          # Double-click entry — runs launch.ps1 invisibly
├── launch.ps1          # Main orchestration script
├── launcher.pyw        # (optional) Python GUI launcher
└── logs/
    ├── backend.log
    └── frontend.log
```

### `launch.ps1` template:

```powershell
# launch.ps1 — canonical Windows launcher template
# Based on patterns from Apex + Project Dashboard (Apr 2026)
# Satisfies non-negotiables #1 (idempotent attach), #2 (readiness gate),
# #6 (tee logs + fail loud + keep window open), #7 (clean shutdown).

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_PORT = 8001
$FRONTEND_PORT = 3000
$backendLog = "$ROOT\logs\backend.log"
New-Item -ItemType Directory -Force -Path "$ROOT\logs" | Out-Null

# Health probe used both for the idempotent check and the readiness gate.
function Test-Healthy($port) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$port/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        return ($r.StatusCode -lt 500)
    } catch { return $false }
}

# 1. Idempotent (NN #1): if the backend is already healthy, attach — don't kill + respawn.
$backend = $null
if (Test-Healthy $BACKEND_PORT) {
    Write-Host "Backend already healthy on $BACKEND_PORT — attaching."
} else {
    # Fallback: free the port only if something dead is squatting on it.
    $conn = Get-NetTCPConnection -LocalPort $BACKEND_PORT -State Listen -ErrorAction SilentlyContinue
    if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue; Start-Sleep -Milliseconds 500 }

    # 2. Start backend (hidden), teeing stdout+stderr to the log (NN #6).
    # Start-Process -RedirectStandard* writes straight to file — no unread pipe to deadlock on.
    $backend = Start-Process -FilePath "python" `
        -ArgumentList "-m","uvicorn","backend.main:app","--port",$BACKEND_PORT `
        -WorkingDirectory $ROOT `
        -WindowStyle Hidden `
        -RedirectStandardOutput $backendLog `
        -RedirectStandardError "$ROOT\logs\backend.err.log" `
        -PassThru
}

# 3. Readiness gate (NN #2): poll health until it answers, with a timeout.
$healthy = $false
$deadline = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $deadline) {
    if (Test-Healthy $BACKEND_PORT) { $healthy = $true; break }
    Start-Sleep -Milliseconds 500
}
if (-not $healthy) {
    # Fail loud with a map (NN #6): print the log path and keep the window open.
    Write-Host "Backend failed to start. Check $backendLog and $ROOT\logs\backend.err.log" -ForegroundColor Red
    if ($backend) { Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue }  # NN #7
    Read-Host "Press Enter to exit"
    exit 1
}

# 4. Launch browser
Start-Process "http://localhost:$FRONTEND_PORT"

# 7. Clean shutdown (NN #7): if we spawned the backend, stop it when this window closes.
if ($backend) {
    $global:LauncherBackendPid = $backend.Id
    Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
        Stop-Process -Id $global:LauncherBackendPid -Force -ErrorAction SilentlyContinue
    } | Out-Null
}
```

---

## When to Use This Skill

- Building any new desktop launcher from scratch
- "The launcher crashes" or "port already in use" errors
- Fixing CMD window visibility issues
- Adding browser/editor window snapping to a launcher
- Any project where `subprocess.Popen` or `Start-Process` is used on Windows

## Do NOT reinvent these patterns — apply them upfront

Every project that needed a Windows launcher (Apex, Project Dashboard) went through a 3-6 commit fix chain for the same issues: port management, startup detection, CMD visibility, and window handles. These patterns are the fix. Use them from the start.
