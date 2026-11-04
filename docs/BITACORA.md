# Bitácora del proyecto

Registro breve de lo que se hizo y por qué. **Regla:** cada avance o decisión se anota aquí y en el `.md` que corresponda.

## 2026-11-03
**Punto de partida**
- Se revisó el proyecto C# de referencia (AbogatoIA). Conclusión: tenía un debate de 3 IAs sin roles ni endpoint, y un flujo médico de una sola IA "actuando" 4 roles. No coincidía con el documento del curso (Python, RAG, rondas de debate).
- **Decisión:** rehacer desde cero en **Python** según el documento. Stack: Streamlit, ChromaDB, SQLite, ReportLab, OpenAI.

**Diseño de agentes** (detalle en `PLAN.md`)
- Agentes con IA: Clínico, Farmacológico, Protocolo (modelo `gpt-6-luna`) y Médico Jefe (`gpt-6.1-terra`).
- Agentes sin IA (código/reglas): validador, normalizador de medicamentos, RAG, verificador de interacciones, orquestador, verificador de citas.
- Presupuesto estimado: ~US$ 0.03 por caso; US$ 10 alcanzan para desarrollo y evaluación.

**Fase 0 — estructura**
- Proyecto en `C:\junta-medica-ia` (fuera de OneDrive), Python 3.12, `.venv`.
- Regla obligatoria: **SOLID**, una responsabilidad por archivo (ver `ARQUITECTURA.md`).
- Creados `junta_medica/config/` y `junta_medica/llm/` con **modo simulado** (`MOCK_MODE=1` en `.env`): permite avanzar sin gastar.
- 14 pruebas automáticas (`python -m pytest`).
- ⚠ La clave del `.env` era una *admin key* de OpenAI: hay que crear una clave de proyecto (`sk-proj-...`).

**Fase 1 — guías clínicas**
- Se eligieron 6 enfermedades: HTA, DM2, insuficiencia cardiaca, fibrilación auricular, ERC y neumonía.
- Descargadas las 6 guías (INS 2026 y EsSalud 2023–2025) → `data/documents/guidelines/`, registradas en `catalog.csv`.
- Se usaron las versiones más recientes: IC 2024 (no 2019), FA 2023 (no 2018), ERC EsSalud 2025 (la del INS 2026 queda como alternativa, no se indexa).
- CIE-10 OPS en español → `data/references/`.

**Fase 2 — caso clínico** (`junta_medica/cases/`)
- Modelo `ClinicalCase` (con `Medication` y `Sexo`), validador y cargador desde diccionario o archivo JSON.
- Validación por **reglas independientes** (una familia por archivo), todas se aplican y se informan juntas (RF02):
  campos obligatorios, campos permitidos, tipos, formato del código `CASO-001` (RF03), edad 18–120, sexo F/M,
  y **ausencia de datos personales** (DNI, teléfono, correo) en cualquier texto (RF03, RNF05).
- Mensajes en español claro, sin tecnicismos (RNF06). CP01 cubierto por una prueba.
- Plantilla de caso en `data/templates/clinical_case.json` (secciones `caso` y `esperado`).
- Convenciones de nombres del proyecto documentadas en `ARQUITECTURA.md`.
- 48 pruebas automáticas.

**Fase 1/2 — farmacología** (`junta_medica/pharmacology/`)
- **Catálogo de 45 medicamentos** elegido con datos: se contaron las menciones de ~60 candidatos en el texto de las 6 guías.
  Aparecieron medicamentos que no estaban previstos (finerenona, dapagliflozina, sacubitrilo/valsartán, eplerenona, gliclazida).
- **Decisión de fuentes:** guías peruanas; datos farmacológicos internacionales (son universales). Se descartó Kaggle
  (licencia de DrugBank, no clínico, no citable) y se eligió **DDInter** (curado por farmacéuticos, con severidad, citable).
- DDInter: la página solo enlaza algunas categorías; las de C, J, M y N existen en el servidor con el mismo nombre y se
  descargaron por enlace directo. Se borraron las categorías que no usamos (D, L, P, R, V).
- **Tabla de interacciones generada** con `scripts/build_interaction_table.py`: 686 pares, 44 graves.
  Sin cobertura: dabigatrán, finerenona, gliclazida.
- **Normalizador:** reconoce DCI, sinónimos, marcas, nombres en inglés, quita dosis y sales ("Losartán potásico 50 mg"),
  y corrige errores de tipeo ("amoxicilna") marcándolos para confirmación.
- **Verificador de interacciones** (diagrama 3): revisa todos los pares; informa graves y moderadas; las graves son alerta destacada.
- 90 pruebas automáticas.

## 2026-11-04
**Reglas fármaco–condición** (`junta_medica/pharmacology/condiciones/`)
- Se buscaron en el texto de las 6 guías las condiciones de uso por función renal, potasio, edad y antecedentes.
  Resultado: **17 reglas**, cada una citada al documento y página (ej. metformina con TFG < 30 → `gpc_dm2:p31`).
- Lo que **no** está en las guías (AINE en ERC/IC, digoxina, dabigatrán, levofloxacino, ivabradina en FA) quedó como
  pendiente para completar con fichas técnicas: no se inventan citas.
- Tres tipos de criterio (laboratorio, edad, antecedente), cada uno en su clase (fácil agregar más).
  Si falta un dato (ej. no hay TFG), la regla se reporta como **no evaluable** para que el agente lo pida.
- `Severity` se movió a `pharmacology/severity.py` porque ahora la usan interacciones y condiciones.
- **Laboratorio estandarizado:** el caso solo acepta claves conocidas (`egfr_ml_min`, `potassium_meq_l`, `lvef_pct`…)
  con valor numérico; sin esto las reglas no podrían leer los datos.
- Prueba de integridad: cada regla debe apuntar a un medicamento del catálogo, a una guía descargada y a un laboratorio reconocido.
- 119 pruebas automáticas.

**Reorganización: arquitectura en capas**
- Motivo: los archivos con nombres genéricos repetidos (`modelo.py`, `fabrica.py`, `almacen_csv.py`) en cada carpeta
  hacían difícil entender qué hacía cada uno.
- Nueva organización por **capas**, como el proyecto C# de referencia: `models/` (Models), `interfaces/`
  (Services/Interfaces), `repositories/` (Persistence + Repositories), `services/` (Services), `factories/` (Program.cs),
  `config/` (appsettings) y `exceptions.py`. Dentro de cada capa, una carpeta por área (`cases/`, `pharmacology/`, `llm/`).
- Cada archivo se llama como su clase (`case_loader.py` → `CaseLoader`); los modelos con varias clases se dividieron
  (ej. `interaction.py` y `interaction_finding.py`).
- Se unificaron lector + catálogo en `DrugRepository`; la lectura de archivos JSON de casos pasó a `CaseRepository`.
- Las pruebas se movieron en espejo (`tests/services/...`, `tests/repositories/...`). 121 pruebas pasando.
- `ARQUITECTURA.md` reescrito con tabla de capas, árbol completo, reglas y una receta "cómo agregar algo nuevo".

**Decisión: pipeline primero, herramientas (function calling) después**
- Se evaluó dar herramientas a los agentes para que decidan qué consultar. Se decidió terminar primero el sistema con
  pipeline y dejar function calling como evolución (Fase 7). Propuesta registrada en `PLAN.md`.

**RAG — base de conocimiento** (capas: `models/`, `interfaces/`, `repositories/`, `services/` y `factories/` de `conocimiento`)
- Se estudió la estructura de las guías: todas tienen una "Lista de recomendaciones" (10–25 págs.) organizada en
  "Pregunta N". Solo esa sección se indexa (`sections.csv`): ~66 de ~2 300 páginas.
- Fragmentación por **pregunta clínica** (61 preguntas → 139 fragmentos), con páginas para la cita (`gpc_ic:p22-23`).
- La revisión de los fragmentos encontró dos problemas, ya corregidos: el limpiador borraba "Fuerza de la recomendación"
  (ahora solo detecta encabezados en el borde de la página) y los flujogramas se extraían ilegibles (se excluyeron).
- Las pruebas detectaron un error real: una pregunta que empieza al inicio de una página se asignaba a la página anterior. Corregido.
- Embeddings e5 locales (gratis) + ChromaDB. Umbral de similitud para "evidencia insuficiente" (RF11), pendiente de calibrar.
- Pruebas con dobles (embeddings falsos, almacén en memoria) + ChromaDB real. 149 pruebas.
- Herramientas: `python -m scripts.index_guidelines` y `python -m scripts.search_guidelines "consulta"`.

**Migración de nombres a inglés (estándar de la industria)**
- Todo el código pasó a inglés: carpetas (`models/`, `services/`, `repositories/`, `factories/`, `tests/`, `scripts/`, `data/`),
  archivos, clases (`CaseLoader`, `InteractionChecker`, `KnowledgeRetriever`, `ChromaVectorStore`…), funciones, variables,
  columnas de CSV, claves JSON y valores categóricos (`severe`, `lab`, `downloaded`).
- Siguen en español: mensajes al usuario, docstrings, comentarios, nombres de medicamentos, textos de reglas, guías y `docs/`.
- Términos estándar de RAG: `Chunk`, `Chunker`, `KnowledgeRetriever`, `VectorStore`, `EmbeddingModel`.
- Claves de laboratorio: `egfr_ml_min`, `potassium_meq_l`, `lvef_pct`… (ver `RECOGNIZED_LAB_TESTS` en `config/cases.py`).
- Variable del `.env`: `MODO_SIMULADO` → `MOCK_MODE`.
- Se hizo con un script que renombra solo identificadores (analizador de Python), probado primero en una copia. 149 pruebas pasando.
- ⚠ La base vectorial (`chroma_db/`) creada antes del cambio guarda claves viejas: **volver a indexar**
  (`python -m scripts.index_guidelines`).

### Aviso de base vectorial desactualizada
- Si `chroma_db/` se creó con una versión anterior (metadatos con nombres viejos), la búsqueda ya no falla con `KeyError`: lanza `OutdatedIndexError` con el mensaje "ejecuta `python -m scripts.index_guidelines`".
- Calibración preliminar (índice anterior): consultas dentro del alcance dieron similitudes de 0.865–0.888. Falta el valor de una consulta fuera de alcance para fijar `MIN_SIMILARITY`.

### Calibración del umbral de evidencia (RF11)
| Consulta | Mejor resultado | Similitud | ¿Dentro del alcance? |
|---|---|---|---|
| suspender espironolactona por potasio alto | gpc_ic p22-23 | 0.887 | sí |
| antibiótico para neumonía en paciente ambulatorio | gpc_nac p12-13 | 0.888 | sí |
| metformina con enfermedad renal | gpc_erc p16 | 0.879 | sí |
| tratamiento de la psoriasis | gpc_nac p14 | 0.843 | **no** |

- `MIN_SIMILARITY` pasa de 0.80 a **0.86** (punto medio entre 0.843 y 0.879). Con 0.80 la consulta de psoriasis se marcaba como "evidencia suficiente".
- El modelo e5 da puntajes muy juntos (casi todo entre 0.83 y 0.89): el margen es chico. Se recalibrará con los 18 casos de evaluación.
- Observación: "metformina con enfermedad renal" trajo fragmentos generales de ERC y no la contraindicación de metformina por TFG. Ese caso lo cubren las reglas deterministas de `condition_rules.csv`, no el RAG.


## 2026-11-04 — Capa de IA genérica (modelos gratuitos)
**Decisión:** el equipo no tiene presupuesto. El sistema deja de depender de OpenAI de pago y acepta **cualquier proveedor compatible
con la API de OpenAI**. Qué modelos gratuitos usar lo decide el equipo; se configura solo en el `.env`.

- `OpenAIProvider` (Responses API, solo OpenAI) se reemplazó por `OpenAICompatibleProvider` (Chat Completions, el formato que aceptan
  OpenRouter, Groq, Gemini, Ollama, LM Studio y OpenAI). El cliente del SDK se le inyecta desde `llm_factory.py`.
- Nuevas variables: `LLM_BASE_URL`, `LLM_API_KEY`, `AGENT_MODEL`, `CHIEF_MODEL`, `CLINICAL_MODEL`/`PHARMACOLOGICAL_MODEL`/`PROTOCOL_MODEL`
  (opcionales), `LLM_JSON_MODE`, `LLM_MERGE_SYSTEM_PROMPT`. Desaparecen `OPENAI_API_KEY` y `REASONING_EFFORT`.
- `LLMClient` ahora sabe qué modelo usa cada rol: `ask(role, instructions, message)` (ya no recibe el modelo).
- Pensado para modelos gratuitos:
  - reintentos automáticos ante límite de uso (429) y caídas (5xx): `REQUEST_RETRIES = 3`;
  - `parse_json` acepta respuestas "sucias": bloque `<think>`, texto antes/después del JSON;
  - opción para modelos que rechazan `response_format` o el mensaje de sistema;
  - modelo sin precio en `PRICES_USD_PER_MILLION` = costo 0.
- Errores del proveedor (clave inválida, modelo inexistente, sin conexión) llegan como `LLMProviderError` con el nombre del modelo.
- Seguridad: la admin key de OpenAI se quitó del `.env`. **Revocarla** en el panel de OpenAI.


## 2026-11-04 — Datos farmacológicos completos y CIE-10
**Fichas técnicas.** Lo que faltaba no estaba en ninguna de las 6 guías (se buscó en el texto completo). Se usaron 9 fichas
técnicas oficiales en español (3 EMA, 6 CIMA), registradas en `catalog.csv` como `ft_<dci>` (detalle en FUENTES §4.1).
- **Interacciones:** 25 pares nuevos para dabigatrán, finerenona y gliclazida (`label_interactions.csv`). Ya no queda ningún
  medicamento del catálogo sin datos de interacciones. Tabla final: 711 pares, 48 graves.
- **Reglas fármaco–condición:** de 17 a **40** (RC18–RC40): dabigatrán, finerenona, ivabradina, digoxina, levofloxacino,
  AINE, y el ajuste renal de amoxicilina, amoxicilina/clavulánico y cefuroxima (tabla 4 de la guía de NAC).
- Criterio de severidad al leer una ficha, escrito para que otro lo pueda repetir (FUENTES §4.1).
- **Verificación:** un script comprobó que la página citada de cada fila contiene el medicamento o el umbral. Las 25
  interacciones pasaron; 4 reglas usan un umbral que la ficha no escribe con número (definición estándar, anotado en FUENTES §5).
- **Cambio de comportamiento:** `ConditionChecker` informa una sola alerta por medicamento y dato (la más grave). Antes,
  espironolactona con K = 6,3 daba dos alertas de potasio; ahora solo la grave.
- Las fichas técnicas **no se indexan** todavía en el RAG (el indexador salta documentos sin filas en `sections.csv`).

**CIE-10.** En vez del subconjunto de ~40 códigos previsto, se extrajo la Lista Tabular **completa** del PDF de la OPS
(11 399 códigos con título y página) con `scripts/build_icd10_table.py`. El PDF trae el texto desordenado en algunas páginas,
así que cada título se empareja con el código que está a su misma altura. Las subcategorías compartidas (diabetes, consumo
de sustancias, glomerulopatías) se generan solo cuando la nota de la categoría nombra la lista correcta; un primer intento
las aplicaba a grupos equivocados (úlceras gástricas recibían las de retraso mental) y se corrigió.

Pruebas: 250 pasan.


## 2026-11-04 — Los 18 casos simulados
- Escritos en `data/cases/` según el plan (6 comunes, 6 polifarmacia, 4 atípicos, 2 fuera de alcance). Tabla en FUENTES §7.
- La sección `expected` se amplió respecto de la plantilla original: diagnóstico principal + diagnósticos aceptables
  (para el top-3), interacciones y alertas que deben detectarse, si debe abstenerse, guías relevantes y puntos clave
  para la revisión manual. Los campos están en `EXPECTED_FIELDS` y `CASE_TYPES` (`config/cases.py`).
- Casos pensados para probar cosas concretas: nombres comerciales (012: Pradaxa, Voltaren), medicamento fuera del
  catálogo (015: fluconazol; 017: hidrocortisona crema), alergia registrada (015), NAC sin fiebre en adulto mayor (013,
  la guía de NAC lo menciona en la p. 27), datos de fichas técnicas (012: dabigatrán con TFG 27).
- Resultado con las herramientas deterministas: 18/18 válidos, 100 % de interacciones y alertas esperadas detectadas,
  todos los códigos CIE-10 existen. Lo fija `tests/repositories/cases/test_case_files.py`.
- Arreglo menor: los mensajes del validador decían "age", "sex", "medical_history" (restos de la migración); ahora
  dicen "edad", "sexo", "antecedentes", "alergias".
- Pendiente de comprobar en la PC con el modelo e5: que los casos 017 y 018 den "evidencia insuficiente" en el RAG.

Pruebas: 323 pasan.


## 2026-11-04 — Fase 3: agentes, debate y Médico Jefe
**Qué se construyó** (estructura en ARQUITECTURA §2, "Agentes y debate"):
- 4 agentes con IA: Clínico (top-3 diagnósticos CIE-10 + plan), Farmacológico (seguridad de la medicación),
  Protocolo (cumplimiento de guías) y Médico Jefe (segunda opinión final). Sus instrucciones están en `data/prompts/*.md`,
  en español, **editables sin tocar código**.
- Cada agente ve información distinta (para que no se copien): el Clínico propone sin ver las alertas de la tabla;
  el Farmacológico no ve el relato de síntomas; el de Protocolo recibe fragmentos de guía buscados para la propuesta
  (no para el caso). Una prueba lo verifica.
- `DebateOrchestrator`: rondas, consenso, abstención, alertas finales, Médico Jefe y verificación de citas.
- `python -m scripts.run_case CASO-008` corre todo y guarda el resultado completo en `output/debates/` (cada
  intervención con su JSON original, modelo, tokens, costo y tiempo: RF14).

**Decisiones:**
- **Una objeción grave bloquea el consenso.** Con 2 revisores, una sola objeción ya da 2/3 = 0,67 y alcanzaba el umbral:
  el debate se cerraba sin que el Clínico corrigiera un riesgo para el paciente. Lo detectó una prueba.
- **Abstención sin debate:** si el buscador no supera el umbral de evidencia, no se llama a la IA (ahorra cuota gratuita
  y evita opinar sin respaldo). Las alertas de medicación se informan igual. Configurable: `ABSTAIN_WITHOUT_DEBATE`.
- **La IA no puede quitar alertas:** las de la tabla y las reglas van siempre al resultado; el Farmacológico solo puede
  agregar alertas con una cita válida.
- **Lectura tolerante** de las respuestas: posturas en español ("de acuerdo", "objeción"), citas como texto suelto,
  campos faltantes. Una postura ilegible se trata como objeción (lo más prudente).
- **Citas inventadas:** toda cita que no esté entre las entregadas al agente se marca como inválida; la trazabilidad
  (afirmaciones con cita válida) se calcula en cada caso.
- El texto de las alertas ahora es legible: "TFG estimada (mL/min/1.73 m²) = 27" en vez de "egfr_ml_min = 27".

**Probado:** con respuestas guionadas (una objeción grave en la ronda 1 → el Clínico corrige en la ronda 2 → el Jefe
cierra), con dos objeciones permanentes (se detiene en la ronda 3 y registra la discrepancia) y con un caso fuera de
alcance (0 llamadas). Pruebas: 352 pasan. **Falta probar con modelos reales** (lo hará el equipo con modelos gratuitos).

## 2026-11-04 — Primera configuración con IA real (OpenRouter, gratis)
- Proveedor: OpenRouter, clave gratuita (**50 llamadas por día**; un caso usa de 4 a 10 → ~5–12 casos por día por clave).
  Para correr los 18 casos de la evaluación conviene que cada integrante use su propia clave o repartirlos en varios días.
- Se probaron 4 modelos gratuitos con la misma pregunta (paciente con IC, enalapril + espironolactona, K 6,3):
  | Modelo | Resultado |
  |---|---|
  | `nvidia/nemotron-3.5-super-vl:free` | ✅ JSON válido, en español, CIE-10 correctos (E87.5, N18.3, I50.9), ~10 s |
  | `nvidia/nemotron-3-ultra-550b-a55b:free` | ⚠ JSON válido pero en inglés y con códigos CIE-10-CM de EE. UU. (N18.31, T46.4X5A), ~21 s |
  | `google/gemma-4-31b-it:free` | ❌ saturado en ese momento (error 429) |
  | `xingchen-agi/xing4.0-29b-a4b:free` | ❌ saturado en ese momento (error 429) |
- Elegido para empezar: `nvidia/nemotron-3.5-super-vl:free` para los 4 roles (`AGENT_MODEL` y `CHIEF_MODEL`).
  El equipo puede cambiarlo en el `.env`.
- Por lo visto con el modelo "ultra", los prompts del Clínico y del Jefe ahora piden explícitamente la CIE-10 de la OMS/OPS
  (no la CIE-10-CM).

## 2026-11-04 — Primer caso con IA real (CASO-008) y ajustes
Resultado: 1 ronda, acuerdo 67 % (Farmacológico de acuerdo con observaciones; Protocolo con objeción moderada),
4 llamadas, 100 s, trazabilidad 88 %, 0 citas inventadas. El Jefe acertó el diagnóstico esperado (E87.5 hiperpotasemia),
recomendó suspender espironolactona citando la regla y la interacción, y registró las discrepancias.

Problemas vistos en el JSON (`output/debates/`) y arreglos:
- **El Agente de Protocolo no veía los fragmentos que la propuesta citaba** (p17, p19 de la guía de IC): objetó porque
  "no podía verificarlos". Ahora recibe los fragmentos citados por la propuesta + los buscados para ella.
- **El buscador del caso no traía la p23 de la guía de IC** (espironolactona y potasio) y sí fragmentos de diabetes:
  solo buscaba por síntomas y antecedentes. Se agregó una tercera consulta: antecedentes + medicación actual.
- El resumen del Jefe terminaba con un "}" suelto (detalle del modelo): se limpia al leer la respuesta.
- Tiempos: Clínico 17 s, Farmacológico 11 s, Protocolo 39 s, Jefe 25 s (el modelo "razona" mucho: hasta 7 000 tokens de salida).
- **Segunda corrida (con los arreglos):** consenso 100 % en la ronda 1 (el Protocolo ya pudo verificar las citas), cita la
  p23–24 de la guía de IC (espironolactona y potasio), trazabilidad 86 %. De las 2 afirmaciones sin cita: una es
  correcta (el ECG urgente no está en las guías y el agente no inventó cita); la otra tenía la cita escrita dentro del
  texto. Ahora una cita escrita así ("... [gpc_ic:p23-24]") se reconoce y se pasa a su campo.
