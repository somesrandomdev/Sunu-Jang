"""Tests de l'interface : erreurs -> toasts français, et secours par la banque."""

import gradio as gr
import pytest

from app import ui
from app.banque import BANQUE_PAR_MATIERE, EX_SUITES
from app.llm import LLMError
from app.schemas import Exercise

GENERATION_EN_PANNE = LLMError("Le modèle local n'a pas renvoyé de réponse exploitable.")


def _valeur(mise_a_jour) -> str:
    """gr.update() est un dict hors contexte Blocks, un objet dedans."""
    if isinstance(mise_a_jour, dict):
        return mise_a_jour.get("value", "") or ""
    return getattr(mise_a_jour, "value", "") or ""


def test_ollama_arrete_pendant_la_recherche_rag_donne_un_toast(monkeypatch):
    # SVT n'a pas d'exercice de banque : l'erreur reste un toast français.
    def retrieve_en_panne(*_args, **_kwargs):
        raise LLMError("Le modèle local ne répond pas. Vérifiez qu'Ollama est lancé.")

    monkeypatch.setattr(ui, "retrieve", retrieve_en_panne)
    with pytest.raises(gr.Error, match="Ollama est lancé"):
        ui.generer_exercice("SVT", "Terminale", "moyen", "")


class TestBanqueDeSecours:
    @staticmethod
    def avaleur_en_panne(monkeypatch) -> list[str]:
        avertissements: list[str] = []

        def faux_warning(message: str, **_kwargs) -> None:
            avertissements.append(message)

        def generate_en_panne(*_args, **_kwargs):
            raise GENERATION_EN_PANNE

        monkeypatch.setattr(ui, "retrieve", lambda *_a, **_k: [])
        monkeypatch.setattr(ui, "generate_exercise", generate_en_panne)
        monkeypatch.setattr(ui.gr, "Warning", faux_warning)
        return avertissements

    def test_generation_en_panne_maths_recoit_la_banque(self, monkeypatch):
        avertissements = self.avaleur_en_panne(monkeypatch)
        resultat = ui.generer_exercice("Maths", "Terminale", "moyen", "suites")
        assert resultat[2] is BANQUE_PAR_MATIERE["Maths"]
        assert resultat[2].titre == EX_SUITES.titre
        assert "banque" in _valeur(resultat[1])
        assert "non généré" in _valeur(resultat[1])
        assert avertissements == ["Génération indisponible : voici un exercice de la banque."]

    def test_generation_en_panne_svt_leve_une_erreur(self, monkeypatch):
        self.avaleur_en_panne(monkeypatch)
        with pytest.raises(gr.Error):
            ui.generer_exercice("SVT", "Terminale", "moyen", "")

    def test_generation_reussie_n_utilise_pas_la_banque(self, monkeypatch):
        exercice_mock = Exercise(
            titre="Exercice généré",
            enonce="Un énoncé généré en direct par le modèle.",
            bareme="sur 20",
            competences_evaluees=["test"],
            corrige="Un corrigé généré en direct, assez long.",
        )
        monkeypatch.setattr(
            ui, "retrieve",
            lambda *_a, **_k: [
                {"source_file": "maths_S2_2023.pdf", "page": 3, "matiere": "maths",
                 "serie": "S2", "annee": 2023, "texte": "extrait"}
            ],
        )
        monkeypatch.setattr(ui, "generate_exercise", lambda *_a, **_k: exercice_mock)
        resultat = ui.generer_exercice("Maths", "Terminale", "moyen", "suites")
        assert resultat[2] is exercice_mock
        assert "banque" not in _valeur(resultat[1])
        assert "maths_S2_2023.pdf" in _valeur(resultat[1])
