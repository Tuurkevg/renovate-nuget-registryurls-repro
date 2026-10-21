#!/usr/bin/env bash
# Usage: bash run.sh [renovate-version ...]   (default: 44.171.1 44.171.2)
# Needs: docker, python3, internet access (to pull images and, when the bug triggers, to reach api.nuget.org).
set -u
cd "$(dirname "$0")"
VERSIONS=("$@"); [ ${#VERSIONS[@]} -eq 0 ] && VERSIONS=(44.171.1 44.171.2)
python3 mockfeed.py 8099 feed-requests.log > mock.out 2>&1 &
MOCK=$!; trap 'kill $MOCK 2>/dev/null' EXIT; sleep 1
for V in "${VERSIONS[@]}"; do
  : > feed-requests.log
  docker run --rm --network host -v "$PWD/repo:/repo" -v "$PWD/config.js:/cfg/config.js:ro" -w /repo \
    -e RENOVATE_CONFIG_FILE=/cfg/config.js -e LOG_LEVEL=debug renovate/renovate:$V --platform=local > "run-$V.log" 2>&1
  n=$(wc -l < feed-requests.log)
  echo "== renovate $V: requests to the configured feed = $n"
  grep -a -E '"registryUrl":|"branchName": "renovate/|Failed to look up nuget' "run-$V.log" | sed -E 's/^ +//; s/ \(repository.*//' | sort -u
done
