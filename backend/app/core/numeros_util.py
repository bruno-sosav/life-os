import math


def js_round(value: float) -> int:
    """Redondeo como Math.round de JS (2.5 → 3), igual que los cálculos originales del frontend."""
    return math.floor(value + 0.5)
