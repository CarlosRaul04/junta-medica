"""
REPOSITORIOS: leen y guardan datos en archivos. Ninguna otra capa abre archivos directamente.

    cases/         -> CaseRepository (archivos JSON de casos)
    knowledge/  -> DocumentRepository, SectionRepository, PDFReader, ChromaVectorStore
    pharmacology/  -> DrugRepository, InteractionRepository, ConditionRuleRepository,
                      LabelInteractionRepository, DDInterImporter (lee las descargas originales de DDInter)
    diagnoses/     -> Icd10Repository, Icd10PdfImporter (CIE-10 desde el PDF de la OPS)
"""
