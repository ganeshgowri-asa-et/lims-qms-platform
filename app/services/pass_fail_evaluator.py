"""
Pass/Fail Criteria Evaluation Engine for IEC Tests
"""
from typing import Dict, Any, List, Optional
from app.models.iec_tests import TestResult
import logging

logger = logging.getLogger(__name__)


class PassFailEvaluator:
    """Evaluate test results against IEC standards criteria"""

    # IEC 61215 Standard Criteria
    IEC_61215_CRITERIA = {
        "max_power_degradation": 5.0,  # Maximum 5% degradation
        "max_voc_degradation": 2.0,
        "max_isc_degradation": 2.0,
        "min_insulation_resistance": 40.0,  # MΩ (at STC)
        "max_series_resistance_increase": 30.0,  # %
    }

    # IEC 61730 Safety Criteria
    IEC_61730_CRITERIA = {
        "min_insulation_resistance_dry": 40.0,  # MΩ per m²
        "min_insulation_resistance_wet": 4.0,  # MΩ per m²
        "max_wet_leakage_current": 0.5,  # mA per kW
        "dielectric_strength_voltage": 1000,  # V + 2×Voc
        "fire_class_requirements": ["A", "B", "C"],
    }

    # IEC 61701 Salt Mist Criteria
    IEC_61701_CRITERIA = {
        "severity_levels": {
            "1": {"max_degradation": 5.0, "cycles": 10},
            "2": {"max_degradation": 5.0, "cycles": 20},
            "3": {"max_degradation": 5.0, "cycles": 30},
            "4": {"max_degradation": 5.0, "cycles": 40},
            "5": {"max_degradation": 5.0, "cycles": 50},
            "6": {"max_degradation": 5.0, "cycles": 60},
        },
        "max_pmax_degradation": 5.0,  # %
        "no_major_defects": True,
    }

    @staticmethod
    def evaluate_iec_61215_test(
        test_data: Dict[str, Any],
        custom_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate IEC 61215 test results

        Args:
            test_data: Test measurement data
            custom_criteria: Optional custom acceptance criteria

        Returns:
            Evaluation results with pass/fail status
        """
        criteria = custom_criteria or PassFailEvaluator.IEC_61215_CRITERIA
        results = {
            "overall_result": TestResult.PASS,
            "criteria_checks": [],
            "failed_criteria": [],
            "warnings": []
        }

        # Check power degradation
        power_degradation = test_data.get("power_degradation", 0)
        max_allowed = criteria.get("max_power_degradation", 5.0)

        if abs(power_degradation) > max_allowed:
            results["criteria_checks"].append({
                "criterion": "Power Degradation",
                "measured": f"{power_degradation:.2f}%",
                "limit": f"±{max_allowed}%",
                "status": "FAIL"
            })
            results["failed_criteria"].append("Power Degradation")
            results["overall_result"] = TestResult.FAIL
        else:
            results["criteria_checks"].append({
                "criterion": "Power Degradation",
                "measured": f"{power_degradation:.2f}%",
                "limit": f"±{max_allowed}%",
                "status": "PASS"
            })

        # Check visual inspection
        visual_pass = test_data.get("visual_inspection_pass", True)
        if not visual_pass:
            results["criteria_checks"].append({
                "criterion": "Visual Inspection",
                "measured": "Defects detected",
                "limit": "No major defects",
                "status": "FAIL"
            })
            results["failed_criteria"].append("Visual Inspection")
            results["overall_result"] = TestResult.FAIL
        else:
            results["criteria_checks"].append({
                "criterion": "Visual Inspection",
                "measured": "No defects",
                "limit": "No major defects",
                "status": "PASS"
            })

        # Check insulation resistance if available
        insulation_resistance = test_data.get("insulation_resistance")
        if insulation_resistance is not None:
            min_required = criteria.get("min_insulation_resistance", 40.0)
            if insulation_resistance < min_required:
                results["criteria_checks"].append({
                    "criterion": "Insulation Resistance",
                    "measured": f"{insulation_resistance:.2f} MΩ",
                    "limit": f"≥{min_required} MΩ",
                    "status": "FAIL"
                })
                results["failed_criteria"].append("Insulation Resistance")
                results["overall_result"] = TestResult.FAIL
            else:
                results["criteria_checks"].append({
                    "criterion": "Insulation Resistance",
                    "measured": f"{insulation_resistance:.2f} MΩ",
                    "limit": f"≥{min_required} MΩ",
                    "status": "PASS"
                })

        return results

    @staticmethod
    def evaluate_iec_61730_test(
        test_data: Dict[str, Any],
        custom_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate IEC 61730 safety test results

        Args:
            test_data: Test measurement data
            custom_criteria: Optional custom acceptance criteria

        Returns:
            Evaluation results with pass/fail status
        """
        criteria = custom_criteria or PassFailEvaluator.IEC_61730_CRITERIA
        results = {
            "overall_result": TestResult.PASS,
            "criteria_checks": [],
            "failed_criteria": [],
            "warnings": []
        }

        # Check wet insulation resistance
        wet_ir = test_data.get("insulation_resistance")
        if wet_ir is not None:
            min_required = criteria.get("min_insulation_resistance_wet", 4.0)
            if wet_ir < min_required:
                results["criteria_checks"].append({
                    "criterion": "Wet Insulation Resistance",
                    "measured": f"{wet_ir:.2f} MΩ",
                    "limit": f"≥{min_required} MΩ/m²",
                    "status": "FAIL"
                })
                results["failed_criteria"].append("Wet Insulation Resistance")
                results["overall_result"] = TestResult.FAIL
            else:
                results["criteria_checks"].append({
                    "criterion": "Wet Insulation Resistance",
                    "measured": f"{wet_ir:.2f} MΩ",
                    "limit": f"≥{min_required} MΩ/m²",
                    "status": "PASS"
                })

        # Check wet leakage current
        leakage_current = test_data.get("wet_leakage_current")
        if leakage_current is not None:
            max_allowed = criteria.get("max_wet_leakage_current", 0.5)
            if leakage_current > max_allowed:
                results["criteria_checks"].append({
                    "criterion": "Wet Leakage Current",
                    "measured": f"{leakage_current:.3f} mA",
                    "limit": f"≤{max_allowed} mA/kW",
                    "status": "FAIL"
                })
                results["failed_criteria"].append("Wet Leakage Current")
                results["overall_result"] = TestResult.FAIL
            else:
                results["criteria_checks"].append({
                    "criterion": "Wet Leakage Current",
                    "measured": f"{leakage_current:.3f} mA",
                    "limit": f"≤{max_allowed} mA/kW",
                    "status": "PASS"
                })

        # Check dielectric strength
        dielectric_pass = test_data.get("dielectric_strength_pass", True)
        results["criteria_checks"].append({
            "criterion": "Dielectric Strength",
            "measured": "Pass" if dielectric_pass else "Fail",
            "limit": "No breakdown",
            "status": "PASS" if dielectric_pass else "FAIL"
        })
        if not dielectric_pass:
            results["failed_criteria"].append("Dielectric Strength")
            results["overall_result"] = TestResult.FAIL

        # Check mechanical tests
        mechanical_pass = test_data.get("mechanical_load_pass", True)
        impact_pass = test_data.get("impact_test_pass", True)

        if not mechanical_pass:
            results["failed_criteria"].append("Mechanical Load")
            results["overall_result"] = TestResult.FAIL

        if not impact_pass:
            results["failed_criteria"].append("Impact Test")
            results["overall_result"] = TestResult.FAIL

        return results

    @staticmethod
    def evaluate_iec_61701_test(
        test_data: Dict[str, Any],
        custom_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate IEC 61701 salt mist corrosion test results

        Args:
            test_data: Test measurement data
            custom_criteria: Optional custom acceptance criteria

        Returns:
            Evaluation results with pass/fail status
        """
        criteria = custom_criteria or PassFailEvaluator.IEC_61701_CRITERIA
        results = {
            "overall_result": TestResult.PASS,
            "criteria_checks": [],
            "failed_criteria": [],
            "warnings": []
        }

        # Check power degradation
        pmax_degradation = test_data.get("pmax_degradation", 0)
        max_allowed = criteria.get("max_pmax_degradation", 5.0)

        if abs(pmax_degradation) > max_allowed:
            results["criteria_checks"].append({
                "criterion": "Pmax Degradation",
                "measured": f"{pmax_degradation:.2f}%",
                "limit": f"±{max_allowed}%",
                "status": "FAIL"
            })
            results["failed_criteria"].append("Pmax Degradation")
            results["overall_result"] = TestResult.FAIL
        else:
            results["criteria_checks"].append({
                "criterion": "Pmax Degradation",
                "measured": f"{pmax_degradation:.2f}%",
                "limit": f"±{max_allowed}%",
                "status": "PASS"
            })

        # Check for visual defects
        corrosion = test_data.get("corrosion_observed", False)
        delamination = test_data.get("delamination_observed", False)
        bubbles = test_data.get("bubble_formation", False)

        defects = []
        if corrosion:
            defects.append("Corrosion")
        if delamination:
            defects.append("Delamination")
        if bubbles:
            defects.append("Bubble Formation")

        if defects:
            results["criteria_checks"].append({
                "criterion": "Visual Defects",
                "measured": ", ".join(defects),
                "limit": "No major defects",
                "status": "FAIL"
            })
            results["failed_criteria"].append("Visual Defects")
            results["overall_result"] = TestResult.FAIL
        else:
            results["criteria_checks"].append({
                "criterion": "Visual Defects",
                "measured": "None",
                "limit": "No major defects",
                "status": "PASS"
            })

        return results

    @staticmethod
    def evaluate_test_sequence(
        test_sequence: List[Dict[str, Any]],
        standard: str
    ) -> Dict[str, Any]:
        """
        Evaluate entire test sequence

        Args:
            test_sequence: List of test results
            standard: IEC standard (61215, 61730, or 61701)

        Returns:
            Overall evaluation results
        """
        evaluator_map = {
            "IEC 61215": PassFailEvaluator.evaluate_iec_61215_test,
            "IEC 61730": PassFailEvaluator.evaluate_iec_61730_test,
            "IEC 61701": PassFailEvaluator.evaluate_iec_61701_test,
        }

        evaluator = evaluator_map.get(standard)
        if not evaluator:
            raise ValueError(f"Unknown standard: {standard}")

        overall_pass = True
        sequence_results = []

        for test in test_sequence:
            result = evaluator(test)
            sequence_results.append(result)

            if result["overall_result"] != TestResult.PASS:
                overall_pass = False

        return {
            "overall_result": TestResult.PASS if overall_pass else TestResult.FAIL,
            "total_tests": len(test_sequence),
            "passed_tests": sum(1 for r in sequence_results if r["overall_result"] == TestResult.PASS),
            "failed_tests": sum(1 for r in sequence_results if r["overall_result"] == TestResult.FAIL),
            "individual_results": sequence_results
        }

    @staticmethod
    def calculate_degradation(initial: float, final: float) -> float:
        """
        Calculate degradation percentage

        Args:
            initial: Initial value
            final: Final value

        Returns:
            Degradation percentage (negative means improvement)
        """
        if initial == 0:
            return 0.0

        return ((initial - final) / initial) * 100.0
