"""
Modelos del debate entre agentes:
    stance.py           -> Stance (postura de un revisor: de acuerdo, con observaciones, objeción)
    cited_item.py       -> CitedItem (una afirmación con sus citas)
    proposed_diagnosis.py -> ProposedDiagnosis (diagnóstico del Agente Clínico, con CIE-10)
    clinical_proposal.py  -> ClinicalProposal (lo que propone el Agente Clínico)
    objection.py        -> Objection (objeción de un revisor, con gravedad)
    review.py           -> Review (revisión del Farmacológico o del de Protocolo)
    chief_verdict.py    -> ChiefVerdict (dictamen del Médico Jefe)
    case_evidence.py    -> CaseEvidence (resultado de las herramientas sin IA)
    agent_turn.py       -> AgentTurn (una intervención de un agente: qué dijo + métricas de la llamada, RF14)
    debate_round.py     -> DebateRound (una ronda: propuesta + revisiones + acuerdo)
    final_alert.py      -> FinalAlert (alerta que va al informe)
    citation_check.py   -> CitationCheck (citas válidas e inválidas, trazabilidad)
    debate_result.py    -> DebateResult (todo el proceso de un caso)
"""
