"""Tests de app.tutor (LLM mocké, PLAN.md §6 M1)."""

import json

import pytest
from conftest import FakeClient, installer
from pydantic import ValidationError

from app.schemas import Exercise, Grade
from app.tutor import generate_exercise, grade_answer, next_difficulty

EXERCICE = Exercise(
    titre="Suites numériques",
    enonce="Soit (u_n) définie par u_0 = 2 et u_{n+1} = 3 u_n - 1.",
    bareme="Q1 : 10 points, Q2 : 10 points",
    competences_evaluees=["récurrence"],
    corrige="On montre par récurrence que u_n > 0.",
)

REPONSE_EXERCICE = {
    "titre": "Suites numériques",
    "enonce": "Soit (u_n) définie par u_0 = 2 et u_{n+1} = 3 u_n - 1.",
    "bareme": "Q1 : 10 points, Q2 : 10 points",
    "competences_evaluees": ["récurrence"],
    "corrige": "On montre par récurrence que u_n > 0.",
}

REPONSE_GRADE = {
    "note": 8,
    "points_forts": ["démarche récursive comprise"],
    "erreurs": ["erreur de calcul au rang 2"],
    "correction_detaillee": "1. Initialisation... 2. Hérédité...",
    "conseil": "Recalculer chaque étape à voix haute.",
}


class TestGenerateExercise:
    def test_genere_un_exercice(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([json.dumps(REPONSE_EXERCICE)]))
        exercice = generate_exercise("Maths", "Terminale", "moyen", "suites numériques")
        assert exercice.titre == "Suites numériques"
        appel = client.appels_chat[0]
        assert appel["temperature"] == 0.4
        assert "Maths" in appel["messages"][1]["content"]
        assert "suites numériques" in appel["messages"][1]["content"]

    def test_theme_vide_recoit_le_theme_par_defaut(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([json.dumps(REPONSE_EXERCICE)]))
        generate_exercise("Philosophie", "Terminale", "facile", theme="  ")
        prompt = client.appels_chat[0]["messages"][1]["content"]
        assert "au choix, conforme au programme" in prompt

    def test_sans_extraits_pas_d_entete_annale(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([json.dumps(REPONSE_EXERCICE)]))
        generate_exercise("Maths", "Première", "facile")
        messages = client.appels_chat[0]["messages"]
        assert all("Voici des extraits" not in m["content"] for m in messages)

    def test_avec_extraits_le_contexte_est_injecte(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([json.dumps(REPONSE_EXERCICE)]))
        extraits = ["Extrait BAC 2023 : étude de suite géométrique."]
        generate_exercise("Maths", "Terminale", "moyen", extraits=extraits)
        prompt = client.appels_chat[0]["messages"][1]["content"]
        assert "Voici des extraits" in prompt
        assert "Extrait BAC 2023" in prompt


class TestGradeAnswer:
    def test_note_une_reponse(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([json.dumps(REPONSE_GRADE)]))
        grade = grade_answer(EXERCICE, "Ma réponse : u_n > 0 par récurrence.", "Terminale")
        assert isinstance(grade, Grade)
        appel = client.appels_chat[0]
        assert appel["temperature"] == 0.1
        prompt = appel["messages"][1]["content"]
        assert EXERCICE.enonce in prompt
        assert EXERCICE.corrige in prompt
        assert "<<<" in prompt and "Ma réponse" in prompt

    def test_reponse_vide_refusee_sans_appeler_le_modele(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([]))
        with pytest.raises(ValueError, match="vide"):
            grade_answer(EXERCICE, "   ", "Terminale")
        assert client.appels_chat == []

    def test_note_hors_bornee_bornee_par_le_schema(self, monkeypatch):
        deborde = {**REPONSE_GRADE, "note": 25}
        installer(monkeypatch, FakeClient([json.dumps(deborde)]))
        assert grade_answer(EXERCICE, "réponse", "Terminale").note == 20.0

    def test_reponse_invalidee_provoque_un_reessai(self, monkeypatch):
        reponses = [{"note": "pas un nombre"}, REPONSE_GRADE]
        installer(monkeypatch, FakeClient([json.dumps(r) for r in reponses]))
        grade = grade_answer(EXERCICE, "réponse", "Terminale")
        assert grade.note == 8.0


class TestNoteDepuisTotal:
    """Revue 2, Step C : la ligne « Total : n/20 » fait foi sur la note JSON."""

    @staticmethod
    def grade_avec_correction(note_json: float, correction: str, monkeypatch):
        reponse = {
            **REPONSE_GRADE,
            "note": note_json,
            "correction_detaillee": correction,
        }
        installer(monkeypatch, FakeClient([json.dumps(reponse)]))
        return grade_answer(EXERCICE, "réponse d'élève", "Terminale")

    def test_total_present_fait_foi(self, monkeypatch):
        grade = self.grade_avec_correction(
            8.0, "Q1 : 6/6. Q2 : 6/6.\nTotal : 12/20", monkeypatch
        )
        assert grade.note == 12.0

    def test_total_absent_garde_la_note_json(self, monkeypatch):
        grade = self.grade_avec_correction(8.0, "Q1 : correct. Bien.", monkeypatch)
        assert grade.note == 8.0

    def test_total_a_virgule(self, monkeypatch):
        grade = self.grade_avec_correction(
            8.0, "Q1 : 6/6. Q2 : 6,5/14.\nTotal : 12,5/20", monkeypatch
        )
        assert grade.note == 12.5

    def test_deux_totaux_le_dernier_gagne(self, monkeypatch):
        grade = self.grade_avec_correction(
            8.0, "Sous-total : 5/20. Recalcul : Q1 6/6, Q2 9/14.\nTotal : 15/20",
            monkeypatch,
        )
        assert grade.note == 15.0

    def test_total_superieur_a_20_borne(self, monkeypatch):
        grade = self.grade_avec_correction(
            8.0, "Q1 : 15/6. Q2 : 10/14.\nTotal : 25/20", monkeypatch
        )
        assert grade.note == 20.0


class TestNextDifficulty:
    @pytest.mark.parametrize(
        ("note", "actuelle", "attendue"),
        [
            (9.5, "moyen", "facile"),
            (10, "moyen", "moyen"),
            (14.5, "moyen", "moyen"),
            (15, "moyen", "difficile"),
            (9.5, "facile", "facile"),  # déjà au plus facile
            (20, "difficile", "difficile"),  # déjà au plus dur
            (5, "difficile", "moyen"),
            (18, "facile", "moyen"),
        ],
    )
    def test_regles(self, note, actuelle, attendue):
        assert next_difficulty(note, actuelle) == attendue

    def test_difficulte_inconnue_refusee(self):
        with pytest.raises(ValueError, match="inconnue"):
            next_difficulty(12, "expert")


def test_exercice_refuse_champ_manquant():
    with pytest.raises(ValidationError):
        Exercise.model_validate({k: v for k, v in REPONSE_EXERCICE.items() if k != "bareme"})
