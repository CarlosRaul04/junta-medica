"""Parámetros de farmacología: normalización de nombres e interacciones."""

LIST_SEPARATOR = "|"   # separa sinónimos, marcas y nombres en inglés en drugs.csv
EMPTY_VALUE = "—"           # valor de celda que significa "vacío"

# --- Normalización de nombres ---
NAME_SIMILARITY_THRESHOLD = 0.88   # 0-1; por encima se acepta como error de tipeo ("amoxicilna")
MIN_LENGTH_FOR_FUZZY = 5   # nombres más cortos no se comparan por similitud (evita confusiones)
SALTS_TO_IGNORE = [              # se quitan del nombre: "losartán potásico" -> "losartán"
    "potasico", "sodico", "calcico", "clorhidrato", "maleato", "besilato",
    "fumarato", "etexilato", "axetilo", "succinato", "tartrato",
]

# --- Interacciones (DDInter) ---
DDINTER_SEVERITY_MAP = {
    "Major": "severe",
    "Moderate": "moderate",
    "Minor": "mild",
    "Unknown": "unknown",
}
REPORTED_SEVERITIES = ["severe", "moderate"]   # las demás no se muestran (evita falsas alarmas)
HIGHLIGHTED_SEVERITIES = ["severe"]               # RF12: alerta destacada en el informe
