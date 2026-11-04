"""Rutas de carpetas y archivos del proyecto."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"
CASES_DIR = DATA_DIR / "cases"
DOCUMENTS_DIR = DATA_DIR / "documents"
MOCK_RESPONSES_DIR = DATA_DIR / "mock_responses"   # respuestas de ejemplo del modo simulado
PROMPTS_DIR = DATA_DIR / "prompts"               # instrucciones de cada agente (editables, en español)
TEMPLATES_DIR = DATA_DIR / "templates"   # formatos de referencia (ej. caso clínico)
REFERENCES_DIR = DATA_DIR / "references" # material de consulta NO indexado (ej. CIE-10)
CATALOG_PATH = DOCUMENTS_DIR / "catalog.csv"
SECTIONS_PATH = DOCUMENTS_DIR / "sections.csv"   # qué páginas de cada guía se indexan
ICD10_PDF_PATH = REFERENCES_DIR / "icd10_ops_2018_vol1.pdf"   # CIE-10 OPS 2018, volumen 1 (fuente)
ICD10_PATH = REFERENCES_DIR / "icd10.csv"                      # tabla generada (scripts/build_icd10_table)

PHARMACOLOGY_DIR = DATA_DIR / "pharmacology"
DRUGS_PATH = PHARMACOLOGY_DIR / "drugs.csv"     # catálogo de medicamentos reconocidos
DDINTER_DIR = PHARMACOLOGY_DIR / "ddinter"                     # descargas originales de DDInter
LABEL_INTERACTIONS_PATH = PHARMACOLOGY_DIR / "label_interactions.csv"  # interacciones de fichas técnicas (curadas a mano)
INTERACTIONS_PATH = PHARMACOLOGY_DIR / "interactions.csv"   # tabla generada (scripts/): DDInter + fichas técnicas
CONDITION_RULES_PATH = PHARMACOLOGY_DIR / "condition_rules.csv"  # reglas fármaco–condición (curadas a mano)

CHROMA_DIR = ROOT_DIR / "chroma_db"             # base vectorial (generada)
OUTPUT_DIR = ROOT_DIR / "output"              # informes PDF, resultados de evaluación
DEBATES_DIR = OUTPUT_DIR / "debates"          # resultado completo de cada caso (JSON)
DATABASE_PATH = ROOT_DIR / "junta_medica.sqlite"      # casos, usuarios, registros
ENV_PATH = ROOT_DIR / ".env"
