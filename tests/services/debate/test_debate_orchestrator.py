"""Debate de punta a punta con una IA falsa (respuestas guionadas) y el buscador de prueba (sin descargar modelos)."""
import json

import pytest

from junta_medica.factories.case_factory import create_case_loader
from junta_medica.factories.debate_factory import create_debate_orchestrator, create_debate_result_repository
from junta_medica.factories.knowledge_factory import create_indexer
from junta_medica.interfaces.llm_provider import LLMProvider
from junta_medica.models.llm.llm_response import RawLLMResponse
from junta_medica.services.knowledge.retriever import KnowledgeRetriever
from junta_medica.services.llm.cost_calculator import CostCalculator
from junta_medica.services.llm.llm_client import LLMClient

ROLES = ["clinical", "pharmacological", "protocol", "chief"]


class ScriptedLLMProvider(LLMProvider):
    """Devuelve, por rol, las respuestas indicadas en orden (la última se repite). Guarda los mensajes recibidos."""

    def __init__(self, script: dict[str, list[dict]]):
        self._script = {role: list(answers) for role, answers in script.items()}
        self.messages: dict[str, list[str]] = {role: [] for role in ROLES}

    def complete(self, request):
        self.messages[request.role].append(request.message)
        answers = self._script[request.role]
        answer = answers.pop(0) if len(answers) > 1 else answers[0]
        return RawLLMResponse(json.dumps(answer), 1000, 200)


PROPOSAL = {"diagnoses": [{"icd10": "E87.5", "name": "Hiperpotasemia", "likelihood": "high",
                           "rationale": "K 6,3", "citations": ["gpc_ic:p23"]}],
            "plan": [{"text": "Mantener espironolactona", "citations": []}]}
FIXED = {**PROPOSAL, "plan": [{"text": "Suspender espironolactona", "citations": ["ft_inventada:p1"]}],
         "response_to_objections": ["Se suspende la espironolactona."]}
OBJECTION = {"stance": "objection", "objections": [{"severity": "severe", "detail": "Mantiene espironolactona con K 6,3",
                                                    "citations": []}]}
AGREE = {"stance": "agree"}
VERDICT = {"summary": "Hiperpotasemia por espironolactona.", "primary_diagnosis": {"icd10": "E87.5", "name": "Hiperpotasemia"},
           "recommendations": [{"text": "Suspender espironolactona", "citations": []}]}


@pytest.fixture
def retriever(fake_embeddings, in_memory_store):
    create_indexer(fake_embeddings, in_memory_store).index()
    return KnowledgeRetriever(fake_embeddings, in_memory_store, 5, 0.05)   # umbral bajo: embeddings de prueba


def run(case_id, retriever, script, threshold=None):
    provider = ScriptedLLMProvider(script)
    client = LLMClient(provider, CostCalculator({"m": (1.0, 5.0)}), 0, {role: "m" for role in ROLES})
    if threshold is not None:
        retriever = KnowledgeRetriever(retriever._embeddings, retriever._store, 5, threshold)
    case = create_case_loader().from_file(f"data/cases/{case_id}.json")
    return create_debate_orchestrator(retriever=retriever, llm_client=client).run(case), provider


def test_objection_forces_second_round_and_chief_closes(retriever):
    script = {"clinical": [PROPOSAL, FIXED], "pharmacological": [OBJECTION, AGREE], "protocol": [AGREE],
              "chief": [VERDICT]}
    result, provider = run("CASO-008", retriever, script)
    assert [r.consensus for r in result.rounds] == [False, True]
    assert result.rounds[0].agreement_level == 0.67     # alcanza el umbral, pero la objeción grave lo bloquea
    assert "Objeciones y comentarios de los otros agentes" in provider.messages["clinical"][1]
    assert "Mantiene espironolactona con K 6,3" in provider.messages["clinical"][1]
    assert result.verdict.output.primary_diagnosis.icd10 == "E87.5"
    assert result.llm_calls == 7                      # 2 rondas x 3 agentes + jefe
    assert "ft_inventada:p1" in result.citation_check.invalid


def test_two_objections_never_reach_consensus_and_stop_at_max_rounds(retriever):
    script = {"clinical": [PROPOSAL], "pharmacological": [OBJECTION], "protocol": [OBJECTION], "chief": [VERDICT]}
    result, _ = run("CASO-008", retriever, script)
    assert len(result.rounds) == 3 and not result.rounds[-1].consensus
    assert result.unresolved_objections                 # la objeción grave queda registrada


def test_severe_table_alerts_are_in_the_result_even_if_agents_ignore_them(retriever):
    script = {"clinical": [PROPOSAL], "pharmacological": [AGREE], "protocol": [AGREE], "chief": [VERDICT]}
    result, provider = run("CASO-008", retriever, script)
    texts = [a.text for a in result.alerts if a.highlighted]
    assert any("enalapril + espironolactona" in t for t in texts)
    assert any(t.startswith("espironolactona") for t in texts)
    assert "enalapril + espironolactona" in provider.messages["pharmacological"][0]
    assert "enalapril + espironolactona" in provider.messages["chief"][0]


def test_each_agent_sees_different_information(retriever):
    script = {"clinical": [PROPOSAL], "pharmacological": [AGREE], "protocol": [AGREE], "chief": [VERDICT]}
    _, provider = run("CASO-008", retriever, script)
    clinical, pharmacological, protocol = (provider.messages[r][0] for r in ("clinical", "pharmacological", "protocol"))
    assert "Interacciones de la tabla" not in clinical          # el Clínico propone sin ver las alertas
    assert "Debilidad marcada" not in pharmacological            # el Farmacológico no ve el relato de síntomas
    assert "Fragmentos de las guías sobre esta propuesta" in protocol
    assert all("expected" not in m and "should_abstain" not in m for m in (clinical, pharmacological, protocol))


def test_out_of_scope_case_abstains_without_calling_the_ai(retriever):
    script = {role: [AGREE] for role in ROLES}
    result, provider = run("CASO-017", retriever, script, threshold=0.99)
    assert result.abstained and result.verdict is None
    assert result.llm_calls == 0 and not any(provider.messages.values())
    assert "Evidencia insuficiente" in result.abstention_reason


def test_result_is_saved_as_json(retriever, tmp_path, monkeypatch):
    script = {"clinical": [PROPOSAL], "pharmacological": [AGREE], "protocol": [AGREE], "chief": [VERDICT]}
    result, _ = run("CASO-008", retriever, script)
    repository = create_debate_result_repository()
    monkeypatch.setattr(repository, "_folder", tmp_path)
    data = json.loads(repository.save(result).read_text(encoding="utf-8"))
    assert data["case_id"] == "CASO-008"
    assert data["summary"]["llm_calls"] == 4 and data["summary"]["rounds"] == 1
    assert data["rounds"][0]["reviews"][0]["output"]["stance"] == "agree"


def test_protocol_receives_the_fragments_the_proposal_cites(retriever):
    script = {"clinical": [PROPOSAL], "pharmacological": [AGREE], "protocol": [AGREE], "chief": [VERDICT]}
    result, provider = run("CASO-008", retriever, script)
    cited = result.evidence.guidelines.chunks[0].chunk.citation
    proposal = {**PROPOSAL, "plan": [{"text": "Suspender espironolactona", "citations": [cited]}]}
    _, provider = run("CASO-008", retriever, {**script, "clinical": [proposal]})
    assert f"[{cited}]" in provider.messages["protocol"][0]
