"""
Genera data/pharmacology/interactions.csv uniendo:
  1. las descargas de DDInter (data/pharmacology/ddinter/), y
  2. las interacciones tomadas de fichas técnicas (data/pharmacology/label_interactions.csv).
Si un par aparece en ambas, queda la severidad más alta.

Uso:  python -m scripts.build_interaction_table
"""
from collections import Counter

from junta_medica.config import pharmacology as config
from junta_medica.config import paths
from junta_medica.factories.pharmacology_factory import create_interaction_repository, create_drug_repository
from junta_medica.repositories.pharmacology.ddinter_importer import DDInterImporter
from junta_medica.repositories.pharmacology.label_interaction_repository import LabelInteractionRepository
from junta_medica.services.pharmacology.interaction_merger import merge_interactions


def main() -> None:
    drugs = create_drug_repository()
    files = sorted(paths.DDINTER_DIR.glob("ddinter_downloads_code_*.csv"))
    importer = DDInterImporter(drugs, config.DDINTER_SEVERITY_MAP)

    from_ddinter = importer.load(files)
    from_labels = LabelInteractionRepository(paths.LABEL_INTERACTIONS_PATH).read_all()
    interactions = merge_interactions(from_ddinter, from_labels)
    create_interaction_repository().save_all(interactions)

    found = importer.found_names(files)
    uncovered = [m.inn for m in drugs.all() if not any(n.lower() in found for n in m.english_names)]
    covered_by_labels = {inn for i in from_labels for inn in (i.drug_a, i.drug_b)}

    print(f"Archivos DDInter leídos: {', '.join(a.name for a in files)}")
    print(f"Interacciones DDInter: {len(from_ddinter)} · de fichas técnicas: {len(from_labels)}")
    print(f"Total en la tabla: {len(interactions)}")
    for severity, total in Counter(i.severity.value for i in interactions).most_common():
        print(f"  {severity}: {total}")
    print(f"Sin datos en DDInter: {', '.join(uncovered) or 'ninguno'}")
    still_missing = [inn for inn in uncovered if inn not in covered_by_labels]
    print(f"Sin datos en ninguna fuente: {', '.join(still_missing) or 'ninguno'}")
    print(f"Tabla guardada en: {paths.INTERACTIONS_PATH}")


if __name__ == "__main__":
    main()
