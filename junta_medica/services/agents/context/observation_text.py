"""Convierte "egfr_ml_min = 27" en "TFG estimada (mL/min/1.73 m²) = 27" (texto para agentes e informe)."""


def readable_observation(observed: str, lab_labels: dict[str, str]) -> str:
    key, separator, value = observed.partition(" = ")
    return f"{lab_labels[key]} = {value}" if separator and key in lab_labels else observed
