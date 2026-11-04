# Arquitectura del proyecto

## 1. Idea general: arquitectura en capas
El código está separado en **capas**. Cada capa tiene **un solo tipo de responsabilidad**, y dentro de cada capa
hay una carpeta por **área** del sistema (`cases/`, `pharmacology/`, `knowledge/`, `diagnoses/`, `llm/`, `agents/`, `debate/`).

Es la misma idea del proyecto C# de referencia (AbogatoIA):

| Capa (carpeta) | Qué contiene | Equivalente en C# | Ejemplo |
|---|---|---|---|
| `config/` | Constantes y parámetros ajustables | `appsettings.json` | `MAX_ROUNDS`, rutas, umbrales |
| `models/` | **Solo datos**: las estructuras del sistema, sin lógica | `Models/` | `ClinicalCase`, `Interaction` |
| `interfaces/` | **Contratos** que cumplen las piezas intercambiables | `Services/Interfaces/` | `LLMProvider` |
| `repositories/` | **Leer y guardar datos** (CSV, JSON; luego SQLite y ChromaDB) | `Persistence/` + `Repositories/` | `DrugRepository` |
| `services/` | **La lógica**: validar, normalizar, detectar, hablar con la IA | `Services/Implementation/` | `InteractionChecker` |
| `factories/` | **Arma y conecta** los objetos (lee config y entrega servicios listos) | `Program.cs` | `create_case_loader()` |
| `exceptions.py` | Errores propios del sistema | — | `InvalidCaseError` |
| `ui/` (Fase 4) | Pantallas de Streamlit | `Controllers/` | — |

### Dirección de las dependencias (nunca al revés)
```
ui ──────► factories ──► services ──► repositories ──► models
                 │             │                            ▲
                 ▼             └──────► interfaces ─────────┘
               config
```
- `models/` no depende de nadie.
- `services/` reciben todo por el constructor: **no leen `config/` ni abren archivos** (salvo los proveedores de IA, que son adaptadores hacia afuera).
- Solo `factories/` conoce `config/` y decide qué implementación concreta se usa.

## 2. Estructura completa
```
junta-medica-ia/
├── README.md · pyproject.toml · requirements.txt · .env · .env.ejemplo · .gitignore
├── docs/
│   ├── BITACORA.md                     # qué se hizo y por qué (leer primero)
│   ├── PLAN.md                         # estado por fases, decisiones, pendientes
│   ├── FUENTES.md                      # enfermedades, guías, medicamentos, interacciones, casos
│   └── ARQUITECTURA.md                 # este archivo
│
├── data/                              # DATOS (no código)
│   ├── cases/                          # casos simulados CASO-XXX.json
│   ├── documents/                     # base de conocimiento del RAG
│   │   ├── catalog.csv                # registro de cada documento (su id se usa en las citas)
│   │   ├── sections.csv               # qué páginas de cada guía se indexan
│   │   ├── guidelines/                      # 6 GPC en PDF
│   │   └── drug_labels/                     # fichas técnicas de medicamentos
│   ├── pharmacology/
│   │   ├── drugs.csv            # catálogo de 45 medicamentos
│   │   ├── ddinter/                    # descargas originales de DDInter (A, B, C, H, J, M, N)
│   │   ├── interactions.csv           # GENERADO por scripts/ (no editar a mano)
│   │   └── condition_rules.csv        # reglas fármaco–condición (curadas, con cita)
│   ├── references/                    # material de consulta NO indexado (CIE-10)
│   ├── templates/                     # formatos de referencia (clinical_case.json)
│   ├── prompts/                       # instrucciones de cada agente (.md, en español, EDITABLES sin tocar código)
│   └── mock_responses/                     # respuestas de ejemplo por agente (modo simulado)
│
├── scripts/                       # scripts que se ejecutan a mano:  python -m scripts.<nombre>
│   ├── build_interaction_table.py  # DDInter -> interactions.csv
│   ├── index_guidelines.py                # guías PDF -> base vectorial (chroma_db/)
│   ├── search_guidelines.py              # prueba una búsqueda desde la terminal
│   ├── build_icd10_table.py              # PDF CIE-10 OPS -> data/references/icd10.csv
│   └── run_case.py                       # corre la junta médica completa sobre un caso
├── chroma_db/                          # base vectorial GENERADA por index_guidelines (no se sube a Git)
│
├── junta_medica/                       # CÓDIGO del sistema
│   ├── config/
│   │   ├── paths.py · environment.py       # carpetas/archivos · variables del .env
│   │   ├── casos.py · farmacologia.py  # reglas de casos · parámetros de farmacología
│   │   ├── modelos.py · debate.py      # modelos de IA y precios · rondas y umbral de consenso
│   │   └── conocimiento.py · texts.py # parámetros del RAG · textos fijos (disclaimer)
│   │
│   ├── models/
│   │   ├── cases/
│   │   │   ├── clinical_case.py         # ClinicalCase (+ sus partes: Medication, Sexo)
│   │   │   └── validation_result.py # ValidationResult (+ ValidationError)
│   │   ├── pharmacology/
│   │   │   ├── severity.py            # Severity
│   │   │   ├── catalog_drug.py   # CatalogDrug (fila del catálogo)
│   │   │   ├── normalized_drug.py  # NormalizedDrug (+ NormalizationMethod)
│   │   │   ├── interaction.py          # Interaction
│   │   │   ├── interaction_finding.py # InteractionFinding
│   │   │   ├── condition_rule.py      # ConditionRule (+ CriterionType)
│   │   │   └── condition_finding.py   # ConditionFinding (+ ConditionCheckResult)
│   │   ├── knowledge/
│   │   │   ├── source_document.py     # SourceDocument (fila de catalog.csv)
│   │   │   ├── document_section.py    # DocumentSection (fila de sections.csv)
│   │   │   ├── page_text.py         # PageText (texto de una página del PDF)
│   │   │   ├── chunk.py            # Chunk (trozo de guía indexado; su .cita = "gpc_ic:p22-23")
│   │   │   ├── retrieved_chunk.py # RetrievedChunk (fragmento + similitud)
│   │   │   ├── search_result.py   # SearchResult (+ sufficient_evidence)
│   │   │   └── indexing_summary.py   # IndexingSummary
│   │   └── llm/
│   │       ├── llm_request.py        # LLMRequest
│   │       └── llm_response.py        # LLMResponse (+ RawLLMResponse)
│   │
│   ├── interfaces/
│   │   ├── llm_provider.py            # LLMProvider
│   │   ├── validation_rule.py         # ValidationRule
│   │   ├── condition_criterion.py       # ConditionCriterion
│   │   ├── embedding_model.py        # EmbeddingModel
│   │   └── vector_store.py        # VectorStore
│   │
│   ├── repositories/
│   │   ├── cases/
│   │   │   └── case_repository.py    # CaseRepository (JSON de casos)
│   │   ├── knowledge/
│   │   │   ├── document_repository.py        # DocumentRepository (catalog.csv)
│   │   │   ├── section_repository.py         # SectionRepository (sections.csv)
│   │   │   ├── pdf_reader.py                    # PDFReader (PyMuPDF)
│   │   │   └── chroma_vector_store.py                # ChromaVectorStore (ChromaDB)
│   │   ├── pharmacology/
│   │   │   ├── drug_repository.py      # DrugRepository
│   │   │   ├── interaction_repository.py     # InteractionRepository
│   │   │   ├── label_interaction_repository.py  # LabelInteractionRepository (interacciones de fichas técnicas)
│   │   │   ├── condition_rule_repository.py  # ConditionRuleRepository
│   │   │   └── ddinter_importer.py            # DDInterImporter (descargas de DDInter)
│   │   └── diagnoses/
│   │       ├── icd10_repository.py        # Icd10Repository (data/references/icd10.csv)
│   │       └── icd10_pdf_importer.py      # Icd10PdfImporter (CIE-10 OPS desde el PDF)
│   │
│   ├── services/
│   │   ├── cases/
│   │   │   ├── case_validator.py       # CaseValidator (aplica todas las reglas)
│   │   │   ├── case_converter.py       # CaseConverter (diccionario -> ClinicalCase)
│   │   │   ├── case_loader.py       # CaseLoader (valida + convierte)
│   │   │   └── validation_rules/
│   │   │       ├── field_rules.py    # obligatorios, permitidos, tipos, formato del código
│   │   │       ├── clinical_rules.py  # edad, sexo, laboratorio
│   │   │       └── privacy_rules.py# sin datos personales
│   │   ├── pharmacology/
│   │   │   ├── name_cleaning.py           # clean_drug_name()
│   │   │   ├── drug_normalizer.py  # DrugNormalizer
│   │   │   ├── interaction_checker.py  # InteractionChecker
│   │   │   ├── condition_checker.py    # ConditionChecker (una alerta por medicamento y dato: la más grave)
│   │   │   ├── interaction_merger.py   # merge_interactions() (DDInter + fichas técnicas)
│   │   │   └── condition_criteria/
│   │   │       ├── comparison.py            # comparar() con el operador de la regla
│   │   │       ├── lab_criterion.py   # LabCriterion
│   │   │       ├── age_criterion.py          # AgeCriterion
│   │   │       └── history_criterion.py   # HistoryCriterion
│   │   ├── knowledge/
│   │   │   ├── text_cleaner.py      # TextCleaner (encabezados, pies, firmas)
│   │   │   ├── chunker.py         # Chunker (una pregunta clínica = un bloque)
│   │   │   ├── indexer.py            # KnowledgeIndexer (PDF -> fragmentos -> vectores -> base)
│   │   │   ├── retriever.py             # KnowledgeRetriever (consulta -> fragmentos)
│   │   │   └── embeddings/
│   │   │       └── e5_embedding_model.py        # E5EmbeddingModel (multilingual-e5, local)
│   │   └── llm/
│   │       ├── llm_client.py          # LLMClient (reintentos, tiempo, costo)
│   │       ├── cost_calculator.py   # CostCalculator
│   │       ├── json_parser.py      # parse_json()
│   │       └── providers/
│   │           ├── openai_compatible_provider.py   # OpenAICompatibleProvider (OpenAI, OpenRouter, Groq, Gemini, Ollama...)
│   │           └── mock_provider.py # MockLLMProvider (sin costo)
│   │
│   ├── factories/
│   │   ├── case_factory.py            # create_case_validator(), create_case_loader()
│   │   ├── pharmacology_factory.py     # create_drug_normalizer(), create_interaction_checker(), create_condition_checker()
│   │   ├── knowledge_factory.py     # create_indexer(), create_retriever()
│   │   ├── diagnosis_factory.py     # create_icd10_repository()
│   │   └── llm_factory.py              # create_llm_client()
│   │
│   └── exceptions.py                  # InvalidCaseError, LLMConfigurationError, LLMProviderError, InvalidResponseError, OutdatedIndexError
│
└── tests/                            # ESPEJO de junta_medica/ (misma ruta, prefijo test_)
    ├── conftest.py                     # datos compartidos (caso de ejemplo) y dobles de prueba
    │                                   # (FakeEmbeddingModel, InMemoryVectorStore: el RAG se prueba sin descargar modelos)
    ├── repositories/{cases, knowledge, pharmacology, diagnoses}/
    └── services/{casos, conocimiento, farmacologia, llm}/
```

Próximas áreas (se agregan en cada capa, con la misma forma):
- `reports/`, `evaluation/` → en `services/`; persistencia SQLite → en `repositories/`; pantallas → `ui/`.

### Agentes y debate (Fase 3)
```
junta_medica/
├── models/debate/            # Stance, ProposedDiagnosis, ClinicalProposal, Objection, Review, ChiefVerdict,
│                             # CaseEvidence, AgentTurn, DebateRound, FinalAlert, CitationCheck, DebateResult
├── repositories/
│   ├── prompts/prompt_repository.py          # PromptRepository (data/prompts/<rol>.md)
│   └── debate/debate_result_repository.py    # DebateResultRepository (output/debates/*.json)
├── services/
│   ├── agents/
│   │   ├── llm_agent.py                  # LLMAgent: lo común (pedir, leer, registrar la intervención)
│   │   ├── clinical_agent.py             # ClinicalAgent.propose()
│   │   ├── pharmacological_agent.py      # PharmacologicalAgent.review()
│   │   ├── protocol_agent.py             # ProtocolAgent.review()
│   │   ├── chief_agent.py                # ChiefAgent.decide()
│   │   ├── context/                      # CaseFormatter, EvidenceFormatter, DebateFormatter (qué ve cada agente)
│   │   └── parsing/                      # ClinicalProposalParser, ReviewParser, ChiefVerdictParser (tolerantes)
│   └── debate/
│       ├── evidence_collector.py         # EvidenceCollector: herramientas sin IA
│       ├── query_builder.py              # QueryBuilder: consultas al buscador
│       ├── consensus_calculator.py       # ConsensusCalculator
│       ├── abstention_policy.py          # AbstentionPolicy (RF11)
│       ├── citation_verifier.py          # CitationVerifier: citas inventadas + trazabilidad
│       ├── alert_consolidator.py         # AlertConsolidator: las alertas de la tabla SIEMPRE van
│       └── debate_orchestrator.py        # DebateOrchestrator.run(case) -> DebateResult
└── factories/debate_factory.py           # create_debate_orchestrator()
```
Flujo de `DebateOrchestrator.run(case)`:
1. `EvidenceCollector`: normaliza medicamentos, detecta interacciones y reglas, busca fragmentos de guía para el caso.
2. `AbstentionPolicy`: sin evidencia suficiente → abstención, **sin llamar a la IA** (las alertas igual se informan).
3. Rondas (máx. 3): Clínico propone → se buscan fragmentos para esa propuesta → Farmacológico y Protocolo revisan →
   `ConsensusCalculator`. Sin consenso, el Clínico recibe las objeciones y corrige.
4. `AlertConsolidator` → `ChiefAgent` → `CitationVerifier`.

## 3. Reglas de código (obligatorias)

### Principios SOLID
| Principio | Cómo se aplica aquí |
|---|---|
| **S** — Responsabilidad única | Un archivo = una clase principal = una responsabilidad. Las capas separan datos, acceso a datos y lógica. |
| **O** — Abierto/cerrado | Para agregar algo se agrega un archivo, no se modifica lo existente (ej. un criterio nuevo = un archivo en `condition_criteria/` + registrarlo en la fábrica). |
| **L** — Sustitución | Cualquier `LLMProvider` (compatible con OpenAI, simulado, falso de pruebas) es intercambiable. El proveedor y los modelos se eligen en el `.env`. |
| **I** — Interfaces pequeñas | Cada interfaz tiene un solo método. |
| **D** — Inversión de dependencias | Los servicios reciben sus dependencias por el constructor; solo `factories/` las crea. |

### Idioma
- **Código en inglés** (estándar real): carpetas, archivos, clases, funciones, variables, columnas de CSV, claves JSON
  y valores categóricos (`severe`, `lab`, `downloaded`…).
- **En español** lo que lee una persona: mensajes al usuario, docstrings y comentarios, nombres de medicamentos,
  textos de las reglas, guías clínicas y la documentación (`docs/`).

### Nombres
| Elemento | Convención | Ejemplo |
|---|---|---|
| Archivo | **el nombre de la clase que contiene**, en `snake_case` | `case_loader.py` → `CaseLoader` |
| Clase | sustantivo, `PascalCase` | `InteractionChecker` |
| Función / método | verbo en inglés | `validate()`, `detect()`, `create_llm_client()` |
| Constante | `UPPER_SNAKE_CASE` | `CONSENSUS_THRESHOLD` |
| Repositorio | `<Cosa>Repository` | `ConditionRuleRepository` |
| Fábrica | `<area>_factory.py` con funciones `create_<cosa>()` | `case_factory.py` → `create_case_loader()` |
| Prueba | `test_<archivo>.py` en la misma ruta espejo | `tests/services/cases/test_case_validator.py` |
| Datos | `snake_case`; casos `CASO-XXX.json` | `condition_rules.csv` |

- **Un archivo de `models/` = una entidad.** Si la entidad tiene partes que solo existen dentro de ella
  (ej. `Sex` y `Medication` dentro de `ClinicalCase`), van en el mismo archivo y se mencionan en su primera línea.
- **Cada carpeta tiene un `__init__.py` que funciona como índice**: dice qué hay en cada archivo.

### Otras reglas
- **Datos fuera del código**: tablas, ejemplos, casos y textos largos van en `data/`.
- **Datos generados vs. datos fuente**: lo generado (`interactions.csv`) se crea con `scripts/` y nunca se edita a mano.
- **Configuración centralizada**: ningún número "mágico"; todo en `config/`.
- **Las pruebas nunca gastan dinero**: usan proveedores falsos o el simulado.
- **Documentar cada avance** en `docs/BITACORA.md` y en el `.md` que corresponda.

## 4. Cómo agregar algo nuevo (receta)
1. ¿Es un dato? → clase en `models/<area>/<entity>.py`.
2. ¿Hay que leerlo/guardarlo? → `repositories/<area>/<cosa>_repository.py`.
3. ¿Es lógica? → `services/<area>/<clase>.py` (recibe todo por el constructor).
4. ¿Hay varias implementaciones posibles? → contrato en `interfaces/` y una clase por implementación.
5. Conectarlo → función `create_<cosa>()` en `factories/<area>_factory.py`.
6. Probarlo → `tests/<capa>/<area>/test_<archivo>.py`.
7. Anotarlo → `docs/BITACORA.md`.
