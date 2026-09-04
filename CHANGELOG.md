# CHANGELOG


## v0.5.8 (2026-09-04)

### Bug Fixes

- **frontend**: Harden theme, renderer, tree, grid, pickers and controls
  ([`fb596b5`](https://github.com/lperezmo/st-mui/commit/fb596b593970db94f80ddaee237c16b1ef05cec9))

Theme: robust CSS color parsing (space/slash rgb, hsl, 8-digit hex), validated palette with
  fallbacks, fractional border radius, MuiPaper follows secondaryBg.

Renderer: per-component Emotion cache keys, correct Shadow DOM host lookup via getRootNode, clearer
  errors.

TreeView: controlled expanded/selected state with reconciliation, valid-id filtering, empty state,
  aria-label, disabled guards.

DataGrid: order-insensitive selection compare, Set-based id filtering, single-sort/filter clamping,
  scrollable disabled mode, empty-columns guard.

Slider/Rating/Autocomplete: clamped slider with bounds watching and a11y labels, ref-guarded rating
  with empty-label handling, hardened autocomplete equality/labels and render-guard effect.

Pickers: isValid min/max guards, StrictMode-safe usePickerId, memoized range commonProps. Add
  @emotion/cache dep, fix format script, moduleResolution bundler, 16 new vitest cases.


## v0.5.7 (2026-08-30)

### Bug Fixes

- **security**: Scope manual releases to trusted version tags
  ([`ed2f83f`](https://github.com/lperezmo/st-mui/commit/ed2f83f52e55194b9d9806366b267d7332f223b0))


## v0.5.6 (2026-08-30)

### Bug Fixes

- **ci**: Disable shared dependency caches throughout workflows
  ([`c7a7351`](https://github.com/lperezmo/st-mui/commit/c7a73516655d38bd30e36259c20235b45d0bb79c))

- **security**: Isolate publishing from caches and patch dependencies
  ([`b9dca44`](https://github.com/lperezmo/st-mui/commit/b9dca44d122cd0f91f33341d0b23690bd5ff94a7))


## v0.5.5 (2026-08-24)

### Bug Fixes

- **security**: Pin CI actions to immutable commits
  ([`b766949`](https://github.com/lperezmo/st-mui/commit/b766949351e12b0f7b4ac7eb841574f91deb7710))

### Testing

- **security**: Guard every workflow action ref
  ([`1dda23e`](https://github.com/lperezmo/st-mui/commit/1dda23e723c3983a8776200d635329f5013f5b80))


## v0.5.4 (2026-08-12)

### Bug Fixes

- **security**: Validate component state and pin release actions
  ([`62ce411`](https://github.com/lperezmo/st-mui/commit/62ce4112350eba49d552c251b22cc601be55c43a))


## v0.5.3 (2026-07-31)

### Bug Fixes

- Read theme variables from the component host element
  ([`c2b66fa`](https://github.com/lperezmo/st-mui/commit/c2b66fa898ba17bff4eeb7a39600bd500dee12a6))

Streamlit declares its --st-* custom properties on a generated class on each element container, not
  on :root. The theme bridge read them from document.documentElement, where they resolve to empty
  strings, so every lookup silently took its fallback: components rendered with Streamlit's stock
  red primary and light-mode defaults no matter what the app configured.

Read the properties from the element the component renders into, which inherits them, following the
  documented pattern of preferring the shadow host when style isolation is active.

Also key the theme cache on every value the theme is built from. Keying on primary, background, and
  mode alone returned a stale theme when only the text, gray, font, or radius token changed.


## v0.5.2 (2026-07-31)

### Bug Fixes

- Align picker minute options with minutes_step
  ([`e88df74`](https://github.com/lperezmo/st-mui/commit/e88df745439b37b6fade82f17318d997dae2d08d))

MUI validates a picker value against minutesStep, but the digital clock kept listing its own default
  minutes, so a value off the step grid rendered as a red validation error while the offered options
  invited users to pick another one that would fail the same way. Forward the step as timeSteps in
  TimePicker, DateTimePicker, and DateTimeRangePicker.

Leave the default step of 1 on MUI's own spacing. It accepts every minute, so its 5-minute default
  cannot offer an invalid choice, and overriding it would replace a 12-entry minute column with a
  60-entry one for every caller who never set the option.

The showcase also rebuilt its controlled defaults on every rerun: each datetime.now() and
  date.today() call produced a newer value that overwrote the user's in-progress selection, and with
  minutes_step set it drifted off the grid into the same red state. Anchor the demo clock once in
  session state, round it up to the next quarter hour, and give the disable_past demos a day of
  headroom so the default cannot fall into the past while a session stays open.

Document the alignment rule on the picker docstrings and in the README, and fix the usage snippets
  that still paired datetime.now() with minutes_step=15.


## v0.5.1 (2026-07-30)

### Bug Fixes

- Make release lock synchronization fail fast
  ([`f3d7b44`](https://github.com/lperezmo/st-mui/commit/f3d7b44c493b49e399a8e62f64d75a05e4827cbe))


## v0.5.0 (2026-07-30)

### Features

- Expand MIT picker components and harden releases
  ([`0c93705`](https://github.com/lperezmo/st-mui/commit/0c93705175c5d1329291b79cc44ba86e97c3045b))


## v0.4.0 (2026-07-30)

### Bug Fixes

- Expand showcase and restore data grid rendering
  ([`dacaeeb`](https://github.com/lperezmo/st-mui/commit/dacaeeb6ef91a8437bab3750aa19635ffa9592f6))

### Features

- Add interactive MUI components and data grid
  ([`1152b9b`](https://github.com/lperezmo/st-mui/commit/1152b9bc95c72d1b0c227a056f1a221b8d426287))


## v0.3.7 (2026-07-30)

### Bug Fixes

- Correct component behavior
  ([`a8824fc`](https://github.com/lperezmo/st-mui/commit/a8824fc5c0f6296001f3e604c8f756daa9378d17))


## v0.3.6 (2026-07-12)


## v0.3.5 (2026-07-12)

### Bug Fixes

- Ship minified production bundles without sourcemaps
  ([`025b1f1`](https://github.com/lperezmo/st-mui/commit/025b1f1f3cd7d5c3dd89c2256d240676e5f59c7c))

build.mjs treated production as opt-in (NODE_ENV === "production"), but neither publish workflow
  sets NODE_ENV, so every wheel since 0.1.0 has shipped unminified bundles plus sourcemaps (~2.1 MB
  + ~3.9 MB per component instead of ~0.8 MB). Default to production and reserve dev output for the
  build:dev / dev scripts, which set NODE_ENV=development.

Adds scripts/assert_prod_build.sh (ported from st-rsuite) and runs it in both publish workflows so a
  dev build can never ship again: the 1.2 MB per-file limit sits between the largest prod bundle
  (0.83 MB) and the smallest dev bundle (1.4 MB), and any .js.map fails the check.


## v0.3.4 (2026-07-12)

### Bug Fixes

- Defer component registration until first use
  ([`d1297c4`](https://github.com/lperezmo/st-mui/commit/d1297c4347daacd6c579a4ed46f9dc8ec841a4f3))

Importing st_mui eagerly registered all six file-backed components, and registration requires the
  Streamlit runtime's manifest discovery to have run, so import st_mui raised StreamlitAPIException
  in any bare Python context (pytest, REPL, tooling) on every Streamlit version. Defer the component
  imports via PEP 562 module __getattr__ (same pattern as st-rsuite); registration now happens on
  first use inside a running app.

Extends the registration smoke test to guard laziness and per-module registration names, and adds a
  Tests workflow: frontend typecheck, a production-asserted frontend build, and the smoke suite
  across Streamlit 1.51 through latest. Verified locally on 1.51, 1.52, 1.55, and 1.59.

- Remove broken data_grid stub
  ([`6044610`](https://github.com/lperezmo/st-mui/commit/60446102eba1737fe10e7142768d977a966e3a7f))

The data_grid module registered a file-backed CCv2 component with no frontend source, no build
  target, and no entry in the component manifest, so importing st_mui.data_grid always failed at
  registration. It was never exported from st_mui or documented; remove it until a real
  implementation ships.

- Remove orphaned data_grid frontend source
  ([`b15d80b`](https://github.com/lperezmo/st-mui/commit/b15d80bf2d146fdbe4e8d9c62e89dc660184495a))

The TSX imports @mui/x-data-grid, which is not a dependency, so it fails typecheck; build.mjs never
  built it either.

- Support Streamlit 1.51 and 1.52 via isolate_styles compat shim
  ([`987603e`](https://github.com/lperezmo/st-mui/commit/987603eaed09885cc0939e245c16859f64b6ae23))

All six components passed isolate_styles=False to st.components.v2.component(), which only accepts
  it from Streamlit 1.53. On 1.51 and 1.52 (the declared floor is >=1.51) importing st_mui raised a
  TypeError. The new st_mui._compat.component() registers the component and applies
  isolate_styles=False wherever the installed Streamlit expects it: at registration on >=1.53, on
  the per-call renderer on 1.51/1.52. Ported from st-rsuite, which shipped the same fix in 0.3.4.

Adds a browser-less registration smoke test that guards the shim, the package import, and CCv2
  manifest discovery.

### Chores

- Replace broken static.streamlit.io badge with shields.io
  ([`8c5d4a2`](https://github.com/lperezmo/st-mui/commit/8c5d4a27f0421e3206edc1cbe6f1b3abe2bea2c8))

- Resolve all 30 open Dependabot alerts (vite 8 + lockfile bumps)
  ([`c4f1f3c`](https://github.com/lperezmo/st-mui/commit/c4f1f3c7b29c5edf6c1b680ad6a57b92749874ae))

Frontend (npm): - vite ^7.1.12 -> ^8.1.4 and @vitejs/plugin-react ^5.1.0 -> ^6.0.3, removing esbuild
  from the dependency tree entirely - build.mjs: minify via the vite 8 oxc default (the old esbuild
  value is a deprecated separate-install path in vite 8 and breaks the build); drop the
  esbuild-specific minify options block - refresh transitive pins for fast-uri, yaml, postcss,
  picomatch, brace-expansion; @babel/core also leaves the tree

Python (uv.lock): - tornado 6.5.7, GitPython 3.1.50, pillow 12.3.0, urllib3 2.7.0, idna 3.18,
  requests 2.34.2

npm audit: 0 vulnerabilities. Verified npm ci + npm run build (all 6 components) and tsc typecheck
  unchanged from master.


## v0.3.3 (2026-03-15)

### Bug Fixes

- Include new component build assets in package data
  ([`121faf7`](https://github.com/lperezmo/st-mui/commit/121faf767f4e49159f6d40e1bb7893c39effdd7a))

DateRangePicker, DateTimeRangePicker, and TreeView frontend builds were missing from setuptools
  package-data, causing import errors. Example app requirements updated

### Chores

- Update example app requirements
  ([`3d4da6d`](https://github.com/lperezmo/st-mui/commit/3d4da6d5e12dd551f467f7665ccb036cd5b6b4b9))

### Documentation

- Add MUI X Pro license warning to README and showcase app
  ([`bb9f384`](https://github.com/lperezmo/st-mui/commit/bb9f38415bd2703792ae37958df69e603363c351))

MUI refused to provide a dev license for the demo — added a visible disclaimer discouraging Pro
  license purchases and noting that open-source replacements for the Pro range components are on the
  way.


## v0.3.2 (2026-03-15)

### Bug Fixes

- **ci**: Use gh release upload instead of create to avoid duplicate release error
  ([`1e4e69a`](https://github.com/lperezmo/st-mui/commit/1e4e69aafb5693e12d5af261e8ae87f727e87dc9))


## v0.3.1 (2026-03-15)


## v0.3.0 (2026-03-15)

### Bug Fixes

- **ci**: Upgrade actions to Node 24 and fix detached HEAD in release workflow
  ([`76b3183`](https://github.com/lperezmo/st-mui/commit/76b3183653b8d1f88be31a43570e5d53f8eeb6e9))

- Bump checkout, setup-python, setup-node to v6 (Node 24 compatible) - Replace
  python-semantic-release/publish-action with gh release create to avoid "Detached HEAD state cannot
  match any release groups" error

### Features

- Add DateRangePicker, DateTimeRangePicker, TreeView and automated releases
  ([`c6b8288`](https://github.com/lperezmo/st-mui/commit/c6b8288f606c8d593d2026692c10a4bcddb880ec))

Add three new components: - DateRangePicker (Pro) — dual-calendar date range selection -
  DateTimeRangePicker (Pro) — datetime range with start/end time - TreeView (MIT) — hierarchical
  tree with checkbox multi-select

Set up python-semantic-release for automated versioning and PyPI publishing on push to master via
  conventional commits. Existing tag-based publish workflow kept as manual fallback.

Also adds shared MUI X license utility, updates README with all 6 components, and expands the
  showcase app.


## v0.2.5 (2026-03-14)


## v0.2.4 (2026-03-14)

### Bug Fixes

- Bump version to 0.2.4, fix author metadata, disable PyPI attestations
  ([`01b4f28`](https://github.com/lperezmo/st-mui/commit/01b4f28a6ca547499a3ae638f47c15974207d971))

Co-authored-by: lperezmo <61613934+lperezmo@users.noreply.github.com>


## v0.2.2 (2026-03-14)

### Bug Fixes

- Use explicit PEP 621 table format for license field
  ([`214cdd5`](https://github.com/lperezmo/st-mui/commit/214cdd570821a9be318cae5c1045854ff183d129))

Co-authored-by: lperezmo <61613934+lperezmo@users.noreply.github.com>


## v0.2.1 (2026-03-14)


## v0.2.0 (2026-03-14)


## v0.1.0 (2026-03-14)
