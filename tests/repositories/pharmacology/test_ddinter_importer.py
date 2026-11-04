from junta_medica.config import pharmacology as config
from junta_medica.repositories.pharmacology.ddinter_importer import DDInterImporter
from junta_medica.models.pharmacology.severity import Severity

from junta_medica.models.pharmacology.catalog_drug import CatalogDrug


class FakeDrugRepository:
    """Reemplaza al DrugRepository: solo necesita el método todos()."""

    def all(self):
        return [
            CatalogDrug("warfarina", "g", "B01AA03", english_names=("Warfarin",)),
            CatalogDrug("ibuprofeno", "g", "M01AE01", english_names=("Ibuprofen",)),
            CatalogDrug("valsartán", "g", "C09CA03", english_names=("Valsartan",)),
            CatalogDrug("sacubitrilo/valsartán", "g", "C09DX04", english_names=("Sacubitril", "Valsartan")),
        ]


CATALOG = FakeDrugRepository()


def write_file(tmp_path, name, rows):
    file = tmp_path / name
    lines = ["DDInterID_A,Drug_A,DDInterID_B,Drug_B,Level"] + rows
    file.write_text("\n".join(lines), encoding="utf-8")
    return file


def test_loads_only_catalog_pairs_and_maps_severity(tmp_path):
    file = write_file(tmp_path, "a.csv", [
        "D1,Warfarin,D2,Ibuprofen,Major",
        "D1,Warfarin,D9,Fluconazole,Major",   # fluconazol no está en el catálogo
    ])
    interactions = DDInterImporter(CATALOG, config.DDINTER_SEVERITY_MAP).load([file])
    assert len(interactions) == 1
    i = interactions[0]
    assert (i.drug_a, i.drug_b, i.severity) == ("ibuprofeno", "warfarina", Severity.SEVERE)
    assert i.citation == "ddinter:D1-D2"


def test_duplicate_pair_keeps_highest_severity(tmp_path):
    a = write_file(tmp_path, "a.csv", ["D1,Warfarin,D2,Ibuprofen,Minor"])
    b = write_file(tmp_path, "b.csv", ["D2,Ibuprofen,D1,Warfarin,Major"])
    interactions = DDInterImporter(CATALOG, config.DDINTER_SEVERITY_MAP).load([a, b])
    assert [i.severity for i in interactions] == [Severity.SEVERE]


def test_component_is_assigned_to_all_its_combinations(tmp_path):
    file = write_file(tmp_path, "a.csv", ["D3,Valsartan,D2,Ibuprofen,Moderate"])
    pairs = {i.pair for i in DDInterImporter(CATALOG, config.DDINTER_SEVERITY_MAP).load([file])}
    assert pairs == {frozenset({"valsartán", "ibuprofeno"}), frozenset({"sacubitrilo/valsartán", "ibuprofeno"})}
