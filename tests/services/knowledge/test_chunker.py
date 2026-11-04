from junta_medica.models.knowledge.page_text import PageText
from junta_medica.services.knowledge.chunker import Chunker

PAGE1_TEXT = "Introducción breve de la sección con texto suficiente.\n\nPregunta 1: ¿Se debería usar metformina?\n1.1 Recomendamos metformina como primera línea en adultos."
PAGE2_TEXT = "Pregunta 2: ¿Se debería usar insulina?\n2.1 Sugerimos insulina basal cuando no se alcanza la meta."


def chunker(max_size=1800):
    return Chunker(r"^\s*Pregunta\s+\d+", max_size, 60, 20)


def test_one_block_per_question_with_title_and_page():
    chunks = chunker().chunk([PageText("gpc_dm2", 13, PAGE1_TEXT), PageText("gpc_dm2", 14, PAGE2_TEXT)], "recommendations")
    titles = [f.title for f in chunks]
    assert titles == ["", "Pregunta 1: ¿Se debería usar metformina?", "Pregunta 2: ¿Se debería usar insulina?"]
    assert [(f.start_page, f.end_page) for f in chunks[1:]] == [(13, 13), (14, 14)]


def test_block_spanning_pages_records_both():
    p1 = PageText("gpc_ic", 22, "Pregunta 7: ¿ARM en ICC?\n7.1 Recomendamos antagonistas de mineralocorticoides.")
    p2 = PageText("gpc_ic", 23, "7.2 Suspender espironolactona si el potasio es mayor a 6 mEq/L.")
    chunk = chunker().chunk([p1, p2], "recommendations")[0]
    assert (chunk.start_page, chunk.end_page, chunk.citation) == (22, 23, "gpc_ic:p22-23")


def test_long_block_is_split_and_each_piece_keeps_the_title():
    paragraphs = "\n\n".join(f"Párrafo número {i} con contenido clínico relevante para la recomendación." for i in range(12))
    page = PageText("gpc_erc", 20, "Pregunta 9: ¿Cómo ajustar dosis en ERC?\n" + paragraphs)
    chunks = chunker(max_size=300).chunk([page], "recommendations")
    assert len(chunks) > 1
    assert all(len(f.text) <= 300 + 60 for f in chunks)
    assert all(f.title.startswith("Pregunta 9") for f in chunks)
    assert chunks[1].text.startswith("Pregunta 9: ¿Cómo ajustar dosis en ERC? (continuación)")
