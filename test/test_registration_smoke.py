"""Fast, browser-less guard that a real ``streamlit run`` would register every
st-mui component on the installed Streamlit.

This mirrors what the Streamlit runtime does at startup: it calls
``discover_and_register_components`` (see ``streamlit/runtime/runtime.py``) and
then resolves each component's ``asset_dir``. If discovery does not register a
component, a real app raises
``Component 'st-mui.<name>' must be declared in pyproject.toml with asset_dir``.
We assert each of the six registrations resolves, that ``import st_mui`` is
safe outside a running app (registration is deferred to first use), and that
the installed Streamlit lets the compat layer disable style isolation (at
registration on Streamlit >= 1.53, or on the per-call renderer on 1.51 / 1.52).

This is intentionally cheap (no server, no browser) so CI can run it across the
whole Streamlit version matrix. Note: ``streamlit.testing.v1.AppTest`` is NOT a
substitute here because it never runs discovery, so file-backed components
always look unregistered under it.
"""

import inspect

import streamlit as st
from streamlit.components.v2.get_bidi_component_manager import (
    get_bidi_component_manager,
)

import st_mui  # noqa: F401  (import must not raise on any supported Streamlit)
from st_mui import _compat

COMPONENTS = [
    "date_picker",
    "time_picker",
    "date_time_picker",
    "date_range_picker",
    "date_time_range_picker",
    "tree_view",
]


def test_import_is_lazy_and_exports_every_component():
    """``import st_mui`` must not register anything (file-backed registration
    needs runtime discovery, so an eager import would raise outside a real
    ``streamlit run``), yet every component must be reachable via PEP 562."""
    assert sorted(st_mui.__all__) == sorted(COMPONENTS)
    for name in COMPONENTS:
        assert name in st_mui._COMPONENT_IMPORTS, f"{name} missing from lazy imports"


def test_isolate_styles_controllable():
    """st-mui renders every component with Shadow DOM isolation disabled. The
    toggle lives on the registration call (Streamlit >= 1.53) or on the per-call
    renderer (Streamlit 1.51 / 1.52); the compat layer must find it in one of
    those places on the installed Streamlit."""
    if _compat._REGISTRATION_TAKES_ISOLATE_STYLES:
        assert (
            "isolate_styles" in inspect.signature(st.components.v2.component).parameters
        )
    else:
        probe = st.components.v2.component(
            "probe.isolate", html="<div></div>", css="", js="console.log(0)"
        )
        assert "isolate_styles" in inspect.signature(probe).parameters, (
            f"Streamlit {st.__version__} exposes isolate_styles at neither "
            "registration nor the call site; st-mui cannot disable isolation"
        )


def test_compat_shim_registers_without_error():
    """The compat shim registers a component without raising on the installed
    Streamlit version (covers both the >=1.53 and 1.51/1.52 branches). Inline
    js/html so no asset_dir is needed outside a running app."""
    renderer = _compat.component(
        "probe.compat", html="<div></div>", css="", js="console.log(0)"
    )
    assert callable(renderer)


def test_discovery_registers_every_component():
    mgr = get_bidi_component_manager()
    try:
        mgr.discover_and_register_components(start_file_watching=False)
    except TypeError:
        # Older signatures without the keyword argument.
        mgr.discover_and_register_components()

    for name in COMPONENTS:
        qualified = f"st-mui.{name}"
        assert mgr.get_component_asset_root(qualified) is not None, (
            f"discovery did not register {qualified} on Streamlit "
            f"{st.__version__}; a real app would raise 'must be declared ... "
            "with asset_dir' for it"
        )


def test_every_component_registers_its_own_name():
    """Each component module must register its manifest-qualified name through
    the compat shim and expose a callable of the same name.

    File-backed registration raises outside a real ``streamlit run`` (pytest
    never runs asset discovery), so the shim is stubbed BEFORE each module
    imports; the modules then register against the stub.
    """
    import importlib
    import sys
    from unittest.mock import patch

    registered: list[str] = []

    def fake_registration(name, **kwargs):
        registered.append(name)
        assert kwargs.get("js") == "index-*.js", f"{name} changed the js glob"

        def render(**call_kwargs):
            return call_kwargs.get("default")

        return render

    # Force a clean import of the component modules so they register against
    # the stub, whatever ran earlier in the session.
    for mod in [f"st_mui.{c}" for c in COMPONENTS]:
        sys.modules.pop(mod, None)

    with patch.object(_compat, "component", fake_registration):
        for name in COMPONENTS:
            registered.clear()
            module = importlib.import_module(f"st_mui.{name}")
            assert registered == [f"st-mui.{name}"], (
                f"st_mui.{name} registered {registered} instead of st-mui.{name}"
            )
            assert callable(getattr(module, name)), f"{name} export is not callable"
