"""
DebateOrchestrator: dirige el proceso completo de un caso.

1. Herramientas sin IA (EvidenceCollector).
2. Si no hay evidencia en las guías -> abstención (RF11), sin gastar llamadas.
3. Rondas (máx. MAX_ROUNDS): el Clínico propone (ronda 1 sin ver a nadie); Farmacológico y Protocolo revisan.
   Si hay consenso, termina; si no, el Clínico corrige con las objeciones.
4. Alertas finales (las de la tabla siempre van) y Médico Jefe.
5. Verificación de citas (trazabilidad).
"""
import time

from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.debate.case_evidence import CaseEvidence
from junta_medica.models.debate.debate_result import DebateResult
from junta_medica.models.debate.debate_round import DebateRound
from junta_medica.models.pharmacology.severity import Severity
from junta_medica.services.agents.chief_agent import ChiefAgent
from junta_medica.services.agents.clinical_agent import ClinicalAgent
from junta_medica.services.agents.pharmacological_agent import PharmacologicalAgent
from junta_medica.services.agents.protocol_agent import ProtocolAgent
from junta_medica.services.debate.abstention_policy import AbstentionPolicy
from junta_medica.services.debate.alert_consolidator import AlertConsolidator
from junta_medica.services.debate.citation_verifier import CitationVerifier
from junta_medica.services.debate.consensus_calculator import ConsensusCalculator
from junta_medica.services.debate.evidence_collector import EvidenceCollector
from junta_medica.services.debate.query_builder import QueryBuilder
from junta_medica.services.knowledge.retriever import KnowledgeRetriever


class DebateOrchestrator:
    def __init__(self, collector: EvidenceCollector, retriever: KnowledgeRetriever, queries: QueryBuilder,
                 clinical: ClinicalAgent, pharmacological: PharmacologicalAgent, protocol: ProtocolAgent,
                 chief: ChiefAgent, consensus: ConsensusCalculator, abstention: AbstentionPolicy,
                 alerts: AlertConsolidator, citations: CitationVerifier, max_rounds: int,
                 protocol_fragments: int, abstention_message: str):
        self._collector = collector
        self._retriever = retriever
        self._queries = queries
        self._clinical = clinical
        self._pharmacological = pharmacological
        self._protocol = protocol
        self._chief = chief
        self._consensus = consensus
        self._abstention = abstention
        self._alerts = alerts
        self._citations = citations
        self._max_rounds = max_rounds
        self._protocol_fragments = protocol_fragments
        self._abstention_message = abstention_message

    def run(self, case: ClinicalCase) -> DebateResult:
        start = time.perf_counter()
        evidence = self._collector.collect(case)
        if self._abstention.should_abstain(evidence):
            return self._abstain(evidence, start)

        rounds = self._debate(evidence)
        last = rounds[-1]
        allowed = self._allowed_citations(evidence, rounds)
        pharmacological_reviews = [t.output for t in last.reviews if t.role == self._pharmacological.role]
        alerts = self._alerts.consolidate(evidence, pharmacological_reviews, allowed)
        unresolved = self._unresolved_severe_objections(last)
        verdict = self._chief.decide(evidence, rounds, alerts, unresolved, sorted(allowed))
        check = self._citations.check([last.proposal, *last.reviews, verdict], allowed)
        return DebateResult(case.case_id, evidence, tuple(rounds), verdict, False, "", tuple(alerts),
                            tuple(unresolved), check, time.perf_counter() - start)

    def _debate(self, evidence: CaseEvidence) -> list[DebateRound]:
        rounds: list[DebateRound] = []
        previous, feedback = None, None
        for number in range(1, self._max_rounds + 1):
            proposal = self._clinical.propose(evidence.case, evidence.guidelines.chunks, number, previous, feedback)
            protocol_fragments = self._protocol_context(evidence, proposal.output)
            reviews = (
                self._pharmacological.review(evidence, proposal.output, number),
                self._protocol.review(evidence.case, proposal.output, protocol_fragments, number),
            )
            level, consensus = self._consensus.evaluate([t.output for t in reviews])
            rounds.append(DebateRound(number, proposal, reviews, level, consensus))
            if consensus:
                break
            previous = proposal.output
            feedback = [(t.role, t.output) for t in reviews]
        return rounds

    def _protocol_context(self, evidence: CaseEvidence, proposal) -> tuple:
        """
        Fragmentos para el Agente de Protocolo: los que la propuesta CITA (para que pueda verificarlos)
        más los que se encuentran buscando por la propuesta (para ver qué recomienda la guía y falta en el plan).
        """
        cited = {c for d in proposal.diagnoses for c in d.citations} | {c for p in proposal.plan for c in p.citations}
        chunks = {r.chunk.chunk_id: r for r in evidence.guidelines.chunks if r.chunk.citation in cited}
        for r in self._retriever.search_many(self._queries.for_proposal(proposal), self._protocol_fragments).chunks:
            chunks.setdefault(r.chunk.chunk_id, r)
        return tuple(chunks.values())

    def _abstain(self, evidence: CaseEvidence, start: float) -> DebateResult:
        alerts = self._alerts.consolidate(evidence, [], set())
        best = evidence.guidelines.chunks[0].similarity if evidence.guidelines.chunks else 0.0
        reason = f"{self._abstention_message} (similitud máxima con las guías: {best:.3f})"
        check = self._citations.check([], set())
        return DebateResult(evidence.case.case_id, evidence, (), None, True, reason, tuple(alerts), (), check,
                            time.perf_counter() - start)

    @staticmethod
    def _allowed_citations(evidence: CaseEvidence, rounds: list[DebateRound]) -> set[str]:
        """Todo lo que el sistema entregó a algún agente: fragmentos, interacciones y reglas."""
        allowed = {c.chunk.citation for c in evidence.guidelines.chunks}
        allowed |= {f.interaction.citation for f in evidence.interactions}
        allowed |= {f.rule.citation for f in evidence.conditions.findings}
        for r in rounds:
            for turn in (r.proposal, *r.reviews):
                allowed |= set(turn.context_citations)
        return allowed

    @staticmethod
    def _unresolved_severe_objections(last: DebateRound) -> list[str]:
        """Una objeción grave se registra como discrepancia aunque se haya alcanzado el umbral (regla del PLAN)."""
        return [f"{t.role}: {o.detail}" for t in last.reviews for o in t.output.objections
                if o.severity is Severity.SEVERE]
