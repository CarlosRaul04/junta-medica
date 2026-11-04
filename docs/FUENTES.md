# Fuentes de conocimiento y diseño de casos (Fase 1)

## 1. Enfermedades cubiertas y guías descargadas ✅ (APROBADO)
El sistema cubre **6 enfermedades de Medicina Interna**. Se eligieron porque suelen presentarse juntas en el mismo
paciente (adulto mayor polimedicado) y generan interacciones farmacológicas relevantes. La neumonía se incluye para
sumar antibióticos (claritromicina, levofloxacino), que interactúan con warfarina, amiodarona y estatinas.
Todo caso fuera de estas 6 enfermedades debe terminar en **"evidencia insuficiente"** (RF11, CP07).

| # | Enfermedad | CIE-10 | Guía (versión extensa) | Institución | Año | Págs. | Archivo |
|---|---|---|---|---|---|---|---|
| 1 | Hipertensión arterial | I10 | GT N.° 006-INS/CETS-2026 — Prevención, diagnóstico y tratamiento de la HTA en adultos | INS | 2026 | 549 | `gpc_hta_ins_2026.pdf` |
| 2 | Diabetes mellitus tipo 2 | E11 | GPC N.° 81 — Manejo farmacológico de personas adultas con DM2 | EsSalud-IETSI | 2025 | 421 | `gpc_dm2_essalud_2025.pdf` |
| 3 | Insuficiencia cardiaca crónica | I50 | GPC N.° 67 — Diagnóstico y tratamiento de la ICC (actualización 2024) | EsSalud-IETSI | 2024 | 294 | `gpc_ic_essalud_2024.pdf` |
| 4 | Fibrilación auricular | I48 | GPC N.° 61 — Manejo de pacientes con FA (actualización 2023) | EsSalud-IETSI | 2023 | 163 | `gpc_fa_essalud_2023.pdf` |
| 5 | Enfermedad renal crónica | N18 | GPC N.° 82 — Tamizaje, diagnóstico y manejo de la ERC (actualización 2025) | EsSalud-IETSI | 2025 | 509 | `gpc_erc_essalud_2025.pdf` |
| 6 | Neumonía adquirida en la comunidad | J18 | GPC N.° 79 — Manejo de la NAC en adultos | EsSalud-IETSI | 2025 | 352 | `gpc_nac_essalud_2025.pdf` |

Todos los archivos están en `data/documents/guidelines/` y registrados en `data/documents/catalog.csv`
(el `id` del catálogo, ej. `gpc_hta`, es el que aparece en las citas del informe). Los 6 PDF tienen texto extraíble (no son escaneos).

**Descargado pero NO indexado** (estado `alternativa`, para no duplicar recomendaciones):
- `gpc_erc_ins_2026.pdf` — INS GT N.° 008-INS/CETS-2026, ERC en el primer nivel de atención. Se prefirió la de EsSalud porque cubre todos los estadios.

**Material de referencia** (no se indexa): `data/references/icd10_ops_2018_vol1.pdf` — CIE-10 OPS en español, vol. 1 (lista tabular). Se usará para construir `data/cie10.csv`.

**Dónde se obtuvieron:**
- IETSI (EsSalud): https://ietsi.essalud.gob.pe/gpc-guias-de-practica-clinica/
- INS (gob.pe): https://www.gob.pe/institucion/ins/informes-publicaciones/tipos/217-guias-de-practica-clinica
- CIE-10: https://www.minsa.gob.pe/reunis/data/volumen1-2018.pdf

**Qué se indexa (RAG):** de las ~2 300 páginas, solo la sección **"Lista (completa) de recomendaciones"** de cada guía
(~66 páginas en total), definida en `data/documents/sections.csv`. Ver la sección 8 de este archivo.

**Nota para el documento del curso:** cambiar "GPC del MINSA" por "GPC del INS y EsSalud (IETSI)".

**Posible ampliación** (solo si sobra tiempo): EsSalud GPC de infección del tracto urinario no complicada (dic-2025), dislipidemia, EPOC.

## 2. Criterio de fuentes
- **Guías clínicas → peruanas** (INS, EsSalud): el tratamiento recomendado depende del sistema de salud local
  (disponibilidad de medicamentos, resistencia antibiótica) y el documento pide verificar adherencia a protocolos locales.
- **Datos farmacológicos → cualquier fuente confiable e internacional**: interacciones y contraindicaciones son propiedades
  del medicamento, iguales en todo el mundo. Lo único local son las **marcas comerciales** (verificar en DIGEMID).
- **No se usan datasets de Kaggle**: suelen derivar de DrugBank (requiere licencia para redistribuir), están pensados para
  machine learning (no traen severidad clínica) y no son una fuente citable.

## 3. Catálogo de medicamentos ✅
Archivo: `data/pharmacology/drugs.csv` — **45 medicamentos** (ver `data/pharmacology/README.md`).
- **Cómo se eligieron:** se contaron en el texto de las 6 guías las menciones de ~60 candidatos y se tomaron los que
  recomiendan, más AINE y paracetamol por su papel en interacciones. Ej.: metformina (517 menciones en la guía de DM2),
  espironolactona (129 en IC), ceftriaxona (170 en NAC), finerenona (56 en ERC).
- Cada medicamento tiene: DCI en español, grupo, código ATC, sinónimos, marcas, nombre(s) en inglés y guías que lo citan.
- ⚠ Verificar antes de la entrega: códigos ATC (índice ATC/DDD de la OMS) y marcas (Observatorio DIGEMID).

## 4. Interacciones fármaco–fármaco ✅
- **Fuente: DDInter** — base curada por farmacéuticos clínicos, con nivel de severidad, gratuita y citable:
  Xiong G. et al. *DDInter: an online drug–drug interaction database towards improving clinical decision-making and patient
  safety.* Nucleic Acids Research 2022;50(D1):D1200–D1207. https://ddinter.scbdd.com/
  (⚠ revisar sus "Terms and conditions" antes de la entrega).
- Descargas usadas: categorías ATC **A, B, C, H, J, M, N** → `data/pharmacology/ddinter/`.
  Las categorías C, J, M y N no tienen enlace en la página de descarga, pero existen en
  `https://ddinter.scbdd.com/static/media/download/ddinter_downloads_code_<LETRA>.csv`.
- La tabla `data/pharmacology/interactions.csv` se **genera** con `python -m scripts.build_interaction_table`
  (independiente de los casos → evita evaluación circular). Une DDInter (686 pares) con las fichas técnicas (25 pares,
  ver abajo). Resultado actual: **711 pares**: 48 graves, 265 moderadas, 33 leves, 365 de severidad desconocida.
  Si un par está en ambas fuentes, queda la severidad más alta (y su cita).
- Severity: Major → grave · Moderate → moderada · Minor → leve · Unknown → desconocida.
  Se informan **grave y moderada**; solo **grave** es alerta destacada (RF12). Configurable en `config/pharmacology.py`.
- Cita de cada interacción: `ddinter:<IDs del par>` (ej. `ddinter:DDInter1951-DDInter906`).
- Ejemplos graves detectados: warfarina + AINE/AAS/claritromicina/levofloxacino, amiodarona + digoxina/warfarina/levofloxacino,
  enalapril + espironolactona (hiperpotasemia), IECA + ARA II (doble bloqueo), ivabradina + diltiazem, atorvastatina + claritromicina.
- **Sin cobertura en DDInter:** dabigatrán, finerenona, gliclazida → completados con sus **fichas técnicas**
  en `data/pharmacology/label_interactions.csv` (25 pares, cada uno con documento y página; ej. `ft_dabigatran:p84`).
  Solo se cargaron los pares con medicamentos de nuestro catálogo.

### 4.1 Fichas técnicas (fuente oficial de medicamentos)
Para lo que las guías no dicen se usan las **fichas técnicas oficiales en español**: EMA (medicamentos con autorización
europea centralizada) y AEMPS-CIMA (autorización española). Están en `data/documents/drug_labels/` y registradas en
`catalog.csv` con id `ft_<dci>`. Se eligió CIMA/EMA porque publican fichas completas, versionadas y en PDF; DIGEMID
no ofrece fichas estructuradas equivalentes (la propia GPC de NAC cita "fichas técnicas ... de la FDA y DIGEMID").

| id | Ficha | Fuente | Se usó para |
|---|---|---|---|
| ft_dabigatran | Pradaxa 150 mg (págs. 78–93 del PDF) | EMA | interacciones (4.3, 4.5), renal, edad |
| ft_finerenona | Kerendia | EMA | interacciones (4.3, 4.5), potasio, TFG |
| ft_ivabradina | Procoralan | EMA | FC, presión, fibrilación auricular |
| ft_gliclazida | Diamicron 60 mg | CIMA | interacciones (4.5) |
| ft_digoxina | Digoxina Kern Pharma 0,25 mg | CIMA | potasio, función renal |
| ft_levofloxacino | Levofloxacino Cinfa 500 mg | CIMA | ajuste renal, epilepsia |
| ft_ibuprofeno · ft_naproxeno · ft_diclofenaco | Cinfa 600 · Normon 500 · Cinfa 50 | CIMA | ERC grave, insuficiencia cardiaca, cardiopatía isquémica |

**Criterio de severidad al leer una ficha** (para que sea reproducible):
- **grave**: "contraindicado", "no se debe usar", "debe evitarse", "interrumpir/suspender".
- **moderada**: "no se recomienda (iniciar)", "precaución", "monitorizar", "considerar reducir la dosis".
Por eso algunas severidades difieren de DDInter (ej. dabigatrán + AINE es moderada en la ficha; warfarina + AINE es grave en DDInter).

## 5. Reglas fármaco–condición ✅
Archivo: `data/pharmacology/condition_rules.csv` (curado a mano). Cada regla sale del **texto de una guía o ficha técnica
descargada** y lleva su documento y página del PDF como cita (ej. `gpc_dm2:p31`, `ft_dabigatran:p84`).
Una prueba automática verifica que la página exista en el PDF. Se buscaron en el texto de las 6 guías las
condiciones de uso por función renal, potasio, edad y antecedentes.

| Regla | Medication | Condición de riesgo | Severity | Cita |
|---|---|---|---|---|
| RC01–RC03 | metformina, glibenclamida, gliclazida | TFG < 30 (contraindicadas) | grave | gpc_dm2 p.31 |
| RC04 | glibenclamida | edad > 60 (hipoglucemia; preferir gliclazida) | moderada | gpc_dm2 p.15 |
| RC05 | pioglitazona | antecedente de insuficiencia cardiaca | moderada | gpc_dm2 p.19 |
| RC06–RC07 | empagliflozina, dapagliflozina | TFG < 20 (no iniciar) | moderada | gpc_dm2 p.21 |
| RC08–RC09 | espironolactona | TFG < 30 · potasio > 6 (suspender) | grave | gpc_ic p.23 |
| RC10–RC11 | espironolactona | potasio ≥ 5,0 · creatinina ≥ 2,5 (no iniciar) | moderada | gpc_ic p.23 |
| RC12–RC13 | eplerenona | TFG < 30 · potasio > 6 (suspender) | grave | gpc_ic p.133 |
| RC14 | finerenona | potasio > 5,5 (suspender temporalmente) | grave | gpc_erc p.25 |
| RC15 | finerenona | TFG < 25 (fuera de indicación) | moderada | gpc_erc p.24 |
| RC16 | diltiazem | FEVI < 40 % | grave | gpc_fa p.63 |
| RC17 | alopurinol | TFG < 60 (ajustar dosis) | moderada | gpc_erc p.22 |

**Desde fichas técnicas y la tabla 4 de la guía de NAC (RC18–RC40):**

| Regla | Medicamento | Condición de riesgo | Severidad | Cita |
|---|---|---|---|---|
| RC18 · RC19 | dabigatrán | TFG < 30 (contraindicado) · TFG < 50 (considerar 110 mg) | grave · moderada | ft_dabigatran p.84 · p.81 |
| RC20 | dabigatrán | edad ≥ 80 (110 mg c/12 h) | moderada | ft_dabigatran p.79 |
| RC21 · RC22 | finerenona | potasio > 5,0 (no iniciar) · TFG < 15 (suspender) | moderada · grave | ft_finerenona p.7 · p.6 |
| RC23 · RC24 | ivabradina | FC < 70 (criterio de inicio) · FC < 50 (bradicardia) | moderada · grave | ft_ivabradina p.4 · p.5 |
| RC25 | ivabradina | PAS ≤ 90 (hipotensión grave) | grave | ft_ivabradina p.4 |
| RC26 | ivabradina | antecedente de fibrilación auricular | moderada | ft_ivabradina p.5 |
| RC27 · RC28 | digoxina | potasio < 3,5 · TFG < 60 | moderada | ft_digoxina p.6 |
| RC29 · RC30 | levofloxacino | TFG < 50 (ajustar dosis) · epilepsia (contraindicado) | moderada · grave | ft_levofloxacino p.2 · p.3 |
| RC31 · RC33 · RC35 | ibuprofeno, naproxeno, diclofenaco | TFG < 30 (contraindicados) | grave | ft_* p.2 |
| RC32 · RC34 | ibuprofeno, naproxeno | antecedente de insuficiencia cardiaca | moderada | ft_ibuprofeno p.4 · ft_naproxeno p.3 |
| RC36 · RC37 | diclofenaco | insuficiencia cardiaca · cardiopatía isquémica (contraindicado) | grave | ft_diclofenaco p.3 |
| RC38 · RC39 · RC40 | amoxicilina, amoxicilina/clavulánico, cefuroxima | TFG < 30 (ajuste renal) | moderada | gpc_nac p.22 · p.23 |

⚠ **Umbrales que la ficha no escribe con número** (se usó la definición clínica estándar): RC27 hipocaliemia = K < 3,5;
RC28 "función renal reducida" = TFG < 60 (ERC G3 en la guía de ERC); RC33 y RC35 "insuficiencia renal grave" = TFG < 30
(la ficha de ibuprofeno lo define así). Las fichas usan aclaramiento de creatinina (Cockcroft-Gault) y los casos usan
TFGe: se tratan como equivalentes, lo que es una simplificación.

**Una sola alerta por dato:** si varias reglas del mismo medicamento y el mismo dato se cumplen (dabigatrán con TFG 28:
RC18 y RC19), solo se informa la más grave.

Tipos de criterio: `laboratorio` (clave de laboratorio + operador + umbral), `edad`, `antecedente` (términos buscados como
palabra completa, sin importar tildes). Si falta el dato (ej. metformina sin TFG), la regla queda como **no evaluable**
y se informa para que el agente pueda pedir el dato.

**Pendiente:** metformina con TFG 30–45 (reducción de dosis) — buscar en la guía de DM2 o en una ficha técnica.

**Laboratorio estandarizado:** para que las reglas funcionen, los casos solo aceptan las claves de
`RECOGNIZED_LAB_TESTS` (`junta_medica/config/cases.py`) y con valor numérico. El validador lo revisa.

## 6. CIE-10 ✅
- Fuente: CIE-10 OPS en español (volumen 1, Lista Tabular, 2018) → `data/references/icd10_ops_2018_vol1.pdf`.
- Se extrae **completa** (no un subconjunto): `python -m scripts.build_icd10_table` genera `data/references/icd10.csv`
  con **11 399 códigos** (2 049 categorías y 9 350 subcategorías), cada uno con su título y la página del PDF.
  Así cualquier código que proponga un agente se puede validar, no solo los de las 6 enfermedades.
- Las subcategorías que la CIE-10 define una sola vez para un grupo (ej. diabetes E10–E14: ".9 Sin mención de complicación")
  se generan automáticamente (E11.9 = "Diabetes mellitus tipo 2: Sin mención de complicación").
- 18 códigos quedaron sin título (letra distinta en el PDF); ninguno es de las 6 enfermedades.
- ⚠ El PDF dice "Material de capacitación. Utilización sin fines de lucro": uso académico, no redistribuir la tabla.

## 7. Casos simulados (18) ✅
Archivos: `data/cases/CASO-001.json` … `CASO-018.json`. Formato y significado de cada campo: `data/templates/README.md`.
Cada caso tiene `case` (lo único que ven los agentes) y `expected` (la respuesta correcta, solo para evaluar).

| Tipo | Casos | Cubre |
|---|---|---|
| Comunes | 001–006 (uno por enfermedad) | CP04 precisión diagnóstica |
| Polifarmacia | 007–012 | CP02/CP03 interacciones y alertas graves |
| Atípicos | 013–016 | CP05 presentación poco frecuente |
| Fuera de alcance | 017–018 | CP07 abstención (sin guía en la base) |

| Caso | Situación | Diagnóstico esperado | Debe detectar |
|---|---|---|---|
| 001 | HTA recién detectada, fumador | I10 | — |
| 002 | Síntomas clásicos de DM2, HbA1c 9,2 | E11.9 | — |
| 003 | IC con FEVI 32 %, post-infarto | I50.0 | — |
| 004 | Palpitaciones, FC 126 irregular | I48.9 | — |
| 005 | Diabético hipertenso con TFG 42 | N18.3 | — |
| 006 | Neumonía sin comorbilidades (CRB-65 = 0) | J18.9 | — |
| 007 | Warfarina + ibuprofeno, INR 4,1, sangrado | I48.9 | warfarina + ibuprofeno (grave) |
| 008 | IC con enalapril + espironolactona, K 6,3 | E87.5 | enalapril + espironolactona (grave) · RC09 |
| 009 | Intoxicación digitálica: digoxina + amiodarona, K 3,1 | T46.0 | amiodarona + digoxina, amiodarona + warfarina (graves) · RC27, RC28 |
| 010 | Hipoglucemias: metformina + glibenclamida, 74 años, TFG 26 | E11.6 | glibenclamida + metformina · RC01, RC02, RC04 |
| 011 | NAC tratada con claritromicina en paciente con warfarina y estatina | J18.9 | claritromicina + warfarina, atorvastatina + claritromicina (graves) |
| 012 | **Pradaxa + Voltaren** (nombres comerciales) + amiodarona, 82 años, TFG 27, hematuria | I48.9 | dabigatrán + diclofenaco, amiodarona + dabigatrán · RC18, RC20, RC35 |
| 013 | NAC en adulto mayor **sin fiebre**, con confusión | J18.9 | — |
| 014 | IC con FEVI preservada que se presenta con tos nocturna | I50.9 | — |
| 015 | DM2 descubierta por infecciones recurrentes; fluconazol (no está en el catálogo) | E11.9 | debe informar "no reconocido" |
| 016 | FA asintomática con ictus previo, solo con aspirina | I48.9 | — |
| 017 | Psoriasis | L40.0 | **abstenerse** |
| 018 | Hipotiroidismo | E03.9 | **abstenerse** |

Decisiones:
- `interactions` y `condition_alerts` son lo que el sistema **debe** detectar, escrito desde el criterio clínico.
  Las herramientas pueden detectar más (ej. interacciones moderadas de DDInter como enalapril + furosemida): no es error.
- `acceptable_diagnoses` permite contar como acierto los diagnósticos razonables del top-3 (en el 009, por ejemplo,
  intoxicación digitálica, FA, hipopotasemia o bradicardia).
- La prueba `tests/repositories/cases/test_case_files.py` valida los 18 casos y confirma que las herramientas detectan
  el **100 %** de lo esperado (sin IA). ⚠ Es un resultado esperable, porque el equipo escribió los casos conociendo las
  tablas: la evaluación de verdad es si el **informe final** de los agentes conserva y explica esas alertas (Fase 5).
- Casos inválidos para CP01: se generan dentro de las pruebas del validador (no cuentan en los 18).

## 8. Base de conocimiento (RAG) ✅
- **Qué se indexa:** la sección "Lista de recomendaciones" de cada guía (páginas en `data/documents/sections.csv`):
  HTA p.15–20 · DM2 p.13–28 · IC p.16–26 · FA p.10–14 · ERC p.12–32 · NAC p.12–18.
- **Qué NO se indexa y por qué:**
  - Métodos, tablas GRADE, referencias y anexos: no son recomendaciones; meterían ruido.
  - **Flujogramas:** son diagramas; al extraer el texto sale desordenado ("Adultos de 18 a os o m s") y su contenido ya está
    en la lista de recomendaciones.
  - Desarrollo/justificación de cada pregunta: se evaluará agregarlo después si la recuperación se queda corta.
- **Cómo se fragmenta:** una **pregunta clínica** ("Pregunta 7: …") con todas sus recomendaciones = un fragmento (61 preguntas).
  Si una pregunta es muy larga (> 1 800 caracteres) se subdivide por párrafos con solapamiento, repitiendo el título de
  la pregunta en cada trozo. Resultado: **139 fragmentos** (HTA 12, DM2 34, IC 23, FA 15, ERC 39, NAC 16).
- **Limpieza:** se quitan encabezados/pies repetidos (solo en el borde de la página, para no borrar "Fuerza de la
  recomendación: Fuerte"), números de página y firmas digitales; se unen palabras cortadas con guion.
- **Embeddings:** `intfloat/multilingual-e5-small` (local, gratis, en español; prefijos `passage:` / `query:`).
- **Base vectorial:** ChromaDB en `chroma_db/` (similitud coseno).
- **Cita de cada fragmento:** `<id de la guía>:p<páginas>` (ej. `gpc_ic:p22-23`).
- **Evidencia insuficiente (RF11):** si el fragmento más parecido tiene similitud < `MIN_SIMILARITY`
  (`config/knowledge.py`, hoy 0.80) → `sufficient_evidence = False`. ⚠ **Calibrar** con búsquedas reales.
