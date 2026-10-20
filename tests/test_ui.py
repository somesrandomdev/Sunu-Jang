"""Tests de l'interface : erreurs -> toasts français, et secours par la banque."""

import gradio as gr
import pytest
from PIL import Image

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


class TestLireCopie:
    """Revue 4, §5 : photo → transcription dans « Ta réponse »."""

    @staticmethod
    def photo(tmp_path) -> str:
        chemin = tmp_path / "copie.jpg"
        Image.new("RGB", (300, 200), color=(245, 245, 245)).save(
            chemin, format="JPEG"
        )
        return str(chemin)

    def test_transcription_remplit_la_reponse(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "app.ui.transcrire_copie",
            lambda *_a, **_k: "1. u_1 = 5 et u_2 = 13.\n2. [non traitée]",
        )
        texte, depuis_photo = ui.lire_copie(EX_SUITES, self.photo(tmp_path))
        assert texte.startswith("1. u_1 = 5")
        assert depuis_photo is True

    def test_sans_exercice_refuse(self, tmp_path):
        with pytest.raises(gr.Error, match="Générez d'abord"):
            ui.lire_copie(None, self.photo(tmp_path))

    def test_sans_image_refuse(self):
        with pytest.raises(gr.Error, match="photo de votre copie"):
            ui.lire_copie(EX_SUITES, None)

    def test_erreur_modele_donnel_erreur_gradio(self, tmp_path, monkeypatch):
        def transcription_en_panne(*_a, **_k):
            raise LLMError("Le modèle local ne répond pas.")

        monkeypatch.setattr("app.ui.transcrire_copie", transcription_en_panne)
        with pytest.raises(gr.Error, match="ne répond pas"):
            ui.lire_copie(EX_SUITES, self.photo(tmp_path))


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


class TestPrechauffage:
    """Revue 6, Step B : le préchauffage ne doit jamais empêcher le lancement."""

    def test_deux_appels_max_tokens_1_les_deux_modeles(self, monkeypatch):
        from conftest import FakeClient, installer

        from app.config import LLM_MODEL, VISION_MODEL

        client = installer(monkeypatch, FakeClient(["ok", "ok"]))
        ui._prechauffer_modeles().join()
        assert len(client.appels_chat) == 2
        assert [appel["model"] for appel in client.appels_chat] == [
            LLM_MODEL,
            VISION_MODEL,
        ]
        assert all(appel["max_tokens"] == 1 for appel in client.appels_chat)

    def test_une_panne_ne_propage_rien(self, monkeypatch, caplog):
        import logging

        from conftest import FakeClient, installer

        installer(
            monkeypatch,
            FakeClient([RuntimeError("Ollama est éteint"), RuntimeError("idem")]),
        )
        with caplog.at_level(logging.WARNING, logger="app.ui"):
            ui._prechauffer_modeles().join()  # ne lève rien
        assert "Préchauffage" in caplog.text
        assert "ignoré" in caplog.text
