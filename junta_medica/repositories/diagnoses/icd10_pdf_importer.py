"""
Icd10PdfImporter: extrae los códigos y títulos de la Lista Tabular del PDF de la CIE-10 (OPS 2018, volumen 1).

Cómo está armado el PDF (se usa la posición y la fuente de cada línea, no solo el texto):
- El código va a la izquierda (x < 60) en Helvetica-Bold; su título, en la misma altura más a la derecha (x >= 75).
  Un título largo continúa en las líneas siguientes, también en Helvetica-Bold.
- El texto de una misma página a veces sale desordenado (primero 5 códigos, luego sus 5 títulos):
  por eso cada título se empareja con el código que está a su MISMA altura.
- Algunos grupos (ej. diabetes E10–E14) no repiten el cuarto carácter en cada categoría: lo definen una vez,
  justo antes de la primera categoría del grupo (".0 Con coma" ... ".9 Sin mención de complicación"; la lista
  puede seguir en la página siguiente), y cada categoría dice "[Para el cuarto carácter ver las subdivisiones
  antes de E10]". Cada lista se guarda con el nombre de la categoría que la sigue (E10) y solo se aplica a las
  categorías cuya nota nombra esa categoría. Si la nota no se puede asociar, NO se inventan subcategorías.
"""
import re
from pathlib import Path

from junta_medica.models.diagnoses.icd10_code import Icd10Code

CODE_PATTERN = re.compile(r"^([A-Z]\d{2}(?:\.\d)?)[*†]?$")
SHARED_SUBDIVISION_PATTERN = re.compile(r"^\.(\d)[*†]?\s*(.*)$")
SHARED_SUBDIVISION_NOTE = re.compile(r"Para el cuarto carácter ver.*?antes de ([A-Z]\d{2})")
CODE_FONT = "Helvetica-Bold"
SHARED_SUBDIVISION_FONT = "Times-Bold"
MIN_FONT_SIZE = 9.5          # descarta encabezados de página (8 pt)
CODE_MAX_X = 60
TITLE_MIN_X = 75
SAME_LINE_TOLERANCE = 3      # puntos de diferencia vertical para considerar "misma altura"
CONTINUATION_MAX_GAP = 16    # distancia máxima entre renglones de un mismo título


class Icd10PdfImporter:
    def load(self, pdf_path: Path) -> list[Icd10Code]:
        import pymupdf  # solo se necesita al regenerar la tabla

        codes: dict[str, Icd10Code] = {}
        shared_lists: dict[str, list[tuple[str, str]]] = {}   # "E10" -> [(".0", "Con coma"), ...]
        pending: list[tuple[str, str]] = []                   # lista compartida que aún no tiene dueño
        notes: list[tuple[str, str]] = []                     # (categoría, categoría dueña de la lista)
        with pymupdf.open(pdf_path) as document:
            for number, page in enumerate(document, start=1):
                lines = sorted(self._lines(page), key=lambda l: l["y"])
                for found in self._page_codes(lines, number):
                    codes.setdefault(found.code, found)    # si se repite, vale la primera aparición
                last_category = None
                for line in lines:
                    subdivision = self._shared_subdivision(line)
                    if subdivision:
                        if pending and int(subdivision[0]) <= int(pending[-1][0]):
                            pending = []                  # empieza otra lista
                        pending.append(subdivision)
                        continue
                    category = self._category_code(line)
                    if category:
                        last_category = category
                        if pending:
                            shared_lists.setdefault(category, pending)
                            pending = []
                        continue
                    note = SHARED_SUBDIVISION_NOTE.search(line["text"])
                    if note and last_category:
                        notes.append((last_category, note.group(1)))
        for category_code, owner in notes:
            category = codes.get(category_code)
            for digit, title in shared_lists.get(owner, []):
                code = f"{category_code}.{digit}"
                if category:
                    codes.setdefault(code, Icd10Code(code, f"{category.title}: {title}", category.page))
        return sorted(codes.values(), key=lambda c: c.code)

    @staticmethod
    def _shared_subdivision(line: dict) -> tuple[str, str] | None:
        if SHARED_SUBDIVISION_FONT in line["font"] and "Italic" not in line["font"]:
            match = SHARED_SUBDIVISION_PATTERN.match(line["text"])
            if match:
                return match.group(1), Icd10PdfImporter._clean(match.group(2))
        return None

    @staticmethod
    def _category_code(line: dict) -> str | None:
        """Código de 3 caracteres (categoría) en la columna de códigos, ej. "E10"."""
        if CODE_FONT in line["font"] and line["size"] >= MIN_FONT_SIZE and line["x"] < CODE_MAX_X:
            match = CODE_PATTERN.match(line["first"])
            if match and "." not in match.group(1):
                return match.group(1)
        return None

    @staticmethod
    def _lines(page) -> list[dict]:
        """Cada línea con su texto, posición y fuente (la del primer fragmento con texto)."""
        lines = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                spans = [s for s in line["spans"] if s["text"].strip()]
                if spans:
                    first = spans[0]
                    lines.append({
                        "x": first["bbox"][0], "y": first["bbox"][3], "font": first["font"],
                        "size": first["size"], "first": first["text"].strip(),
                        "rest": " ".join(s["text"].strip() for s in spans[1:]),
                        "text": " ".join(s["text"].strip() for s in spans),
                    })
        return lines

    def _page_codes(self, lines: list[dict], page_number: int) -> list[Icd10Code]:
        bold = [l for l in lines if CODE_FONT in l["font"] and l["size"] >= MIN_FONT_SIZE]
        code_lines = [l for l in bold if l["x"] < CODE_MAX_X and CODE_PATTERN.match(l["first"])]
        titles = sorted(
            [(l["y"], l["text"]) for l in bold if l["x"] >= TITLE_MIN_X]
            + [(l["y"], l["rest"]) for l in code_lines if l["rest"]],   # título en la misma línea del código
        )
        pending = list(code_lines)
        result: dict[str, list] = {}
        current, previous_y = None, None
        for y, text in titles:
            match = next((c for c in pending if abs(c["y"] - y) < SAME_LINE_TOLERANCE), None)
            if match:
                pending.remove(match)
                current = CODE_PATTERN.match(match["first"]).group(1)
                result[current] = [text]
            elif current and previous_y is not None and y - previous_y < CONTINUATION_MAX_GAP:
                result[current].append(text)
            else:
                current = None
            previous_y = y
        for line in pending:                      # código sin título detectado: se conserva igual
            result.setdefault(CODE_PATTERN.match(line["first"]).group(1), [])
        return [Icd10Code(code, self._clean(" ".join(parts)), page_number) for code, parts in result.items()]

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[\x00-\x1f]", " ", text)).strip()   # quita caracteres de control
