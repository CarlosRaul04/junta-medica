"""
Genera data/references/icd10.csv a partir del PDF de la CIE-10 (OPS 2018, volumen 1).

Uso:  python -m scripts.build_icd10_table
"""
from collections import Counter

from junta_medica.config import paths
from junta_medica.factories.diagnosis_factory import create_icd10_repository
from junta_medica.repositories.diagnoses.icd10_pdf_importer import Icd10PdfImporter

EXAMPLES = ["I10", "E11.9", "I50.0", "I48.0", "N18.3", "J18.9"]


def main() -> None:
    codes = Icd10PdfImporter().load(paths.ICD10_PDF_PATH)
    repository = create_icd10_repository()
    repository.save_all(codes)

    kinds = Counter("categoría (3 caracteres)" if c.is_category else "subcategoría (4 caracteres)" for c in codes)
    print(f"Códigos extraídos: {len(codes)}")
    for kind, total in kinds.items():
        print(f"  {kind}: {total}")
    print(f"Sin título detectado: {sum(1 for c in codes if not c.title)}")
    for code in EXAMPLES:
        found = repository.find(code)
        print(f"  {code}: {found.title if found else 'NO ENCONTRADO'}")
    print(f"Tabla guardada en: {paths.ICD10_PATH}")


if __name__ == "__main__":
    main()
