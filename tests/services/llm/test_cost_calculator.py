from junta_medica.services.llm.cost_calculator import CostCalculator


def test_cost_of_one_million_tokens():
    calculator = CostCalculator({"modelo-x": (0.10, 0.50)})
    assert calculator.calculate("modelo-x", 1_000_000, 0) == 0.10
    assert calculator.calculate("modelo-x", 0, 1_000_000) == 0.50


def test_model_without_price_costs_zero():
    assert CostCalculator({}).calculate("desconocido", 1000, 1000) == 0.0
