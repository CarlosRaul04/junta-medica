"""
Corre la junta médica completa sobre un caso y muestra el resultado.

Uso:  python -m scripts.run_case CASO-008
      python -m scripts.run_case data/cases/CASO-008.json
Con MOCK_MODE=1 (en el .env) usa respuestas de ejemplo, sin IA real ni internet.
El resultado completo se guarda en output/debates/.
"""
import sys
from pathlib import Path

from junta_medica.config import paths, texts
from junta_medica.exceptions import InvalidCaseError, LLMConfigurationError, LLMProviderError, OutdatedIndexError
from junta_medica.factories.case_factory import create_case_loader
from junta_medica.factories.debate_factory import create_debate_orchestrator, create_debate_result_repository


def case_path(argument: str) -> Path:
    path = Path(argument)
    return path if path.suffix == ".json" else paths.CASES_DIR / f"{argument}.json"


def print_result(result) -> None:
    print(f"\n=== {result.case_id} ===")
    evidence = result.evidence
    if evidence.unrecognized_drugs:
        print(f"Medicamentos no reconocidos: {', '.join(evidence.unrecognized_drugs)}")
    print(f"Evidencia en guías: {'suficiente' if evidence.guidelines.sufficient_evidence else 'INSUFICIENTE'}")

    print("\nAlertas:")
    for alert in result.alerts:
        mark = "!!" if alert.highlighted else "  "
        print(f" {mark} [{texts.SEVERITY_LABELS[alert.severity.value]}] {alert.text}  {' '.join(alert.citations)}")
    if not result.alerts:
        print("    (ninguna)")

    if result.abstained:
        print(f"\n{result.abstention_reason}")
    else:
        for r in result.rounds:
            stances = ", ".join(f"{texts.ROLE_LABELS[t.role]}: {texts.STANCE_LABELS[t.output.stance.value]}" for t in r.reviews)
            print(f"\nRonda {r.number} — acuerdo {r.agreement_level:.0%} — {stances}")
            for d in r.proposal.output.diagnoses:
                print(f"   {d.icd10} {d.name} ({d.likelihood})")
        verdict = result.verdict.output
        print(f"\n{texts.ROLE_LABELS['chief']}: {verdict.summary}")
        if verdict.primary_diagnosis:
            print(f"Diagnóstico principal: {verdict.primary_diagnosis.icd10} {verdict.primary_diagnosis.name}")
        for rec in verdict.recommendations:
            print(f" - {rec.text} {' '.join(rec.citations)}")
        for item in (*result.unresolved_objections, *verdict.disagreements):
            print(f" ⚠ Discrepancia: {item}")

    check = result.citation_check
    print(f"\nTrazabilidad: {check.traceability:.0%} ({check.cited_claims}/{check.total_claims} afirmaciones con cita válida)")
    if check.invalid:
        print(f"Citas inválidas (inventadas): {', '.join(check.invalid)}")
    print(f"Llamadas a la IA: {result.llm_calls} · costo: US$ {result.cost_usd:.4f} · tiempo: {result.seconds:.1f} s")
    print(f"\n{texts.DISCLAIMER}")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: python -m scripts.run_case CASO-008")
    try:
        case = create_case_loader().from_file(case_path(sys.argv[1]))
        result = create_debate_orchestrator().run(case)
    except InvalidCaseError as error:
        sys.exit("El caso no es válido:\n- " + "\n- ".join(e.message for e in error.errors))
    except (LLMConfigurationError, LLMProviderError, OutdatedIndexError) as error:
        sys.exit(str(error))
    print_result(result)
    print(f"Resultado completo: {create_debate_result_repository().save(result)}")


if __name__ == "__main__":
    main()
