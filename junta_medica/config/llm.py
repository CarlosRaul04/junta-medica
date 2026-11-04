"""Parámetros de las llamadas a los modelos de lenguaje (los modelos en sí se eligen en el .env)."""

TEMPERATURE = 0.2               # baja = respuestas más estables (lo pide el documento)
JSON_RETRIES = 2                # reintentos si el modelo no devuelve JSON válido
REQUEST_RETRIES = 3             # reintentos ante límite de uso (429) o caída del servidor (5xx)
REQUEST_TIMEOUT_SECONDS = 120

MOCK_MODEL_NAME = "mock"        # nombre de modelo que se registra en modo simulado

# USD por 1 millón de tokens: (entrada, salida). Modelo que no esté aquí = costo 0 (gratuito).
# Si el equipo usa un modelo de pago, agregar su precio para que el costo por caso sea real.
PRICES_USD_PER_MILLION: dict[str, tuple[float, float]] = {}
