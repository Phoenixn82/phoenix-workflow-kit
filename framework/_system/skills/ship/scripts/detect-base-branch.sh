#!/usr/bin/env bash
# Detect the project's base branch (main / master / trunk / develop).
# Spec: PHASE_5_DISPATCH.md § 5.2

set -uo pipefail

root="${1:-.}"

if [ -d "$root" ]; then
  cd "$root" || { echo "main"; exit 1; }
fi

if ! command -v git >/dev/null 2>&1; then
  echo "main"
  exit 1
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "main"
  exit 1
fi

head_ref=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null || true)
if [ -n "$head_ref" ]; then
  name=${head_ref#refs/remotes/origin/}
  if [ -n "$name" ]; then
    echo "$name"
    exit 0
  fi
fi

for candidate in main master trunk develop; do
  if git show-ref --verify --quiet "refs/remotes/origin/$candidate"; then
    echo "$candidate"
    exit 0
  fi
done

for candidate in main master trunk develop; do
  if git show-ref --verify --quiet "refs/heads/$candidate"; then
    echo "$candidate"
    exit 0
  fi
done

echo "main"
exit 1
