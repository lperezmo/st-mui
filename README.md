<div align="center">
<table><tr><td bgcolor="#fff3cd" align="center">
<h3>Looking for a fully open-source alternative?</h3>
<p>Check out <a href="https://github.com/lperezmo/st-rsuite"><b>st-rsuite</b></a> — and try the <a href="https://rsuite.streamlit.app"><b>sample app</b></a>!</p>
</td></tr></table>
</div>

---

<div align="center">

> **WARNING — MUI X Pro Licensing**
>
> MUI was contacted and asked to provide a development/demo license solely to run the showcase app without displaying a watermark. **They refused.**
>
> I therefore **strongly encourage everyone NOT to purchase a MUI X Pro license.** `st-mui` no longer ships MUI X Pro: both range widgets are implemented with MIT-licensed Community pickers and require no license key.

</div>

---

<div align="center">
  <img src="https://raw.githubusercontent.com/lperezmo/st-mui/master/assets/logo.svg" alt="st-mui logo" width="380">

  <h1>st-mui</h1>
  <p>Material UI and MUI X components for Streamlit, built with <a href="https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component">Components v2</a></p>

  <a href="https://pypi.org/project/st-mui/"><img src="https://img.shields.io/pypi/v/st-mui" alt="PyPI version"></a>
  <a href="https://pypistats.org/packages/st-mui"><img src="https://img.shields.io/pypi/dm/st-mui" alt="Downloads"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue" alt="Python ≥3.10"></a>
  <a href="https://github.com/lperezmo/st-mui/blob/main/LICENSE"><img src="https://img.shields.io/github/license/lperezmo/st-mui" alt="License"></a>
  <br>
  <a href="https://st-mui.streamlit.app/"><img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white" alt="Open in Streamlit"></a>
</div>

---

## Components

| Component | Description | License | Streamlit equivalent |
|-----------|-------------|---------|----------------------|
| `time_picker` | Clock UI, AM/PM toggle, min/max bounds | MIT | `st.time_input` |
| `date_time_picker` | Combined date + time, AM/PM toggle, calendar popover | MIT | `st.date_input` + `st.time_input` |
| `date_picker` | Calendar popover with format control | MIT | `st.date_input` |
| `date_range_picker` | Validated start/end date selection | MIT | `st.date_input` (range mode) |
| `date_time_range_picker` | Validated start/end datetime selection | MIT | -- |
| `tree_view` | Hierarchical tree with checkboxes and multi-select | MIT | -- |
| `autocomplete` | Searchable single/multi-select and free-form entry | MIT | `st.selectbox` / `st.multiselect` |
| `slider` | Numeric single-value and range slider with marks | MIT | `st.slider` |
| `rating` | Accessible star rating with fractional precision | MIT | -- |
| `data_grid` | Sortable, filterable, pageable Community Data Grid | MIT | `st.dataframe` |

## Installation

```bash
uv add st-mui
```

or with pip:

```bash
pip install st-mui
```

## Quick start

```python
import streamlit as st
from datetime import time, datetime, date, timedelta
from st_mui import (
    time_picker, date_time_picker, date_picker,
    date_range_picker, date_time_range_picker,
    tree_view, autocomplete, slider, rating, data_grid,
)

t = time_picker(label="Pick a time", value=time(9, 30), ampm=True, key="my_time")

# A default recomputed on every rerun replaces the user's in-progress
# selection, so anchor dynamic values in session state.
if "start" not in st.session_state:
    st.session_state["start"] = datetime.now().replace(second=0, microsecond=0)
start_value = st.session_state["start"]

dt = date_time_picker(label="Select date & time", value=start_value, key="my_datetime")

d = date_picker(label="Pick a date", value=date.today(), key="my_date")

start, end = date_range_picker(
    label="Trip dates",
    value=(date.today(), date.today() + timedelta(days=7)),
    key="my_range",
)

start_dt, end_dt = date_time_range_picker(
    label="Event",
    value=(start_value, start_value + timedelta(hours=2)),
    key="my_dt_range",
)

selected = tree_view(
    items=[
        {"id": "docs", "label": "Documents", "children": [
            {"id": "resume", "label": "Resume.pdf"},
        ]},
        {"id": "photos", "label": "Photos"},
    ],
    checkbox_selection=True,
    multi_select=True,
    key="my_tree",
)

destination = autocomplete(
    [{"label": "Los Angeles", "value": "LAX"}, "Other"],
    label="Destination",
    key="destination",
)

price_range = slider(
    "Price range", value=(20, 80), min_value=0, max_value=100, key="price"
)

score = rating("Score", value=4.5, precision=0.5, key="score")

grid_state = data_grid(
    rows=[{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}],
    columns=["name"],
    checkbox_selection=True,
    key="people",
)
```

## Behavior notes

- Date-time pickers represent browser-local wall-clock values and return
  timezone-naive Python `datetime` objects. This avoids silently shifting a
  selected time to UTC and works consistently on every supported Python
  version, including Python 3.10. Any timezone information on input values is
  intentionally ignored.
- The range picker `on_change` callback runs once when either the start or end
  value changes.
- `minutes_step` constrains which minutes the picker accepts, so a `value`
  whose minute is not a multiple of the step renders in a validation error
  state. Round dynamic defaults such as `datetime.now()` up to the next
  boundary, and hold them in `st.session_state` so a rerun does not replace
  the user's in-progress selection.
- All five date/time widgets support helper text, clearability, read-only mode,
  past/future guards, configurable initial/available views, and keyboard input.
  Date widgets can show ISO week numbers; time widgets support minute-step and
  display-format controls.
- Range widgets are composed from two MIT Community fields and enforce start ≤
  end in both the browser and Python. Historical `license_key` and `calendars`
  arguments remain accepted as compatibility shims but are no longer used.
- `tree_view(disabled=True)` disables selection and expansion for every item.
- `autocomplete` values are JSON-safe strings, numbers, or booleans. Dictionary
  options let display labels differ from returned values. Integer values must
  fit JavaScript's exact integer range.
- A two-item `slider` value enables range mode. Slider state is committed when
  the drag ends rather than on every pixel moved. With `step=None`, provide a
  non-empty marks list and use marked values for the initial selection.
  `marks=True` is capped at 1,000 generated marks; use explicit marks for
  larger numeric ranges.
- `rating` precision must be from `0.01` through `1`, divide one star into an
  integer number of steps, and align with the selected value.
- `data_grid` uses the MIT Community package only. Its single `on_change`
  callback covers selection, sorting, filtering, and pagination. Community
  pagination is limited to 100 rows per page.

## API

### `time_picker`

```python
time_picker(
    label="Select a time",
    value=None,           # time object or HH:MM string
    ampm=True,            # 12-hour vs 24-hour
    min_time=None,
    max_time=None,
    disabled=False,
    on_change=None,
    key=None,
    *,
    helper_text=None,
    clearable=True,
    read_only=False,
    disable_past=False,
    disable_future=False,
    open_to=None,        # "hours", "minutes", or "seconds"
    views=None,
    minutes_step=1,
    format=None,
) -> time | None
```

### `date_time_picker`

```python
date_time_picker(
    label="Select date & time",
    value=None,           # datetime object or ISO string
    min_datetime=None,
    max_datetime=None,
    ampm=True,
    disabled=False,
    on_change=None,
    key=None,
    *,
    helper_text=None,
    clearable=True,
    read_only=False,
    disable_past=False,
    disable_future=False,
    open_to=None,
    views=None,          # year/month/day/hours/minutes/seconds
    minutes_step=1,
    format=None,
) -> datetime | None
```

### `date_picker`

```python
date_picker(
    label="Select a date",
    value=None,           # date object or YYYY-MM-DD string
    min_date=None,
    max_date=None,
    format="MM/DD/YYYY",  # MUI format tokens
    disabled=False,
    on_change=None,
    key=None,
    *,
    helper_text=None,
    clearable=True,
    read_only=False,
    disable_past=False,
    disable_future=False,
    open_to=None,        # "year", "month", or "day"
    views=None,
    display_week_number=False,
) -> date | None
```

### `date_range_picker`

```python
date_range_picker(
    label="Select date range",
    value=None,           # tuple of (date, date) or (str, str)
    min_date=None,
    max_date=None,
    calendars=2,          # deprecated compatibility argument
    disabled=False,
    license_key=None,     # deprecated compatibility argument
    on_change=None,
    key=None,
    *,
    start_label=None,
    end_label=None,
    format="MM/DD/YYYY",
    helper_text=None,
    clearable=False,
    read_only=False,
    disable_past=False,
    disable_future=False,
    open_to=None,
    views=None,
    display_week_number=False,
) -> tuple[date | None, date | None]
```

### `date_time_range_picker`

```python
date_time_range_picker(
    label="Select date & time range",
    value=None,           # tuple of (datetime, datetime) or (str, str)
    min_datetime=None,
    max_datetime=None,
    ampm=True,
    disabled=False,
    license_key=None,     # deprecated compatibility argument
    on_change=None,
    key=None,
    *,
    start_label=None,
    end_label=None,
    format=None,
    helper_text=None,
    clearable=False,
    read_only=False,
    disable_past=False,
    disable_future=False,
    open_to=None,
    views=None,
    minutes_step=1,
) -> tuple[datetime | None, datetime | None]
```

### `tree_view`

```python
tree_view(
    items=None,           # list of {"id", "label", "children": [...]}
    label=None,
    multi_select=False,
    checkbox_selection=True,
    default_expanded=None,
    default_selected=None,
    disabled=False,
    on_change=None,
    key=None,
) -> list[str]  # selected item IDs
```

### `autocomplete`

```python
autocomplete(
    options=None,        # scalars or {"label", "value", "disabled"} mappings
    label="Select an option",
    value=None,
    multiple=False,
    free_solo=False,
    placeholder=None,
    helper_text=None,
    clearable=True,
    disabled=False,
    on_change=None,
    key=None,
) -> str | int | float | bool | list | None
```

### `slider`

```python
slider(
    label="Select a value",
    value=None,          # number or two-number sequence for range mode
    min_value=0,
    max_value=100,
    step=1,             # None enables marks-only selection
    marks=False,        # bool or [{"value": 0, "label": "Low"}, ...]
    value_label_display="auto",
    disabled=False,
    on_change=None,
    key=None,
) -> int | float | tuple[int | float, int | float]
```

### `rating`

```python
rating(
    label="Rating",
    value=None,
    max_value=5,         # integer from 1 through 100
    precision=1.0,       # 1/n from 0.01 through 1; value must align
    size="medium",      # "small", "medium", or "large"
    disabled=False,
    read_only=False,
    clearable=True,
    on_change=None,
    key=None,
) -> float | None
```

### `data_grid` (Community)

```python
data_grid(
    rows=None,           # records or a DataFrame containing the id field
    columns=None,        # field names or supported column mappings
    id_field="id",
    selected_rows=None,
    sort_model=None,
    filter_model=None,
    page_size=10,        # Community edition maximum: 100
    page_size_options=(10, 25, 50, 100),
    height=400,
    checkbox_selection=False,
    density="standard",
    disabled=False,
    on_change=None,
    key=None,
) -> dict  # selection, sort, filter, and pagination models
```

The Community Data Grid supports JSON-safe rows, unique string/numeric row IDs,
column types `string`, `number`, `boolean`, and `singleSelect`, plus Pythonic
column aliases such as `header_name`, `min_width`, and `value_options`.

## Range picker migration

The range widgets use paired MIT-licensed Community fields. Applications
upgrading from 0.4.0 can keep passing `license_key` or `calendars` while they
remove those arguments; both are ignored and `license_key` emits a
`DeprecationWarning`. No MUI X license environment variable is read or bundled.

## Running the example

```bash
pip install st-mui
streamlit run examples/showcase.py
```

## Development

```bash
# Clone and install
git clone https://github.com/lperezmo/st-mui.git
cd st-mui
uv sync --dev

# Build frontend
cd st_mui/frontend
npm install
npm test
npm run typecheck
npm run build
cd ../..

# Run Python tests
uv run --with pytest pytest

# Run showcase
uv run streamlit run examples/showcase.py
```

## License

MIT
