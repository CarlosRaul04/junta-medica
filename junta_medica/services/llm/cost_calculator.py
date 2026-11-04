"""CostCalculator: costo en dólares de una llamada al modelo según los tokens usados."""


class CostCalculator:
    def __init__(self, prices_usd_per_million: dict[str, tuple[float, float]]):
        self._prices = prices_usd_per_million

    def calculate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        input_price, output_price = self._prices.get(model, (0.0, 0.0))
        return (input_tokens * input_price + output_tokens * output_price) / 1_000_000
