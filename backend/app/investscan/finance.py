"""Transparent project economics with purchase-dependent costs solved algebraically."""

from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP

from app.investscan.schemas import FinanceInput


def rub(value):
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calculate(payload: FinanceInput) -> dict:
    def d(value):
        return Decimal(str(value))

    finance_rate = (
        d(payload.annual_finance_pct)
        / 100
        * d(payload.holding_months)
        / 12
        * d(payload.financed_share_pct)
        / 100
    )
    acquisition_rate = d(payload.acquisition_cost_pct) / 100
    sale_rate = d(payload.sale_cost_pct) / 100
    fixed = (
        payload.repairs
        + payload.legal_costs
        + payload.other_costs
        + payload.reserve
        + payload.monthly_holding * payload.holding_months
    )
    purchase = d(payload.purchase_price)

    def scenario(multiplier):
        sale = d(payload.resale_price) * multiplier
        sale_cost = sale * sale_rate
        financing = purchase * finance_rate
        acquisition = purchase * acquisition_rate
        total = purchase + fixed + sale_cost + financing + acquisition
        profit = sale - total
        ceiling = (
            (sale - sale_cost - fixed - payload.target_profit)
            / (1 + finance_rate + acquisition_rate)
        ).to_integral_value(rounding=ROUND_FLOOR)
        return {
            "resale_price": rub(sale),
            "max_buyout_price": max(0, int(ceiling)),
            "profit": rub(profit),
            "total_cost": rub(total),
            "financing_cost": rub(financing),
            "sale_cost": rub(sale_cost),
            "acquisition_cost": rub(acquisition),
            "project_roi_pct": round(float(profit / total * 100), 2) if total else None,
        }

    base = scenario(Decimal(1))
    return {
        **base,
        "fixed_costs": fixed,
        "headroom": base["max_buyout_price"] - payload.purchase_price,
        "scenarios": {
            "stress": scenario(Decimal("0.9")),
            "base": base,
            "upside": scenario(Decimal("1.1")),
        },
        "assumptions": "Цена продажи задана аналитиком. Резерв включён в расходы. Финансирование: простые проценты на долю цены покупки. Налоги указываются в расходах отдельно.",
    }
