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

| Component | Description | Standard Streamlit equivalent |
|-----------|-------------|-------------------------------|
| `time_picker` | Clock UI, AM/PM toggle, min/max bounds | `st.time_input` (text field only) |
| `date_time_picker` | Combined date + time in one widget, AM/PM toggle, calendar popover | `st.datetime_input` (text field only) |
| `date_picker` | Calendar popover with format control | `st.date_input` |

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
from datetime import time, datetime, date
from st_mui import time_picker, date_time_picker, date_picker

t = time_picker(
    label="Pick a time",
    value=time(9, 30),
    ampm=True,
    key="my_time",
)

dt = date_time_picker(
    label="Select date & time",
    value=datetime.now(),
    key="my_datetime",
)

d = date_picker(
    label="Pick a date",
    value=date.today(),
    key="my_date",
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
