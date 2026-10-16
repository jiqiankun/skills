"""Run with: python -m unittest discover -s tests -p test_name_checks.py -v."""

import copy
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "name_checks.py"
SPEC = importlib.util.spec_from_file_location("name_checks", SCRIPT)
NC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NC)


def request(given="清和", surname="李", **extra):
    return {"surname": surname, "candidates": [{"given": given}], **extra}


def scored(value=5):
    return {key: {"value": value, "reason": "已提供人工核验说明"} for key in NC.DIMENSIONS}


class NameChecksTest(unittest.TestCase):
    def candidate(self, data):
        return NC.evaluate(data)["candidates"][0]

    def assert_invalid(self, data):
        with self.assertRaises(NC.InputError):
            NC.evaluate(data)

    def test_compound_surname_is_explicit(self):
        result = self.candidate(request(surname="欧阳", constraints={"given_lengths": [2]}))
        self.assertEqual((result["surname"], result["given"], result["full_name"]), ("欧阳", "清和", "欧阳清和"))
        self.assertTrue(result["hard_constraints_passed"])

    def test_surname_is_never_inferred_from_given(self):
        result = self.candidate(request(given="欧阳", surname="司马"))
        self.assertEqual(result["full_name"], "司马欧阳")

    def test_banned_chars_apply_only_to_given(self):
        result = self.candidate(request(surname="李", constraints={"banned_chars": ["李"]}))
        self.assertFalse(result["blocked"])
        result = self.candidate(request(given="李清", constraints={"banned_chars": ["李"]}))
        self.assertTrue(result["blocked"])

    def test_required_chars_not_satisfied_by_surname(self):
        result = self.candidate(request(constraints={"required_chars": ["李"]}))
        self.assertTrue(result["blocked"])

    def test_required_char_can_appear_in_any_position(self):
        for given in ("清和", "和清"):
            with self.subTest(given=given):
                self.assertFalse(self.candidate(request(given=given, constraints={"required_chars": ["清"]}))["blocked"])

    def test_rejected_names_match_full_name_exactly(self):
        result = self.candidate(request(constraints={"rejected_names": ["李清和"]}))
        self.assertTrue(result["blocked"])
        self.assertIn("已拒绝", result["blocked_reasons"][0])
        result = self.candidate(request(constraints={"rejected_names": ["清和"]}))
        self.assertFalse(result["blocked"])

    def test_banned_names_are_complete_not_substring(self):
        self.assertTrue(self.candidate(request(constraints={"banned_names": ["李清和"]}))["blocked"])
        self.assertFalse(self.candidate(request(constraints={"banned_names": ["清"]}))["blocked"])

    def test_given_length_uses_given_not_full_name(self):
        self.assertFalse(self.candidate(request(surname="上官", constraints={"given_lengths": [2]}))["blocked"])
        self.assertTrue(self.candidate(request(surname="上官", constraints={"given_lengths": [1]}))["blocked"])

    def test_no_length_constraint_is_assumed(self):
        self.assertFalse(self.candidate(request(given="清和明远"))["blocked"])

    def test_constraint_conflict_is_input_error(self):
        self.assert_invalid(request(constraints={"banned_chars": ["清"], "required_chars": ["清"]}))
        self.assert_invalid(request(constraints={"required_chars": ["清", "和"], "given_lengths": [1]}))

    def test_duplicate_required_char_is_not_two_required_characters(self):
        result = NC.evaluate(request(given="清", constraints={"required_chars": ["清", "清"], "given_lengths": [1]}))
        self.assertFalse(result["candidates"][0]["blocked"])
        self.assertEqual(result["constraints"]["required_chars"], ["清"])

    def test_constraint_types_and_single_char_entries(self):
        for constraints in ({"given_lengths": [0]}, {"given_lengths": [-1]}, {"given_lengths": [True]},
                            {"given_lengths": [2.0]}, {"given_lengths": "2"}, {"banned_chars": ["清和"]},
                            {"required_chars": [""]}, {"banned_names": [None]}, {"banned_chars": "清"}):
            with self.subTest(constraints=constraints):
                self.assert_invalid(request(constraints=constraints))

    def test_ordered_exact_deduplication_and_strip(self):
        data = {"surname": " 李 ", "candidates": [{"given": "清和"}, {"given": "明远"}, {"given": " 清和 "}]}
        result = NC.evaluate(data)
        self.assertEqual([item["full_name"] for item in result["candidates"]], ["李清和", "李明远", "李清和"])
        self.assertEqual(result["unique_full_names"], ["李清和", "李明远"])
        self.assertTrue(result["candidates"][2]["duplicate"])
        self.assertEqual(result["candidates"][2]["duplicate_of"], 0)
        self.assertEqual(result["duplicates"], [{"input_index": 2, "duplicate_of": 0}])

    def test_simplified_traditional_and_compatibility_not_normalized(self):
        data = {"surname": "李", "candidates": [{"given": value} for value in ("龙", "龍", "Ａ", "A")]}
        self.assertEqual(NC.evaluate(data)["unique_count"], 4)

    def test_extended_han_is_accepted_without_official_claim(self):
        result = self.candidate(request(given="𠮷𰻞", constraints={"given_lengths": [2]}))
        self.assertEqual(result["given"], "𠮷𰻞")
        checks = {item["check"]: item for item in result["objective_checks"]}
        self.assertEqual(checks["official_character_table"]["status"], "unverified")

    def test_empty_names_whitespace_controls_and_surrogates_rejected(self):
        for value in ("", "  ", "清 和", "清\t和", "清\n和", "清\x00和", "清\u200b和", "\ud800"):
            with self.subTest(value=repr(value)):
                self.assert_invalid(request(given=value))
                self.assert_invalid(request(surname=value))

    def test_default_all_unknown_does_not_impute_score(self):
        result = self.candidate(request())
        self.assertIsNone(result["score"])
        self.assertFalse(result["score_complete"])
        self.assertEqual(result["score_interval"], [0, 100])
        self.assertEqual(result["coverage"]["percent"], 0)
        self.assertTrue(all(value is None for value in result["contributions"].values()))

    def test_default_weights_and_complete_score(self):
        data = request()
        data["candidates"][0]["scores"] = scored(4)
        result = self.candidate(data)
        self.assertEqual(result["score"], 80)
        self.assertEqual(result["score_interval"], [80, 80])
        self.assertEqual(result["coverage"]["known_weight"], 100)
        self.assertEqual(result["contributions"]["phonology"], 16)

    def test_custom_weights_change_score(self):
        data = request(weights={key: 100 if key == "family" else 0 for key in NC.DIMENSIONS})
        data["candidates"][0]["scores"] = scored(5)
        data["candidates"][0]["scores"]["family"]["value"] = 1
        self.assertEqual(self.candidate(data)["score"], 20)

    def test_unknown_dimension_does_not_redistribute_weight(self):
        data = request()
        data["candidates"][0]["scores"] = {"phonology": {"value": 4, "reason": "人工读音评估"}}
        result = self.candidate(data)
        self.assertIsNone(result["score"])
        self.assertEqual(result["score_interval"], [16, 96])
        self.assertEqual(result["known_contribution"], 16)
        self.assertEqual(result["coverage"]["unknown_weight"], 80)

    def test_explicit_null_requires_reason_and_stays_unknown(self):
        data = request()
        data["candidates"][0]["scores"] = {"phonology": {"value": None, "reason": "方言尚未核验"}}
        self.assertIsNone(self.candidate(data)["scores"]["phonology"]["value"])
        data["candidates"][0]["scores"]["phonology"]["reason"] = " "
        self.assert_invalid(data)

    def test_unknown_zero_weight_does_not_prevent_complete_total(self):
        data = request(weights={key: 100 if key == "meaning" else 0 for key in NC.DIMENSIONS})
        data["candidates"][0]["scores"] = {"meaning": {"value": 3, "reason": "人工释义"}}
        result = self.candidate(data)
        self.assertEqual(result["score"], 60)
        self.assertTrue(result["score_complete"])
        self.assertEqual(result["coverage"]["unknown_weight"], 0)

    def test_score_rounding_is_half_up(self):
        data = request(weights={key: 100 if key == "family" else 0 for key in NC.DIMENSIONS})
        data["candidates"][0]["scores"] = {"family": {"value": 4.025, "reason": "边界舍入"}}
        result = self.candidate(data)
        self.assertEqual(result["score"], 81)
        self.assertEqual(result["score_interval"], [80, 81])

    def test_interval_rounds_outward_for_partial_evidence(self):
        data = request()
        data["candidates"][0]["scores"] = {"phonology": {"value": 4.01, "reason": "人工评估"}}
        result = self.candidate(data)
        self.assertEqual(result["score_interval"], [16, 97])

    def test_invalid_score_numbers(self):
        for value in (True, "5", -0.01, 5.01, float("nan"), float("inf"), -float("inf"), [], {}):
            with self.subTest(value=value):
                data = request()
                data["candidates"][0]["scores"] = {"meaning": {"value": value, "reason": "说明"}}
                self.assert_invalid(data)

    def test_invalid_score_shape_or_missing_reason(self):
        for scores in (None, [], {"meaning": 5}, {"meaning": {"value": 5}},
                       {"meaning": {"value": 5, "reason": 8}},
                       {"meaning": {"value": 5, "reason": "说明", "extra": 1}}):
            with self.subTest(scores=scores):
                data = request()
                data["candidates"][0]["scores"] = scores
                self.assert_invalid(data)

    def test_invalid_custom_weights(self):
        cases = [None, [], {}, {key: 0 for key in NC.DIMENSIONS},
                 {**NC.DEFAULT_WEIGHTS, "family": -5}, {**NC.DEFAULT_WEIGHTS, "family": 6},
                 {**NC.DEFAULT_WEIGHTS, "family": True}, {**NC.DEFAULT_WEIGHTS, "family": "5"},
                 {**NC.DEFAULT_WEIGHTS, "family": float("inf")}, {**NC.DEFAULT_WEIGHTS, "traditional": 0}]
        for weights in cases:
            with self.subTest(weights=weights):
                self.assert_invalid(request(weights=weights))

    def test_custom_weight_sum_is_exact_without_tolerance_inflation(self):
        weights = {**NC.DEFAULT_WEIGHTS, "family": 5.0000000001}
        self.assert_invalid(request(weights=weights))

    def test_serious_risk_blocks_independently_of_high_score(self):
        data = request()
        data["candidates"][0].update(scores=scored(5), risks=[{"severity": "serious", "reason": "家庭已确认严重谐音"}])
        result = self.candidate(data)
        self.assertEqual(result["score"], 100)
        self.assertTrue(result["blocked"])
        self.assertTrue(result["hard_constraints_passed"])
        self.assertIn("严重风险", result["blocked_reasons"][0])

    def test_other_risk_levels_are_reported_without_automatic_block(self):
        for severity in ("moderate", "minor", "none", "unverified"):
            with self.subTest(severity=severity):
                data = request()
                data["candidates"][0]["risks"] = [{"severity": severity, "reason": "待人工判断"}]
                result = self.candidate(data)
                self.assertFalse(result["blocked"])
                self.assertEqual(result["risks"][0]["severity"], severity)

    def test_risk_shape_and_severity_validation(self):
        for risks in (None, {}, [None], [{"severity": "severe", "reason": "说明"}],
                      [{"severity": True, "reason": "说明"}], [{"severity": "serious", "reason": ""}],
                      [{"severity": "serious"}], [{"severity": "minor", "reason": "说明", "score": 8}]):
            with self.subTest(risks=risks):
                data = request()
                data["candidates"][0]["risks"] = risks
                self.assert_invalid(data)

    def test_unknown_fields_reject_traditional_score_everywhere(self):
        data = request(traditional_score=99)
        self.assert_invalid(data)
        data = request()
        data["candidates"][0]["traditional"] = 99
        self.assert_invalid(data)
        data = request()
        data["candidates"][0]["scores"] = {"traditional": {"value": 5, "reason": "笔画"}}
        self.assert_invalid(data)
        self.assert_invalid(request(constraints={"bazi": "木"}))

    def test_invalid_root_and_candidate_shapes(self):
        for data in (None, [], {}, request(candidates=[]), {"surname": "李", "candidates": "清和"},
                     {"surname": "李", "candidates": [None]}, {"surname": "李", "candidates": [{}]},
                     {"surname": "李", "candidates": [{"given": 1}]}, request(constraints=None)):
            with self.subTest(data=data):
                self.assert_invalid(data)

    def test_duplicates_do_not_bypass_validation(self):
        data = {"surname": "李", "candidates": [{"given": "清和"}, {"given": "清和", "traditional": 99}]}
        self.assert_invalid(data)

    def test_duplicate_assessments_preserve_serious_risk_and_different_score(self):
        data = {"surname": "李", "candidates": [
            {"given": "清和", "scores": scored(5)},
            {"given": "清和", "scores": scored(1), "risks": [{"severity": "serious", "reason": "补充核验发现严重问题"}]},
        ]}
        result = NC.evaluate(data)
        self.assertEqual(result["unique_count"], 1)
        self.assertEqual([item["score"] for item in result["candidates"]], [100, 20])
        self.assertTrue(result["candidates"][0]["blocked"])
        self.assertIn("同名另一评估", result["candidates"][0]["blocked_reasons"][0])
        self.assertEqual(result["candidates"][0]["risks"], [])
        self.assertTrue(result["candidates"][1]["blocked"])

    def test_unconfigured_constraints_say_no_constraint(self):
        result = self.candidate(request())
        configured_checks = [item for item in result["objective_checks"] if item["status"] == "pass"]
        self.assertEqual(len(configured_checks), 5)
        self.assertTrue(all("未设置" in item["reason"] for item in configured_checks))

    def test_serious_risk_only_propagates_to_exact_same_full_name(self):
        data = {"surname": "李", "candidates": [
            {"given": "龙", "risks": [{"severity": "serious", "reason": "已确认的问题"}]},
            {"given": "龍"}, {"given": "明远"}, {"given": "龙"},
        ]}
        result = NC.evaluate(data)
        self.assertEqual([item["blocked"] for item in result["candidates"]], [True, False, False, True])
        self.assertEqual(result["candidates"][3]["risks"], [])

    def test_input_is_not_mutated(self):
        data = request(constraints={"required_chars": ["清", "清"]})
        before = copy.deepcopy(data)
        NC.evaluate(data)
        self.assertEqual(data, before)

    def test_no_automatic_sort_or_recommendation(self):
        data = {"surname": "李", "candidates": [{"given": "清和", "scores": scored(1)}, {"given": "明远", "scores": scored(5)}]}
        result = NC.evaluate(data)
        self.assertEqual([item["given"] for item in result["candidates"]], ["清和", "明远"])
        self.assertIn("未被拦截不代表推荐", result["notice"])

    def test_unverified_checks_never_claim_official_or_language_success(self):
        result = self.candidate(request())
        checks = {item["check"]: item["status"] for item in result["objective_checks"]}
        for key in NC.UNVERIFIED_CHECKS:
            self.assertEqual(checks[key], "unverified")


class CliTest(unittest.TestCase):
    def run_cli(self, source, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *(args or ("-",))], input=source,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=15)

    def assert_cli_error(self, source):
        result = self.run_cli(source)
        self.assertEqual(result.returncode, 2, result.stderr.decode("utf-8", errors="replace"))
        self.assertEqual(result.stderr, b"")
        self.assertEqual(json.loads(result.stdout)["error"]["type"], "input_error")

    def test_valid_utf8_stdin(self):
        result = self.run_cli(json.dumps(request(), ensure_ascii=False).encode("utf-8"))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["candidates"][0]["full_name"], "李清和")
        self.assertEqual(result.stderr, b"")

    def test_utf8_file_branch_requests_bom_aware_encoding(self):
        output = io.StringIO()
        with patch.object(Path, "read_text", return_value=json.dumps(request())) as read_text:
            with contextlib.redirect_stdout(output):
                code = NC.main(["input.json"])
        self.assertEqual(code, 0)
        read_text.assert_called_once_with(encoding="utf-8-sig")
        self.assertEqual(json.loads(output.getvalue())["unique_count"], 1)

    def test_bom_stdin(self):
        source = b"\xef\xbb\xbf" + json.dumps(request(), ensure_ascii=False).encode("utf-8")
        result = self.run_cli(source)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["unique_count"], 1)

    def test_malformed_empty_and_invalid_utf8(self):
        for source in (b"", b"  ", b"{", b"[]", b"{} trailing", b"\xff", b"null"):
            with self.subTest(source=source):
                self.assert_cli_error(source)

    def test_duplicate_json_keys_including_nested_keys(self):
        self.assert_cli_error('{"surname":"李","surname":"王","candidates":[{"given":"清"}]}'.encode("utf-8"))
        self.assert_cli_error('{"surname":"李","candidates":[{"given":"清","given":"和"}]}'.encode("utf-8"))

    def test_nan_infinity_and_overflowing_exponent(self):
        for numeric in ("NaN", "Infinity", "-Infinity", "1e999"):
            source = ('{"surname":"李","candidates":[{"given":"清","scores":{"meaning":'
                      '{"value":' + numeric + ',"reason":"说明"}}}]}').encode("utf-8")
            with self.subTest(numeric=numeric):
                self.assert_cli_error(source)

    def test_missing_file_and_wrong_argument_count_are_json_errors(self):
        result = self.run_cli(b"", str(SCRIPT.parent / "__missing_input__.json"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"]["type"], "input_error")
        result = self.run_cli(b"", "-", "extra")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"]["type"], "input_error")

    def test_unpaired_surrogate_is_json_input_error(self):
        self.assert_cli_error(b'{"surname":"Li","candidates":[{"given":"\\ud800"}]}')

    def test_excessive_nesting_has_no_traceback(self):
        self.assert_cli_error(b"[" * 2000 + b"]" * 2000)


if __name__ == "__main__":
    unittest.main()
