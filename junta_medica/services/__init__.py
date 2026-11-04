"""
SERVICIOS: la lógica del sistema. Reciben lo que necesitan por el constructor (no abren archivos ni leen config).

    cases/         -> validar, convertir y cargar casos clínicos
    pharmacology/  -> normalizar nombres, detectar interacciones y reglas fármaco–condición
    knowledge/  -> RAG: limpiar, fragmentar, indexar y buscar en las guías
    llm/           -> hablar con la IA (cliente, costos, lectura del JSON, proveedores)
"""
