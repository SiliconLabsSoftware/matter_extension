#!/usr/bin/env bash
# Prints Slack-oriented commit summary: parent repo + third_party/matter_sdk gitlink only.
# PREV_BASELINE: previous Jenkins Git commit (GIT_PREVIOUS_SUCCESSFUL_COMMIT or GIT_PREVIOUS_COMMIT).

set +e
MAX=40
PREV="${PREV_BASELINE:-}"
HEADS=$(git rev-parse --short HEAD 2>/dev/null || echo "?")

if [ -n "$PREV" ]; then
  PREVS=$(git rev-parse --short "$PREV" 2>/dev/null || echo "$PREV" | cut -c1-7)
  MAIN=$(git log --oneline --no-merges "${PREV}..HEAD" 2>/dev/null | head -n "$MAX")
  [ -z "$MAIN" ] && MAIN="(no commits in range)"
  printf "*matter_extension (%s..%s):*\n%s\n\n" "$PREVS" "$HEADS" "$MAIN"
else
  MAIN=$(git log -n 20 --oneline HEAD 2>/dev/null)
  printf "*matter_extension (no baseline; last 20 commits):*\n%s\n\n" "$MAIN"
fi

git submodule update --init --quiet third_party/matter_sdk 2>/dev/null || true
CURR_SM=$(git rev-parse HEAD:third_party/matter_sdk 2>/dev/null)
PREV_SM=
if [ -n "$PREV" ]; then
  PREV_SM=$(git rev-parse "${PREV}:third_party/matter_sdk" 2>/dev/null)
fi

if [ -n "$PREV_SM" ] && [ -n "$CURR_SM" ] && [ "$PREV_SM" != "$CURR_SM" ]; then
  git -C third_party/matter_sdk fetch --quiet origin "$PREV_SM" "$CURR_SM" 2>/dev/null || true
  SM_LOG=$(git -C third_party/matter_sdk log --oneline "${PREV_SM}..${CURR_SM}" 2>/dev/null | head -n "$MAX")
  PS=$(echo "$PREV_SM" | cut -c1-7)
  CS=$(echo "$CURR_SM" | cut -c1-7)
  [ -z "$SM_LOG" ] && SM_LOG="(unable to list commits; pointer ${PS} -> ${CS})"
  printf "*matter_sdk (%s..%s):*\n%s\n" "$PS" "$CS" "$SM_LOG"
elif [ -n "$CURR_SM" ]; then
  CS=$(echo "$CURR_SM" | cut -c1-7)
  printf "*matter_sdk:* unchanged at %s (or no prior baseline)\n" "$CS"
else
  printf "*matter_sdk:* (gitlink not found)\n"
fi
