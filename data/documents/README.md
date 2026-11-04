# Documentos de la base de conocimiento

- `guidelines/`  → PDF de las Guías de Práctica Clínica (se indexan en el RAG).
- `drug_labels/` → fichas técnicas de medicamentos (EMA y CIMA). Se citan desde las reglas e interacciones; **aún no se indexan** en el RAG (no tienen filas en `sections.csv`).
- `catalog.csv` → **registro obligatorio** de cada documento: id, archivo, institución, año, URL de origen y estado.
  El `id` es el que aparecerá en las citas del informe. Un PDF que no está en el catálogo NO se indexa.

Convención de nombres: guías `gpc_<condicion>_<institucion>_<año>.pdf`; fichas técnicas `ft_<dci>.pdf` (minúsculas, sin tildes ni espacios).
Al descargar un archivo: guardarlo con el nombre de la columna `file` y cambiar `status` a `downloaded`.

Estados (`status`): `pending` (falta descargar) · `downloaded` (disponible; se indexa si tiene filas en `sections.csv`) · `alternative` (descargado pero NO se usa, para no duplicar recomendaciones).

## sections.csv — qué páginas se indexan
`document_id, type, start_page, end_page` (páginas del PDF contando desde 1, inclusive).
Hoy solo se indexa la lista de recomendaciones de cada guía (ver `docs/FUENTES.md`, sección 8).
Tras cambiar este archivo o agregar una guía: `python -m scripts.index_guidelines`.
