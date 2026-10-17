"""Tests des contrats de données (PLAN.md §4)."""

import pytest
from pydantic import ValidationError

from app.schemas import Exercise, Grade

EXERCICE_VALIDE = {
    "titre": "Suites numériques",
    "enonce": "Soit la suite (u_n) définie par u_0 = 2 et u_{n+1} = 3u_n - 1.",
    "bareme": "1. Question 1 : 10 points. 2. Question 2 : 10 points.",
    "competences_evaluees": ["Raisonnement par récurrence"],
    "corrige": "1. Montrons par récurrence que u_n > 0 pour tout n.",
}


class TestExercise:
    def test_valide(self):
        exercice = Exercise.model_validate(EXERCICE_VALIDE)
        assert exercice.titre == "Suites numériques"

    def test_enonce_trop_court_refuse(self):
        donnees = {**EXERCICE_VALIDE, "enonce": "court"}
        with pytest.raises(ValidationError):
            Exercise.model_validate(donnees)

    def test_corrige_manquant_refuse(self):
        donnees = {k: v for k, v in EXERCICE_VALIDE.items() if k != "corrige"}
        with pytest.raises(ValidationError):
            Exercise.model_validate(donnees)

    def test_competences_vides_refusees(self):
        donnees = {**EXERCICE_VALIDE, "competences_evaluees": []}
        with pytest.raises(ValidationError):
            Exercise.model_validate(donnees)

    def test_champs_supplementaires_ignores(self):
        donnees = {**EXERCICE_VALIDE, "champ_imprevu": "x"}
        assert Exercise.model_validate(donnees).titre == "Suites numériques"


class TestGrade:
    @staticmethod
    def grade(note) -> Grade:
        return Grade(
            note=note,
            points_forts=["démarche claire"],
            erreurs=["erreur de signe"],
            correction_detaillee="étape par étape",
            conseil="vérifier le signe",
        )

    def test_note_dans_la_borne(self):
        assert self.grade(13).note == 13.0

    def test_note_25_bornee_a_20(self):
        assert self.grade(25).note == 20.0

    def test_note_negative_bornee_a_0(self):
        assert self.grade(-3).note == 0.0

    def test_note_en_chaine_convertie(self):
        assert self.grade("12").note == 12.0

    def test_pas_de_demi_point(self):
        assert self.grade(12.3).note == 12.5

    def test_champs_vides_acceptes_mais_correction_requise(self):
        with pytest.raises(ValidationError):
            Grade(
                note=10,
                points_forts=[],
                erreurs=[],
                correction_detaillee="",
                conseil="x",
            )


class TestGradeTolerance:
    """Le modèle renvoie parfois des types voisins : on les accepte."""

    def test_correction_en_liste_est_aplatie(self):
        grade = Grade(
            note=10,
            points_forts=["a"],
            erreurs=[],
            correction_detaillee=["étape 1", "étape 2"],
            conseil="x",
        )
        assert grade.correction_detaillee == "étape 1\nétape 2"

    def test_erreurs_en_chaine_est_ensachee(self):
        grade = Grade(
            note=10,
            points_forts=[],
            erreurs="erreur unique",
            correction_detaillee="x",
            conseil="y",
        )
        assert grade.erreurs == ["erreur unique"]
