#!/usr/bin/env bash
# Guard against accidentally shipping development frontend builds.
#
# Each component's production build is one fully minified index-*.js entry.
# Vite's transform minifier and Rolldown's output minifier are both required:
# transform-only output contains `//#region node_modules/` annotations and is
# materially larger. Run this after `npm run build` in every packaging path.
set -euo pipefail

LIMIT_BYTES=1048576       # 1 MiB per component
TOTAL_LIMIT_BYTES=6291456 # 6 MiB across the current ten components
COMPONENTS=(
  date_picker
  time_picker
  date_time_picker
  date_range_picker
  date_time_range_picker
  tree_view
  autocomplete
  slider
  rating
  data_grid
)
fail=0
total_size=0

for c in "${COMPONENTS[@]}"; do
  dir="st_mui/$c/frontend/build"
  entries=("$dir"/index-*.js)
  scripts=("$dir"/*.js)
  if [ ! -e "${entries[0]}" ] || [ "${#entries[@]}" -ne 1 ] \
    || [ ! -e "${scripts[0]}" ] || [ "${#scripts[@]}" -ne 1 ]; then
    echo "FAIL: expected exactly one JS file, named index-*.js, under $dir/" >&2
    fail=1
    continue
  fi
  size=$(wc -c <"${entries[0]}")
  total_size=$((total_size + size))
  if [ "$size" -gt "$LIMIT_BYTES" ]; then
    echo "FAIL: ${entries[0]} is $size bytes (limit $LIMIT_BYTES); output is not fully minified" >&2
    fail=1
  fi
  if grep -Fq '//#region node_modules/' "${entries[0]}"; then
    echo "FAIL: ${entries[0]} contains Rolldown region annotations; output minification is disabled" >&2
    fail=1
  fi
  # Community MUI itself mentions @mui/x-date-pickers-pro in one adapter error
  # message, so that package-name string alone is not evidence of Pro code.
  if grep -Eq 'react\.development\.js|sourceMappingURL|@mui/x-license|__MUI_LICENSE_INFO__|MUI X:.*license key' "${entries[0]}"; then
    echo "FAIL: ${entries[0]} contains development, sourcemap, or commercial-license runtime markers" >&2
    fail=1
  fi
  for f in "$dir"/*.js.map; do
    [ -e "$f" ] || continue
    echo "FAIL: sourcemap $f present; production builds must not emit sourcemaps" >&2
    fail=1
  done
done

if grep -REq \
  '@mui/x-date-pickers-pro|@mui/x-license|__MUI_LICENSE_INFO__' \
  st_mui/frontend/src st_mui/frontend/package.json st_mui/frontend/package-lock.json; then
  echo "FAIL: frontend sources or dependency manifests still reference the commercial MUI runtime" >&2
  fail=1
fi

if [ "$total_size" -gt "$TOTAL_LIMIT_BYTES" ]; then
  echo "FAIL: production JS totals $total_size bytes (limit $TOTAL_LIMIT_BYTES)" >&2
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "OK: all ${#COMPONENTS[@]} bundles fully minified ($total_size bytes total), one entry each, no sourcemaps or commercial runtime"
fi
exit "$fail"
