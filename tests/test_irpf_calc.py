import pytest

from irpf_calc import (
    SIMPLIFIED_DISCOUNT_CAP,
    calculate_complete,
    calculate_simplified,
    calculate_tax,
    compare_models,
)


def test_calculate_tax_below_first_bracket_is_zero():
    assert calculate_tax(0) == 0.0
    assert calculate_tax(22847.76) == 0.0


def test_calculate_tax_known_values():
    assert calculate_tax(90370.64) == 14419.61
    assert calculate_tax(200000) == 47308.41


def test_calculate_simplified_discount_is_capped():
    result = calculate_simplified(500000, inss=0)
    assert result["discount_applied"] == SIMPLIFIED_DISCOUNT_CAP


def test_calculate_simplified_low_income_no_tax():
    result = calculate_simplified(20000, inss=0)
    assert result["tax_amount"] == 0.0


def test_calculate_complete_includes_dependent_discount():
    result = calculate_complete(
        annual_income=100000, deductions=5000, inss=8000, pension=0, dependents=2
    )
    assert result["deduction_breakdown"]["dependent_discount"] == pytest.approx(4550.16)
    assert result["deduction_total"] == pytest.approx(17550.16)


def test_compare_models_recommends_lower_tax():
    payload = {
        "salary": 5000,
        "extraIncome": 0,
        "deductions": 0,
        "inss": 500,
        "pension": 0,
        "dependents": 0,
    }
    result = compare_models(payload)
    assert result["recommended"] == "simplified"
    assert result["difference"] == pytest.approx(
        result["complete"]["tax_amount"] - result["simplified"]["tax_amount"]
    )


def test_compare_models_rejects_negative_input():
    with pytest.raises(ValueError):
        compare_models({"salary": -100})
