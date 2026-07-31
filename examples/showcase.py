"""
st-mui Showcase
===============
Interactive demo of Material UI and MUI X components for Streamlit,
with side-by-side comparisons against standard widgets.
"""

# Picker values intentionally use naive local wall-clock datetimes.
# ruff: noqa: DTZ001, DTZ005

from datetime import date, datetime, time, timedelta
from functools import partial

import streamlit as st

from st_mui import (
    autocomplete,
    data_grid,
    date_picker,
    date_range_picker,
    date_time_picker,
    date_time_range_picker,
    rating,
    slider,
    time_picker,
    tree_view,
)

# -- Page config -------------------------------------------------------------
st.set_page_config(
    page_title="st-mui | MUI X for Streamlit",
    page_icon=":material/widgets:",
    layout="wide",
)

st.markdown(
    """<style>
    .block-container {
        padding-top: 1rem;
    }
</style>""",
    unsafe_allow_html=True,
)

# -- Helpers: branded column banners -----------------------------------------
_IS_DARK = st.context.theme.type == "dark"

_MUI_BANNER_LIGHT = """
<div style="
    background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
    color: white;
    padding: 0.55rem 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
    font-size: 0.85rem;
    display: flex; align-items: center; gap: 0.5rem;
    box-shadow: 0 2px 8px rgba(99,102,241,0.25);
">&#9670; st-mui</div>
"""

_MUI_BANNER_DARK = """
<div style="
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
    color: white;
    padding: 0.55rem 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
    font-size: 0.85rem;
    display: flex; align-items: center; gap: 0.5rem;
    box-shadow: 0 2px 12px rgba(99,102,241,0.35);
">&#9670; st-mui</div>
"""

_ST_BANNER_LIGHT = """
<div style="
    background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
    color: white;
    padding: 0.55rem 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
    font-size: 0.85rem;
    display: flex; align-items: center; gap: 0.5rem;
    box-shadow: 0 2px 8px rgba(100,116,139,0.25);
">&#9671; Streamlit built-in</div>
"""

_ST_BANNER_DARK = """
<div style="
    background: linear-gradient(135deg, #475569 0%, #64748b 100%);
    color: #e2e8f0;
    padding: 0.55rem 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
    font-size: 0.85rem;
    display: flex; align-items: center; gap: 0.5rem;
    box-shadow: 0 2px 12px rgba(71,85,105,0.35);
">&#9671; Streamlit built-in</div>
"""


def _banner_mui():
    st.html(_MUI_BANNER_DARK if _IS_DARK else _MUI_BANNER_LIGHT)


def _banner_st():
    st.html(_ST_BANNER_DARK if _IS_DARK else _ST_BANNER_LIGHT)


def _record_change(component_name):
    """Make callback behavior visible without coupling it to widget state."""
    state_key = f"_showcase_{component_name}_changes"
    st.session_state[state_key] = st.session_state.get(state_key, 0) + 1


def _change_callback(component_name):
    return partial(_record_change, component_name)


def _change_count(component_name):
    count = st.session_state.get(f"_showcase_{component_name}_changes", 0)
    st.caption(f"`on_change` callbacks observed this session: **{count}**")


def _ceil_to_quarter_hour(value: datetime) -> datetime:
    """Return the first :00, :15, :30, or :45 boundary at or after ``value``.

    Pickers configured with ``minutes_step=15`` reject a value whose minute is
    not a multiple of 15, so an unaligned default renders as a red validation
    error instead of a usable widget.
    """
    truncated = value.replace(second=0, microsecond=0)
    if truncated < value:
        truncated += timedelta(minutes=1)
    return truncated + timedelta(minutes=-truncated.minute % 15)


# Dynamic defaults must stay stable across Streamlit reruns. A fresh
# datetime.now() on every rerun feeds the components a newer controlled value,
# which overwrites whatever the user is in the middle of selecting.
if "_showcase_datetime_anchor" not in st.session_state:
    st.session_state["_showcase_datetime_anchor"] = datetime.now().replace(
        second=0, microsecond=0
    )
_SHOWCASE_NOW = st.session_state["_showcase_datetime_anchor"]
_SHOWCASE_QUARTER_HOUR = _ceil_to_quarter_hour(_SHOWCASE_NOW)
_SHOWCASE_TODAY = _SHOWCASE_NOW.date()

# Demos that combine disable_past with a frozen anchor need enough headroom
# that the default stays in the future for the whole session. An hour of slack
# would put the value back in the past, and back in the red, after an hour.
_SHOWCASE_APPOINTMENT = _SHOWCASE_QUARTER_HOUR + timedelta(days=1)


# -- Header ------------------------------------------------------------------
_HEADER_GRADIENT = (
    "linear-gradient(135deg, #818cf8, #c4b5fd)"
    if _IS_DARK
    else "linear-gradient(135deg, #6366f1, #a78bfa)"
)
st.html(f"""
<div style="text-align:center; padding:1.5rem 0 0.5rem;">
    <h1 style="
        margin:0; font-size:2.5rem; font-weight:800;
        background:{_HEADER_GRADIENT};
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-clip:text;
    ">st-mui</h1>
    <p style="margin:0.4rem 0 0; font-size:1rem; opacity:0.7;">
        Material UI components for Streamlit, powered by Components v2
    </p>
</div>
""")

st.caption(
    ":violet[**10 interactive widgets**] · "
    ":blue[**5 expanded picker APIs**] · "
    ":green[**100% MIT widget licenses**] · "
    ":orange[**No Pro range runtime**]",
    text_alignment="center",
)

# -- Sidebar: global controls ------------------------------------------------
with st.sidebar:
    st.header("Global Settings")
    disabled = st.toggle("Disable all components", value=False)
    st.caption(
        "Use this to verify disabled and read-only interaction handling across "
        "the whole gallery."
    )
    st.divider()
    st.markdown(
        "**st-mui** brings production-grade Material UI components to Streamlit "
        "using the new Components v2 API."
    )
    st.markdown("Components included:")
    st.markdown("- :material/schedule: TimePicker")
    st.markdown("- :material/calendar_month: DateTimePicker")
    st.markdown("- :material/event: DatePicker")
    st.markdown("- :material/date_range: DateRangePicker (Community)")
    st.markdown("- :material/date_range: DateTimeRangePicker (Community)")
    st.markdown("- :material/account_tree: TreeView")
    st.markdown("- :material/search: Autocomplete")
    st.markdown("- :material/tune: Slider")
    st.markdown("- :material/star: Rating")
    st.markdown("- :material/table_view: DataGrid (Community)")
    st.divider()
    st.markdown("**Feature tour**")
    st.markdown(
        "The picker tabs cover paired MIT ranges, helper text, clearability, "
        "read-only mode, validation guards, views, formats, week numbers, and "
        "minute steps. The remaining tabs cover every advanced widget mode."
    )

# -- Tabs for each component -------------------------------------------------
(
    tab_time,
    tab_datetime,
    tab_date,
    tab_daterange,
    tab_dtrange,
    tab_tree,
    tab_autocomplete,
    tab_slider,
    tab_rating,
    tab_grid,
) = st.tabs(
    [
        ":material/schedule: TimePicker",
        ":material/calendar_month: DateTimePicker",
        ":material/event: DatePicker",
        ":material/date_range: DateRangePicker",
        ":material/date_range: DTRangePicker",
        ":material/account_tree: TreeView",
        ":material/search: Autocomplete",
        ":material/tune: Slider",
        ":material/star: Rating",
        ":material/table_view: DataGrid",
    ]
)

# ============================================================================
# TIME PICKER TAB
# ============================================================================
with tab_time:
    st.subheader("TimePicker")
    st.markdown("A time picker with clock UI, AM/PM support, and keyboard input.")

    # -- 12-hour AM/PM comparison --
    st.markdown("#### 12-hour (AM/PM)")

    with st.container(horizontal=True):
        _banner_mui()
        t_mui1 = time_picker(
            label="Pick a time",
            value=time(9, 30),
            ampm=True,
            disabled=disabled,
            key="tp_12h",
        )
        st.code(f"Selected: {t_mui1}")

    with st.container(horizontal=True):
        _banner_st()
        t_st1 = st.time_input(
            "Pick a time",
            value=time(9, 30),
            disabled=disabled,
            key="st_time_12h",
        )
        st.code(f"Selected: {t_st1}")

    st.divider()

    # -- 24-hour with bounds comparison --
    st.markdown("#### 24-hour with bounds")

    with st.container(horizontal=True):
        _banner_mui()
        t_mui2 = time_picker(
            label="Business hours only",
            value=time(14, 0),
            ampm=False,
            min_time=time(8, 0),
            max_time=time(17, 0),
            minutes_step=15,
            format="HH:mm",
            helper_text="Quarter-hour appointments from 08:00 to 17:00",
            disabled=disabled,
            key="tp_24h",
        )
        st.code(f"Selected: {t_mui2}")

    with st.container(horizontal=True):
        _banner_st()
        t_st2 = st.time_input(
            "Business hours only",
            value=time(14, 0),
            disabled=disabled,
            key="st_time_24h",
        )
        st.code(f"Selected: {t_st2}")

    st.divider()
    st.markdown("#### Read-only view with a focused clock flow")
    _banner_mui()
    t_mui3 = time_picker(
        label="Recorded handoff",
        value=time(16, 45),
        ampm=False,
        helper_text="Read-only, non-clearable, and opened directly to minutes.",
        clearable=False,
        read_only=True,
        open_to="minutes",
        views=["hours", "minutes"],
        minutes_step=15,
        disabled=disabled,
        key="tp_read_only",
    )
    st.code(f"Selected: {t_mui3}")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import time_picker
from datetime import time

selected = time_picker(
    label="Pick a time",
    value=time(9, 30),
    ampm=True,
    min_time=time(8, 0),
    max_time=time(17, 0),
    minutes_step=15,
    format="HH:mm",
    helper_text="Business hours",
    clearable=True,
    key="my_time",
)""",
            language="python",
        )

# ============================================================================
# DATETIME PICKER TAB
# ============================================================================
with tab_datetime:
    st.subheader("DateTimePicker")
    st.markdown(
        "Combined date and time selection in a single component with "
        "AM/PM toggle, calendar popover, and rich keyboard navigation."
    )

    # -- Basic --
    st.markdown("#### Basic")

    with st.container(horizontal=True):
        _banner_mui()
        dt_mui1 = date_time_picker(
            label="Select date & time",
            value=_SHOWCASE_NOW,
            disabled=disabled,
            key="dtp_basic",
        )
        st.code(f"Selected: {dt_mui1}")

    with st.container(horizontal=True):
        _banner_st()
        dt_st1_date = st.date_input(
            "Select date",
            value=_SHOWCASE_NOW.date(),
            disabled=disabled,
            key="st_dt_basic_date",
        )
        dt_st1_time = st.time_input(
            "Select time",
            value=_SHOWCASE_NOW.time(),
            disabled=disabled,
            key="st_dt_basic_time",
        )
        dt_st1 = datetime.combine(dt_st1_date, dt_st1_time)
        st.code(f"Selected: {dt_st1}")

    st.divider()

    # -- With bounds --
    st.markdown("#### With bounds")

    with st.container(horizontal=True):
        _banner_mui()
        dt_mui2 = date_time_picker(
            label="Next 7 days only",
            value=_SHOWCASE_APPOINTMENT,
            min_datetime=_SHOWCASE_QUARTER_HOUR,
            max_datetime=_SHOWCASE_QUARTER_HOUR + timedelta(days=7),
            ampm=False,
            helper_text="Future appointments in 15-minute increments",
            disable_past=True,
            open_to="hours",
            views=["day", "hours", "minutes"],
            minutes_step=15,
            format="DD MMM YYYY HH:mm",
            disabled=disabled,
            key="dtp_bounded",
        )
        st.code(f"Selected: {dt_mui2}")

    with st.container(horizontal=True):
        _banner_st()
        dt_st2_date = st.date_input(
            "Next 7 days",
            value=_SHOWCASE_APPOINTMENT.date(),
            min_value=_SHOWCASE_QUARTER_HOUR.date(),
            max_value=(_SHOWCASE_QUARTER_HOUR + timedelta(days=7)).date(),
            disabled=disabled,
            key="st_dt_bounded_date",
        )
        dt_st2_time = st.time_input(
            "Appointment time",
            value=_SHOWCASE_APPOINTMENT.time(),
            step=timedelta(minutes=15),
            disabled=disabled,
            key="st_dt_bounded_time",
        )
        dt_st2 = datetime.combine(dt_st2_date, dt_st2_time)
        st.code(f"Selected: {dt_st2}")

    st.divider()
    st.markdown("#### Read-only timestamp")
    _banner_mui()
    dt_mui3 = date_time_picker(
        label="Deployment recorded",
        value=datetime(2026, 7, 30, 16, 45),
        helper_text="The value is visible but cannot be edited or cleared.",
        clearable=False,
        read_only=True,
        disabled=disabled,
        key="dtp_read_only",
    )
    st.code(f"Selected: {dt_mui3}")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import date_time_picker
from datetime import datetime, timedelta

# minutes_step=15 means the value must land on a quarter hour, and the anchor
# must be stable or every rerun replaces the user's in-progress selection.
if "anchor" not in st.session_state:
    now = datetime.now().replace(second=0, microsecond=0)
    st.session_state["anchor"] = now + timedelta(minutes=-now.minute % 15)
anchor = st.session_state["anchor"]

selected = date_time_picker(
    label="Select date & time",
    value=anchor + timedelta(days=1),
    min_datetime=anchor,
    max_datetime=anchor + timedelta(days=7),
    ampm=False,
    disable_past=True,
    views=["day", "hours", "minutes"],
    open_to="hours",
    minutes_step=15,
    format="DD MMM YYYY HH:mm",
    helper_text="Next seven days",
    key="my_datetime",
)""",
            language="python",
        )

# ============================================================================
# DATE PICKER TAB
# ============================================================================
with tab_date:
    st.subheader("DatePicker")
    st.markdown(
        "A date picker with calendar popover, keyboard navigation, and validation."
    )

    # -- Basic comparison --
    st.markdown("#### Basic")

    with st.container(horizontal=True):
        _banner_mui()
        d_mui1 = date_picker(
            label="Pick any date",
            value=_SHOWCASE_TODAY,
            disabled=disabled,
            key="dp_basic",
        )
        st.code(f"Selected: {d_mui1}")

    with st.container(horizontal=True):
        _banner_st()
        d_st1 = st.date_input(
            "Pick any date",
            value=_SHOWCASE_TODAY,
            disabled=disabled,
            key="st_date_basic",
        )
        st.code(f"Selected: {d_st1}")

    st.divider()

    # -- With bounds comparison --
    st.markdown("#### With bounds")

    with st.container(horizontal=True):
        _banner_mui()
        d_mui2 = date_picker(
            label="This year only",
            min_date=date(2026, 1, 1),
            max_date=date(2026, 12, 31),
            disabled=disabled,
            key="dp_bounded",
        )
        st.code(f"Selected: {d_mui2}")

    with st.container(horizontal=True):
        _banner_st()
        d_st2 = st.date_input(
            "This year only",
            min_value=date(2026, 1, 1),
            max_value=date(2026, 12, 31),
            disabled=disabled,
            key="st_date_bounded",
        )
        st.code(f"Selected: {d_st2}")

    st.divider()

    # -- Custom format --
    st.markdown("#### Custom format")

    with st.container(horizontal=True):
        _banner_mui()
        d_mui3 = date_picker(
            label="DD/MM/YYYY format",
            value=date(2026, 3, 14),
            format="DD/MM/YYYY",
            helper_text="Includes ISO week numbers and opens on month selection.",
            clearable=False,
            open_to="month",
            views=["year", "month", "day"],
            display_week_number=True,
            disabled=disabled,
            key="dp_format",
        )
        st.code(f"Selected: {d_mui3}")

    with st.container(horizontal=True):
        _banner_st()
        d_st3 = st.date_input(
            "DD/MM/YYYY format",
            value=date(2026, 3, 14),
            format="DD/MM/YYYY",
            disabled=disabled,
            key="st_date_format",
        )
        st.code(f"Selected: {d_st3}")

    st.divider()
    st.markdown("#### Future-only read-only date")
    _banner_mui()
    d_mui4 = date_picker(
        label="Next review",
        value=_SHOWCASE_TODAY + timedelta(days=30),
        helper_text="Past dates are disabled; this value is read-only.",
        read_only=True,
        disable_past=True,
        disable_future=False,
        disabled=disabled,
        key="dp_read_only",
    )
    st.code(f"Selected: {d_mui4}")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import date_picker
from datetime import date

selected = date_picker(
    label="Pick a date",
    value=_SHOWCASE_TODAY,
    min_date=date(2026, 1, 1),
    max_date=date(2026, 12, 31),
    format="MM/DD/YYYY",
    helper_text="Pick a date this year",
    clearable=True,
    views=["year", "month", "day"],
    open_to="month",
    display_week_number=True,
    key="my_date",
)""",
            language="python",
        )

# ============================================================================
# DATE RANGE PICKER TAB
# ============================================================================
with tab_daterange:
    st.subheader("DateRangePicker (MIT Community)")
    st.markdown(
        "Two controlled MUI X Community fields provide an entirely MIT-licensed "
        "range workflow with cross-field validation and one composite callback."
    )
    st.success("No Pro package, license key, watermark, or license runtime is shipped.")

    # -- Basic --
    st.markdown("#### Future trip with custom labels and callback")

    with st.container(horizontal=True):
        _banner_mui()
        dr = date_range_picker(
            label="Trip dates",
            value=(_SHOWCASE_TODAY, _SHOWCASE_TODAY + timedelta(days=7)),
            start_label="Depart",
            end_label="Return",
            helper_text="The return date can never precede departure.",
            clearable=True,
            disable_past=True,
            on_change=_change_callback("date_range"),
            disabled=disabled,
            key="drp_basic",
        )
        st.code(f"Start: {dr[0]}  End: {dr[1]}")
        _change_count("date_range")

    with st.container(horizontal=True):
        _banner_st()
        dr_st = st.date_input(
            "Trip dates",
            value=(_SHOWCASE_TODAY, _SHOWCASE_TODAY + timedelta(days=7)),
            disabled=disabled,
            key="st_daterange_basic",
        )
        if isinstance(dr_st, tuple) and len(dr_st) == 2:
            st.code(f"Start: {dr_st[0]}  End: {dr_st[1]}")
        else:
            st.code(f"Selected: {dr_st}")

    st.divider()

    # -- With bounds and display controls --
    st.markdown("#### Bounded range with format, views, and week numbers")

    with st.container(horizontal=True):
        _banner_mui()
        dr2 = date_range_picker(
            label="Release window",
            value=(date(2026, 8, 3), date(2026, 8, 14)),
            min_date=date(2026, 8, 1),
            max_date=date(2026, 8, 31),
            format="DD MMM YYYY",
            open_to="day",
            views=["month", "day"],
            display_week_number=True,
            disabled=disabled,
            key="drp_bounded",
        )
        st.code(f"Start: {dr2[0]}  End: {dr2[1]}")

    with st.container(horizontal=True):
        _banner_st()
        dr2_st = st.date_input(
            "Release window",
            value=(date(2026, 8, 3), date(2026, 8, 14)),
            min_value=date(2026, 8, 1),
            max_value=date(2026, 8, 31),
            disabled=disabled,
            key="st_daterange_bounded",
        )
        if isinstance(dr2_st, tuple) and len(dr2_st) == 2:
            st.code(f"Start: {dr2_st[0]}  End: {dr2_st[1]}")
        else:
            st.code(f"Selected: {dr2_st}")

    st.divider()
    st.markdown("#### Read-only policy window")
    _banner_mui()
    dr3 = date_range_picker(
        label="Policy period",
        value=(date(2026, 1, 1), date(2026, 12, 31)),
        helper_text="Read-only and non-clearable.",
        clearable=False,
        read_only=True,
        disable_future=False,
        disabled=disabled,
        key="drp_read_only",
    )
    st.code(f"Start: {dr3[0]}  End: {dr3[1]}")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import date_range_picker
from datetime import date, timedelta

start, end = date_range_picker(
    label="Trip dates",
    value=(_SHOWCASE_TODAY, _SHOWCASE_TODAY + timedelta(days=7)),
    min_date=date(2026, 1, 1),
    max_date=date(2026, 12, 31),
    start_label="Depart",
    end_label="Return",
    helper_text="Return must follow departure",
    clearable=True,
    views=["month", "day"],
    display_week_number=True,
    on_change=handle_change,
    key="my_range",
)""",
            language="python",
        )

# ============================================================================
# DATE TIME RANGE PICKER TAB
# ============================================================================
with tab_dtrange:
    st.subheader("DateTimeRangePicker (MIT Community)")
    st.markdown(
        "A paired Community DateTimePicker keeps timezone-naive wall-clock "
        "semantics while enforcing an ordered interval."
    )
    st.success("This range widget is MIT-only and has no commercial runtime.")

    # -- Basic --
    st.markdown("#### Meeting window with callback")

    with st.container(horizontal=True):
        _banner_mui()
        dtr = date_time_range_picker(
            label="Event",
            value=(
                _SHOWCASE_APPOINTMENT,
                _SHOWCASE_APPOINTMENT + timedelta(hours=2),
            ),
            start_label="Starts",
            end_label="Ends",
            helper_text="Quarter-hour steps with a single range callback.",
            clearable=True,
            disable_past=True,
            minutes_step=15,
            on_change=_change_callback("datetime_range"),
            disabled=disabled,
            key="dtrp_basic",
        )
        st.code(f"Start: {dtr[0]}")
        st.code(f"End:   {dtr[1]}")
        _change_count("datetime_range")

    st.divider()

    # -- 24-hour format --
    st.markdown("#### 24-hour format")

    with st.container(horizontal=True):
        _banner_mui()
        dtr2 = date_time_range_picker(
            label="Shift schedule",
            value=(
                datetime(2026, 8, 3, 8, 0),
                datetime(2026, 8, 3, 16, 30),
            ),
            ampm=False,
            format="DD MMM YYYY HH:mm",
            open_to="hours",
            views=["day", "hours", "minutes"],
            minutes_step=30,
            disabled=disabled,
            key="dtrp_24h",
        )
        st.code(f"Start: {dtr2[0]}")
        st.code(f"End:   {dtr2[1]}")

    st.divider()
    st.markdown("#### Read-only maintenance window")
    _banner_mui()
    dtr3 = date_time_range_picker(
        label="Maintenance",
        value=(
            datetime(2026, 8, 8, 22, 0),
            datetime(2026, 8, 9, 1, 0),
        ),
        helper_text="Read-only and non-clearable.",
        clearable=False,
        read_only=True,
        disable_future=False,
        disabled=disabled,
        key="dtrp_read_only",
    )
    st.code(f"Start: {dtr3[0]}")
    st.code(f"End:   {dtr3[1]}")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import date_time_range_picker
from datetime import datetime, timedelta

# minutes_step=15 means both endpoints must land on a quarter hour, and the
# anchor must be stable or every rerun replaces the user's selection.
if "anchor" not in st.session_state:
    now = datetime.now().replace(second=0, microsecond=0)
    st.session_state["anchor"] = now + timedelta(minutes=-now.minute % 15)
anchor = st.session_state["anchor"]

start, end = date_time_range_picker(
    label="Event",
    value=(anchor, anchor + timedelta(hours=2)),
    start_label="Starts",
    end_label="Ends",
    ampm=False,
    format="DD MMM YYYY HH:mm",
    helper_text="Quarter-hour scheduling",
    clearable=True,
    views=["day", "hours", "minutes"],
    minutes_step=15,
    on_change=handle_change,
    key="my_dt_range",
)""",
            language="python",
        )

# ============================================================================
# TREE VIEW TAB
# ============================================================================
with tab_tree:
    st.subheader("TreeView")
    st.markdown(
        "A hierarchical tree view for displaying nested data. "
        "Uses MUI X RichTreeView (MIT, free)."
    )

    # -- Basic --
    st.markdown("#### File browser")

    _banner_mui()

    file_tree = [
        {
            "id": "docs",
            "label": "Documents",
            "children": [
                {"id": "docs-resume", "label": "Resume.pdf"},
                {"id": "docs-cover", "label": "Cover Letter.docx"},
                {
                    "id": "docs-projects",
                    "label": "Projects",
                    "children": [
                        {"id": "docs-proj-a", "label": "ProjectA.zip"},
                        {"id": "docs-proj-b", "label": "ProjectB.zip"},
                    ],
                },
            ],
        },
        {
            "id": "photos",
            "label": "Photos",
            "children": [
                {"id": "photos-vacation", "label": "vacation.jpg"},
                {"id": "photos-family", "label": "family.png"},
            ],
        },
        {
            "id": "music",
            "label": "Music",
            "children": [
                {"id": "music-song1", "label": "song1.mp3"},
                {"id": "music-song2", "label": "song2.mp3"},
            ],
        },
    ]

    selected = tree_view(
        items=file_tree,
        label="My Files",
        checkbox_selection=True,
        default_expanded=["docs"],
        disabled=disabled,
        key="tv_files",
    )
    st.code(f"Selected: {selected}")

    st.divider()

    # -- Multi-select --
    st.markdown("#### Multi-select with checkboxes")

    _banner_mui()

    org_tree = [
        {
            "id": "eng",
            "label": "Engineering",
            "children": [
                {"id": "eng-fe", "label": "Frontend"},
                {"id": "eng-be", "label": "Backend"},
                {"id": "eng-infra", "label": "Infrastructure"},
            ],
        },
        {
            "id": "design",
            "label": "Design",
            "children": [
                {"id": "design-ux", "label": "UX"},
                {"id": "design-ui", "label": "UI"},
            ],
        },
        {
            "id": "product",
            "label": "Product",
        },
    ]

    selected2 = tree_view(
        items=org_tree,
        label="Select teams",
        multi_select=True,
        checkbox_selection=True,
        default_expanded=["eng", "design"],
        disabled=disabled,
        key="tv_org",
    )
    st.code(f"Selected teams: {selected2}")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import tree_view

items = [
    {
        "id": "docs",
        "label": "Documents",
        "children": [
            {"id": "docs-resume", "label": "Resume.pdf"},
            {"id": "docs-cover", "label": "Cover Letter.docx"},
        ],
    },
    {"id": "photos", "label": "Photos"},
]

selected = tree_view(
    items=items,
    label="My Files",
    multi_select=True,
    checkbox_selection=True,
    default_expanded=["docs"],
    key="my_tree",
)
""",
            language="python",
        )

# ============================================================================
# AUTOCOMPLETE TAB
# ============================================================================
with tab_autocomplete:
    st.subheader("Autocomplete")
    st.markdown(
        "Searchable single- and multi-select inputs using MIT-licensed Material UI. "
        "The examples below exercise custom labels, typed scalar identity, disabled "
        "options, free-form values, helper text, clearability, and callbacks."
    )

    city_column, skills_column = st.columns(2)
    with city_column:
        st.markdown("#### Labeled values and disabled options")
        _banner_mui()
        city = autocomplete(
            [
                {"label": "Los Angeles", "value": "LAX"},
                {"label": "New York", "value": "NYC"},
                {"label": "Seattle", "value": "SEA"},
                {
                    "label": "Maintenance window",
                    "value": "OFFLINE",
                    "disabled": True,
                },
            ],
            label="Destination",
            value="LAX",
            placeholder="Search cities",
            helper_text="The UI label and returned value can differ",
            clearable=True,
            disabled=disabled,
            on_change=_change_callback("autocomplete_city"),
            key="autocomplete_city",
        )
        st.code(f"Returned value: {city!r}")
        _change_count("autocomplete_city")

    with skills_column:
        st.markdown("#### Multi-select plus free-form entries")
        _banner_mui()
        skills = autocomplete(
            ["Python", "TypeScript", "Rust"],
            label="Skills",
            value=["Python"],
            multiple=True,
            free_solo=True,
            placeholder="Add a skill and press Enter",
            helper_text="Suggestions become chips; custom strings are welcome",
            clearable=True,
            disabled=disabled,
            on_change=_change_callback("autocomplete_skills"),
            key="autocomplete_skills",
        )
        st.code(f"Returned values: {skills!r}")
        _change_count("autocomplete_skills")

    st.divider()
    st.markdown("#### Scalar types retain their identity")
    st.caption(
        "Numeric `1`, string `'1'`, and boolean `True` are deliberately distinct. "
        "This required-selection example also demonstrates `clearable=False`."
    )
    _banner_mui()
    typed_value = autocomplete(
        [
            {"label": "Number: 1", "value": 1},
            {"label": "String: '1'", "value": "1"},
            {"label": "Boolean: True", "value": True},
        ],
        label="Typed JSON scalar",
        value=1,
        helper_text="Inspect repr(value) below to see the preserved Python type",
        clearable=False,
        disabled=disabled,
        on_change=_change_callback("autocomplete_typed"),
        key="autocomplete_typed",
    )
    st.code(f"value={typed_value!r}  type={type(typed_value).__name__}")
    _change_count("autocomplete_typed")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import autocomplete

destination = autocomplete(
    [
        {"label": "Los Angeles", "value": "LAX"},
        {"label": "Temporarily unavailable", "value": "N/A", "disabled": True},
    ],
    label="Destination",
    placeholder="Search cities",
    helper_text="Labels can differ from returned values",
    clearable=False,
    on_change=handle_destination_change,
    key="destination",
)

skills = autocomplete(
    ["Python", "TypeScript", "Rust"],
    label="Skills",
    value=["Python"],
    multiple=True,
    free_solo=True,
    key="skills",
)
""",
            language="python",
        )

# ============================================================================
# SLIDER TAB
# ============================================================================
with tab_slider:
    st.subheader("Slider")
    st.markdown(
        "Single-value and range sliders that update Streamlit when a drag is "
        "committed. Generated marks are safety-capped; marks-only mode accepts "
        "only the explicit values you provide."
    )

    volume_column, budget_column = st.columns(2)
    with volume_column:
        st.markdown("#### Single value with generated marks")
        _banner_mui()
        volume = slider(
            "Volume",
            40,
            min_value=0,
            max_value=100,
            step=10,
            marks=True,
            value_label_display="auto",
            disabled=disabled,
            on_change=_change_callback("slider_volume"),
            key="slider_volume",
        )
        st.metric("Committed volume", volume)
        _change_count("slider_volume")

    with budget_column:
        st.markdown("#### Range with custom labeled marks")
        _banner_mui()
        budget = slider(
            "Budget",
            (25, 75),
            min_value=0,
            max_value=100,
            step=5,
            marks=[
                {"value": 0, "label": "$0"},
                {"value": 50, "label": "$50"},
                {"value": 100, "label": "$100"},
            ],
            value_label_display="on",
            disabled=disabled,
            on_change=_change_callback("slider_budget"),
            key="slider_budget",
        )
        st.code(f"Committed range: {budget}")
        _change_count("slider_budget")

    st.divider()
    st.markdown("#### Discrete marks-only selection")
    st.caption(
        "`step=None` prevents intermediate values, which is useful for named tiers "
        "or intentionally irregular numeric choices."
    )
    _banner_mui()
    capacity = slider(
        "Deployment capacity",
        25,
        min_value=0,
        max_value=100,
        step=None,
        marks=[
            {"value": 0, "label": "Off"},
            {"value": 10, "label": "Canary"},
            {"value": 25, "label": "Quarter"},
            {"value": 50, "label": "Half"},
            {"value": 100, "label": "Full"},
        ],
        value_label_display="off",
        disabled=disabled,
        on_change=_change_callback("slider_capacity"),
        key="slider_capacity",
    )
    st.code(f"Only an explicit mark can be returned: {capacity}")
    _change_count("slider_capacity")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import slider

low, high = slider(
    "Price range",
    value=(20, 80),
    min_value=0,
    max_value=100,
    step=5,
    marks=[
        {"value": 0, "label": "$0"},
        {"value": 50, "label": "$50"},
        {"value": 100, "label": "$100"},
    ],
    value_label_display="on",
    on_change=handle_price_change,
    key="price",
)

tier = slider(
    "Capacity",
    value=25,
    min_value=0,
    max_value=100,
    step=None,
    marks=[{"value": 0, "label": "Off"}, {"value": 25, "label": "Quarter"}],
    key="capacity",
)
""",
            language="python",
        )

# ============================================================================
# RATING TAB
# ============================================================================
with tab_rating:
    st.subheader("Rating")
    st.markdown(
        "Accessible star ratings with configurable size, maximum, fractional "
        "precision, clearability, disabled state, and read-only presentation."
    )

    interactive_column, readonly_column = st.columns(2)
    with interactive_column:
        st.markdown("#### Interactive half-star rating")
        _banner_mui()
        score = rating(
            "How useful is st-mui?",
            value=4,
            precision=0.5,
            size="large",
            clearable=True,
            disabled=disabled,
            on_change=_change_callback("rating_useful"),
            key="rating_useful",
        )
        st.code(f"Rating: {score!r}")
        _change_count("rating_useful")

    with readonly_column:
        st.markdown("#### Read-only ten-star score")
        _banner_mui()
        readonly_score = rating(
            "Aggregate score",
            value=7.5,
            max_value=10,
            precision=0.5,
            size="medium",
            read_only=True,
            clearable=False,
            key="rating_readonly",
        )
        st.code(f"Read-only rating: {readonly_score!r}")

    st.divider()
    st.markdown("#### Size and precision gallery")
    small_column, medium_column, large_column = st.columns(3)
    with small_column:
        small_score = rating(
            "Small / whole stars",
            value=3,
            precision=1,
            size="small",
            disabled=disabled,
            key="rating_small",
        )
        st.code(repr(small_score))
    with medium_column:
        medium_score = rating(
            "Medium / half stars",
            value=3.5,
            precision=0.5,
            size="medium",
            disabled=disabled,
            key="rating_medium",
        )
        st.code(repr(medium_score))
    with large_column:
        large_score = rating(
            "Large / quarter stars",
            value=3.75,
            precision=0.25,
            size="large",
            clearable=False,
            disabled=disabled,
            key="rating_large",
        )
        st.code(repr(large_score))

    with st.expander("Usage code"):
        st.code(
            """from st_mui import rating

score = rating(
    "Score",
    value=3.5,
    max_value=5,
    precision=0.5,
    size="large",
    clearable=True,
    on_change=handle_score_change,
    key="score",
)

readonly_score = rating(
    "Aggregate score",
    value=7.5,
    max_value=10,
    precision=0.5,
    read_only=True,
    clearable=False,
    key="aggregate",
)
""",
            language="python",
        )

# ============================================================================
# DATA GRID TAB
# ============================================================================
with tab_grid:
    st.subheader("DataGrid (Community)")
    st.markdown(
        "The MIT-licensed MUI X Community Data Grid with selection, sorting, "
        "filtering, pagination, typed columns, density controls, custom row IDs, "
        "and one composite callback. Community edition intentionally supports one "
        "sort and one filter item at a time."
    )

    grid_rows = [
        {
            "key": "emp-001",
            "name": "Ada Lovelace",
            "team": "Platform",
            "score": 98,
            "active": True,
        },
        {
            "key": "emp-002",
            "name": "Grace Hopper",
            "team": "Research",
            "score": 99,
            "active": True,
        },
        {
            "key": "emp-003",
            "name": "Margaret Hamilton",
            "team": "Platform",
            "score": 97,
            "active": True,
        },
        {
            "key": "emp-004",
            "name": "Alan Turing",
            "team": "Research",
            "score": 96,
            "active": False,
        },
        {
            "key": "emp-005",
            "name": "Katherine Johnson",
            "team": "Analytics",
            "score": 99,
            "active": True,
        },
        {
            "key": "emp-006",
            "name": "Edsger Dijkstra",
            "team": "Platform",
            "score": 95,
            "active": False,
        },
        {
            "key": "emp-007",
            "name": "Radia Perlman",
            "team": "Infrastructure",
            "score": 98,
            "active": True,
        },
        {
            "key": "emp-008",
            "name": "Donald Knuth",
            "team": "Research",
            "score": 97,
            "active": True,
        },
        {
            "key": "emp-009",
            "name": "Barbara Liskov",
            "team": "Platform",
            "score": 99,
            "active": True,
        },
        {
            "key": "emp-010",
            "name": "Mary Jackson",
            "team": "Analytics",
            "score": 96,
            "active": True,
        },
        {
            "key": "emp-011",
            "name": "Guido van Rossum",
            "team": "Infrastructure",
            "score": 94,
            "active": True,
        },
        {
            "key": "emp-012",
            "name": "Frances Allen",
            "team": "Research",
            "score": 98,
            "active": False,
        },
    ]

    st.markdown("#### Fully configured typed grid")
    st.caption(
        "Starts sorted by score with active rows filtered in. Clear the filter, "
        "change pages, select rows, and inspect the controlled model below."
    )
    _banner_mui()
    grid_state = data_grid(
        rows=grid_rows,
        columns=[
            {
                "field": "key",
                "header_name": "Employee ID",
                "width": 120,
                "sortable": False,
                "filterable": False,
                "resizable": False,
            },
            {
                "field": "name",
                "header_name": "Name",
                "description": "Full employee name",
                "min_width": 180,
                "flex": 1,
            },
            {
                "field": "team",
                "header_name": "Team",
                "type": "singleSelect",
                "value_options": [
                    "Platform",
                    "Research",
                    "Analytics",
                    "Infrastructure",
                ],
                "min_width": 140,
            },
            {
                "field": "score",
                "header_name": "Score",
                "type": "number",
                "width": 110,
                "align": "right",
                "header_align": "right",
            },
            {
                "field": "active",
                "header_name": "Active",
                "type": "boolean",
                "width": 100,
            },
        ],
        id_field="key",
        selected_rows=["emp-002", "emp-005"],
        sort_model=[{"field": "score", "sort": "desc"}],
        filter_model={
            "items": [
                {
                    "id": "active-filter",
                    "field": "active",
                    "operator": "is",
                    "value": True,
                }
            ]
        },
        page_size=5,
        page_size_options=(5, 10),
        height=440,
        checkbox_selection=True,
        density="compact",
        disabled=disabled,
        on_change=_change_callback("data_grid_configured"),
        key="community_grid",
    )
    st.json(grid_state)
    _change_count("data_grid_configured")

    st.divider()
    st.markdown("#### Zero-config column inference")
    st.caption(
        "No `columns` argument is supplied. Fields are inferred in stable first-seen "
        "order across every row, including fields that appear after row one."
    )
    _banner_mui()
    inferred_grid_state = data_grid(
        rows=[
            {"id": 1, "name": "First row"},
            {"id": 2, "name": "Adds priority", "priority": 2},
            {
                "id": 3,
                "name": "Adds shipped",
                "priority": 1,
                "shipped": True,
            },
        ],
        page_size=3,
        page_size_options=(3,),
        height=280,
        density="comfortable",
        disabled=disabled,
        on_change=_change_callback("data_grid_inferred"),
        key="inferred_grid",
    )
    st.json(inferred_grid_state)
    _change_count("data_grid_inferred")

    with st.expander("Usage code"):
        st.code(
            """from st_mui import data_grid

state = data_grid(
    rows=[
        {"key": "emp-1", "name": "Ada", "score": 98, "active": True},
        {"key": "emp-2", "name": "Grace", "score": 99, "active": True},
    ],
    columns=[
        {"field": "name", "header_name": "Name", "min_width": 180, "flex": 1},
        {"field": "score", "type": "number", "width": 110},
        {"field": "active", "type": "boolean", "width": 100},
    ],
    id_field="key",
    selected_rows=["emp-2"],
    sort_model=[{"field": "score", "sort": "desc"}],
    filter_model={"items": []},
    page_size=5,
    page_size_options=(5, 10),
    height=440,
    checkbox_selection=True,
    density="compact",
    on_change=handle_grid_change,
    key="people",
)
""",
            language="python",
        )

# -- Footer ------------------------------------------------------------------
st.divider()
st.caption(
    "Built with [st-mui](https://github.com/lperezmo/st-mui) | "
    "Material UI + MIT-licensed MUI X Community | Streamlit Components v2"
)
