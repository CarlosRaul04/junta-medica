# Junta Médica IA

Sistema multiagente con RAG y debate colegiado para el apoyo en segundas opiniones médicas en Medicina Interna (proyecto académico, Agentes Inteligentes 2026-1).

> Herramienta de apoyo a la decisión: no reemplaza el criterio médico. Solo usa casos simulados.

## Primeros pasos (para el equipo)
Requisitos: **Python 3.12** y Git. En Windows, usar Git Bash.

```bash
git clone <url-del-repositorio> junta-medica-ia
cd junta-medica-ia
py -3.12 -m venv .venv
source .venv/Scripts/activate        # Git Bash  (PowerShell: .venv\Scripts\activate)
pip install -r requirements.txt      # tarda: instala PyTorch y el modelo de búsqueda
cp .env.ejemplo .env                 # luego completar el .env (ver abajo)
python -m pytest                     # todo debe pasar
python -m scripts.index_guidelines   # una vez: arma la base de búsqueda (descarga ~470 MB la primera vez)
python -m scripts.run_case CASO-008  # corre la junta médica sobre un caso
```

**El `.env` es personal y NUNCA se sube a Git** (está en `.gitignore`). Para probar sin IA real: `MOCK_MODE=1`.
Para usar IA real, cada integrante crea **su propia clave gratuita** en https://openrouter.ai/keys y la pone en
`LLM_API_KEY` (cada clave gratuita da 50 llamadas por día; un caso usa de 4 a 10). Configuración probada:
```
MOCK_MODE=0
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-...
AGENT_MODEL=nvidia/nemotron-3.5-super-vl:free
CHIEF_MODEL=nvidia/nemotron-3.5-super-vl:free
```
Cada resultado se guarda completo en `output/debates/` (no se sube a Git).

## Elegir el proveedor y los modelos de IA
El sistema funciona con **cualquier proveedor compatible con la API de OpenAI**, incluidos los gratuitos
(OpenRouter con modelos `:free`, Groq, Google Gemini, Ollama en tu PC). Todo se configura en el `.env`, sin tocar código:

| Variable | Qué es |
|---|---|
| `MOCK_MODE` | `1` = respuestas de ejemplo (sin internet). `0` = usa el proveedor real |
| `LLM_BASE_URL` | URL del proveedor (vacío = OpenAI oficial) |
| `LLM_API_KEY` | Clave del proveedor (Ollama no necesita) |
| `AGENT_MODEL` / `CHIEF_MODEL` | Modelo de los 3 agentes / del Médico Jefe |
| `CLINICAL_MODEL`, `PHARMACOLOGICAL_MODEL`, `PROTOCOL_MODEL` | Opcional: un modelo distinto por agente |
| `LLM_JSON_MODE`, `LLM_MERGE_SYSTEM_PROMPT` | Compatibilidad, cambiar solo si el proveedor da error |

En `.env.ejemplo` están las URLs de cada proveedor. Consejos para modelos gratuitos:
- Tienen **límite de solicitudes por minuto**. Un caso hace de 4 a 10 llamadas; el sistema reintenta solo ante el error 429.
- Elegir modelos que sigan bien instrucciones en **español** y devuelvan **JSON**. Si responden texto suelto, el sistema
  intenta extraer el JSON y reintenta hasta 2 veces.
- Los modelos gratuitos cambian seguido: anotar en `docs/BITACORA.md` cuál se usó en cada prueba.

## Comandos útiles
```bash
python -m scripts.run_case CASO-008                      # corre la junta médica completa sobre un caso
python -m scripts.index_guidelines                       # construye la base vectorial (chroma_db/)
python -m scripts.search_guidelines "consulta clínica"  # prueba el buscador
python -m scripts.build_interaction_table         # regenera interactions.csv (DDInter + fichas técnicas)
python -m scripts.build_icd10_table                # regenera la tabla CIE-10 desde el PDF de la OPS
```

## Pruebas
```bash
python -m pytest -v
```

## Alcance
Cubre 6 enfermedades de Medicina Interna: hipertensión arterial, diabetes mellitus tipo 2, insuficiencia cardiaca crónica,
fibrilación auricular, enfermedad renal crónica y neumonía adquirida en la comunidad. Base de conocimiento: guías de práctica
clínica del INS y EsSalud (IETSI).

## Documentación (leer en este orden)
1. [Bitácora](docs/BITACORA.md) — qué se hizo y por qué
2. [Plan del proyecto](docs/PLAN.md) — estado por fases, decisiones y pendientes
3. [Fuentes](docs/FUENTES.md) — enfermedades, guías descargadas, medicamentos, interacciones y casos
4. [Arquitectura y reglas de código (SOLID)](docs/ARQUITECTURA.md)
