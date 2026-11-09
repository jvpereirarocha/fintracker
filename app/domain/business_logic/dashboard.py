from decimal import ROUND_HALF_UP, Decimal

ONE_HUNDRED = Decimal("100.00")
TWO_PLACES = Decimal("0.01")


def compute_percentages(amounts: list[Decimal]) -> list[Decimal]:
    """
    Share of each amount over their sum, rounded to 2 places.

    The rounding difference goes to the largest amount so the result always
    adds up to exactly 100.00 (e.g. three equal parts -> 33.34, 33.33, 33.33).
    """
    total = sum(amounts, Decimal(0))
    if not amounts or total == 0:
        return [Decimal("0.00") for _ in amounts]

    percentages = [
        (amount / total * 100).quantize(TWO_PLACES, rounding=ROUND_HALF_UP) for amount in amounts
    ]
    largest = max(range(len(amounts)), key=lambda index: amounts[index])
    percentages[largest] += ONE_HUNDRED - sum(percentages, Decimal(0))
    return percentages
