#!/usr/bin/env bash
# Prepend a Keep-a-Changelog block to CHANGELOG.md.
# Spec: PHASE_5_DISPATCH.md § 5.5

set -uo pipefail

root="${1:-}"
new_version="${2:-}"
since_ref=""
override_body=""

shift 2 2>/dev/null || true
while [ $# -gt 0 ]; do
  case "$1" in
    --since) since_ref="$2"; shift 2 ;;
    --body) override_body="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [ -z "$root" ] || [ -z "$new_version" ]; then
  echo "usage: changelog-update.sh <project-root> <new-version> [--since <ref>] [--body <text>]" >&2
  exit 1
fi

cd "$root" || { echo "root not found: $root" >&2; exit 1; }

today=$(date -u +%Y-%m-%d)

if [ -f CHANGELOG.md ] && grep -q "## \[${new_version}\]" CHANGELOG.md; then
  echo "version ${new_version} already in CHANGELOG.md" >&2
  exit 1
fi

if [ -z "$since_ref" ]; then
  last_tag=$(git describe --tags --abbrev=0 2>/dev/null || true)
  if [ -n "$last_tag" ]; then since_ref="$last_tag"; else since_ref="HEAD~10"; fi
fi

added=()
changed=()
fixed=()
removed=()
other=()

if [ -z "$override_body" ] && command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    case "$line" in
      "feat:"*|"feat("*) added+=("${line#feat*: }") ;;
      "fix:"*|"fix("*) fixed+=("${line#fix*: }") ;;
      "refactor:"*|"refactor("*|"perf:"*|"perf("*) changed+=("${line#*: }") ;;
      "BREAKING"*|*"BREAKING CHANGE"*) removed+=("${line}") ;;
      *) other+=("$line") ;;
    esac
  done < <(git log --pretty=format:'%s' "${since_ref}..HEAD" 2>/dev/null || echo)
fi

build_block() {
  printf '## [%s] - %s\n\n' "$new_version" "$today"

  if [ -n "$override_body" ]; then
    printf '%s\n\n' "$override_body"
    return
  fi

  if [ ${#added[@]} -gt 0 ]; then
    printf '### Added\n'
    for item in "${added[@]}"; do printf -- '- %s\n' "$item"; done
    printf '\n'
  fi
  if [ ${#changed[@]} -gt 0 ]; then
    printf '### Changed\n'
    for item in "${changed[@]}"; do printf -- '- %s\n' "$item"; done
    printf '\n'
  fi
  if [ ${#fixed[@]} -gt 0 ]; then
    printf '### Fixed\n'
    for item in "${fixed[@]}"; do printf -- '- %s\n' "$item"; done
    printf '\n'
  fi
  if [ ${#removed[@]} -gt 0 ]; then
    printf '### Removed\n'
    for item in "${removed[@]}"; do printf -- '- %s\n' "$item"; done
    printf '\n'
  fi
  if [ ${#other[@]} -gt 0 ]; then
    printf '### Other\n'
    for item in "${other[@]}"; do printf -- '- %s\n' "$item"; done
    printf '\n'
  fi
  if [ ${#added[@]} -eq 0 ] && [ ${#changed[@]} -eq 0 ] && [ ${#fixed[@]} -eq 0 ] && [ ${#removed[@]} -eq 0 ] && [ ${#other[@]} -eq 0 ]; then
    printf 'No notable changes recorded since %s.\n\n' "$since_ref"
  fi
}

block=$(build_block)

if [ ! -f CHANGELOG.md ]; then
  cat > CHANGELOG.md <<EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

$block
EOF
else
  header_end=$(grep -n '^## ' CHANGELOG.md | head -n 1 | cut -d: -f1)
  if [ -z "$header_end" ]; then
    cat CHANGELOG.md > CHANGELOG.md.tmp
    printf '\n%s' "$block" >> CHANGELOG.md.tmp
    mv CHANGELOG.md.tmp CHANGELOG.md
  else
    head -n $((header_end - 1)) CHANGELOG.md > CHANGELOG.md.tmp
    printf '%s\n' "$block" >> CHANGELOG.md.tmp
    tail -n +"$header_end" CHANGELOG.md >> CHANGELOG.md.tmp
    mv CHANGELOG.md.tmp CHANGELOG.md
  fi
fi

echo "wrote CHANGELOG.md block for ${new_version}"
exit 0
