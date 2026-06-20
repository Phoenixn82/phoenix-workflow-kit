#!/usr/bin/env bash
# Bump semver in VERSION / package.json / pyproject.toml / Cargo.toml.
# Spec: PHASE_5_DISPATCH.md § 5.4

set -uo pipefail

root="${1:-}"
level="${2:-}"
dry_run=""
[ "${3:-}" = "--dry-run" ] && dry_run=1

if [ -z "$root" ] || [ -z "$level" ]; then
  echo "usage: version-bump.sh <project-root> {major|minor|patch} [--dry-run]" >&2
  exit 1
fi
case "$level" in major|minor|patch) ;; *) echo "invalid level: $level" >&2; exit 1 ;; esac

cd "$root" || { echo "root not found: $root" >&2; exit 1; }

source=""
current=""

if [ -f VERSION ]; then
  source="VERSION"
  current=$(head -n 1 VERSION | tr -d ' \r\n')
elif [ -f package.json ]; then
  source="package.json"
  if command -v jq >/dev/null 2>&1; then
    current=$(jq -r '.version' package.json)
  else
    current=$(grep -m1 '"version"' package.json | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
  fi
elif [ -f pyproject.toml ]; then
  source="pyproject.toml"
  current=$(grep -m1 -E '^version[[:space:]]*=' pyproject.toml | sed -E 's/version[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/')
  [ -z "$current" ] && current=$(grep -m1 -E '^\[tool\.poetry\]' pyproject.toml >/dev/null && awk '/^\[tool\.poetry\]/,/^\[/{if($0~/^version/) {gsub(/.*"|".*/,""); print; exit}}' pyproject.toml)
elif [ -f Cargo.toml ]; then
  source="Cargo.toml"
  current=$(awk '/^\[package\]/,/^\[/{if($0~/^version[[:space:]]*=/) {gsub(/.*"|".*/,""); print; exit}}' Cargo.toml)
elif [ -f setup.py ]; then
  source="setup.py"
  current=$(grep -m1 -E 'version[[:space:]]*=' setup.py | sed -E "s/.*version[[:space:]]*=[[:space:]]*['\"]([^'\"]+)['\"].*/\1/")
fi

if [ -z "$source" ] || [ -z "$current" ]; then
  echo "no version source found" >&2
  exit 1
fi

if ! echo "$current" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "non-semver version: $current" >&2
  exit 1
fi

major=$(echo "$current" | cut -d. -f1)
minor=$(echo "$current" | cut -d. -f2)
patch=$(echo "$current" | cut -d. -f3)

case "$level" in
  major) major=$((major + 1)); minor=0; patch=0 ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  patch) patch=$((patch + 1)) ;;
esac
new="${major}.${minor}.${patch}"

if [ -n "$dry_run" ]; then
  echo "${current} -> ${new} (dry-run, $source not modified)"
  exit 0
fi

case "$source" in
  VERSION)
    printf '%s\n' "$new" > VERSION.tmp && mv VERSION.tmp VERSION
    ;;
  package.json)
    if command -v jq >/dev/null 2>&1; then
      jq --arg v "$new" '.version = $v' package.json > package.json.tmp && mv package.json.tmp package.json
    else
      sed -i.bak -E "s/(\"version\"[[:space:]]*:[[:space:]]*)\"[^\"]+\"/\1\"${new}\"/" package.json && rm -f package.json.bak
    fi
    ;;
  pyproject.toml)
    sed -i.bak -E "0,/^version[[:space:]]*=/{s/(^version[[:space:]]*=[[:space:]]*)\"[^\"]+\"/\1\"${new}\"/}" pyproject.toml && rm -f pyproject.toml.bak
    ;;
  Cargo.toml)
    sed -i.bak -E "0,/^version[[:space:]]*=/{s/(^version[[:space:]]*=[[:space:]]*)\"[^\"]+\"/\1\"${new}\"/}" Cargo.toml && rm -f Cargo.toml.bak
    ;;
  setup.py)
    sed -i.bak -E "s/(version[[:space:]]*=[[:space:]]*['\"])[^'\"]+(['\"])/\1${new}\2/" setup.py && rm -f setup.py.bak
    ;;
esac

echo "${current} -> ${new}"
exit 0
