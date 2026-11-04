"""Prueba el importador con un PDF pequeño que imita el formato de la CIE-10 de la OPS."""
import pymupdf

from junta_medica.repositories.diagnoses.icd10_pdf_importer import Icd10PdfImporter


def write(page, x, y, text, font="hebo", size=10):
    page.insert_text((x, y), text, fontname=font, fontsize=size)


def build_pdf(path):
    document = pymupdf.open()
    page = document.new_page()
    write(page, 32, 60, "I50", size=12)
    write(page, 80, 60, "Insuficiencia cardíaca", size=12)
    # el texto sale "desordenado": primero los códigos, luego los títulos (a la misma altura)
    write(page, 32, 80, "I50.0")
    write(page, 32, 100, "I50.9")
    write(page, 80, 80, "Insuficiencia cardíaca congestiva")
    write(page, 80, 100, "Insuficiencia cardíaca, no")
    write(page, 80, 112, "especificada")                          # título en dos renglones
    write(page, 80, 124, "Insuficiencia cardíaca SAI", font="tiro")  # nota en letra normal: no es título
    # subdivisiones compartidas (como en diabetes E10–E14)
    write(page, 80, 160, ".0 Con coma", font="tibo")
    write(page, 80, 175, ".9 Sin mención de complicación", font="tibo")
    write(page, 32, 200, "E11", size=12)
    write(page, 80, 200, "Diabetes mellitus tipo 2", size=12)
    write(page, 80, 214, "[Para el cuarto carácter ver las subdivisiones antes de E11]", font="tiro")
    document.save(path)


def test_extracts_codes_titles_and_shared_subdivisions(tmp_path):
    pdf = tmp_path / "cie10.pdf"
    build_pdf(pdf)
    codes = {c.code: c for c in Icd10PdfImporter().load(pdf)}
    assert codes["I50"].title == "Insuficiencia cardíaca"
    assert codes["I50.0"].title == "Insuficiencia cardíaca congestiva"
    assert codes["I50.9"].title == "Insuficiencia cardíaca, no especificada"
    assert codes["E11.9"].title == "Diabetes mellitus tipo 2: Sin mención de complicación"
    assert codes["E11.0"].page == 1
