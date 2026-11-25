#!/usr/bin/env python3
"""Deterministic name checks; no dictionaries, network, or aesthetic judgments.

Run ``python name_checks.py input.json`` or pipe UTF-8 JSON to ``... -``.
All results, including input errors, are JSON on stdout. Input errors exit 2.
The module's ``evaluate`` function also accepts an already decoded JSON object.
"""

from __future__ import annotations

import json
import sys
import unicodedata
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


DIMENSIONS = (
    "phonology", "meaning", "usability", "longevity", "distinctiveness",
    "context", "family",
)
DEFAULT_WEIGHTS = dict(zip(DIMENSIONS, (20, 20, 20, 15, 10, 10, 5)))
SEVERITIES = {"serious", "moderate", "minor", "none", "unverified"}
UNVERIFIED_CHECKS = {
    "official_character_table": "无法验证：未连接或内置官方规范字表。",
    "household_registration": "无法验证：户籍登记可用性须向办理机关核实。",
    "pronunciation": "无法验证：未内置读音、多音字和变调资料。",
    "dialect": "无法验证：方言及家庭实际发音须人工核实。",
    "population_name_frequency": "无法验证：没有权威重名统计数据。",
    "semantics_and_allusions": "无法验证：字义、典故和引文须核对可靠来源。",
    "aesthetic_suitability": "无法验证：本工具不作自动审美判断。",
}


class InputError(ValueError):
    """A safe, user-facing validation error."""


def _object(value, where, allowed, required=()):
    if not isinstance(value, dict):
        raise InputError(f"{where} 必须是 JSON 对象。")
    unknown = set(value) - set(allowed)
    if unknown:
        raise InputError(f"{where} 含未知字段：{', '.join(sorted(map(repr, unknown)))}。")
    missing = set(required) - set(value)
    if missing:
        raise InputError(f"{where} 缺少字段：{', '.join(sorted(missing))}。")
    return value


def _text(value, where, name=False):
    if not isinstance(value, str):
        raise InputError(f"{where} 必须是字符串。")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise InputError(f"{where} 含无效 Unicode 代理字符。") from None
    value = value.strip()
    if not value:
        raise InputError(f"{where} 不得为空。")
    if name and any(char.isspace() or unicodedata.category(char) in {"Cc", "Cf", "Cs"}
                    for char in value):
        raise InputError(f"{where} 内部不得含空白或控制字符。")
    return value


def _list(value, where):
    if not isinstance(value, list):
        raise InputError(f"{where} 必须是数组。")
    return value


def _number(value, where, minimum=0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{where} 必须是有限数字，不能是布尔值。")
    try:
        result = Decimal(str(value))
    except (ValueError, ArithmeticError):
        raise InputError(f"{where} 必须是有限数字。") from None
    if not result.is_finite():
        raise InputError(f"{where} 必须是有限数字。")
    if result < minimum or (maximum is not None and result > maximum):
        upper = f" 至 {maximum}" if maximum is not None else " 以上"
        raise InputError(f"{where} 必须在 {minimum}{upper}的范围内。")
    return Fraction(result)


def _json_number(value):
    """Keep integral contributions integral and decimal fractions JSON-safe."""
    return int(value) if value.denominator == 1 else float(value)


def _constraints(raw):
    allowed = ("banned_chars", "banned_names", "rejected_names", "required_chars", "given_lengths")
    _object(raw, "constraints", allowed)
    result = {}
    for key in allowed[:-1]:
        values = _list(raw.get(key, []), f"constraints.{key}")
        normalized = []
        for index, value in enumerate(values):
            value = _text(value, f"constraints.{key}[{index}]", name=True)
            if key.endswith("_chars") and len(value) != 1:
                raise InputError(f"constraints.{key}[{index}] 必须是单个字符。")
            if value not in normalized:
                normalized.append(value)
        result[key] = normalized
    lengths = _list(raw.get("given_lengths", []), "constraints.given_lengths")
    result["given_lengths"] = []
    for index, length in enumerate(lengths):
        if isinstance(length, bool) or not isinstance(length, int) or length <= 0:
            raise InputError(f"constraints.given_lengths[{index}] 必须是正整数。")
        if length not in result["given_lengths"]:
            result["given_lengths"].append(length)
    overlap = set(result["required_chars"]) & set(result["banned_chars"])
    if overlap:
        raise InputError("constraints 冲突：同一个名用字不能同时必含和禁用。")
    if lengths and len(result["required_chars"]) > max(lengths):
        raise InputError("constraints 冲突：必含的不同字符数量超过所有允许的名长度。")
    return result


def _weights(raw):
    _object(raw, "weights", DIMENSIONS, DIMENSIONS)
    result = {key: _number(raw[key], f"weights.{key}", 0, 100) for key in DIMENSIONS}
    if sum(result.values()) != 100:
        raise InputError("weights 的七维权重总和必须为 100。")
    return result


def _scores(raw, weights, where):
    _object(raw, where, DIMENSIONS)
    normalized = {}
    contributions = {}
    known = Fraction(0)
    unknown_weight = Fraction(0)
    known_weight = Fraction(0)
    for key in DIMENSIONS:
        if key not in raw:
            value = None
            reason = "未提供此维度的证据或评分。"
        else:
            item = _object(raw[key], f"{where}.{key}", ("value", "reason"), ("value", "reason"))
            reason = _text(item["reason"], f"{where}.{key}.reason")
            value = None if item["value"] is None else _number(item["value"], f"{where}.{key}.value", 0, 5)
        normalized[key] = {"value": None if value is None else _json_number(value), "reason": reason}
        if value is None:
            contributions[key] = None
            unknown_weight += weights[key]
        else:
            contribution = value * weights[key] / 5
            contributions[key] = _json_number(contribution)
            known += contribution
            known_weight += weights[key]
    complete = unknown_weight == 0
    score = (2 * known.numerator + known.denominator) // (2 * known.denominator) if complete else None
    return {
        "scores": normalized,
        "score": score,
        "score_complete": complete,
        "coverage": {
            "known_weight": _json_number(known_weight),
            "unknown_weight": _json_number(unknown_weight),
            "percent": _json_number(known_weight),
            "known_dimensions": [key for key in DIMENSIONS if normalized[key]["value"] is not None],
            "unknown_dimensions": [key for key in DIMENSIONS if normalized[key]["value"] is None],
        },
        "score_interval": [known.numerator // known.denominator,
                           -(-(known + unknown_weight).numerator // (known + unknown_weight).denominator)],
        "known_contribution": _json_number(known),
        "contributions": contributions,
    }


def _risks(raw, where):
    result = []
    for index, item in enumerate(_list(raw, where)):
        item_where = f"{where}[{index}]"
        _object(item, item_where, ("severity", "reason"), ("severity", "reason"))
        severity = item["severity"]
        if not isinstance(severity, str) or severity not in SEVERITIES:
            raise InputError(f"{item_where}.severity 值无效。")
        result.append({"severity": severity, "reason": _text(item["reason"], f"{item_where}.reason")})
    return result


def _checks(surname, given, full_name, constraints):
    checks = []
    violations = []
    conditions = (
        ("banned_chars", not any(char in given for char in constraints["banned_chars"]),
         "名中不含禁用字。", "名中含禁用字。"),
        ("banned_names", full_name not in constraints["banned_names"],
         "全名不在禁用姓名列表中。", "全名在禁用姓名列表中。"),
        ("rejected_names", full_name not in constraints["rejected_names"],
         "全名不在已拒绝姓名列表中。", "全名在已拒绝姓名列表中。"),
        ("required_chars", all(char in given for char in constraints["required_chars"]),
         "名中包含全部必含字。", "名中缺少必含字。"),
        ("given_lengths", not constraints["given_lengths"] or len(given) in constraints["given_lengths"],
         "名的 Unicode 字符数量符合所给长度约束。", "名的 Unicode 字符数量不符合所给长度约束。"),
    )
    for key, passed, yes, no in conditions:
        reason = "未设置此项硬约束，无此限制。" if not constraints[key] else (yes if passed else no)
        checks.append({"check": key, "status": "pass" if passed else "fail", "reason": reason})
        if not passed:
            violations.append(reason)
    for key, reason in UNVERIFIED_CHECKS.items():
        checks.append({"check": key, "status": "unverified", "reason": reason})
    return checks, violations


def evaluate(data):
    """Validate a request and return checks without sorting or recommending names."""
    _object(data, "input", ("surname", "candidates", "constraints", "weights"), ("surname", "candidates"))
    surname = _text(data["surname"], "surname", name=True)
    candidates = _list(data["candidates"], "candidates")
    if not candidates:
        raise InputError("candidates 不得为空。")
    constraints = _constraints(data.get("constraints", {}))
    weights = _weights(data.get("weights", DEFAULT_WEIGHTS))
    results = []
    duplicates = []
    seen = {}
    for index, raw in enumerate(candidates):
        where = f"candidates[{index}]"
        _object(raw, where, ("given", "scores", "risks"), ("given",))
        given = _text(raw["given"], f"{where}.given", name=True)
        full_name = surname + given
        # Keep every assessment: deduplication must not hide a risk or conflicting score.
        scores = _scores(raw.get("scores", {}), weights, f"{where}.scores")
        risks = _risks(raw.get("risks", []), f"{where}.risks")
        duplicate_of = seen.get(full_name)
        duplicate = full_name in seen
        if duplicate:
            duplicates.append({"input_index": index, "duplicate_of": duplicate_of})
        else:
            seen[full_name] = index
        checks, blocked_reasons = _checks(surname, given, full_name, constraints)
        blocked_reasons.extend("严重风险：" + item["reason"] for item in risks if item["severity"] == "serious")
        results.append({
            "input_index": index, "surname": surname, "given": given,
            "full_name": full_name, "duplicate": duplicate, "duplicate_of": duplicate_of,
            **scores, "risks": risks, "objective_checks": checks,
            "hard_constraints_passed": all(item["status"] != "fail" for item in checks),
            "blocked": bool(blocked_reasons), "blocked_reasons": blocked_reasons,
        })
    serious_by_name = {}
    for result in results:
        for risk in result["risks"]:
            if risk["severity"] == "serious":
                serious_by_name.setdefault(result["full_name"], []).append((result["input_index"], risk["reason"]))
    for result in results:
        for source_index, reason in serious_by_name.get(result["full_name"], []):
            if source_index != result["input_index"]:
                result["blocked_reasons"].append(f"同名另一评估（输入索引 {source_index}）的严重风险：{reason}")
        result["blocked"] = bool(result["blocked_reasons"])
    return {
        "surname": surname,
        "weights": {key: _json_number(weights[key]) for key in DIMENSIONS},
        "constraints": constraints,
        "candidates": results, "duplicates": duplicates, "unique_full_names": list(seen),
        "input_count": len(candidates), "unique_count": len(seen),
        "notice": "未被拦截不代表推荐；评分与风险来自输入，未验证项目仍须核实。",
    }


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"JSON 含重复字段：{key!r}。")
        result[key] = value
    return result


def _constant(value):
    raise InputError(f"JSON 不允许非有限数字：{value}。")


def _emit(value):
    # ASCII escapes remain valid UTF-8 and also work in legacy Windows terminals.
    sys.stdout.write(json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":")) + "\n")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args == ["--help"]:
        _emit({"usage": "python name_checks.py INPUT.json | python name_checks.py -",
               "input": {"surname": "李", "candidates": [{"given": "清和"}]}})
        return 0
    try:
        if len(args) != 1:
            raise InputError("请提供一个 UTF-8 JSON 文件路径，或使用 - 从标准输入读取。")
        if args[0] == "-":
            if hasattr(sys.stdin, "buffer"):
                source = sys.stdin.buffer.read().decode("utf-8-sig")
            else:
                source = sys.stdin.read().removeprefix("\ufeff")
        else:
            source = Path(args[0]).read_text(encoding="utf-8-sig")
        data = json.loads(source, object_pairs_hook=_pairs, parse_constant=_constant)
        _emit(evaluate(data))
        return 0
    except (InputError, json.JSONDecodeError, UnicodeError, OSError, ValueError, RecursionError) as error:
        if isinstance(error, InputError):
            message = str(error)
        elif isinstance(error, json.JSONDecodeError):
            message = f"JSON 格式错误：第 {error.lineno} 行，第 {error.colno} 列。"
        elif isinstance(error, UnicodeError):
            message = "输入必须是有效的 UTF-8 文本。"
        elif isinstance(error, OSError):
            message = "无法读取输入文件。"
        elif isinstance(error, RecursionError):
            message = "JSON 嵌套过深。"
        else:
            message = "JSON 数字或数据格式无效。"
        _emit({"error": {"type": "input_error", "message": message}})
        return 2


if __name__ == "__main__":
    sys.exit(main())
