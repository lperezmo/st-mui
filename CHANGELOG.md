# CHANGELOG


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
