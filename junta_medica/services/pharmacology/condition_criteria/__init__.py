"""
Criterios de las reglas fármaco–condición (implementan interfaces.condition_criterion.ConditionCriterion):
    comparison.py           -> comparar(): aplica el operador (<, <=, >, >=) de la regla
    lab_criterion.py  -> LabCriterion  (ej. egfr_ml_min < 30)
    age_criterion.py         -> AgeCriterion         (ej. edad > 60)
    history_criterion.py  -> HistoryCriterion  (ej. antecedente de insuficiencia cardiaca)
Para agregar un tipo nuevo: crear su archivo aquí y registrarlo en factories/pharmacology_factory.py.
"""
