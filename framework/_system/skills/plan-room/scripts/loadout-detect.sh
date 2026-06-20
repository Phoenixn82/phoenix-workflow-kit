#!/usr/bin/env bash
# Snapshot current plugin/MCP/skill loadout.
# Spec: _archive/claude_projects_2026-05-pre-rebuild/Rebuild/PHASE_5_DISPATCH.md § 6.3 (archive only)

set -uo pipefail

emit_json=""
scope="user"

while [ $# -gt 0 ]; do
  case "$1" in
    --json) emit_json=1; shift ;;
    --scope) scope="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

CLAUDE_HOME="${HOME}/.claude"
PROJECT_ROOT="${PWD}"

collect_plugins() {
  local raw=""
  if command -v claude >/dev/null 2>&1; then
    raw=$(claude plugins list 2>/dev/null || true)
  fi
  if [ -n "$raw" ]; then
    printf '%s\n' "$raw" | grep -E '^[[:space:]]*❯' | sed -E 's/^[[:space:]]*❯[[:space:]]*//' | sed -E 's/@.*$//'
    return
  fi
  if [ -d "${CLAUDE_HOME}/plugins" ]; then
    find "${CLAUDE_HOME}/plugins" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null
  fi
}

collect_mcps() {
  local raw=""
  if command -v claude >/dev/null 2>&1; then
    raw=$(claude mcp list 2>/dev/null || true)
  fi
  if [ -n "$raw" ]; then
    printf '%s\n' "$raw" | grep -E ':[[:space:]]+[A-Za-z]' | \
      grep -vE '^[[:space:]]*Checking' | \
      sed -E 's/^[[:space:]]*//' | sed -E 's/:[[:space:]].*$//'
    return
  fi
  for f in "${CLAUDE_HOME}/mcp-servers.json" "${CLAUDE_HOME}/.mcp.json"; do
    if [ -f "$f" ] && command -v jq >/dev/null 2>&1; then
      jq -r '.mcpServers | keys[]?' "$f" 2>/dev/null || true
    fi
  done
  if [ "$scope" = "project" ] && [ -f "${PROJECT_ROOT}/.mcp.json" ] && command -v jq >/dev/null 2>&1; then
    jq -r '.mcpServers | keys[]?' "${PROJECT_ROOT}/.mcp.json" 2>/dev/null || true
  fi
}

collect_skills() {
  local out=""
  if [ -d "${CLAUDE_HOME}/skills" ]; then
    out=$(find "${CLAUDE_HOME}/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort -u)
  fi
  if [ "$scope" = "project" ] && [ -d "${PROJECT_ROOT}/.claude/skills" ]; then
    out="${out}"$'\n'"$(find "${PROJECT_ROOT}/.claude/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort -u)"
  fi
  printf '%s\n' "$out"
}

normalize() {
  printf '%s\n' "$1" | grep -v '^$' | sort -u
}

plugins=$(normalize "$(collect_plugins)")
mcps=$(normalize "$(collect_mcps)")
skills=$(normalize "$(collect_skills)")

if [ -n "$emit_json" ]; then
  json_array() {
    local arr="$1"
    if [ -z "$arr" ]; then printf '[]'; return; fi
    if command -v jq >/dev/null 2>&1; then
      printf '%s' "$arr" | jq -R . | jq -s .
    else
      printf '[%s]' "$(printf '%s' "$arr" | awk 'BEGIN{first=1} {if(!first)printf ","; printf "\"%s\"", $0; first=0}')"
    fi
  }
  printf '{"plugins":%s,"mcps":%s,"skills":%s,"scope":"%s"}\n' \
    "$(json_array "$plugins")" \
    "$(json_array "$mcps")" \
    "$(json_array "$skills")" \
    "$scope"
else
  printf 'Plugins:\n'
  if [ -n "$plugins" ]; then printf '%s\n' "$plugins" | sed 's/^/  - /'; else printf '  (none)\n'; fi
  printf '\nMCPs:\n'
  if [ -n "$mcps" ]; then printf '%s\n' "$mcps" | sed 's/^/  - /'; else printf '  (none)\n'; fi
  printf '\nSkills:\n'
  if [ -n "$skills" ]; then printf '%s\n' "$skills" | sed 's/^/  - /'; else printf '  (none)\n'; fi
fi

exit 0
