"""Tests de l'interface : les erreurs du modèle deviennent des toasts français."""

import gradio as gr
import pytest

from app import ui
from app.llm import LLMError


def test_ollama_arrete_pendant_la_recherche_rag_donne_un_toast(monkeypatch):
    def retrieve_en_panne(*_args, **_kwargs):
        raise LLMError("Le modèle local ne répond pas. Vérifiez qu'Ollama est lancé.")

    monkeypatch.setattr(ui, "retrieve", retrieve_en_panne)
    with pytest.raises(gr.Error, match="Ollama est lancé"):
        ui.generer_exercice("Maths", "Terminale", "moyen", "")
