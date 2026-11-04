"""Reglas de los casos clínicos (RF01, RF02, RF03)."""

# Según el documento (validar_caso y CP01). "medicacion" es obligatoria.
REQUIRED_FIELDS = ["case_id", "age", "sex", "chief_complaint", "symptoms", "medications"]
OPTIONAL_FIELDS = ["medical_history", "allergies", "lab_results"]
ALLOWED_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS  # cualquier otro campo se rechaza (RF03)

# Tipo esperado de cada campo (ver field_rules.FieldTypes)
FIELD_TYPES = {
    "case_id": "text",
    "age": "integer",
    "sex": "text",
    "chief_complaint": "text",
    "symptoms": "text_list",
    "medical_history": "text_list",
    "allergies": "text_list",
    "medications": "medication_list",
    "lab_results": "dict",
}

# Nombres en español claro para los mensajes al usuario (RNF06)
FIELD_LABELS = {
    "case_id": "código del caso",
    "age": "edad",
    "sex": "sexo",
    "chief_complaint": "motivo de consulta",
    "symptoms": "síntomas",
    "medical_history": "antecedentes",
    "allergies": "alergias",
    "medications": "medicación",
    "lab_results": "resultados de laboratorio",
}

MIN_AGE = 18     # Medicina Interna de adultos
MAX_AGE = 120

# Código del caso: identifica al caso sin datos personales (RF03)
CASE_ID_PATTERN = r"CASO-\d{3}"
CASE_ID_EXAMPLE = "CASO-001"

# Patrones de datos personales que NO pueden aparecer en el caso (RF03, RNF05, Ley 29733)
PERSONAL_DATA_PATTERNS = {
    "DNI": r"\b\d{8}\b",
    "teléfono": r"\b9\d{8}\b",
    "correo electrónico": r"[\w.+-]+@[\w-]+\.[\w.]+",
}

# Resultados de laboratorio reconocidos: clave -> descripción (con unidad).
# Las reglas fármaco–condición usan estas claves, por eso solo se aceptan estas (y con valor numérico).
RECOGNIZED_LAB_TESTS = {
    "egfr_ml_min": "TFG estimada (mL/min/1.73 m²)",
    "creatinine_mg_dl": "Creatinina sérica (mg/dL)",
    "potassium_meq_l": "Potasio sérico (mEq/L)",
    "sodium_meq_l": "Sodio sérico (mEq/L)",
    "glucose_mg_dl": "Glucosa (mg/dL)",
    "hba1c_pct": "Hemoglobina glicosilada HbA1c (%)",
    "inr": "INR",
    "lvef_pct": "Fracción de eyección del ventrículo izquierdo (%)",
    "hemoglobin_g_dl": "Hemoglobina (g/dL)",
    "wbc_mm3": "Leucocitos (/mm³)",
    "crp_mg_l": "Proteína C reactiva (mg/L)",
    "systolic_bp_mmhg": "Presión arterial sistólica (mmHg)",
    "diastolic_bp_mmhg": "Presión arterial diastólica (mmHg)",
    "heart_rate_bpm": "Frecuencia cardiaca (lpm)",
    "spo2_pct": "Saturación de oxígeno (%)",
}

# --- Sección "expected" de los casos simulados (la respuesta correcta; los agentes NUNCA la ven) ---
CASE_TYPES = {                       # tipo -> casos de prueba del documento que cubre
    "common": ["CP04"],              # precisión diagnóstica
    "polypharmacy": ["CP02", "CP03"],  # interacciones y alertas graves
    "atypical": ["CP05"],            # presentación poco frecuente
    "out_of_scope": ["CP07"],        # abstención por evidencia insuficiente
}
EXPECTED_FIELDS = [
    "type", "test_cases", "primary_diagnosis", "acceptable_diagnoses", "interactions",
    "condition_alerts", "should_abstain", "relevant_guidelines", "key_points", "case_source",
]
