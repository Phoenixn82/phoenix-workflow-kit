#!/usr/bin/env python3
"""Fail-closed gate for pushes or visibility flips to public GitHub repos."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


BOUNDARY = (
    "FILESYSTEM BOUNDARY: do NOT read or modify anything under ~/.claude/, "
    "~/.agents/, .claude/skills/, or agents/. Work only in the guard skill, "
    "the approved manuals, and git config."
)
ZERO_SHA = re.compile(r"^0{40,64}$")
GATE = "[public-push-gate]"
SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_DENYLIST = SCRIPT_DIR / "denylist.local.json"
EXAMPLE_DENYLIST = SCRIPT_DIR / "denylist.example.json"


@dataclass(frozen=True)
class Finding:
    source: str
    location: str
    label: str
    excerpt: str = ""


class GateBlock(Exception):
    pass


class GateSkip(Exception):
    pass


DENYLIST: list[tuple[str, re.Pattern[str]]] = []
ALLOWLIST: list[tuple[str, re.Pattern[str], frozenset[str] | None]] = []
TOOL_PATHS: dict[str, list[str]] = {}

REAL_ONEDRIVE_PATH = re.compile(
    r"(?i)\b[A-Z]:\\Users\\(?P<user>[^\\\s<>]+)\\OneDrive(?:\\|$)"
)
CODEX_VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
        "findings": {"type": "string"},
    },
    "required": ["verdict", "findings"],
    "additionalProperties": False,
}


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def selected_config_path() -> Path | None:
    forced = os.environ.get("GUARD_DENYLIST_FILE")
    if forced:
        path = Path(forced)
        if not path.exists():
            raise GateBlock(f"GUARD_DENYLIST_FILE does not exist: {path}")
        return path
    if LOCAL_DENYLIST.exists():
        return LOCAL_DENYLIST
    if EXAMPLE_DENYLIST.exists():
        return EXAMPLE_DENYLIST
    return None


def load_config() -> None:
    global DENYLIST, ALLOWLIST, TOOL_PATHS

    path = selected_config_path()
    if not path:
        DENYLIST = []
        ALLOWLIST = []
        TOOL_PATHS = {}
        return

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GateBlock(f"cannot parse denylist config {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise GateBlock(f"denylist config must be a JSON object: {path}")

    entries = raw.get("denylist", [])
    if not isinstance(entries, list):
        raise GateBlock(f"denylist config field must be a list: {path}")

    compiled: list[tuple[str, re.Pattern[str]]] = []
    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise GateBlock(f"denylist entry {idx} must be an object: {path}")
        if entry.get("disabled"):
            continue
        label = str(entry.get("label") or f"denylist entry {idx}")
        regex = entry.get("regex")
        if not isinstance(regex, str) or not regex:
            raise GateBlock(f"denylist entry {idx} missing regex: {path}")
        flags = 0 if entry.get("case_sensitive") else re.IGNORECASE
        try:
            compiled.append((label, re.compile(regex, flags)))
        except re.error as exc:
            raise GateBlock(f"invalid regex in denylist entry {idx} ({label}): {exc}") from exc

    allowlist_entries = raw.get("allowlist", [])
    if not isinstance(allowlist_entries, list):
        raise GateBlock(f"allowlist config field must be a list: {path}")

    compiled_allowlist: list[tuple[str, re.Pattern[str], frozenset[str] | None]] = []
    for idx, entry in enumerate(allowlist_entries, start=1):
        if not isinstance(entry, dict):
            raise GateBlock(f"allowlist entry {idx} must be an object: {path}")
        if entry.get("disabled"):
            continue
        label = str(entry.get("label") or f"allowlist entry {idx}")
        regex = entry.get("regex")
        if not isinstance(regex, str) or not regex:
            raise GateBlock(f"allowlist entry {idx} missing regex: {path}")
        repos = None
        if "repos" in entry:
            raw_repos = entry.get("repos")
            if not isinstance(raw_repos, list):
                raise GateBlock(f"allowlist entry {idx} repos must be a list: {path}")
            repos = frozenset(str(repo).casefold() for repo in raw_repos if str(repo).strip())
        flags = 0 if entry.get("case_sensitive") else re.IGNORECASE
        try:
            compiled_allowlist.append((label, re.compile(regex, flags), repos))
        except re.error as exc:
            raise GateBlock(f"invalid regex in allowlist entry {idx} ({label}): {exc}") from exc

    raw_tool_paths = raw.get("tool_paths", {})
    if raw_tool_paths and not isinstance(raw_tool_paths, dict):
        raise GateBlock(f"tool_paths config field must be an object: {path}")

    paths: dict[str, list[str]] = {}
    for name, values in raw_tool_paths.items():
        if not isinstance(values, list):
            raise GateBlock(f"tool_paths.{name} must be a list: {path}")
        paths[str(name)] = [str(value) for value in values if value]

    DENYLIST = compiled
    ALLOWLIST = compiled_allowlist
    TOOL_PATHS = paths


def run(
    args: list[str],
    *,
    cwd: str | None = None,
    input_text: str | None = None,
    timeout: int = 60,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(
        args,
        cwd=cwd,
        input=input_text,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if check and cp.returncode != 0:
        detail = (cp.stderr or cp.stdout or "").strip()
        raise GateBlock(f"command failed: {' '.join(args)}\n{detail}")
    return cp


def shim_argv(tool_path: str, rest_args: list[str]) -> list[str]:
    suffix = Path(tool_path).suffix.casefold()
    if os.name == "nt" and suffix in {".cmd", ".bat"}:
        return ["cmd", "/c", tool_path, *rest_args]
    if os.name == "nt" and suffix == ".ps1":
        return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", tool_path, *rest_args]
    return [tool_path, *rest_args]


def sort_newest(paths: Iterable[Path]) -> list[Path]:
    return sorted(paths, key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)


def codex_windows_exes() -> list[str]:
    if os.name != "nt":
        return []

    candidates: list[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        npm_node_modules = Path(appdata) / "npm" / "node_modules" / "@openai" / "codex" / "node_modules"
        candidates.extend(sort_newest(npm_node_modules.glob("@openai/codex-*/vendor/**/codex.exe")))

    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        codex_bin = Path(localappdata) / "OpenAI" / "Codex" / "bin"
        candidates.extend(sort_newest(codex_bin.glob("*/codex.exe")))
        candidates.append(codex_bin / "codex.exe")

    return [str(path) for path in candidates if path.exists()]


def find_tool(name: str) -> str | None:
    if name == "codex":
        preferred = [os.environ.get("CODEX_CLI_PATH"), *TOOL_PATHS.get("codex", [])]
        for candidate in preferred:
            if candidate and Path(candidate).exists():
                return candidate
        for candidate in codex_windows_exes():
            return candidate
    if os.name == "nt":
        for suffix in (".exe", ".cmd", ".bat", ""):
            found = shutil.which(name + suffix)
            if found:
                return found
    return shutil.which(name)


def require_tool(name: str) -> str:
    found = find_tool(name)
    if not found:
        raise GateBlock(f"required tool not found on PATH: {name}")
    return found


def parse_owner_repo(remote_url: str) -> str | None:
    forced_repo = os.environ.get("GUARD_FORCE_OWNER_REPO")
    if forced_repo:
        return forced_repo.strip().removesuffix(".git")

    remote_url = remote_url.strip()
    if not remote_url:
        return None

    ssh_match = re.match(r"^(?:ssh://)?git@github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$", remote_url)
    if ssh_match:
        return f"{ssh_match.group('owner')}/{ssh_match.group('repo')}"

    parsed = urlparse(remote_url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return None
    repo = parts[1].removesuffix(".git")
    return f"{parts[0]}/{repo}"


def forced_visibility(args: argparse.Namespace) -> str | None:
    raw = args.force_visibility or os.environ.get("GUARD_FORCE_VISIBILITY")
    if not raw:
        return None
    value = raw.strip().upper()
    if value not in {"PUBLIC", "PRIVATE", "MISSING"}:
        raise GateBlock("GUARD_FORCE_VISIBILITY must be PUBLIC, PRIVATE, or MISSING")
    return value


def github_visibility(owner_repo: str, gh: str, args: argparse.Namespace) -> str:
    forced = forced_visibility(args)
    if forced:
        return forced

    cp = run(shim_argv(gh, ["repo", "view", owner_repo, "--json", "visibility"]), timeout=30)
    if cp.returncode != 0:
        output = f"{cp.stdout}\n{cp.stderr}".lower()
        if "could not resolve to a repository" in output or "not found" in output or "http 404" in output:
            return "MISSING"
        raise GateBlock(f"cannot determine GitHub repo visibility for {owner_repo}; gh failed:\n{cp.stderr.strip()}")
    try:
        return json.loads(cp.stdout)["visibility"].upper()
    except Exception as exc:
        raise GateBlock(f"cannot parse gh visibility response for {owner_repo}: {exc}") from exc


def override_enabled() -> bool:
    return os.environ.get("GUARD_ALLOW_PUBLIC_PUSH") == "1"


def print_override_banner() -> None:
    eprint("")
    eprint("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    eprint("!! PUBLIC PUSH SAFETY GATE BYPASSED BY HUMAN OVERRIDE    !!")
    eprint("!! GUARD_ALLOW_PUBLIC_PUSH=1 was set for this operation. !!")
    eprint("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    eprint("")


def read_updates(stdin_file: str | None) -> list[tuple[str, str, str, str]]:
    if not stdin_file:
        return []
    text = Path(stdin_file).read_text(encoding="utf-8", errors="replace")
    updates: list[tuple[str, str, str, str]] = []
    for raw in text.splitlines():
        parts = raw.split()
        if len(parts) >= 4:
            updates.append((parts[0], parts[1], parts[2], parts[3]))
    return updates


def git_exists(ref: str) -> bool:
    return run(["git", "cat-file", "-e", f"{ref}^{{commit}}"], timeout=15).returncode == 0


def git_output(args: list[str], *, timeout: int = 60) -> str:
    return run(["git", *args], timeout=timeout, check=True).stdout


def git_lines(args: list[str], *, timeout: int = 60) -> list[str]:
    return [line for line in git_output(args, timeout=timeout).splitlines() if line.strip()]


def default_branch(owner_repo: str, remote_name: str, gh: str | None) -> str | None:
    if not os.environ.get("GUARD_FORCE_VISIBILITY") and gh:
        cp = run(shim_argv(gh, ["repo", "view", owner_repo, "--json", "defaultBranchRef"]), timeout=30)
        if cp.returncode == 0:
            try:
                branch = json.loads(cp.stdout)["defaultBranchRef"]["name"]
                if branch:
                    return branch
            except Exception:
                pass

    cp = run(["git", "remote", "show", remote_name], timeout=30)
    if cp.returncode == 0:
        for line in cp.stdout.splitlines():
            if "HEAD branch:" in line:
                branch = line.split(":", 1)[1].strip()
                if branch and branch != "(unknown)":
                    return branch
    return None


def ensure_remote_default_ref(remote_name: str, branch: str) -> str | None:
    candidates = [
        f"refs/remotes/{remote_name}/{branch}",
        f"{remote_name}/{branch}",
        branch,
    ]
    for candidate in candidates:
        if git_exists(candidate):
            return candidate

    run(["git", "fetch", "--quiet", "--depth=1", remote_name, f"refs/heads/{branch}:refs/remotes/{remote_name}/{branch}"], timeout=60)
    candidate = f"refs/remotes/{remote_name}/{branch}"
    if git_exists(candidate):
        return candidate
    return None


@dataclass
class ScanPlan:
    log_opts: list[str]
    file_specs: list[tuple[str, str]]
    metadata_ranges: list[str]


def build_push_scan_plan(updates: list[tuple[str, str, str, str]], remote_name: str, owner_repo: str, gh: str | None) -> ScanPlan:
    log_opts: list[str] = []
    file_specs: list[tuple[str, str]] = []
    metadata_ranges: list[str] = []

    for _local_ref, local_sha, _remote_ref, remote_sha in updates:
        if ZERO_SHA.match(local_sha):
            continue

        if not git_exists(local_sha):
            raise GateBlock(f"local commit not found for pushed ref: {local_sha}")

        base: str | None = None
        if not ZERO_SHA.match(remote_sha):
            if git_exists(remote_sha):
                base = remote_sha
        else:
            branch = default_branch(owner_repo, remote_name, gh)
            if branch:
                base = ensure_remote_default_ref(remote_name, branch)

        if base:
            range_expr = f"{base}..{local_sha}"
            changed = git_lines(["diff", "--name-only", "--diff-filter=ACMRT", base, local_sha], timeout=60)
        else:
            range_expr = local_sha
            changed = git_lines(["ls-tree", "-r", "--name-only", local_sha], timeout=60)

        log_opts.append(range_expr)
        metadata_ranges.append(range_expr)
        file_specs.extend((local_sha, path) for path in changed)

    if not log_opts:
        raise GateSkip("no pushed commits to scan")

    return ScanPlan(log_opts=dedupe(log_opts), file_specs=dedupe_pairs(file_specs), metadata_ranges=dedupe(metadata_ranges))


def build_publicize_scan_plan() -> ScanPlan:
    head = git_output(["rev-parse", "HEAD"], timeout=15).strip()
    if not git_exists(head):
        raise GateBlock("HEAD is not a commit")
    files = git_lines(["ls-tree", "-r", "--name-only", head], timeout=60)
    return ScanPlan(log_opts=["--all"], file_specs=[(head, path) for path in files], metadata_ranges=["--all"])


def dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def dedupe_pairs(values: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    result: list[tuple[str, str]] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def safe_excerpt(text: str, start: int, end: int) -> str:
    left = max(0, start - 40)
    right = min(len(text), end + 40)
    excerpt = text[left:right].replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", excerpt).strip()[:180]


def line_bounds(text: str, start: int, end: int) -> tuple[int, int]:
    left = text.rfind("\n", 0, start) + 1
    right = text.find("\n", end)
    if right == -1:
        right = len(text)
    return left, right


def is_placeholder_user(segment: str) -> bool:
    value = segment.strip().lower()
    return value in {"you", "your-name", "other-user"} or value.startswith("your-")


def is_real_onedrive_path_match(text: str, start: int, end: int) -> bool:
    left, right = line_bounds(text, start, end)
    for match in REAL_ONEDRIVE_PATH.finditer(text[left:right]):
        if not is_placeholder_user(match.group("user")):
            return True
    return False


def is_repo_owner_handle_match(match_text: str, owner_repo: str) -> bool:
    if "/" not in owner_repo:
        return False
    owner = owner_repo.split("/", 1)[0]
    return match_text.casefold() == owner.casefold()


def should_report_match(label: str, match: re.Match[str], text: str, owner_repo: str) -> bool:
    normalized = label.casefold()
    if "onedrive" in normalized:
        return is_real_onedrive_path_match(text, match.start(), match.end())
    if "public handle" in normalized and is_repo_owner_handle_match(match.group(0), owner_repo):
        return False
    return True


def is_allowlisted_personal_match(match_text: str, owner_repo: str) -> bool:
    normalized_repo = owner_repo.casefold()
    for _label, pattern, repos in ALLOWLIST:
        if repos is not None and normalized_repo not in repos:
            continue
        if pattern.search(match_text):
            return True
    return False


def scan_text(source: str, location: str, text: str, owner_repo: str) -> list[Finding]:
    findings: list[Finding] = []
    for label, pattern in DENYLIST:
        for match in pattern.finditer(text):
            if not should_report_match(label, match, text, owner_repo):
                continue
            if is_allowlisted_personal_match(match.group(0), owner_repo):
                continue
            findings.append(Finding(source, location, label, safe_excerpt(text, match.start(), match.end())))
    return findings


def git_blob(commit: str, path: str) -> str | None:
    cp = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if cp.returncode != 0:
        return None
    if b"\x00" in cp.stdout[:4096]:
        return None
    return cp.stdout[:2_000_000].decode("utf-8", errors="replace")


def denylist_scan(plan: ScanPlan, owner_repo: str) -> list[Finding]:
    findings: list[Finding] = []

    for commit, path in plan.file_specs:
        findings.extend(scan_text("path", f"{commit}:{path}", path, owner_repo))
        content = git_blob(commit, path)
        if content is not None:
            findings.extend(scan_text("file", f"{commit}:{path}", content, owner_repo))

    for range_expr in plan.metadata_ranges:
        cp = run(
            ["git", "log", "--format=%H%n%an <%ae>%n%cn <%ce>%n%s%n%b", range_expr],
            timeout=60,
            check=False,
        )
        if cp.returncode == 0 and cp.stdout.strip():
            findings.extend(scan_text("commit", range_expr, cp.stdout, owner_repo))

    return dedupe_findings(findings)


def dedupe_findings(findings: Iterable[Finding]) -> list[Finding]:
    seen: set[tuple[str, str, str, str]] = set()
    result: list[Finding] = []
    for finding in findings:
        key = (finding.source, finding.location, finding.label, finding.excerpt)
        if key not in seen:
            seen.add(key)
            result.append(finding)
    return result


def gitleaks_scan(plan: ScanPlan, gitleaks: str) -> list[Finding]:
    findings: list[Finding] = []
    for log_opts in plan.log_opts:
        with tempfile.TemporaryDirectory(prefix="public-push-gate-") as temp_dir:
            report_path = Path(temp_dir) / "gitleaks.json"
            cmd = shim_argv(
                gitleaks,
                [
                    "git",
                    "--no-banner",
                    "--redact",
                    "--exit-code",
                    "1",
                    "--report-format",
                    "json",
                    "--report-path",
                    str(report_path),
                    "--log-opts",
                    log_opts,
                ],
            )
            cp = run(cmd, timeout=180)
            if cp.returncode not in (0, 1):
                raise GateBlock(f"gitleaks failed for {log_opts}:\n{cp.stderr.strip() or cp.stdout.strip()}")
            if report_path.exists() and report_path.stat().st_size:
                try:
                    leaks = json.loads(report_path.read_text(encoding="utf-8", errors="replace"))
                except json.JSONDecodeError as exc:
                    raise GateBlock(f"could not parse gitleaks report: {exc}") from exc
                for leak in leaks:
                    location = leak.get("File") or leak.get("Commit") or log_opts
                    rule = leak.get("RuleID") or leak.get("Description") or "secret"
                    findings.append(Finding("gitleaks", location, str(rule), "redacted by gitleaks"))
    return dedupe_findings(findings)


def codex_review(plan: ScanPlan, owner_repo: str, codex: str, deterministic_findings: list[Finding]) -> None:
    if deterministic_findings:
        return

    paths = dedupe(path for _commit, path in plan.file_specs)
    path_summary = "\n".join(f"- {path}" for path in paths[:200])
    if len(paths) > 200:
        path_summary += f"\n- ... {len(paths) - 200} more paths"
    if not path_summary:
        path_summary = "- no file paths supplied"

    prompt = f"""Task: final public-push safety verdict for {owner_repo}.

You are being invoked non-interactively by a Git hook. Do not ask for context, do not write files, and do not run shared-log or coordination steps. Use only the supplied scan summary below.

{BOUNDARY}

Deterministic scans already passed:
- gitleaks found no secrets
- the personal-data denylist found no hits in changed file paths, changed file contents, or commit metadata

File count scanned: {len(plan.file_specs)}
File paths scanned:
{path_summary}

Return a JSON object matching the schema:
{{"verdict":"PASS","findings":"No findings."}}
or
{{"verdict":"FAIL","findings":"<brief findings>"}}
"""
    codex_env = os.environ.copy()
    codex_env.pop("AOS_SESSION_ID", None)
    model = os.environ.get("GUARD_CODEX_MODEL", "gpt-5.4-mini")
    codex_cwd = Path(__file__).resolve().parents[4]
    with tempfile.TemporaryDirectory(prefix="public-push-codex-") as temp_dir:
        schema_path = Path(temp_dir) / "verdict.schema.json"
        schema_path.write_text(json.dumps(CODEX_VERDICT_SCHEMA), encoding="utf-8")
        try:
            cp = subprocess.run(
                shim_argv(
                    codex,
                    [
                        "exec",
                        "--skip-git-repo-check",
                        "--ignore-rules",
                        "--ephemeral",
                        "--model",
                        model,
                        "--output-schema",
                        str(schema_path),
                        prompt,
                    ],
                ),
                cwd=str(codex_cwd),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=codex_env,
                timeout=180,
            )
        except subprocess.TimeoutExpired as exc:
            raise GateBlock("codex review timed out") from exc
    if cp.returncode != 0:
        raise GateBlock(f"codex review failed:\n{cp.stderr.strip() or cp.stdout.strip()}")

    verdict = None
    for line in cp.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            verdict = json.loads(line)
            break
        except json.JSONDecodeError:
            continue

    if not verdict:
        raise GateBlock(f"codex review did not return JSON:\n{cp.stdout.strip() or '(no output)'}")
    if verdict.get("verdict") != "PASS":
        raise GateBlock(f"codex review failed: {verdict.get('findings', 'no findings supplied')}")


def print_findings(findings: list[Finding]) -> None:
    eprint(f"{GATE} FAIL: public target blocked; findings:")
    for idx, finding in enumerate(findings[:50], start=1):
        detail = f" [{finding.excerpt}]" if finding.excerpt else ""
        eprint(f"  {idx}. {finding.source}: {finding.location}: {finding.label}{detail}")
    if len(findings) > 50:
        eprint(f"  ... {len(findings) - 50} more findings")


def run_gate(plan: ScanPlan, owner_repo: str) -> None:
    require_tool("gh")
    gitleaks = require_tool("gitleaks")
    codex = require_tool("codex")
    require_tool("git")

    eprint(f"{GATE} scanning public target {owner_repo}")
    findings = []
    findings.extend(gitleaks_scan(plan, gitleaks))
    findings.extend(denylist_scan(plan, owner_repo))
    findings = dedupe_findings(findings)

    if findings:
        print_findings(findings)
        raise SystemExit(1)

    codex_review(plan, owner_repo, codex, findings)
    eprint(f"{GATE} PASS: gitleaks, denylist, and Codex review passed")


def pre_push(args: argparse.Namespace) -> int:
    owner_repo = parse_owner_repo(args.remote_url)
    visibility = forced_visibility(args)
    if not owner_repo and visibility:
        owner_repo = os.environ.get("GUARD_FORCE_OWNER_REPO", "local/public-push-test")
    if not owner_repo:
        eprint(f"{GATE} non-GitHub remote; gate skipped")
        return 0

    if override_enabled():
        print_override_banner()
        return 0

    gh = require_tool("gh")
    visibility = github_visibility(owner_repo, gh, args)
    if visibility in {"PRIVATE", "MISSING"}:
        eprint(f"{GATE} {owner_repo} is {visibility.lower()}; gate skipped")
        return 0
    if visibility != "PUBLIC":
        raise GateBlock(f"unexpected GitHub visibility for {owner_repo}: {visibility}")

    plan = build_push_scan_plan(read_updates(args.stdin_file), args.remote_name, owner_repo, gh)
    run_gate(plan, owner_repo)
    return 0


def publicize(args: argparse.Namespace) -> int:
    owner_repo = args.repo
    if not owner_repo:
        gh = require_tool("gh")
        cp = run(shim_argv(gh, ["repo", "view", "--json", "nameWithOwner"]), timeout=30, check=True)
        owner_repo = json.loads(cp.stdout)["nameWithOwner"]

    if override_enabled():
        print_override_banner()
        return 0

    plan = build_publicize_scan_plan()
    run_gate(plan, owner_repo)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guard public GitHub pushes and visibility flips.")
    parser.add_argument("--mode", choices=["pre-push", "publicize"], required=True)
    parser.add_argument("--remote-name", default="")
    parser.add_argument("--remote-url", default="")
    parser.add_argument("--stdin-file")
    parser.add_argument("--repo")
    parser.add_argument("--force-visibility", choices=["PUBLIC", "PRIVATE", "MISSING"])
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        load_config()
        if args.mode == "pre-push":
            return pre_push(args)
        if args.mode == "publicize":
            return publicize(args)
        raise GateBlock(f"unknown mode: {args.mode}")
    except GateSkip as exc:
        eprint(f"{GATE} {exc}; gate skipped")
        return 0
    except GateBlock as exc:
        eprint(f"{GATE} BLOCKED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
