from junta_medica.factories.knowledge_factory import create_text_cleaner
from junta_medica.models.knowledge.page_text import PageText


def pages(bodies):
    return [PageText("gpc_x", i, f"Guía Técnica N° 006 - INS\n{body}\n{i}") for i, body in enumerate(bodies, start=1)]


def test_removes_repeated_headers_and_page_numbers():
    cleaned = create_text_cleaner().clean(pages(["Recomendación A", "Recomendación B", "Recomendación C"]))
    assert [p.text for p in cleaned] == ["Recomendación A", "Recomendación B", "Recomendación C"]


def test_keeps_repeated_content_in_the_middle_of_the_page():
    body = "linea 1\nlinea 2\nlinea 3\nlinea 4\nFuerza de la recomendación: Fuerte\nlinea 6\nlinea 7\nlinea 8\nlinea 9"
    cleaned = create_text_cleaner().clean(pages([body] * 4))
    assert all("Fuerza de la recomendación: Fuerte" in p.text for p in cleaned)


def test_removes_digital_signatures_and_joins_hyphenated_words():
    page = PageText("gpc_x", 1, "Firmado digitalmente por PÉREZ\nla espirono-\nlactona se suspende")
    assert create_text_cleaner().clean([page])[0].text == "la espironolactona se suspende"
