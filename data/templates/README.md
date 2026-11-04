# Plantillas

## clinical_case.json
Formato de los archivos de casos simulados (`data/cases/CASO-XXX.json`). Es una copia del CASO-007 con id `CASO-000`.

### `case` — los datos clínicos (lo ÚNICO que ven los agentes)
- Obligatorios: `case_id` (formato `CASO-001`), `age` (18–120), `sex` (`F`/`M`), `chief_complaint`, `symptoms`, `medications`.
- Opcionales: `medical_history`, `allergies`, `lab_results`.
- `medications`: lista de `{"name": ..., "dose": ...}` (o solo el nombre como texto). Puede ir el nombre comercial
  (`Pradaxa`, `Voltaren`): el normalizador lo traduce a la DCI.
- `lab_results`: `clave: valor numérico` (ej. `"egfr_ml_min": 38`). Solo se aceptan las claves de
  `RECOGNIZED_LAB_TESTS` en `junta_medica/config/cases.py` (egfr_ml_min, creatinine_mg_dl, potassium_meq_l,
  sodium_meq_l, glucose_mg_dl, hba1c_pct, inr, lvef_pct, hemoglobin_g_dl, wbc_mm3, crp_mg_l,
  systolic_bp_mmhg, diastolic_bp_mmhg, heart_rate_bpm, spo2_pct).
- **Prohibido** cualquier otro campo o dato personal (nombre, DNI, teléfono, correo). El validador lo rechaza.

### `expected` — la respuesta correcta (solo para la evaluación; los agentes NUNCA la ven)
| Campo | Contenido |
|---|---|
| `type` | `common`, `polypharmacy`, `atypical` u `out_of_scope` |
| `test_cases` | casos de prueba del documento que cubre (`CP04`…); se fija según el tipo (`CASE_TYPES` en `config/cases.py`) |
| `primary_diagnosis` | `{"icd10": "I48.9", "name": "..."}` — el diagnóstico correcto |
| `acceptable_diagnoses` | códigos CIE-10 que cuentan como acierto en el top-3 (una categoría como `I48` acepta cualquier `I48.x`) |
| `interactions` | interacciones que el sistema **debe** detectar: `{"drugs": [a, b], "severity": "severe"}`. Puede detectar más (no es error) |
| `condition_alerts` | reglas de `condition_rules.csv` que **deben** dispararse (ej. `RC09`) |
| `should_abstain` | `true` solo en los casos fuera de alcance: el sistema debe declarar evidencia insuficiente |
| `relevant_guidelines` | ids del catálogo de documentos que el informe debería citar |
| `key_points` | lo que una buena segunda opinión debería decir (para la revisión manual) |
| `case_source` | de dónde sale el caso |

La prueba `tests/repositories/cases/test_case_files.py` valida todo esto y comprueba que las herramientas
detecten las interacciones y alertas esperadas.
