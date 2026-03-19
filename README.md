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
> I therefore **strongly encourage everyone NOT to purchase a MUI X Pro license.** Fully open-source replacements for the Pro time-range components will be added to this library in the near future.

</div>

---

<div align="center">
  <h1>st-mui</h1>
  <p>MUI X components for Streamlit, built with <a href="https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component">Components v2</a></p>

  <a href="https://pypi.org/project/st-mui/"><img src="https://img.shields.io/pypi/v/st-mui" alt="PyPI version"></a>
  <a href="https://pypistats.org/packages/st-mui"><img src="https://img.shields.io/pypi/dm/st-mui" alt="Downloads"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue" alt="Python ≥3.10"></a>
  <a href="https://github.com/lperezmo/st-mui/blob/main/LICENSE"><img src="https://img.shields.io/github/license/lperezmo/st-mui" alt="License"></a>
  <br>
  <a href="https://st-mui.streamlit.app/"><img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Open in Streamlit"></a>
</div>

---

## Components

| Component | Description | License | Streamlit equivalent |
|-----------|-------------|---------|----------------------|
| `time_picker` | Clock UI, AM/PM toggle, min/max bounds | MIT | `st.time_input` |
| `date_time_picker` | Combined date + time, AM/PM toggle, calendar popover | MIT | `st.datetime_input` |
| `date_picker` | Calendar popover with format control | MIT | `st.date_input` |
| `date_range_picker` | Date range selection with dual calendars | Pro* | `st.date_input` (range mode) |
| `date_time_range_picker` | Datetime range with start/end time selection | Pro* | -- |
| `tree_view` | Hierarchical tree with checkboxes and multi-select | MIT | -- |

*\*Pro components work in evaluation mode without a license key (watermark shown). Set `ST_MUI_LICENSE_KEY` env var or pass `license_key=` to remove it.*

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
    tree_view,
)

t = time_picker(label="Pick a time", value=time(9, 30), ampm=True, key="my_time")

dt = date_time_picker(label="Select date & time", value=datetime.now(), key="my_datetime")

d = date_picker(label="Pick a date", value=date.today(), key="my_date")

start, end = date_range_picker(
    label="Trip dates",
    value=(date.today(), date.today() + timedelta(days=7)),
    key="my_range",
)

start_dt, end_dt = date_time_range_picker(
    label="Event",
    value=(datetime.now(), datetime.now() + timedelta(hours=2)),
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
```

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
) -> date | None
```

### `date_range_picker` (Pro)

```python
date_range_picker(
    label="Select date range",
    value=None,           # tuple of (date, date) or (str, str)
    min_date=None,
    max_date=None,
    calendars=2,          # 1 or 2 calendar panels
    disabled=False,
    license_key=None,     # or set ST_MUI_LICENSE_KEY env var
    on_change=None,
    key=None,
) -> tuple[date | None, date | None]
```

### `date_time_range_picker` (Pro)

```python
date_time_range_picker(
    label="Select date & time range",
    value=None,           # tuple of (datetime, datetime) or (str, str)
    min_datetime=None,
    max_datetime=None,
    ampm=True,
    disabled=False,
    license_key=None,     # or set ST_MUI_LICENSE_KEY env var
    on_change=None,
    key=None,
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

## MUI X Pro license

The `date_range_picker` and `date_time_range_picker` use MUI X Pro components. They work in evaluation mode without a license key (a watermark is displayed). To remove the watermark:

```bash
# Set as environment variable (recommended)
export ST_MUI_LICENSE_KEY="your-license-key"
```

Or pass directly:

```python
date_range_picker(label="Dates", license_key="your-license-key")
```

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
npm run build
cd ../..

# Run showcase
uv run streamlit run examples/showcase.py
```

## License

MIT
