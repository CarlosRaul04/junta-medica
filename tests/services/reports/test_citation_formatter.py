from junta_medica.factories.report_factory import create_citation_formatter


def test_citations_become_readable_sources():
    formatter = create_citation_formatter()
    assert formatter.format("gpc_ic:p22-23").startswith("GPC Insuficiencia cardiaca")
    assert formatter.format("gpc_ic:p22-23").endswith("pág. 22-23")
    assert formatter.format("ft_dabigatran:p84") == "Ficha técnica: dabigatrán, pág. 84"
    assert formatter.format("ddinter:DDInter48-DDInter76").startswith("DDInter")
    assert formatter.format("desconocido:p3") == "desconocido, pág. 3"
