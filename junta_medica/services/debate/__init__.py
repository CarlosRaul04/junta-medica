"""
Debate (sin IA propia: organiza a los agentes y verifica lo que dicen):
    query_builder.py        -> QueryBuilder: consultas al buscador a partir del caso o de la propuesta
    evidence_collector.py   -> EvidenceCollector: corre las herramientas sin IA (medicamentos, interacciones, reglas, guías)
    consensus_calculator.py -> ConsensusCalculator: nivel de acuerdo de una ronda
    citation_verifier.py    -> CitationVerifier: detecta citas inventadas y mide la trazabilidad
    alert_consolidator.py   -> AlertConsolidator: alertas finales (las de la tabla SIEMPRE van)
    abstention_policy.py    -> AbstentionPolicy: decide si el sistema se abstiene (RF11)
    debate_orchestrator.py  -> DebateOrchestrator: rondas, consenso y Médico Jefe
"""
