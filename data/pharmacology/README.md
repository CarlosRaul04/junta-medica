# Datos farmacológicos

## drugs.csv — catálogo de medicamentos reconocidos
| Columna | Contenido |
|---|---|
| `inn` | Denominación Común Internacional en español. Es el nombre "oficial" que usa todo el sistema. |
| `drug_class` | Grupo terapéutico. |
| `atc` | Código ATC (OMS). ⚠ Verificar contra el índice ATC/DDD de la OMS antes de la entrega. |
| `synonyms` | Otras formas de escribirlo (sin tilde, sal, inglés). Separados por `\|`. |
| `brands` | Nombres comerciales de referencia. Separados por `\|`. ⚠ Verificar en el Observatorio de Productos de DIGEMID. |
| `english_names` | Nombre en inglés tal como aparece en DDInter. En combinaciones, cada componente (`Amoxicillin\|Clavulanic acid`). |
| `guidelines` | Guías que lo mencionan (`hta`, `dm2`, `ic`, `fa`, `erc`, `nac`). `—` = no está en las guías pero se incluye por su relevancia en interacciones (AINE). |

Un medicamento que no esté aquí se marca como **"no reconocido"** y se informa al usuario.

## ddinter/ — datos fuente (descargas originales)
Archivos `ddinter_downloads_code_<A|B|C|H|J|M|N>.csv` de https://ddinter.scbdd.com/ (columnas: `DDInterID_A, Drug_A, DDInterID_B, Drug_B, Level`).
No se modifican.

## label_interactions.csv — interacciones de fichas técnicas (curadas a mano)
Para los medicamentos que DDInter no cubre (dabigatrán, finerenona, gliclazida).
| Columna | Contenido |
|---|---|
| `drug_a`, `drug_b` | DCI del catálogo |
| `severity` | `severe` o `moderate` (criterio de lectura en `docs/FUENTES.md` §4.1) |
| `source`, `page` | id de la ficha en `data/documents/catalog.csv` y página del PDF (la cita queda `ft_x:p84`) |
| `note` | qué dice la ficha, en una frase |

## interactions.csv — tabla GENERADA (no editar a mano)
Se crea con: `python -m scripts.build_interaction_table` (une DDInter + `label_interactions.csv`; por par queda la severidad más alta).
Columnas: `drug_a, drug_b` (DCI, orden alfabético), `severity` (severe/moderate/mild/unknown), `source`, `source_id`.
Si se agrega un medicamento a `drugs.csv` o una fila a `label_interactions.csv`, volver a ejecutar el comando.

## condition_rules.csv — reglas fármaco–condición (curadas a mano)
| Columna | Contenido |
|---|---|
| `rule_id` | `RC01`, `RC02`… (único) |
| `drug` | DCI del catálogo |
| `criterion_type` | `lab`, `age` o `history` |
| `parameter` | clave de laboratorio (ej. `egfr_ml_min`), `age`, o nombre de la condición |
| `operator` | `<`, `<=`, `>`, `>=` · para antecedentes: `contains` |
| `value` | umbral numérico · para antecedentes: términos separados por `\|` |
| `severity` | `severe`, `moderate`, `mild` |
| `effect`, `recommendation` | texto que se muestra en el informe (en español) |
| `source`, `page` | id del documento en `data/documents/catalog.csv` (guía o ficha técnica) y página del PDF (la cita) |

**Regla:** toda fila nueva debe tener una fuente descargada y una página que exista en el PDF. Las pruebas
`tests/repositories/pharmacology/test_condition_rule_repository.py` y `test_label_interaction_repository.py` lo verifican.
