#!/usr/bin/env bash
# issue.sh open LABEL TITLE BODY_FILE | close LABEL COMMENT
# keeps one open issue per label and title: a repeat comments only when the text changed
set -euo pipefail

action=$1
label=$2

case "$action" in
  open)
    export TITLE=$3
    body=$4
    gh label create "$label" --color d73a4a --force > /dev/null
    number=$(gh issue list --state open --label "$label" --json number,title \
      --jq '.[] | select(.title == env.TITLE) | .number' | head -n1)
    if [ -z "$number" ]; then
      gh issue create --title "$TITLE" --label "$label" --body-file "$body"
      exit 0
    fi
    latest=$(gh issue view "$number" --json body,comments --jq '[.body] + [.comments[].body] | last')
    if [ "$latest" = "$(cat "$body")" ]; then
      echo "issue #$number already says this"
    else
      gh issue comment "$number" --body-file "$body"
    fi
    ;;
  close)
    comment=$3
    numbers=$(gh issue list --state open --label "$label" --json number --jq '.[].number')
    for number in $numbers; do
      gh issue close "$number" --comment "$comment"
    done
    ;;
  *)
    echo "usage: $0 open LABEL TITLE BODY_FILE | close LABEL COMMENT" >&2
    exit 2
    ;;
esac
