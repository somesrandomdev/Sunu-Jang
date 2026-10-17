"""Contrats de données : Exercise et Grade (voir PLAN.md §4)."""

from pydantic import BaseModel, Field, field_validator


class Exercise(BaseModel):
    titre: str = Field(min_length=1)
    enonce: str = Field(min_length=10)
    bareme: str = Field(min_length=1)
    competences_evaluees: list[str] = Field(min_length=1)
    # Requis : la correction en dépend. Jamais affiché avant la correction.
    corrige: str = Field(min_length=10)


class Grade(BaseModel):
    note: float
    points_forts: list[str]
    erreurs: list[str]
    correction_detaillee: str = Field(min_length=1)
    conseil: str = Field(min_length=1)

    @field_validator("note")
    @classmethod
    def clamp(cls, v: float) -> float:
        return max(0.0, min(20.0, round(v * 2) / 2))  # borné à [0, 20], pas de 0,5
