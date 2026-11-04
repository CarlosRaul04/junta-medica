from junta_medica.repositories.pharmacology.interaction_repository import InteractionRepository
from junta_medica.models.pharmacology.interaction import Interaction
from junta_medica.models.pharmacology.severity import Severity


def test_save_and_read_keeps_data(tmp_path):
    original = [Interaction("ibuprofeno", "warfarina", Severity.SEVERE, "DDInter", "D1-D2")]
    path = tmp_path / "interactions.csv"
    repository = InteractionRepository(path)
    repository.save_all(original)
    assert repository.read_all() == original
