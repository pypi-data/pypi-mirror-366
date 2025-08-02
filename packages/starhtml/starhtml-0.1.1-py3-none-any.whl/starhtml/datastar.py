"""Pythonic API for Datastar attributes in StarHTML."""

import json
import re
from re import Pattern
from typing import Any

from fastcore.xml import NotStr


class DatastarAttr:
    """Wrapper that enables flat API usage without ** unpacking."""

    def __init__(self, attrs):
        self.attrs = attrs

    def __repr__(self):
        return f"DatastarAttr({self.attrs})"


# ============================================================================
# Helper Functions & Expression Utilities
# ============================================================================


def t(template: str) -> str:
    """JavaScript template literal using Python f-string style."""
    return f"`{re.sub(r'{([^}]+)}', r'${\1}', template)}`"


def if_(condition: str | dict[str, str], *args, **kwargs) -> str:
    """CSS-aligned conditional matching if() function."""
    if len(args) == 2:
        return f"{condition} ? {_to_js_value(args[0])} : {_to_js_value(args[1])}"

    if kwargs:
        default = kwargs.pop("_", "null")
        result = _to_js_value(default)
        for pattern, value in reversed(kwargs.items()):
            check = (
                condition
                if pattern == "true"
                else f"!{condition}"
                if pattern == "false"
                else f"{condition} === {_to_js_value(pattern)}"
            )
            result = f"{check} ? {_to_js_value(value)} : {result}"
        return result

    if isinstance(condition, dict):
        conditions = [(c, v) for c, v in condition.items() if c != "_"]
        result = _to_js_value(condition.get("_", "null"))
        for cond, val in reversed(conditions):
            result = f"{cond} ? {_to_js_value(val)} : {result}"
        return result

    raise ValueError("if_ requires either 2 positional args or keyword args with conditions")


# ============================================================================
# Internal Utilities
# ============================================================================


def _make_comparison(op: str):
    def compare(signal: str, value: Any) -> str:
        sig = signal if signal.startswith("$") else f"${{{signal}}}"
        val = _to_js_value(value) if op == "===" else value
        return f"{sig} {op} {val}"

    return compare


equals = _make_comparison("===")
gt = _make_comparison(">")
lt = _make_comparison("<")
gte = _make_comparison(">=")
lte = _make_comparison("<=")


def _to_js_value(value: Any) -> str:  # noqa: PLR0911
    match value:
        case bool():
            return "true" if value else "false"
        case str() if value.startswith(("$", "`")):
            return value
        case str():
            return json.dumps(value)
        case int() | float():
            return str(value)
        case None:
            return "null"
        case dict() | list() | tuple():
            return json.dumps(value)
        case _:
            return json.dumps(str(value))


def _normalize_value(value: Any, wrap_strings: bool = False) -> Any:
    match value:
        case bool():
            return "true" if value else "false"
        case int() | float():
            return value
        case str():
            return NotStr(value) if wrap_strings else value
        case dict() | list() | tuple():
            return json.dumps(value)
        case _:
            return str(value)


def _process_patterns(patterns: str | list[str | Pattern]) -> str | list[str]:
    if isinstance(patterns, str):
        return f"/{patterns}/"

    patterns = patterns if isinstance(patterns, list | tuple) else [patterns]
    result = [f"/{p.pattern}/" if hasattr(p, "pattern") else f"/{p}/" for p in patterns]
    return result[0] if len(result) == 1 else result


# ============================================================================
# Core Datastar Attributes
# ============================================================================


def ds_show(value: bool | str) -> DatastarAttr:
    return DatastarAttr({"data-show": _normalize_value(value)})


def ds_text(value: str) -> DatastarAttr:
    return DatastarAttr({"data-text": _normalize_value(value)})


def ds_bind(signal: str, case: str | None = None) -> DatastarAttr:
    if case:
        return DatastarAttr({f"data-bind-{signal}__case.{case}": True})
    return DatastarAttr({"data-bind": signal})


def ds_ref(name: str) -> DatastarAttr:
    return DatastarAttr({"data-ref": name})


def ds_indicator(name: str) -> DatastarAttr:
    return DatastarAttr({"data-indicator": name})


def ds_effect(expression: str) -> DatastarAttr:
    return DatastarAttr({"data-effect": NotStr(expression)})


def ds_computed(name: str, expression: str, case: str | None = None) -> DatastarAttr:
    key = f"data-computed-{name}" + (f"__case.{case}" if case else "")
    return DatastarAttr({key: expression})


# ============================================================================
# Conditional Attributes (class, style, attr)
# ============================================================================


def _make_attr_func(prefix: str):
    def attr_func(**kwargs) -> DatastarAttr:
        return DatastarAttr(
            {f"{prefix}-{name.replace('_', '-')}": _normalize_value(value) for name, value in kwargs.items()}
        )

    return attr_func


ds_class = _make_attr_func("data-class")
ds_style = _make_attr_func("data-style")
ds_attr = _make_attr_func("data-attr")


# ============================================================================
# Signals & State Management
# ============================================================================


def ds_signals(*args, **kwargs) -> DatastarAttr:
    ifmissing = kwargs.pop("ifmissing", None)
    signals = args[0] if args and isinstance(args[0], dict) else kwargs

    result = {}
    if ifmissing:
        result["data-signals__ifmissing"] = ifmissing

    for name, value in signals.items():
        result[f"data-signals-{name}"] = _to_js_value(value)

    return DatastarAttr(result)


def ds_persist(*signals, include=None, exclude=None, session=False, key=None):
    attr_key = f"data-persist-{key}" if key else "data-persist" + ("__session" if session else "")

    value = (
        ",".join(signals)
        if signals
        else json.dumps({k: _process_patterns(v) for k, v in [("include", include), ("exclude", exclude)] if v})
        if include or exclude
        else None
    )

    return DatastarAttr({attr_key: value})


def ds_json_signals(show=True, include=None, exclude=None, terse=False):
    key = "data-json-signals" + ("__terse" if terse else "")

    value = (
        json.dumps({k: _process_patterns(v) for k, v in [("include", include), ("exclude", exclude)] if v})
        if include or exclude
        else "false"
        if show is False
        else True
    )

    return DatastarAttr({key: value})


# ============================================================================
# Event Handlers
# ============================================================================


def _build_event_key(base: str, modifiers: list[str], value_mods: dict[str, str]) -> str:
    modifier_parts = modifiers.copy()

    for name, value in value_mods.items():
        if value is True:
            modifier_parts.append(name)
        elif name in ("debounce", "throttle"):
            if match := re.search(r"(\d+)", str(value)):
                modifier_parts.append(f"{name}.{match.group(1)}ms")
        elif name == "duration":
            if match := re.search(r"(\d+)(ms|s)?", str(value)):
                num, unit = match.groups()
                modifier_parts.append(f"duration.{num}{'s' if unit == 's' else 'ms'}")
        else:
            modifier_parts.append(f"{name}.{value}")

    return f"{base}__{'.'.join(modifier_parts)}" if modifier_parts else base


def _create_event_handler(event_name: str):
    def handler(expression: str, *modifiers, **kwargs) -> DatastarAttr:
        key = _build_event_key(f"data-on-{event_name}", list(modifiers), kwargs)
        return DatastarAttr({key: NotStr(expression)})

    return handler


ds_on_click = _create_event_handler("click")
ds_on_input = _create_event_handler("input")
ds_on_change = _create_event_handler("change")
ds_on_submit = _create_event_handler("submit")
ds_on_keydown = _create_event_handler("keydown")
ds_on_keyup = _create_event_handler("keyup")
ds_on_focus = _create_event_handler("focus")
ds_on_blur = _create_event_handler("blur")
ds_on_scroll = _create_event_handler("scroll")
ds_on_resize = _create_event_handler("resize")
ds_on_load = _create_event_handler("load")
ds_on_interval = _create_event_handler("interval")
ds_on_intersect = _create_event_handler("intersect")


def ds_on(event: str, expression: str, *modifiers, **kwargs) -> DatastarAttr:
    key = _build_event_key(f"data-on-{event}", list(modifiers), kwargs)
    return DatastarAttr({key: NotStr(expression)})


# ============================================================================
# Special Attributes
# ============================================================================


def ds_disabled(value: bool | str) -> DatastarAttr:
    return DatastarAttr({"data-disabled": _normalize_value(value)})


def ds_ignore(*modifiers) -> DatastarAttr:
    if "self" in modifiers:
        return DatastarAttr({"data-ignore__self": ""})
    return DatastarAttr({"data-ignore": ""})


def ds_preserve_attr(*attrs) -> DatastarAttr:
    return DatastarAttr({"data-preserve-attr": ",".join(attrs) if attrs else "*"})


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "t",
    "if_",
    "equals",
    "gt",
    "lt",
    "gte",
    "lte",
    "ds_show",
    "ds_text",
    "ds_bind",
    "ds_ref",
    "ds_indicator",
    "ds_effect",
    "ds_computed",
    "ds_class",
    "ds_style",
    "ds_attr",
    "ds_signals",
    "ds_persist",
    "ds_json_signals",
    "ds_on_click",
    "ds_on_input",
    "ds_on_change",
    "ds_on_submit",
    "ds_on_keydown",
    "ds_on_keyup",
    "ds_on_focus",
    "ds_on_blur",
    "ds_on_scroll",
    "ds_on_resize",
    "ds_on_load",
    "ds_on_interval",
    "ds_on_intersect",
    "ds_on",
    "ds_disabled",
    "ds_ignore",
    "ds_preserve_attr",
]
