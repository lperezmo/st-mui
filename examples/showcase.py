"""
st-mui Showcase
===============
Interactive demo of MUI X components for Streamlit,
with side-by-side comparisons against standard widgets.
"""

import streamlit as st
from datetime import date, time, datetime, timedelta

from st_mui import date_picker, time_picker, date_time_picker

# -- Page config -------------------------------------------------------------
st.set_page_config(
    page_title="st-mui | MUI X for Streamlit",
    page_icon=":material/widgets:",
    layout="wide",
)

st.markdown("""<style>
    .block-container {
        padding-top: 0rem;
    }
</style>""", unsafe_allow_html=True)

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
        MUI X components for Streamlit, powered by Components v2
    </p>
</div>
""")

# -- Sidebar: global controls ------------------------------------------------
with st.sidebar:
    st.header("Global Settings")
    disabled = st.toggle("Disable all components", value=False)
    st.divider()
    st.markdown(
        "**st-mui** brings production-grade MUI X components to Streamlit "
        "using the new Components v2 API."
    )
    st.markdown("Components included:")
    st.markdown("- :material/schedule: TimePicker")
    st.markdown("- :material/calendar_month: DateTimePicker")
    st.markdown("- :material/event: DatePicker")

# -- Tabs for each component -------------------------------------------------
tab_time, tab_datetime, tab_date, tab_combined = st.tabs([
    ":material/schedule: TimePicker",
    ":material/calendar_month: DateTimePicker",
    ":material/event: DatePicker",
    ":material/groups: Combined Example",
])

# ============================================================================
# TIME PICKER TAB
# ============================================================================
with tab_time:
    st.subheader("TimePicker")
    st.markdown(
        "A time picker with clock UI, AM/PM support, and keyboard input."
    )

    # -- 12-hour AM/PM comparison --
    st.markdown("#### 12-hour (AM/PM)")
    row = st.container(horizontal=True)

    with row:
        _banner_mui()
        t_mui1 = time_picker(
            label="Pick a time",
            value=time(9, 30),
            ampm=True,
            disabled=disabled,
            key="tp_12h",
        )
        st.code(f"Selected: {t_mui1}")

    with row:
        _banner_st()
        t_st1 = st.time_input(
            "Pick a time",
            value=time(9, 30),
            disabled=disabled,
            key="st_time_12h",
        )
        st.code(f"Selected: {t_st1}")

    # -- 24-hour with bounds comparison --
    st.markdown("#### 24-hour with bounds")
    row2 = st.container(horizontal=True)

    with row2:
        _banner_mui()
        t_mui2 = time_picker(
            label="Business hours only",
            value=time(14, 0),
            ampm=False,
            min_time=time(8, 0),
            max_time=time(17, 0),
            disabled=disabled,
            key="tp_24h",
        )
        st.code(f"Selected: {t_mui2}")

    with row2:
        _banner_st()
        t_st2 = st.time_input(
            "Business hours only",
            value=time(14, 0),
            disabled=disabled,
            key="st_time_24h",
        )
        st.code(f"Selected: {t_st2}")

    with st.expander("Usage code"):
        st.code(
            '''from st_mui import time_picker
from datetime import time

selected = time_picker(
    label="Pick a time",
    value=time(9, 30),
    ampm=True,
    min_time=time(8, 0),
    max_time=time(17, 0),
    key="my_time",
)''',
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
    row = st.container(horizontal=True)

    with row:
        _banner_mui()
        dt_mui1 = date_time_picker(
            label="Select date & time",
            value=datetime.now(),
            disabled=disabled,
            key="dtp_basic",
        )
        st.code(f"Selected: {dt_mui1}")

    with row:
        _banner_st()
        dt_st1 = st.datetime_input(
            "Select date & time",
            value=datetime.now(),
            disabled=disabled,
            key="st_dt_basic",
        )
        st.code(f"Selected: {dt_st1}")

    # -- With bounds --
    st.markdown("#### With bounds")
    row2 = st.container(horizontal=True)

    with row2:
        _banner_mui()
        dt_mui2 = date_time_picker(
            label="Next 7 days only",
            min_datetime=datetime.now(),
            max_datetime=datetime.now() + timedelta(days=7),
            ampm=False,
            disabled=disabled,
            key="dtp_bounded",
        )
        st.code(f"Selected: {dt_mui2}")

    with row2:
        _banner_st()
        dt_st2 = st.datetime_input(
            "Next 7 days only",
            value=datetime.now(),
            min_value=datetime.now(),
            max_value=datetime.now() + timedelta(days=7),
            disabled=disabled,
            key="st_dt_bounded",
        )
        st.code(f"Selected: {dt_st2}")

    with st.expander("Usage code"):
        st.code(
            '''from st_mui import date_time_picker
from datetime import datetime, timedelta

selected = date_time_picker(
    label="Select date & time",
    value=datetime.now(),
    min_datetime=datetime.now(),
    max_datetime=datetime.now() + timedelta(days=7),
    ampm=True,
    key="my_datetime",
)''',
            language="python",
        )

# ============================================================================
# DATE PICKER TAB
# ============================================================================
with tab_date:
    st.subheader("DatePicker")
    st.markdown(
        "A date picker with calendar popover, keyboard navigation, "
        "and validation."
    )

    # -- Basic comparison --
    st.markdown("#### Basic")
    row = st.container(horizontal=True)

    with row:
        _banner_mui()
        d_mui1 = date_picker(
            label="Pick any date",
            value=date.today(),
            disabled=disabled,
            key="dp_basic",
        )
        st.code(f"Selected: {d_mui1}")

    with row:
        _banner_st()
        d_st1 = st.date_input(
            "Pick any date",
            value=date.today(),
            disabled=disabled,
            key="st_date_basic",
        )
        st.code(f"Selected: {d_st1}")

    # -- With bounds comparison --
    st.markdown("#### With bounds")
    row2 = st.container(horizontal=True)

    with row2:
        _banner_mui()
        d_mui2 = date_picker(
            label="This year only",
            min_date=date(2026, 1, 1),
            max_date=date(2026, 12, 31),
            disabled=disabled,
            key="dp_bounded",
        )
        st.code(f"Selected: {d_mui2}")

    with row2:
        _banner_st()
        d_st2 = st.date_input(
            "This year only",
            min_value=date(2026, 1, 1),
            max_value=date(2026, 12, 31),
            disabled=disabled,
            key="st_date_bounded",
        )
        st.code(f"Selected: {d_st2}")

    # -- Custom format --
    st.markdown("#### Custom format")
    row3 = st.container(horizontal=True)

    with row3:
        _banner_mui()
        d_mui3 = date_picker(
            label="DD/MM/YYYY format",
            value=date(2026, 3, 14),
            format="DD/MM/YYYY",
            disabled=disabled,
            key="dp_format",
        )
        st.code(f"Selected: {d_mui3}")

    with row3:
        _banner_st()
        d_st3 = st.date_input(
            "DD/MM/YYYY format",
            value=date(2026, 3, 14),
            format="DD/MM/YYYY",
            disabled=disabled,
            key="st_date_format",
        )
        st.code(f"Selected: {d_st3}")

    with st.expander("Usage code"):
        st.code(
            '''from st_mui import date_picker
from datetime import date

selected = date_picker(
    label="Pick a date",
    value=date.today(),
    min_date=date(2026, 1, 1),
    max_date=date(2026, 12, 31),
    format="MM/DD/YYYY",
    key="my_date",
)''',
            language="python",
        )

# ============================================================================
# COMBINED EXAMPLE TAB
# ============================================================================
with tab_combined:
    st.subheader("Real-world Example: Meeting Scheduler")
    st.markdown(
        "This example combines multiple st-mui components to build "
        "a simple meeting scheduler interface."
    )

    with st.container(border=True):
        st.markdown("##### :material/event_available: Schedule a Meeting")

        row = st.container(horizontal=True)
        with row:
            meeting_date = date_picker(
                label="Meeting date",
                value=date.today() + timedelta(days=1),
                min_date=date.today(),
                key="meeting_date",
            )
        with row:
            meeting_time = time_picker(
                label="Start time",
                value=time(10, 0),
                ampm=True,
                min_time=time(8, 0),
                max_time=time(18, 0),
                key="meeting_time",
            )

        meeting_dt_picker = date_time_picker(
            label="Or pick exact date & time",
            value=datetime.now() + timedelta(days=1),
            ampm=True,
            key="meeting_datetime",
        )

    if meeting_date and meeting_time:
        meeting_dt = datetime.combine(meeting_date, meeting_time)
        st.success(
            f"Meeting scheduled for **{meeting_dt.strftime('%B %d, %Y at %I:%M %p')}**"
        )

# -- Footer ------------------------------------------------------------------
st.divider()
st.caption(
    "Built with [st-mui](https://github.com/lperezmo/st-mui) | "
    "MUI X (Community, MIT) | Streamlit Components v2"
)
