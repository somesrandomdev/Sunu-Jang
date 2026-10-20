"""Contrats de données : Exercise et Grade (voir PLAN.md §4)."""

from pydantic import BaseModel, Field, field_validator


class Exercise(BaseModel):
    titre: str = Field(min_length=1)
    enonce: str = Field(min_length=10)
    bareme: str = Field(min_length=1)
    competences_evaluees: list[str] = Field(min_length=1)
    # Requis : la correction en dépend. Jamais affiché avant la correction.
    corrige: str = Field(min_length=10)


class PointsQuestion(BaseModel):
    """Points d'une question du barème, tels que déclarés par le modèle."""

    question: str
    obtenu: float
    max: float


def _nombre_flexible(v: object) -> float:
    """float depuis un nombre ou une chaîne numérique ('4', '2,5')."""
    if isinstance(v, bool):
        raise TypeError("bool")
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        return float(v.strip().replace(",", "."))
    raise TypeError(f"type non numérique : {type(v).__name__}")


class Grade(BaseModel):
    note: float
    points_forts: list[str]
    erreurs: list[str]
    correction_detaillee: str = Field(min_length=1)
    conseil: str = Field(min_length=1)
    points_par_question: list[PointsQuestion] = []

    @field_validator("points_par_question", mode="before")
    @classmethod
    def _ecarter_entrees_mal_formees(cls, v: object) -> list[dict[str, object]]:
        # Le modèle 3b produit parfois des entrées cassées dans ce champ ;
        # on les écarte silencieusement au lieu de faire échouer toute la
        # correction — la note saura s'en passer (voir app.tutor._note_finale).
        if not isinstance(v, list):
            return []
        valides: list[dict[str, object]] = []
        for entree in v:
            if not isinstance(entree, dict):
                continue
            try:
                question = entree["question"]
                obtenu = _nombre_flexible(entree["obtenu"])
                maxi = _nombre_flexible(entree["max"])
            except (KeyError, TypeError, ValueError):
                continue
            if obtenu < 0 or maxi <= 0 or obtenu > maxi:
                continue
            valides.append(
                {"question": str(question), "obtenu": obtenu, "max": maxi}
            )
        return valides

    @field_validator("note")
    @classmethod
    def clamp(cls, v: float) -> float:
        return max(0.0, min(20.0, round(v * 2) / 2))  # borné à [0, 20], pas de 0,5

    @field_validator("correction_detaillee", "conseil", mode="before")
    @classmethod
    def _aplatir(cls, v: object) -> object:
        # le modèle renvoie parfois une liste au lieu d'un texte
        if isinstance(v, list):
            return "\n".join(str(item) for item in v)
        return v

    @field_validator("points_forts", "erreurs", mode="before")
    @classmethod
    def _ensacher(cls, v: object) -> object:
        # …et parfois une seule chaîne au lieu d'une liste
        if isinstance(v, str):
            return [v] if v.strip() else []
        return v
