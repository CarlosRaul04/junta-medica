# Instrucciones de los agentes (prompts)

Cada archivo es el "papel" de un agente. Se envía al modelo como mensaje de sistema. Están en español y **se pueden
editar sin tocar código**: el sistema los lee al arrancar.

| Archivo | Agente | Qué ve |
|---|---|---|
| `clinical.md` | Agente Clínico | caso completo + fragmentos de guía del caso + (desde la ronda 2) las objeciones |
| `pharmacological.md` | Agente Farmacológico | medicación, alergias, laboratorio, hallazgos de la tabla y reglas + propuesta clínica |
| `protocol.md` | Agente de Protocolo | resumen del caso + propuesta clínica + fragmentos de guía de esa propuesta |
| `chief.md` | Médico Jefe | todo el debate + alertas del sistema + lista de citas permitidas |

Cada agente ve **distinta información a propósito**, para que no se copien entre sí (ver `docs/PLAN.md`, diseño de agentes).

Reglas para editar:
- **No cambiar los nombres de las claves del JSON** (`diagnoses`, `stance`, `citations`…): el código las lee.
- Si se cambia el formato, actualizar el ejemplo del final de cada archivo y las respuestas de `data/mock_responses/`.
- Al cambiar un prompt, anotar en `docs/BITACORA.md` qué se cambió y por qué (afecta los resultados de la evaluación).
