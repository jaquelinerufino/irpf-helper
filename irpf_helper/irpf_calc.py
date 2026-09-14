from typing import Any, Dict, List, Tuple

# Faixas do IRPF vigentes para o ano-calendário 2024.
# Atualizar quando a Receita Federal divulgar novos valores.
IRPF_BRACKETS: List[Tuple[float, float, float]] = [
    (0.00, 22847.76, 0.00),
    (22847.76, 33919.80, 0.075),
    (33919.80, 45012.60, 0.15),
    (45012.60, 55976.16, 0.225),
    (55976.16, 90370.64, 0.275),
    (90370.64, float("inf"), 0.30),
]

# Desconto simplificado 2024: 20% da renda tributável, limitado ao teto anual.
SIMPLIFIED_DISCOUNT_RATE = 0.20
SIMPLIFIED_DISCOUNT_CAP = 16754.34

# Dedução anual por dependente, 2024.
DEPENDENT_DEDUCTION_ANNUAL = 2275.08


def round_money(value: float) -> float:
    return round(float(value), 2)


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calculate_tax(base: float) -> float:
    tax = 0.0
    for lower, upper, rate in IRPF_BRACKETS:
        if base <= lower:
            continue
        taxable_amount = min(base, upper) - lower
        if taxable_amount > 0:
            tax += taxable_amount * rate
    return round_money(tax)


def _to_non_negative_float(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Valor inválido para '{field_name}'.")
    if number < 0:
        raise ValueError(f"'{field_name}' não pode ser negativo.")
    return number


def _to_non_negative_int(value: Any, field_name: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"Valor inválido para '{field_name}'.")
    if number < 0:
        raise ValueError(f"'{field_name}' não pode ser negativo.")
    return number


def _extract_inputs(payload: Dict[str, Any]) -> Dict[str, float]:
    return {
        "salary": _to_non_negative_float(payload.get("salary", 0) or 0, "salary"),
        "extra_income": _to_non_negative_float(payload.get("extraIncome", 0) or 0, "extraIncome"),
        "deductions": _to_non_negative_float(payload.get("deductions", 0) or 0, "deductions"),
        "inss": _to_non_negative_float(payload.get("inss", 0) or 0, "inss"),
        "irrf": _to_non_negative_float(payload.get("irrf", 0) or 0, "irrf"),
        "pension": _to_non_negative_float(payload.get("pension", 0) or 0, "pension"),
        "dependents": _to_non_negative_int(payload.get("dependents", 0) or 0, "dependents"),
    }


def calculate_annual_income(inputs: Dict[str, float]) -> float:
    return inputs["salary"] * 12 + inputs["extra_income"]


def calculate_simplified(annual_income: float, inss: float) -> Dict[str, Any]:
    discount_applied = min(annual_income * SIMPLIFIED_DISCOUNT_RATE, SIMPLIFIED_DISCOUNT_CAP)
    taxable_base = max(0.0, annual_income - discount_applied - inss)
    tax_amount = calculate_tax(taxable_base)
    effective_rate = (tax_amount / annual_income * 100) if annual_income > 0 else 0.0

    return {
        "discount_applied": round_money(discount_applied),
        "taxable_base": round_money(taxable_base),
        "tax_amount": round_money(tax_amount),
        "effective_rate": round_money(effective_rate),
    }


def calculate_complete(
    annual_income: float,
    deductions: float,
    inss: float,
    pension: float,
    dependents: int,
) -> Dict[str, Any]:
    dependent_discount = dependents * DEPENDENT_DEDUCTION_ANNUAL
    discount_total = deductions + inss + pension + dependent_discount
    taxable_base = max(0.0, annual_income - discount_total)
    tax_amount = calculate_tax(taxable_base)
    effective_rate = (tax_amount / annual_income * 100) if annual_income > 0 else 0.0

    return {
        "deduction_total": round_money(discount_total),
        "deduction_breakdown": {
            "deductions": round_money(deductions),
            "inss": round_money(inss),
            "pension": round_money(pension),
            "dependent_discount": round_money(dependent_discount),
        },
        "taxable_base": round_money(taxable_base),
        "tax_amount": round_money(tax_amount),
        "effective_rate": round_money(effective_rate),
    }


def compare_models(payload: Dict[str, Any]) -> Dict[str, Any]:
    inputs = _extract_inputs(payload)
    annual_income = calculate_annual_income(inputs)

    simplified = calculate_simplified(annual_income, inputs["inss"])
    complete = calculate_complete(
        annual_income,
        inputs["deductions"],
        inputs["inss"],
        inputs["pension"],
        inputs["dependents"],
    )

    # Saldo final = imposto devido no ano menos o que já foi retido na fonte
    # (IRRF) pela fonte pagadora. Positivo = falta pagar; negativo = valor a
    # restituir. O IRRF já retido não muda o imposto devido em si (isso
    # depende só da base tributável de cada modelo), só o saldo final.
    simplified["balance"] = round_money(simplified["tax_amount"] - inputs["irrf"])
    complete["balance"] = round_money(complete["tax_amount"] - inputs["irrf"])

    if simplified["tax_amount"] < complete["tax_amount"]:
        recommended = "simplified"
        difference = complete["tax_amount"] - simplified["tax_amount"]
    elif complete["tax_amount"] < simplified["tax_amount"]:
        recommended = "complete"
        difference = simplified["tax_amount"] - complete["tax_amount"]
    else:
        recommended = "equal"
        difference = 0.0

    return {
        "annual_income": round_money(annual_income),
        "irrf": round_money(inputs["irrf"]),
        "simplified": simplified,
        "complete": complete,
        "recommended": recommended,
        "difference": round_money(difference),
    }
