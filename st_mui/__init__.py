"""st-mui: MUI X components for Streamlit, built with Components v2."""

# Component modules register a file-backed CCv2 component the moment they are
# imported, and registration needs the Streamlit runtime's manifest discovery
# to have run. Deferring the imports (PEP 562) keeps `import st_mui` safe in
# any context (tests, REPLs, tooling); the actual registration happens on first
# use, inside a running app.
_COMPONENT_IMPORTS = {
    "date_picker": "st_mui.date_picker",
    "time_picker": "st_mui.time_picker",
    "date_time_picker": "st_mui.date_time_picker",
    "date_range_picker": "st_mui.date_range_picker",
    "date_time_range_picker": "st_mui.date_time_range_picker",
    "tree_view": "st_mui.tree_view",
}


def __getattr__(name: str):
    if name in _COMPONENT_IMPORTS:
        import importlib
        import sys

        func = getattr(importlib.import_module(_COMPONENT_IMPORTS[name]), name)
        # Bind the function directly on this module so __getattr__ isn't
        # called again AND so it shadows the subpackage module reference.
        setattr(sys.modules[__name__], name, func)
        return func
    raise AttributeError(f"module 'st_mui' has no attribute {name!r}")


__all__ = [
    "date_picker",
    "time_picker",
    "date_time_picker",
    "date_range_picker",
    "date_time_range_picker",
    "tree_view",
]
