#!/usr/bin/env bash
# Guard against accidentally shipping development frontend builds.
#
# Each component's production build is a single minified index-*.js entry
# (0.45 - 0.83 MB as of vite 8). A dev build (NODE_ENV=development) leaves the
# bundle unminified at ~2.1 MB and writes a .js.map next to it. The 1.2 MB
# per-file limit sits between the two so a dev build can never ship. Run this
# after `npm run build` in any workflow that packages or tests the built
# assets.
set -euo pipefail

LIMIT_BYTES=1258291 # 1.2 MB
COMPONENTS=(date_picker time_picker date_time_picker date_range_picker date_time_range_picker tree_view)
fail=0

for c in "${COMPONENTS[@]}"; do
  dir="st_mui/$c/frontend/build"
  entries=("$dir"/index-*.js)
  if [ ! -e "${entries[0]}" ] || [ "${#entries[@]}" -ne 1 ]; then
    echo "FAIL: expected exactly one index-*.js entry under $dir/ (the Python side registers js=\"index-*.js\", which must match exactly one file)" >&2
    fail=1
    continue
  fi
  size=$(wc -c <"${entries[0]}")
  if [ "$size" -gt "$LIMIT_BYTES" ]; then
    echo "FAIL: ${entries[0]} is $size bytes (limit $LIMIT_BYTES); looks like a dev build" >&2
    fail=1
  fi
  for f in "$dir"/*.js.map; do
    [ -e "$f" ] || continue
    echo "FAIL: sourcemap $f present; production builds must not emit sourcemaps" >&2
    fail=1
  done
done

if [ "$fail" -eq 0 ]; then
  echo "OK: all ${#COMPONENTS[@]} bundles minified (<=$LIMIT_BYTES bytes), one entry each, no sourcemaps"
fi
exit "$fail"
