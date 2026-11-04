# Plan del proyecto — Sistema Multiagente de Segunda Opinión Médica

> Proyecto final de Agentes Inteligentes (Grupo 1). Se rehace **desde cero en Python** siguiendo el documento del curso.
> El código C# del amigo (AbogatoIA) queda solo como **referencia** (ver Anexo al final).

## Estado actual
- [x] Revisión completa del código C# original
- [x] Análisis crítico del documento del curso
- [x] Decisión de stack: **Python + Streamlit + ChromaDB + SQLite + ReportLab**
- [x] ~~Decisión de modelos: OpenAI de pago~~ → **cambio (2026-11-04): presupuesto cero.** El sistema acepta cualquier proveedor compatible con OpenAI (OpenRouter `:free`, Groq, Gemini, Ollama). **La elección de los modelos gratuitos queda a cargo del equipo** (ver README → "Elegir el proveedor y los modelos de IA")
- [x] Editor: **VS Code**
- [x] Fase 0 — Entorno (Python 3.12 + .venv) y estructura base SOLID: paquete `junta_medica/` (ver ARQUITECTURA.md), cliente de IA con proveedor genérico compatible con OpenAI + simulado, pruebas
- [ ] **Equipo:** elegir proveedor gratuito y modelos (AGENT_MODEL, CHIEF_MODEL), probarlos con un caso y anotarlos en BITACORA
- [ ] Revocar en el panel de OpenAI la admin key que estaba en el .env (ya se quitó del archivo)
- [ ] Fase 1 — Datos (detalle en **[FUENTES.md](FUENTES.md)**)
  - [x] Elegir las 6 enfermedades: HTA, DM2, insuficiencia cardiaca, fibrilación auricular, ERC, neumonía
  - [x] Descargar las 6 guías (INS y EsSalud) y registrarlas en `data/documents/catalog.csv`
  - [x] Descargar CIE-10 OPS en español (`data/references/`)
  - [x] Catálogo de 45 medicamentos elegidos desde las guías (`data/pharmacology/drugs.csv`)
  - [x] CIE-10 completa (11 399 códigos con página) → `data/references/icd10.csv`
  - [x] Tabla de interacciones fármaco–fármaco desde DDInter (686 pares, 44 graves)
  - [x] Interacciones de dabigatrán, finerenona y gliclazida desde fichas técnicas (25 pares) → `label_interactions.csv`
  - [x] Tabla de reglas fármaco–condición: 40 reglas citadas a guía o ficha técnica y página (`condition_rules.csv`)
  - [x] Reglas que no están en las guías (AINE, digoxina, dabigatrán, finerenona, ivabradina, levofloxacino) desde 9 fichas técnicas EMA/CIMA
  - [ ] Metformina con TFG 30–45 (reducción de dosis)
  - [ ] (Opcional) Indexar las secciones 4.2–4.5 de las fichas técnicas en el RAG
  - [x] Sinónimos y marcas en el catálogo (marca/sinónimo → DCI)
  - [x] 18 casos simulados en JSON (`data/cases/`), con sección `expected` validada por pruebas
- [ ] Fase 2 — Herramientas sin LLM
  - [x] Caso clínico: modelo, validador (RF02, RF03, CP01) y cargador — `junta_medica/services/cases/`
  - [x] Normalizador de medicamentos (exacto, sinónimo, marca, aproximado) — `junta_medica/services/pharmacology/drug_normalizer.py`
  - [x] Verificador de interacciones por pares (CP02, CP03) — `junta_medica/services/pharmacology/interaction_checker.py`
  - [x] Verificador de reglas fármaco–condición (laboratorio, edad, antecedente) — `junta_medica/services/pharmacology/condition_checker.py`
  - [x] Laboratorio estandarizado: claves reconocidas y valores numéricos (validador del caso)
  - [x] RAG: limpieza, fragmentación por pregunta clínica, indexación (ChromaDB + e5) y búsqueda con umbral de evidencia
  - [ ] RAG: indexar en la PC con el modelo real (`python -m scripts.index_guidelines`) y **calibrar el umbral** de evidencia
  - [ ] RAG: evaluar si conviene indexar también la justificación de cada pregunta
  - [x] Verificador de citas / abstención (`CitationVerifier`, `AbstentionPolicy`)
- [x] Fase 3 — Agentes LLM + orquestador del debate + Médico Jefe (probado con IA simulada y con IA falsa guionada)
  - [x] 4 agentes con prompts editables en `data/prompts/` · cada agente ve información distinta
  - [x] Rondas con consenso (umbral 0,67; una objeción GRAVE bloquea el consenso) · máx. 3 rondas
  - [x] Abstención sin gastar llamadas (RF11) · alertas de la tabla siempre en el resultado (RF12)
  - [x] Verificación de citas inventadas y trazabilidad · resultado completo en JSON (`output/debates/`, RF14)
  - [ ] **Equipo:** probar con modelos reales gratuitos (`MOCK_MODE=0`) y ajustar los prompts
  - [ ] Validar el código CIE-10 que propone cada agente contra `icd10.csv` (lo hará la evaluación)
- [ ] Fase 4 — Interfaz Streamlit + informe PDF + historial (SQLite) + usuarios/roles
- [ ] Fase 5 — Script de evaluación (métricas) + baseline + experimentos de configuración
- [ ] Fase 6 — Actualizar el documento (secciones 4.3, 4.4.3, 4.4.4 con resultados)
- [ ] Fase 7 (EVOLUCIÓN, después de tener todo funcionando) — Herramientas para agentes (*function calling*)

## Evolución futura: herramientas para los agentes (function calling) — NO hacer todavía
Decisión (2026-11-04): primero se termina el sistema completo con **pipeline** (el orquestador ejecuta las
herramientas y entrega los resultados a los agentes). Function calling se evalúa después, como mejora.
Propuesta registrada (enfoque híbrido):
1. **Herramientas obligatorias** (siempre, por el orquestador): validar, normalizar, interacciones, reglas fármaco–condición, RAG.
   Son la red de seguridad: la detección de interacciones graves no puede depender de que el modelo "decida" revisarlas.
2. **Herramientas a elección del agente**: Clínico → `search_guidelines`, `buscar_cie10`; Farmacológico → `verificar_interacciones`,
   `evaluar_condiciones`, `search_guidelines`; Protocolo → `search_guidelines`; Jefe → ninguna.
3. Arquitectura: `interfaces/herramienta.py` + `services/scripts/` (una clase por herramienta que envuelve un servicio
   existente) + ciclo de herramientas en `LLMClient`. Límite configurable de llamadas por agente y ronda. Registro de cada llamada (RF14).
Para que la evolución sea fácil: los servicios ya son independientes y reciben todo por el constructor (se podrán envolver sin cambiarlos).


## Documentación del proyecto
- [BITACORA.md](BITACORA.md) — qué se hizo, cuándo y por qué (leer primero si te unes al proyecto)
- [FUENTES.md](FUENTES.md) — enfermedades, guías, medicamentos, interacciones, casos
- [ARQUITECTURA.md](ARQUITECTURA.md) — estructura de carpetas y reglas de código

## Estructura y reglas de código
Ver **[ARQUITECTURA.md](ARQUITECTURA.md)** — **arquitectura en capas** (config, modelos, interfaces, repositorios, servicios, fábricas), igual que el proyecto C# de referencia; reglas SOLID; un archivo = una clase; datos fuera del código.

## Interfaz
- **Streamlit** (lo dice el documento). Ya NO se hará frontend en React (decisión anterior descartada).
- Pantallas: Login · Registro de caso (formulario o JSON) · Resultado (tarjeta por agente + dictamen + alertas destacadas + disclaimer) · Historial (filtros + CSV) · Descarga PDF.

## Fuentes de conocimiento (ajustado al documento)
- Núcleo: **RAG local** con 6 GPC del INS y EsSalud (ver [FUENTES.md](FUENTES.md)) + fichas farmacológicas, en español, en ChromaDB.
- **Tabla de interacciones determinista** construida desde una fuente independiente de los casos (cada par con su cita).
- **CIE-10** para normalizar diagnósticos y comparar en las métricas.
- Diccionario de medicamentos: marca/sinónimo → DCI en español.
- Extras OPCIONALES (solo si sobra tiempo): PubMed (búsqueda en inglés, filtros, resúmenes, verificación de PMIDs), openFDA, RxNorm. Ver Anexo.


---

# ✅ DECISIONES TOMADAS
- **Se rehace desde cero en Python** (según el documento). El código C# queda solo como referencia.
- Proveedor de modelos: **cualquiera compatible con OpenAI**, elegido por el equipo en el `.env`. Presupuesto: **cero** (modelos gratuitos).

## Diseño de agentes (APROBADO)
| Agente | ¿LLM? | Modelo | Recibe | Devuelve |
|---|---|---|---|---|
| Validador del caso | No (código) | — | Caso JSON | Válido / campos faltantes |
| Normalizador de medicamentos | No (diccionario) | — | Nombres comerciales | DCI en español / "no reconocido" |
| Recuperador RAG | No (embeddings) | multilingual-e5 local | Caso | Fragmentos con id y fuente |
| Verificador de interacciones | No (tabla de reglas) | — | Medicamentos | Pares con severidad + fuente |
| **Agente Clínico** | Sí | AGENT_MODEL | Caso + fragmentos GPC + CIE-10 | Top-3 dx (CIE-10), justificación, plan, citas |
| **Agente Farmacológico** | Sí | AGENT_MODEL | Medicación, alergias, labs renal/hepático, hallazgos de la tabla, fichas, plan del clínico | Alertas + postura sobre el plan + citas |
| **Agente de Protocolo** | Sí | AGENT_MODEL | Plan del clínico + fragmentos GPC | Cumplimiento/desvíos + postura + citas |
| Orquestador | No (código) | — | Posturas | Acuerdo, nueva ronda o cierre |
| **Médico Jefe** | Sí | CHIEF_MODEL | Todo el debate | Dictamen, nivel de acuerdo, discrepancias, alertas, o abstención |
| Verificador de citas | No (código) | — | Dictamen | Citas válidas / "evidencia insuficiente" |

Reglas clave:
- Ronda 1: el Clínico propone SIN ver a nadie (ni las alertas de la tabla); Farmacológico y Protocolo revisan.
- Rondas 2–3: el Clínico corrige según objeciones; los revisores re-evalúan.
- Postura: `de_acuerdo` | `de_acuerdo_con_observaciones` | `objecion` (con gravedad y cita).
- Una objeción de seguridad grave **bloquea el consenso** (aunque el nivel llegue a 0,67) y, si sigue en la última ronda, se registra como discrepancia.
- La tabla de interacciones es la fuente de verdad: el LLM puede AGREGAR alertas con cita, nunca QUITAR una alerta grave de la tabla.
- Cada agente con contexto distinto (no todos ven todo) para que no se "copien".

## Estimación de costo (HISTÓRICO: plan original con OpenAI de pago, ya no aplica)
- gpt-6-luna: $0.10 entrada / $0.50 salida por 1M tokens. gpt-6.1-terra: $1 / $5.
- Supuesto por llamada: ~4 000 tokens de entrada, ~1 500 de salida (incluye razonamiento). Máx. 10 llamadas por caso.
- Todo con Luna: ~US$ 0.012 por caso. Agentes Luna + Jefe Terra: ~US$ 0.03 por caso. Todo Terra: ~US$ 0.12 por caso.
- Evaluación completa (20 casos × 3 ejecuciones = 60) con la mezcla: ~US$ 2. Desarrollo con Luna: centavos.
- Medir el costo real con el `usage` de cada respuesta y registrarlo. Poner límite de gasto en el panel de OpenAI.
- Verificar en la documentación si gpt-6-luna/terra aceptan `temperature` (el documento pide 0.2); si no, usar `reasoning.effort` bajo y justificarlo.
- Experimento extra para el informe: comparar configuración "todo Luna" vs "Luna + Jefe Terra" vs baseline de 1 sola llamada.

---

# 📄 Análisis crítico del documento del curso (TF Grupo 1)

## ⚠️ Decisión 0 (bloqueante): el stack del documento ≠ el código
- Documento: **Python + Streamlit + ChromaDB + SQLite + embeddings multilingües + ReportLab**, orquestador propio.
- Código del amigo: **C# / ASP.NET + SQL Server + OpenRouter**, sin RAG, sin base vectorial, sin PDF.
- Opciones: (A) rehacer en Python según el documento; (B) quedarse en C# y reescribir la sección 4.3/4.4.3 del documento.
- Lo reutilizable del código C# es poco (auth, clientes PubChem/PubMed); el debate y el RAG hay que hacerlos de cero en ambos casos.
- DECISIÓN PENDIENTE DEL EQUIPO.

## Lo que el documento exige y el código NO tiene
- RAG con base vectorial (GPC MINSA + fichas farmacológicas + CIE-10) — es el Objetivo 1.
- Tabla de interacciones determinista (diagrama 3) — el código no tiene nada.
- Rondas de debate con umbral de consenso (MAX_ROUNDS=3, UMBRAL=0.67).
- Abstención por evidencia insuficiente (RF11).
- Informe PDF (RF13), trazabilidad por agente (RF14), disclaimer (RF17).
- Roles de usuario (RF15), historial + CSV (RF16).
- 15–20 casos simulados en JSON con diagnóstico correcto e interacciones esperadas.

## Lo que el código tiene y el documento NO pide (recortar)
- Planes FREE/PRO y saldo de tokens, login con Google, Zoho CRM, Plan B Gemini, lectura de PDFs del usuario.
- PubChem/PubMed/openFDA/RxNorm no aparecen en el documento: el documento usa RAG local con documentos acotados. PubMed queda como extra opcional.

## Huecos del diseño del documento (hay que definirlos)
- **"Acuerdo" no está definido**: `calcular_acuerdo` cuenta `postura == 'de acuerdo'`, pero ¿de acuerdo con qué? Farmacológico y Protocolo no diagnostican. Propuesta: el Clínico propone (top-3 dx con CIE-10 + plan); Farmacológico y Protocolo revisan y responden `de acuerdo` / `objeción` con motivo y cita; el Clínico corrige en la ronda siguiente. Acuerdo = proporción sin objeciones bloqueantes.
- **Abstención**: definir regla concreta (ej. similitud de recuperación < umbral, o el dictamen sin citas válidas).
- **Trazabilidad ≥90 %**: cada afirmación debe llevar `fuente_id`/`fragmento_id`; el código verifica que el id esté entre los fragmentos recuperados (automático) + revisión manual de una muestra.
- **Riesgo de evaluación circular**: si la tabla de interacciones se arma con las mismas interacciones esperadas de los casos, la sensibilidad del 90 % es trivial. Armarla desde una fuente independiente (y citar cada par) e incluir pares que no están en los casos.
- **Normalización de medicamentos**: la tabla usa nombres en español (warfarina); hace falta diccionario de sinónimos/marcas → DCI en español.
- **RNF03 reproducibilidad**: exige modelos fijos y temperatura baja → incompatible con `openrouter/auto` y con modelos `:free` que rotan.
- **Costo/cuota**: ~10 llamadas por caso × 20 casos × 3 ejecuciones (consistencia) ≈ 600 llamadas + línea base → supera las 50 req/día gratis de OpenRouter.

## Lo que vale la pena AGREGAR
- **Script de evaluación automática**: corre todos los casos y calcula las 6 métricas → tabla para la sección Pruebas.
- **Línea base (baseline)**: comparar "1 sola IA con un prompt" vs "sistema multiagente con debate". Justifica todo el proyecto. (El `GeminiService` actual es literalmente esa línea base.)
- Salida JSON con esquema validado por agente (reintento si el JSON es inválido).
- Registro de tiempo y costo por caso.

## Correcciones al documento
- Tabla 4.3: dice "CrewAI / LangGraph" pero el texto dice "orquestador propio" → alinear.
- Introducción menciona CIE-11 y "vademécums"; luego solo CIE-10 → unificar.
- 2.3 dice que recibe "notas de evolución"; RF01 no las incluye → unificar.
- Tablas de hardware por integrante con "[completar]".
- RF15: evaluar si "revisor" es necesario (puede bastar médico + administrador).

---

# 📎 ANEXO — Proyecto C# original (solo referencia)

## Notas del código C# original

Contexto: el proyecto se hizo para **abogados** (AbogatoIA: 3 IAs debaten y un Juez da el veredicto).
Ahora se está adaptando al **tema médico** (segunda opinión médica multiagente).

---

## 🔴 Urgente / Seguridad
- [ ] **Clave de OpenRouter expuesta** del amigo: está en `AbogatoIA/appsettings.json` y escrita a fuego en `Services/Implementation/GeminiService.cs` (constructor). Reemplazar por clave propia y quitar la clave del código.
- [ ] Mover claves a *User Secrets* (clic derecho en AbogatoIA → "Administrar secretos de usuario") en vez de `appsettings.json`.
- [ ] Clave JWT de `appsettings.json` es de desarrollo; cambiarla si se publica.

## 🟠 El debate multiagente (núcleo del proyecto)
- [ ] **No existe endpoint para el debate**: `OpenRouterService.ProcesarConsulta` / `ConsultarConDebateLegal` no lo llama ningún controller. Crear un controller (ej. `DebateController`).
- [ ] **Los 3 modelos NO tienen roles distintos**: los 3 reciben exactamente el mismo mensaje del usuario, sin instrucción de sistema. Solo cambia el modelo. Hay que darle a cada uno un rol/prompt propio.
- [ ] **No hay debate real**: los 3 responden en paralelo sin ver lo que dicen los otros; solo el Juez los lee. Considerar una 2ª ronda donde cada agente critica a los demás.
- [ ] El "sistema médico" actual (`GeminiService.EvaluarCasoClinicoAsync`) es **una sola llamada a una IA** que finge 4 roles. Convertirlo en llamadas separadas por agente (Clínico, Farmacológico, Protocolo → Médico Jefe).
- [ ] Unificar: hoy hay dos flujos (debate legal en `OpenRouterService` y caso médico en `GeminiService`). Quedarse con uno médico.
- [ ] Verificar que los modelos gratuitos sigan existiendo en OpenRouter: `google/gemma-3-27b-it:free`, `arcee-ai/trinity-mini:free`, `stepfun/step-3.5-flash:free`, juez `openrouter/aurora-alpha`. Ponerlos en `appsettings.json` en vez de en el código.
- [ ] `LlamarModelo` traga los errores (`errorDetail` se lee pero no se registra). Loguear el detalle.

## 🟡 Cambiar de "abogado" a "médico"
- [ ] Prompt del Juez: "Abogado Senior en Perú" → "Médico Jefe / Junta médica".
- [ ] `GeminiClient._systemInstruction`: dice "Eres 'Abogato IA', asistente legal" → cambiar a asistente médico.
- [ ] Nombres: `ConsultarConDebateLegal`, `AbogatoPolicy` (CORS), `X-Title: Abogato IA`, título de Swagger "Abogato IA API v1", base de datos `AbogatoDb`, nombre de la solución.
- [ ] `GeminiController` / `GeminiService` se llaman "Gemini" pero usan OpenRouter → renombrar (ej. `CasoClinicoController`).
- [ ] CORS apunta a `https://abogatoai.vercel.app` (frontend del amigo) → poner el propio.
- [ ] Agregar aviso/disclaimer: "no reemplaza la opinión de un médico".

## 🔵 Models — sin usar o por mejorar
- [ ] `GeminiResponse.cs` (+ GeminiCandidate/Content/Part): **sin usar** (la librería de Google ya da el texto). Borrar.
- [ ] `SaldoUsuarioDto.cs`: **sin usar**; `AuthController.ObtenerSaldo` devuelve un objeto anónimo con los mismos campos. Usar el DTO.
- [ ] `DocumentAnalysisRequest.cs`: **sin usar**, función a medias de subir PDFs. Idea médica: subir resultados de laboratorio/historia clínica en PDF.
- [ ] `ApplicationUser.NombreCompleto`: **sin usar**. Pedirlo en el registro o quitarlo.
- [ ] `CasoClinicoDto`: sin validaciones (`[Required]`, rango de edad, etc.).
- [ ] Falta un DTO de entrada para el debate (si se usa texto libre) o reutilizar `CasoClinicoDto`.
- [ ] `Models.csproj` trae `JwtBearer` sin necesitarlo.

## 🔵 Services — sin usar o por mejorar
- [ ] `PdfReaderService`: registrado en `Program.cs` pero **ningún controller lo usa**.
- [ ] `GeminiClient` (Plan B cuando no hay saldo): requiere `Gemini:ApiKey` en configuración, que **no existe** → fallaría.
- [ ] `ZohoCrmService` / `ZohoController` (ruta `api/Crm`): requiere `Zoho:ClientId/ClientSecret/RefreshToken` que **no existen**. Decidir si se quita (no tiene relación con lo médico).
- [ ] `PubChemService` y `PubMedService` ✅ útiles para lo médico; mantener.
- [ ] `OpenRouterService` crea su propio `new HttpClient()`; mejor registrarlo con `AddHttpClient` como los demás.

## 🔵 API / Controllers
- [ ] `WeatherForecastController.cs` y `WeatherForecast.cs`: plantilla de Visual Studio, **borrar**.
- [ ] `AbogatoIA.http`: solo prueba weatherforecast; actualizar con los endpoints reales.
- [ ] `GeminiController.evaluar-caso` **no pide login** (`[Authorize]`) ni descuenta tokens; el control de saldo solo está en el flujo legal.
- [ ] Login con Google requiere `Google:ClientId` que **no existe**.
- [ ] Límite gratis `50` repetido en `AuthController` y `OpenRouterService` → ponerlo en configuración.
- [ ] Swagger no tiene botón "Authorize" para JWT configurado (`AddSwaggerGen` sin esquema Bearer).

## 🔵 Base de datos
- [ ] BD local: `(localdb)\mssqllocaldb`, base `AbogatoDb`. Crear con `Update-Database -Project Persistence -StartupProject AbogatoIA`.
- [ ] Solo guarda usuarios. Recomendado: tabla de **historial de cases/consultas** (caso, respuestas de cada agente, veredicto, fecha, usuario) — útil para mostrar el debate y para el informe del curso.

## 🔵 Despliegue
- [ ] Perfiles de Azure en `Properties/ServiceDependencies/` son del amigo; crear los propios si se publica (Azure App Service + Azure SQL).
- [ ] No hay frontend en este repo.

---

## 📌 Diseño propuesto para el debate médico (hacer después de revisar módulos)
1. `LlamarModelo` debe aceptar una **instrucción de sistema** (rol) además del mensaje:
   `messages = [ {role:"system", content: rol}, {role:"user", content: caso} ]`.
2. Tres agentes separados, cada uno con rol propio (y si se puede, modelo distinto):
   - **Clínico**: top-3 diagnósticos presuntivos con justificación.
   - **Farmacológico**: interacciones, alergias, contraindicaciones (con datos de PubChem).
   - **Protocolo/Auditoría**: cumplimiento de guías clínicas con citas de PubMed.
3. (Opcional) **Ronda 2 de debate**: cada agente lee las respuestas de los otros y critica/corrige.
4. **Médico Jefe**: sintetiza, resuelve discrepancias y emite dictamen final (JSON).

## 📌 Tabla de historial de casos clínicos (CONFIRMADO: se va a hacer)
1. Crear `Models/ClinicalCase.cs` (entidad): Id, UsuarioId, Fecha, datos del caso (o JSON del `CasoClinicoDto`),
   RespuestaClinico, RespuestaFarmacologico, RespuestaProtocolo, DictamenJefe.
2. Agregar `public DbSet<ClinicalCase> Casos { get; set; }` en `Persistence/ApplicationDbContext.cs`.
3. `Add-Migration AgregarCasos -Project Persistence -StartupProject AbogatoIA`
4. `Update-Database -Project Persistence -StartupProject AbogatoIA`
5. Crear `ICasoRepository` / `CasoRepository` (guardar caso, listar historial por usuario).
6. Endpoint para ver el historial del usuario.

## 🔵 Services — hallazgos adicionales (revisión del módulo)
- [ ] **`OpenRouterService` no se puede crear sin `Gemini:ApiKey`**: su constructor pide `IGeminiClient`, y el constructor de `GeminiClient` lanza excepción si falta la clave. O sea, el futuro endpoint del debate fallará al arrancar aunque no se use el Plan B. Agregar la clave o hacer el Plan B opcional.
- [ ] **PubMed se busca en español** (`Motivo` + `Sintomas`), pero PubMed indexa en inglés → pocos o ningún resultado. Traducir términos (o pedirle a una IA que genere la búsqueda en inglés / términos MeSH).
- [ ] **PubChem necesita nombres en inglés** (`aspirin`, no `aspirina`); si no, devuelve error y queda "No se encontraron datos".
- [ ] PubChem devuelve JSON crudo que se pega tal cual en el prompt; conviene extraer solo los campos útiles.
- [ ] `GeminiService` usa modelo `openrouter/auto` (elige solo, puede ser de pago) — fijar modelo en configuración.
- [ ] `GeminiService` no valida que la respuesta sea JSON válido (solo quita ```json).
- [ ] El archivo `Services/Interfaces/PubChemService.cs` contiene `IPubChemService` → renombrar a `IPubChemService.cs`.
- [ ] Paquete `Mscc.GenerativeAI` en `AbogatoIA.csproj` parece no usarse (GeminiClient usa `Google_GenerativeAI`).
- [ ] `ZohoCrmService` pide un token nuevo a Zoho en cada llamada y modifica `DefaultRequestHeaders` del HttpClient compartido.

## 🔵 API (AbogatoIA) — hallazgos de la revisión del módulo
- [ ] **Swagger**: por `RoutePrefix = string.Empty` (Program.cs) la página real es `http://localhost:5063/index.html` (comprobado). `launchSettings.json` tiene `"launchUrl": "swagger"` → abre una página que no existe. Cambiar `launchUrl` a `"index.html"` en los 3 perfiles (o quitar el `RoutePrefix` para que vuelva a ser `/swagger`).
- [ ] Namespaces inconsistentes: `GeminiController` y `PubChemController` usan `namespace Controllers`; `AuthController` y `CrmController` usan `AbogatoIA.Controllers`. Unificar.
- [ ] El archivo `ZohoController.cs` contiene la clase `CrmController` (ruta `api/Crm`). Nombre de archivo ≠ clase.
- [ ] `CrmController.CrearClienteEnZoho` recibe los datos por query string en vez de un DTO en el body.
- [ ] Los DTOs `RegisterDto`, `LoginDto`, `GoogleLoginDto` están dentro de `AuthController.cs` → moverlos a Models.
- [ ] `GeminiController` no tiene `[Authorize]`: cualquiera sin login puede usarlo y gastar créditos de OpenRouter.
- [ ] Swagger se publica siempre (también en producción); está bien para el curso, pero tenerlo en cuenta.

## (OBSOLETO) Frontend React — reemplazado por Streamlit
- React + Vite en una carpeta `frontend/` dentro del MISMO repositorio (CORS ya permite `http://localhost:5173`).
- Hacerlo DESPUÉS de que el debate funcione en Swagger.
- El backend debe devolver la respuesta de cada agente por separado (no solo el veredicto) para mostrar el debate.
- Pantallas mínimas: Login/Registro · Formulario de caso clínico · Resultado (tarjeta por agente + dictamen del Médico Jefe) · Historial.

## 📌 Fuentes médicas — rediseño (CONFIRMADO: se va a corregir)

### Problemas actuales
- Medicamentos se envían tal cual los escribe el usuario (español, marca, errores de tipeo) → PubChem falla y se ignora en silencio.
- No se valida que el medicamento exista ni se avisa al usuario.
- PubChem solo da **fórmula, peso molecular e IUPAC**: datos químicos que NO sirven para evaluar interacciones/contraindicaciones.
- PubMed: se busca `Motivo + todos los síntomas` en español, todo junto → búsqueda demasiado específica, pocos o ningún resultado, y sin filtros de calidad.
- Solo se traen **títulos** de PubMed (no resúmenes): la IA no puede "usar la evidencia", solo ve títulos → riesgo de inventar respaldo.
- No se verifica que las citas del dictamen final (PMIDs) sean las que realmente se recuperaron.
- No se manda `api_key`/`tool`/`email` a NCBI (límite 3 req/s sin clave, 10 con clave).

### Medicamentos — flujo propuesto
1. **Normalizar**: el usuario escribe "paracetamol", "Panadol", "amoxicilina" → convertir a nombre genérico en inglés (INN) — p.ej. agente/llamada IA "normalizador" con salida JSON, o diccionario propio.
2. **Validar** con **RxNorm** (NLM, gratis, sin clave): `approximateTerm` / `drugs` para confirmar que existe y obtener RxCUI y genérico. (OJO: la API de *interacciones* de RxNav fue DESCONTINUADA en enero 2024; RxNorm de nombres sigue activa.)
3. Si no se valida → marcar "NO VERIFICADO", avisar al usuario y no enviar basura a los agentes.
4. **Datos clínicos reales** desde **openFDA Drug Label API** (`https://api.fda.gov/drug/label.json`, gratis): `contraindications`, `drug_interactions`, `warnings`, `boxed_warning`, `adverse_reactions`. Resumir/recortar antes de pasarlo al agente Farmacológico.
5. PubChem puede quedar como dato secundario (o quitarse).
6. Devolver al frontend la lista de medicamentos con su estado (verificado / no verificado / nombre normalizado).

### PubMed — flujo propuesto
1. **Generar la búsqueda en inglés** (IA o diccionario): motivo/diagnóstico principal en inglés, idealmente términos MeSH.
2. Armar query estructurada: `(<término>[MeSH Terms] OR <término>[tiab])` + filtros: `humans[mh]`, últimos ~5-10 años, tipos `review[pt] OR meta-analysis[pt] OR practice guideline[pt] OR systematic review`, `sort=relevance`.
3. Si 0 resultados → reintentar con query más amplia (sin filtros / menos términos).
4. Traer **resúmenes** con `efetch` (`rettype=abstract`), no solo títulos.
5. (Opcional) Que un agente filtre por relevancia antes de dárselos a los demás.
6. En el prompt: "solo puedes citar estos PMIDs". Después **validar** que cada PMID del dictamen esté en la lista recuperada; si no, marcarlo/eliminarlo.
7. Agregar `api_key` (cuenta NCBI), `tool` y `email` en la configuración; respetar límite de requests.
8. Mostrar en el frontend los artículos con enlace `https://pubmed.ncbi.nlm.nih.gov/<PMID>/`.
