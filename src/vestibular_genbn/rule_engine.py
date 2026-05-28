from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

from .exceptions import RuleEvaluationError

_TRUE_VALUES = {True, 1, 1.0, "1", "true", "True", "yes", "present", "positive"}
_FALSE_VALUES = {False, 0, 0.0, "0", "false", "False", "no", "absent", "negative"}

Token = tuple[str, str]


def normalize_value(value: Any) -> Any:
    if value is None:
        return "unknown"
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return "unknown"
        if stripped in _TRUE_VALUES:
            return "yes"
        if stripped in _FALSE_VALUES:
            return "no"
        if stripped.lower() in {"unknown", "na", "n/a", "nan", "not_yet_observed"}:
            return stripped.lower()
        return stripped
    if value in _TRUE_VALUES:
        return "yes"
    if value in _FALSE_VALUES:
        return "no"
    return value


def truthy_yes(value: Any) -> bool | None:
    value = normalize_value(value)
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def _and3(a: bool | None, b: bool | None) -> bool | None:
    if a is False or b is False:
        return False
    if a is True and b is True:
        return True
    return None


def _or3(a: bool | None, b: bool | None) -> bool | None:
    if a is True or b is True:
        return True
    if a is False and b is False:
        return False
    return None


_TOKEN_RE = re.compile(
    r"\s*(?:(AND|OR|in)\b|([A-Za-z_][A-Za-z0-9_]*)|(==|!=)|([{}(),])|([.])|([^ \t\n\r]+))"
)


def _tokenize(rule: str) -> list[Token]:
    tokens: list[Token] = []
    for match in _TOKEN_RE.finditer(rule):
        keyword, ident, op, punct, dot, other = match.groups()
        if dot:
            continue
        if keyword:
            tokens.append((keyword.upper() if keyword in {"AND", "OR"} else "IN", keyword))
        elif ident:
            tokens.append(("IDENT", ident))
        elif op:
            tokens.append(("OP", op))
        elif punct:
            tokens.append((punct, punct))
        elif other:
            tokens.append(("VALUE", other))
    return tokens


@dataclass
class Parser:
    tokens: list[Token]
    values: Mapping[str, Any]
    pos: int = 0

    def peek(self) -> Token | None:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def accept(self, kind: str) -> Token | None:
        token = self.peek()
        if token and token[0] == kind:
            self.pos += 1
            return token
        return None

    def expect(self, kind: str) -> Token:
        token = self.accept(kind)
        if token is None:
            raise RuleEvaluationError(f"Expected {kind}, got {self.peek()}")
        return token

    def parse(self) -> bool | None:
        result = self.parse_or()
        return result

    def parse_or(self) -> bool | None:
        result = self.parse_and()
        while self.accept("OR"):
            rhs = self.parse_and()
            result = _or3(result, rhs)
        return result

    def parse_and(self) -> bool | None:
        result = self.parse_factor()
        while self.accept("AND"):
            rhs = self.parse_factor()
            result = _and3(result, rhs)
        return result

    def parse_factor(self) -> bool | None:
        if self.accept("("):
            result = self.parse_or()
            self.expect(")")
            return result
        return self.parse_atom()

    def parse_atom(self) -> bool | None:
        key = self.expect("IDENT")[1]
        token = self.peek()

        if token and token[0] == "OP":
            op = self.expect("OP")[1]
            expected = self.expect("IDENT")[1]
            actual = normalize_value(self.values.get(key, "unknown"))
            expected = normalize_value(expected)
            if actual == "unknown":
                return None
            result = actual == expected
            return result if op == "==" else not result

        if token and token[0] == "IN":
            self.expect("IN")
            self.expect("{")
            options = []
            while True:
                nxt = self.peek()
                if nxt is None:
                    raise RuleEvaluationError("Unclosed set in rule")
                if nxt[0] == "}":
                    self.expect("}")
                    break
                if nxt[0] in {"IDENT", "VALUE"}:
                    options.append(normalize_value(self.expect(nxt[0])[1]))
                    self.accept(",")
                    continue
                raise RuleEvaluationError(f"Unexpected token in set: {nxt}")

            actual = normalize_value(self.values.get(key, "unknown"))
            if actual == "unknown":
                return None
            return actual in set(options)

        return truthy_yes(self.values.get(key, "unknown"))


def evaluate_rule(rule: str, values: Mapping[str, Any]) -> bool | None:
    """Evaluate the limited JSON rule language with three-valued logic."""

    rule = rule.strip().strip(".")
    if not rule:
        return None
    tokens = _tokenize(rule)
    parser = Parser(tokens, values)
    result = parser.parse()
    if parser.peek() is not None:
        raise RuleEvaluationError(f"Unexpected trailing token: {parser.peek()}")
    return result
