"""Parámetros de la base de conocimiento y la recuperación (RAG)."""

# --- Embeddings ---
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"  # multilingüe, corre en CPU, gratis
EMBEDDING_BATCH_SIZE = 16

# --- Base vectorial (ChromaDB) ---
COLLECTION_NAME = "guias_clinicas"

# --- Fragmentación ---
BLOCK_START_PATTERN = r"^\s*Pregunta\s+\d+"   # cada pregunta clínica de la guía = un bloque
MAX_CHUNK_SIZE = 1800                 # caracteres (~450 tokens; e5 admite 512)
CHUNK_OVERLAP = 300                   # caracteres repetidos entre trozos de un bloque largo
MIN_CHUNK_SIZE = 80                   # trozos más cortos se descartan (ruido)

# --- Limpieza del texto extraído del PDF ---
HEADER_RATIO = 0.6     # línea del borde que se repite en >= 60 % de las páginas = encabezado/pie -> se elimina
EDGE_LINES = 4                # cuántas líneas del inicio y del final de cada página se revisan como posible encabezado/pie
LINE_PATTERNS_TO_REMOVE = [
    r"^\s*\d{1,3}\s*$",                     # número de página suelto
    r"(?i)firmado digitalmente",
    r"(?i)^\s*motivo:\s*(soy el autor|doy v)",
    r"(?i)^\s*fecha:\s*\d{2}\.\d{2}\.\d{4}",
]

# --- Recuperación ---
TOP_K = 5                       # fragmentos por consulta
MIN_SIMILARITY = 0.86      # si el mejor fragmento está por debajo: evidencia insuficiente (RF11). Calibrado: dentro de alcance 0.879–0.888, fuera de alcance 0.843 (ver BITACORA)
