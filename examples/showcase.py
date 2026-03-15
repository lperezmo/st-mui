"""
st-mui Showcase
===============
Interactive demo of MUI X components for Streamlit,
with side-by-side comparisons against standard widgets.
"""

import streamlit as st
from datetime import date, time, datetime, timedelta

from st_mui import (
    date_picker,
    time_picker,
    date_time_picker,
    date_range_picker,
    date_time_range_picker,
    tree_view,
)

# -- Page config -------------------------------------------------------------
st.set_page_config(
    page_title="st-mui | MUI X for Streamlit",
    page_icon=":material/widgets:",
    layout="wide",
)

st.markdown("""<style>
    .block-container {
        padding-top: 1rem;
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
    st.markdown("- :material/date_range: DateRangePicker (Pro)")
    st.markdown("- :material/date_range: DateTimeRangePicker (Pro)")
    st.markdown("- :material/account_tree: TreeView")

# -- Tabs for each component -------------------------------------------------
tab_time, tab_datetime, tab_date, tab_daterange, tab_dtrange, tab_tree = st.tabs([
    ":material/schedule: TimePicker",
    ":material/calendar_month: DateTimePicker",
    ":material/event: DatePicker",
    ":material/date_range: DateRangePicker",
    ":material/date_range: DTRangePicker",
    ":material/account_tree: TreeView",
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

    with st.container(horizontal=True):
        _banner_mui()
        dt_mui1 = date_time_picker(
            label="Select date & time",
            value=datetime.now(),
            disabled=disabled,
            key="dtp_basic",
        )
        st.code(f"Selected: {dt_mui1}")

    with st.container(horizontal=True):
        _banner_st()
        dt_st1 = st.datetime_input(
            "Select date & time",
            value=datetime.now(),
            disabled=disabled,
            key="st_dt_basic",
        )
        st.code(f"Selected: {dt_st1}")

    st.divider()

    # -- With bounds --
    st.markdown("#### With bounds")

    with st.container(horizontal=True):
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

    with st.container(horizontal=True):
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

    with st.container(horizontal=True):
        _banner_mui()
        d_mui1 = date_picker(
            label="Pick any date",
            value=date.today(),
            disabled=disabled,
            key="dp_basic",
        )
        st.code(f"Selected: {d_mui1}")

    with st.container(horizontal=True):
        _banner_st()
        d_st1 = st.date_input(
            "Pick any date",
            value=date.today(),
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
# DATE RANGE PICKER TAB
# ============================================================================
with tab_daterange:
    st.subheader("DateRangePicker (Pro)")
    st.markdown(
        "Select a date range with start and end dates. "
        "This is a MUI X Pro component -- works in evaluation mode without a license key."
    )

    # -- Basic --
    st.markdown("#### Basic")

    with st.container(horizontal=True):
        _banner_mui()
        dr = date_range_picker(
            label="Trip dates",
            value=(date.today(), date.today() + timedelta(days=7)),
            disabled=disabled,
            key="drp_basic",
        )
        st.code(f"Start: {dr[0]}  End: {dr[1]}")

    with st.container(horizontal=True):
        _banner_st()
        dr_st = st.date_input(
            "Trip dates",
            value=(date.today(), date.today() + timedelta(days=7)),
            disabled=disabled,
            key="st_daterange_basic",
        )
        if isinstance(dr_st, tuple) and len(dr_st) == 2:
            st.code(f"Start: {dr_st[0]}  End: {dr_st[1]}")
        else:
            st.code(f"Selected: {dr_st}")

    st.divider()

    # -- With bounds --
    st.markdown("#### With bounds (this month, single calendar)")

    with st.container(horizontal=True):
        _banner_mui()
        dr2 = date_range_picker(
            label="This month only",
            min_date=date(2026, 3, 1),
            max_date=date(2026, 3, 31),
            calendars=1,
            disabled=disabled,
            key="drp_bounded",
        )
        st.code(f"Start: {dr2[0]}  End: {dr2[1]}")

    with st.container(horizontal=True):
        _banner_st()
        dr2_st = st.date_input(
            "This month only",
            value=(date(2026, 3, 1), date(2026, 3, 15)),
            min_value=date(2026, 3, 1),
            max_value=date(2026, 3, 31),
            disabled=disabled,
            key="st_daterange_bounded",
        )
        if isinstance(dr2_st, tuple) and len(dr2_st) == 2:
            st.code(f"Start: {dr2_st[0]}  End: {dr2_st[1]}")
        else:
            st.code(f"Selected: {dr2_st}")

    with st.expander("Usage code"):
        st.code(
            '''from st_mui import date_range_picker
from datetime import date, timedelta

start, end = date_range_picker(
    label="Trip dates",
    value=(date.today(), date.today() + timedelta(days=7)),
    min_date=date(2026, 1, 1),
    max_date=date(2026, 12, 31),
    calendars=2,
    # license_key="YOUR_KEY",  # or set ST_MUI_LICENSE_KEY env var
    key="my_range",
)''',
            language="python",
        )

# ============================================================================
# DATE TIME RANGE PICKER TAB
# ============================================================================
with tab_dtrange:
    st.subheader("DateTimeRangePicker (Pro)")
    st.markdown(
        "Select a datetime range with start and end dates and times. "
        "This is a MUI X Pro component -- works in evaluation mode without a license key."
    )

    # -- Basic --
    st.markdown("#### Basic (AM/PM)")

    with st.container(horizontal=True):
        _banner_mui()
        dtr = date_time_range_picker(
            label="Event",
            value=(datetime.now(), datetime.now() + timedelta(hours=2)),
            disabled=disabled,
            key="dtrp_basic",
        )
        st.code(f"Start: {dtr[0]}")
        st.code(f"End:   {dtr[1]}")

    st.divider()

    # -- 24-hour format --
    st.markdown("#### 24-hour format")

    with st.container(horizontal=True):
        _banner_mui()
        dtr2 = date_time_range_picker(
            label="Shift schedule",
            ampm=False,
            disabled=disabled,
            key="dtrp_24h",
        )
        st.code(f"Start: {dtr2[0]}")
        st.code(f"End:   {dtr2[1]}")

    with st.expander("Usage code"):
        st.code(
            '''from st_mui import date_time_range_picker
from datetime import datetime, timedelta

start, end = date_time_range_picker(
    label="Event",
    value=(datetime.now(), datetime.now() + timedelta(hours=2)),
    ampm=True,
    # license_key="YOUR_KEY",  # or set ST_MUI_LICENSE_KEY env var
    key="my_dt_range",
)''',
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
            '''from st_mui import tree_view

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
''',
            language="python",
        )

# -- Footer ------------------------------------------------------------------
st.divider()
st.caption(
    "Built with [st-mui](https://github.com/lperezmo/st-mui) | "
    "MUI X (Community + Pro) | Streamlit Components v2"
)
