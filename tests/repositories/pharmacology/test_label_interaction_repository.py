"""Integridad de data/pharmacology/label_interactions.csv: cada fila trazable a una página real de una ficha técnica."""
import csv

import pymupdf
import pytest

from junta_medica.config import paths
from junta_medica.config import pharmacology as config
from junta_medica.factories.pharmacology_factory import create_drug_repository
from junta_medica.repositories.pharmacology.label_interaction_repository import LabelInteractionRepository

INTERACTIONS = LabelInteractionRepository(paths.LABEL_INTERACTIONS_PATH).read_all()
with open(paths.CATALOG_PATH, encoding="utf-8") as _file:
    DOCUMENTS = {row["id"]: row for row in csv.DictReader(_file)}


def test_no_duplicate_pairs():
    pairs = [i.pair for i in INTERACTIONS]
    assert len(pairs) == len(set(pairs))


@pytest.mark.parametrize("interaction", INTERACTIONS, ids=lambda i: f"{i.drug_a}+{i.drug_b}")
def test_each_interaction_is_traceable(interaction):
    drugs = create_drug_repository()
    assert drugs.find(interaction.drug_a) and drugs.find(interaction.drug_b), "medicamento fuera del catálogo"
    assert interaction.severity.value in config.REPORTED_SEVERITIES, "una fila manual debe ser reportable"
    document = DOCUMENTS[interaction.source]
    assert document["status"] == "downloaded"
    with pymupdf.open(paths.DOCUMENTS_DIR / document["file"]) as pdf:
        assert 0 < int(interaction.source_id.lstrip("p")) <= pdf.page_count
    assert interaction.citation == f"{interaction.source}:{interaction.source_id}"


def test_reads_pairs_in_alphabetical_order(tmp_path):
    file = tmp_path / "label.csv"
    file.write_text("drug_a,drug_b,severity,source,page,note\nwarfarina,dabigatrán,severe,ft_x,84,n\n", encoding="utf-8")
    interaction = LabelInteractionRepository(file).read_all()[0]
    assert (interaction.drug_a, interaction.drug_b) == ("dabigatrán", "warfarina")
    assert interaction.citation == "ft_x:p84"
