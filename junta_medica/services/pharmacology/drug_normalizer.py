"""DrugNormalizer: traduce cualquier forma de escribir un medicamento a su DCI."""
from difflib import SequenceMatcher, get_close_matches

from junta_medica.repositories.pharmacology.drug_repository import DrugRepository
from junta_medica.services.pharmacology.name_cleaning import clean_drug_name
from junta_medica.models.pharmacology.normalized_drug import NormalizedDrug, NormalizationMethod


class DrugNormalizer:
    def __init__(self, drugs: DrugRepository, similarity_threshold: float,
                 min_length_for_fuzzy: int, salts_to_ignore: list[str]):
        self._threshold = similarity_threshold
        self._min_length = min_length_for_fuzzy
        self._salts = salts_to_ignore
        self._index = self._build_index(drugs)

    def normalize(self, name: str) -> NormalizedDrug:
        cleaned_text = clean_drug_name(name, self._salts)
        if cleaned_text in self._index:
            inn, method = self._index[cleaned_text]
            return NormalizedDrug(name, inn, method)
        return self._find_approximate(name, cleaned_text)

    def normalize_many(self, names: list[str]) -> list[NormalizedDrug]:
        return [self.normalize(name) for name in names]

    def _find_approximate(self, original: str, cleaned_text: str) -> NormalizedDrug:
        if len(cleaned_text) >= self._min_length:
            candidates = get_close_matches(cleaned_text, self._index.keys(), n=1, cutoff=self._threshold)
            if candidates:
                inn, _ = self._index[candidates[0]]
                similarity = SequenceMatcher(None, cleaned_text, candidates[0]).ratio()
                return NormalizedDrug(original, inn, NormalizationMethod.APPROXIMATE, round(similarity, 2))
        return NormalizedDrug(original, None, NormalizationMethod.UNRECOGNIZED, 0.0)

    def _build_index(self, drugs: DrugRepository) -> dict[str, tuple[str, NormalizationMethod]]:
        """texto limpio -> (DCI, método). Falla si un mismo nombre apunta a dos DCI distintas."""
        idx: dict[str, tuple[str, NormalizationMethod]] = {}
        for drug in drugs.all():
            names = [(drug.inn, NormalizationMethod.EXACT)]
            names += [(s, NormalizationMethod.SYNONYM) for s in drug.synonyms]
            names += [(m, NormalizationMethod.BRAND) for m in drug.brands]
            # el nombre en inglés solo sirve como sinónimo si es un medicamento simple (no combinación)
            if len(drug.english_names) == 1:
                names.append((drug.english_names[0], NormalizationMethod.SYNONYM))
            for name, method in names:
                key = clean_drug_name(name, self._salts)
                existing = idx.get(key)
                if existing and existing[0] != drug.inn:
                    raise ValueError(f"'{name}' apunta a dos medicamentos: {existing[0]} y {drug.inn}")
                if not existing or method is NormalizationMethod.EXACT:
                    idx[key] = (drug.inn, method)
        return idx
