"""A validator for the part of JSON Schema (draft 2020-12) that the rule schema uses.

The rule format has a versioned JSON Schema (``rule_db/schema/rule.v1.schema.json``) and
every rule is validated against it on load. The usual library for that, ``jsonschema``,
is not among this repository's dependencies, which are kept to the standard library,
PyYAML and, optionally, matplotlib (``tests/test_repo_hygiene.py``). So the keywords the
schema uses are implemented here, and only those: :func:`unsupported_keywords` lists any
keyword in a schema that this module does not implement, and a test fails if the rule
schema has one. A keyword cannot be ignored silently.

Implemented: ``type``, ``enum``, ``const``; ``properties``, ``required``,
``additionalProperties``, ``propertyNames``, ``minProperties``, ``maxProperties``;
``items``, ``minItems``, ``maxItems``, ``uniqueItems``; ``pattern``, ``minLength``,
``maxLength``; ``minimum``, ``maximum``, ``exclusiveMinimum``, ``exclusiveMaximum``;
``allOf``, ``anyOf``, ``oneOf``, ``not``; ``$ref`` to ``#/$defs/...`` within the same
schema. Annotations (``$schema``, ``$id``, ``title``, ``description``, ``$comment``,
``default``, ``examples``) are accepted and have no effect, as in the standard.

``pattern`` is matched with Python's ``re.search``: unanchored, as the standard says. The
patterns in the rule schema use only what Python's and ECMA 262's syntax share.
"""

from __future__ import annotations

import math
import re
from typing import Any, Mapping

ANNOTATIONS = frozenset({"$schema", "$id", "title", "description", "$comment", "default", "examples"})
ASSERTIONS = frozenset(
    {
        "type", "enum", "const",
        "properties", "required", "additionalProperties", "propertyNames", "minProperties", "maxProperties",
        "items", "minItems", "maxItems", "uniqueItems",
        "pattern", "minLength", "maxLength",
        "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
        "allOf", "anyOf", "oneOf", "not",
        "$ref", "$defs",
    }
)
SUPPORTED = ANNOTATIONS | ASSERTIONS
TYPES = ("object", "array", "string", "number", "integer", "boolean", "null")


def unsupported_keywords(schema: Any) -> set[str]:
    """Every keyword used anywhere in ``schema`` that this module does not implement."""
    found: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, bool):
            return
        if not isinstance(node, Mapping):
            found.add(f"<not a schema: {type(node).__name__}>")
            return
        for key, value in node.items():
            if key not in SUPPORTED:
                found.add(key)
            elif key in ("properties", "$defs"):
                for child in value.values():
                    walk(child)
            elif key in ("additionalProperties", "propertyNames", "items", "not"):
                walk(value)
            elif key in ("allOf", "anyOf", "oneOf"):
                for child in value:
                    walk(child)

    walk(schema)
    return found


def _is_type(value: Any, name: str) -> bool:
    if name == "null":
        return value is None
    if name == "boolean":
        return isinstance(value, bool)
    if name == "string":
        return isinstance(value, str)
    if name == "object":
        return isinstance(value, Mapping)
    if name == "array":
        return isinstance(value, (list, tuple))
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if name == "number":
        return not (isinstance(value, float) and not math.isfinite(value))
    if name == "integer":
        return isinstance(value, int) or (math.isfinite(value) and float(value).is_integer())
    raise ValueError(f"unknown JSON Schema type {name!r}")


def json_equal(a: Any, b: Any) -> bool:
    """Equality as JSON sees it: 1 equals 1.0, but true is not 1."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        return set(a) == set(b) and all(json_equal(a[key], b[key]) for key in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(json_equal(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b


class Validator:
    """Validates instances against one schema document."""

    def __init__(self, schema: Mapping[str, Any]):
        unsupported = unsupported_keywords(schema)
        if unsupported:
            raise ValueError(f"the schema uses keywords this validator does not implement: {sorted(unsupported)}")
        self.schema = schema

    def errors(self, instance: Any) -> list[str]:
        """Every way ``instance`` fails the schema, as ``"<path>: <what>"``; empty if it passes."""
        found: list[str] = []
        self._check(instance, self.schema, "$", found)
        return found

    # --- internals ------------------------------------------------------------------------

    def _resolve(self, reference: str) -> Any:
        if not reference.startswith("#/$defs/"):
            raise ValueError(f"only references to '#/$defs/...' are supported, got {reference!r}")
        name = reference[len("#/$defs/"):]
        definitions = self.schema.get("$defs", {})
        if name not in definitions:
            raise ValueError(f"unknown reference {reference!r}")
        return definitions[name]

    def _check(self, value: Any, schema: Any, path: str, out: list[str]) -> None:
        if schema is True:
            return
        if schema is False:
            out.append(f"{path}: nothing is allowed here")
            return
        if "$ref" in schema:
            self._check(value, self._resolve(schema["$ref"]), path, out)

        if "type" in schema:
            names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
            if not any(_is_type(value, name) for name in names):
                out.append(f"{path}: expected {' or '.join(names)}, got {_describe(value)}")
                return  # the other keywords would only repeat the complaint
        if "const" in schema and not json_equal(value, schema["const"]):
            out.append(f"{path}: must be {schema['const']!r}, got {value!r}")
        if "enum" in schema and not any(json_equal(value, option) for option in schema["enum"]):
            out.append(f"{path}: must be one of {list(schema['enum'])}, got {value!r}")

        if isinstance(value, Mapping):
            self._check_object(value, schema, path, out)
        elif isinstance(value, (list, tuple)):
            self._check_array(value, schema, path, out)
        elif isinstance(value, str):
            if "pattern" in schema and not re.search(schema["pattern"], value):
                out.append(f"{path}: {value!r} does not match the pattern {schema['pattern']!r}")
            if "minLength" in schema and len(value) < schema["minLength"]:
                out.append(f"{path}: must have at least {schema['minLength']} character(s)")
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                out.append(f"{path}: must have at most {schema['maxLength']} character(s)")
        elif _is_type(value, "number"):
            for keyword, fails, words in (
                ("minimum", lambda v, b: v < b, "at least"),
                ("maximum", lambda v, b: v > b, "at most"),
                ("exclusiveMinimum", lambda v, b: v <= b, "more than"),
                ("exclusiveMaximum", lambda v, b: v >= b, "less than"),
            ):
                if keyword in schema and fails(value, schema[keyword]):
                    out.append(f"{path}: must be {words} {schema[keyword]}, got {value!r}")

        for sub in schema.get("allOf", ()):
            self._check(value, sub, path, out)
        if "anyOf" in schema:
            self._one_or_any(value, schema["anyOf"], path, out, exactly_one=False)
        if "oneOf" in schema:
            self._one_or_any(value, schema["oneOf"], path, out, exactly_one=True)
        if "not" in schema and not self._fails(value, schema["not"], path):
            out.append(f"{path}: must not match the schema under 'not'")

    def _check_object(self, value: Mapping[str, Any], schema: Mapping[str, Any], path: str, out: list[str]) -> None:
        for key in schema.get("required", ()):
            if key not in value:
                out.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            child = f"{path}.{key}"
            if not isinstance(key, str):
                out.append(f"{path}: property names must be text, got {key!r}")
                continue
            if "propertyNames" in schema:
                self._check(key, schema["propertyNames"], f"{path} (property name {key!r})", out)
            if key in properties:
                self._check(item, properties[key], child, out)
            elif "additionalProperties" in schema:
                extra = schema["additionalProperties"]
                if extra is False:
                    out.append(f"{path}: unknown property {key!r}; allowed: {sorted(properties)}")
                else:
                    self._check(item, extra, child, out)
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            out.append(f"{path}: must have at least {schema['minProperties']} propert(ies)")
        if "maxProperties" in schema and len(value) > schema["maxProperties"]:
            out.append(f"{path}: must have at most {schema['maxProperties']} propert(ies)")

    def _check_array(self, value: Any, schema: Mapping[str, Any], path: str, out: list[str]) -> None:
        if "minItems" in schema and len(value) < schema["minItems"]:
            out.append(f"{path}: must have at least {schema['minItems']} item(s)")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            out.append(f"{path}: must have at most {schema['maxItems']} item(s)")
        if schema.get("uniqueItems"):
            for i, first in enumerate(value):
                if any(json_equal(first, second) for second in value[i + 1 :]):
                    out.append(f"{path}: items must be distinct; {first!r} appears twice")
                    break
        if "items" in schema:
            for index, item in enumerate(value):
                self._check(item, schema["items"], f"{path}[{index}]", out)

    def _fails(self, value: Any, schema: Any, path: str) -> list[str]:
        found: list[str] = []
        self._check(value, schema, path, found)
        return found

    def _one_or_any(self, value: Any, options: Any, path: str, out: list[str], exactly_one: bool) -> None:
        results = [self._fails(value, option, path) for option in options]
        passing = sum(1 for errors in results if not errors)
        if exactly_one and passing == 1 or not exactly_one and passing >= 1:
            return
        if passing > 1:
            out.append(f"{path}: matches {passing} of the allowed forms; it must match exactly one")
            return
        # Report the form it came closest to: the one with the fewest complaints.
        closest = min(results, key=len)
        out.append(f"{path}: does not match any of the allowed forms; the closest fails with:")
        out.extend(f"    {line}" for line in closest)


def _describe(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, Mapping):
        return "an object"
    if isinstance(value, (list, tuple)):
        return "an array"
    if isinstance(value, str):
        return f"text {value!r}"
    return f"{type(value).__name__} {value!r}"
