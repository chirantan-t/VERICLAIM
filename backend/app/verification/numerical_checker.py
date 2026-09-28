"""
Numerical consistency checker for scientific claims.

Extracts numbers with units from claim and evidence texts, then checks
for exact matches, approximate matches, and discrepancies. Avoids
flagging harmless formatting differences.
"""

import re
from typing import Any, Dict, List, Tuple


class NumericalChecker:
    def __init__(self):
        # Matches numbers with optional commas, decimals, percentage signs, and units
        self.number_pattern = re.compile(
            r"(?<![.\w])"
            r"(\d+(?:,\d{3})*(?:\.\d+)?)"
            r"\s*"
            r"(%|percent|ms|seconds|sec|hours|hr|minutes|min|"
            r"GB|MB|KB|TB|Hz|GHz|MHz|kHz|"
            r"mm|cm|m|km|mg|g|kg|ml|L|"
            r"epochs?|iterations?|steps?|samples?|"
            r"pp|bps|dB|fps)?"
            r"(?![.\w])",
            re.IGNORECASE,
        )
        # Relative tolerance for approximate matching (10%)
        self.relative_tolerance = 0.10

    def _normalize_number(self, num_str: str) -> float:
        """Normalize a number string to a float."""
        clean = num_str.replace(",", "")
        return float(clean)

    def _extract_numbers(self, text: str) -> List[Dict[str, Any]]:
        """Extract numbers with their units from text."""
        matches = self.number_pattern.findall(text)
        results = []
        for num_str, unit in matches:
            try:
                value = self._normalize_number(num_str)
                raw = f"{num_str}{unit}".strip() if unit else num_str
                results.append(
                    {"raw": raw, "value": value, "unit": unit.lower().strip() if unit else ""}
                )
            except ValueError:
                continue
        return results

    def _is_approximate_match(
        self, val1: float, val2: float, unit1: str, unit2: str
    ) -> bool:
        """Check if two values are approximately equal (within tolerance)."""
        # Units must match (or both be empty)
        if unit1 != unit2:
            return False
        if val1 == 0 and val2 == 0:
            return True
        if val1 == 0 or val2 == 0:
            return abs(val1 - val2) < 0.01
        relative_diff = abs(val1 - val2) / max(abs(val1), abs(val2))
        return relative_diff <= self.relative_tolerance

    def check_consistency(self, claim: str, evidence: str) -> Dict[str, Any]:
        """
        Extracts numbers from claim and evidence, then checks consistency.

        Returns:
            Dictionary with status, matched/missing/approximate numbers, and message.
            Status is one of: CONSISTENT, APPROXIMATE, DISCREPANCY, NO_NUMBERS_IN_CLAIM
        """
        claim_numbers = self._extract_numbers(claim)
        evidence_numbers = self._extract_numbers(evidence)

        if not claim_numbers:
            return {
                "status": "NO_NUMBERS_IN_CLAIM",
                "claim_numbers": [],
                "evidence_numbers": [n["raw"] for n in evidence_numbers],
                "missing_numbers": [],
                "approximate_matches": [],
                "matched_numbers": [],
                "message": None,
            }

        matched: List[str] = []
        approximate_matches: List[Dict[str, str]] = []
        missing: List[str] = []

        for cn in claim_numbers:
            found_exact = False
            found_approx = False
            approx_evidence = None

            for en in evidence_numbers:
                # Exact match (value and unit)
                if cn["value"] == en["value"] and cn["unit"] == en["unit"]:
                    found_exact = True
                    matched.append(cn["raw"])
                    break
                # Exact value, different/no unit formatting
                elif cn["value"] == en["value"]:
                    found_exact = True
                    matched.append(cn["raw"])
                    break
                # Approximate match
                elif self._is_approximate_match(
                    cn["value"], en["value"], cn["unit"], en["unit"]
                ):
                    found_approx = True
                    approx_evidence = en["raw"]

            if not found_exact:
                if found_approx and approx_evidence:
                    approximate_matches.append(
                        {"claim": cn["raw"], "evidence": approx_evidence}
                    )
                else:
                    missing.append(cn["raw"])

        # Determine status
        if missing:
            status = "DISCREPANCY"
            msg_parts = []
            if missing:
                msg_parts.append(
                    f"Numerical mismatch: {', '.join(missing)} found in claim "
                    f"but not in evidence."
                )
            if approximate_matches:
                approx_strs = [
                    f"{a['claim']}≈{a['evidence']}" for a in approximate_matches
                ]
                msg_parts.append(f"Approximate matches: {', '.join(approx_strs)}.")
            message = " ".join(msg_parts)
        elif approximate_matches:
            status = "APPROXIMATE"
            approx_strs = [
                f"{a['claim']}≈{a['evidence']}" for a in approximate_matches
            ]
            message = f"Approximate numerical matches: {', '.join(approx_strs)}."
        else:
            status = "CONSISTENT"
            message = None

        return {
            "status": status,
            "claim_numbers": [n["raw"] for n in claim_numbers],
            "evidence_numbers": [n["raw"] for n in evidence_numbers],
            "missing_numbers": missing,
            "approximate_matches": approximate_matches,
            "matched_numbers": matched,
            "message": message,
        }
