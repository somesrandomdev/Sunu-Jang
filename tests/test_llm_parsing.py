"""Tests du parsing JSON et des réessais de app.llm (client mocké)."""

import json

import httpx
import numpy as np
import pytest
from conftest import FakeClient, installer
from openai import APIStatusError, InternalServerError, NotFoundError
from pydantic import BaseModel

from app import llm
from app.llm import LLMError, chat_json, embed
from app.schemas import Exercise


def erreur_api(status: int) -> APIStatusError:
    requete = httpx.Request("POST", "http://test/v1/chat/completions")
    reponse = httpx.Response(status, request=requete)
    if status >= 500:
        return InternalServerError("boom", response=reponse, body=None)
    return NotFoundError("absent", response=reponse, body=None)

SCHEMA = {
    "titre": "Suites numériques",
    "enonce": "un énoncé assez long pour valider",
    "bareme": "sur 20",
    "competences_evaluees": ["récurrence"],
    "corrige": "un corrigé assez long pour valider",
}


class Exercice(BaseModel):
    titre: str


def contenu(donnees: dict) -> str:
    return json.dumps(donnees, ensure_ascii=False)


def test_json_valide(monkeypatch):
    client = installer(monkeypatch, FakeClient([contenu(SCHEMA)]))
    resultat = chat_json("systeme", "utilisateur", Exercice)
    assert resultat.titre == "Suites numériques"
    assert len(client.appels_chat) == 1


def test_json_entoure_de_balises_code(monkeypatch):
    brut = "```json\n" + contenu(SCHEMA) + "\n```"
    installer(monkeypatch, FakeClient([brut]))
    assert chat_json("s", "u", Exercice).titre == "Suites numériques"


def test_json_avec_prose_autour(monkeypatch):
    brut = "Voici ma réponse :\n" + contenu(SCHEMA) + "\nCordialement."
    installer(monkeypatch, FakeClient([brut]))
    assert chat_json("s", "u", Exercice).titre == "Suites numériques"


def test_invalide_puis_valide_le_reessai_fonctionne(monkeypatch):
    reponses = ["Ce n'est pas du JSON.", contenu(SCHEMA)]
    client = installer(monkeypatch, FakeClient(reponses))
    assert chat_json("s", "u", Exercice).titre == "Suites numériques"
    assert len(client.appels_chat) == 2
    messages = client.appels_chat[1]["messages"]
    assert any("était invalide" in m["content"] for m in messages)


def test_invalide_deux_fois_leve_llmerror(monkeypatch):
    installer(monkeypatch, FakeClient(["non.", "toujours pas."]))
    with pytest.raises(LLMError, match="deux essais"):
        chat_json("s", "u", Exercice)


def test_corrige_manquant_declenche_le_reessai(monkeypatch):
    incomplet = {k: v for k, v in SCHEMA.items() if k != "corrige"}
    reponses = [contenu(incomplet), contenu(SCHEMA)]
    client = installer(monkeypatch, FakeClient(reponses))
    exercice = chat_json("s", "u", Exercise)
    assert exercice.titre == "Suites numériques"
    assert len(client.appels_chat) == 2


def test_champ_manquant_deux_fois_leve_llmerror(monkeypatch):
    incomplet = {k: v for k, v in SCHEMA.items() if k != "corrige"}
    installer(monkeypatch, FakeClient([contenu(incomplet)] * 2))
    with pytest.raises(LLMError):
        chat_json("s", "u", Exercise)


def test_connexion_refusee_message_francais(monkeypatch):
    installer(monkeypatch, FakeClient([], fail_connexion=True))
    with pytest.raises(LLMError, match="Ollama est lancé"):
        chat_json("s", "u", Exercice)


def test_chat_json_passe_format_json_et_temperature(monkeypatch):
    client = installer(monkeypatch, FakeClient([contenu(SCHEMA)]))
    chat_json("s", "u", Exercice, temperature=0.1)
    appel = client.appels_chat[0]
    assert appel["response_format"] == {"type": "json_object"}
    assert appel["temperature"] == 0.1


class TestLatexDansJson:
    """Les commandes LaTeX mal échappées ne doivent pas corrompre le texte."""

    def test_times_mal_echappe_recupere(self, monkeypatch):
        brut = '{"titre": "$u_n = 4 \\times 2^n$"}'  # \times brut dans le JSON
        installer(monkeypatch, FakeClient([brut]))
        assert chat_json("s", "u", Exercice).titre == "$u_n = 4 \\times 2^n$"

    def test_frac_casse_le_json_mais_est_repare(self, monkeypatch):
        brut = '{"titre": "$\\frac{a}{b}$"}'  # \f est un échappement JSON (saut de page)
        installer(monkeypatch, FakeClient([brut]))
        assert chat_json("s", "u", Exercice).titre == "$\\frac{a}{b}$"

    def test_vrai_saut_de_ligne_conserve(self, monkeypatch):
        brut = '{"titre": "ligne un\\nligne deux"}'  # \n légitime, pas \neq
        installer(monkeypatch, FakeClient([brut]))
        assert chat_json("s", "u", Exercice).titre == "ligne un\nligne deux"

    def test_echappements_invalides_repares(self, monkeypatch):
        brut = '{"titre": "$(u_n)_{n \\in \\Delta, \\pi > 0}$"}'
        installer(monkeypatch, FakeClient([brut]))
        assert chat_json("s", "u", Exercice).titre == "$(u_n)_{n \\in \\Delta, \\pi > 0}$"

    def test_latex_correctement_echappe_inchange(self, monkeypatch):
        # Cas le plus fréquent (JSON valide produit par Ollama en mode json) :
        # la réparation ne doit RIEN modifier, sans réessai.
        titre = r"$a \times b$, $x \in \mathbb{R}$, $\frac{1}{2}$, $\Delta$, $\nu$"
        client = installer(monkeypatch, FakeClient([contenu({"titre": titre})]))
        assert chat_json("s", "u", Exercice).titre == titre
        assert len(client.appels_chat) == 1

    def test_antislash_litteral_double_conserve(self, monkeypatch):
        titre = "chemin C:\\dossier et saut\nde ligne"
        installer(monkeypatch, FakeClient([contenu({"titre": titre})]))
        assert chat_json("s", "u", Exercice).titre == titre

    def test_melange_bien_et_mal_echappe(self, monkeypatch):
        brut = '{"titre": "$\\\\frac{1}{2} \\times 3 \\in E$"}'
        installer(monkeypatch, FakeClient([brut]))
        assert chat_json("s", "u", Exercice).titre == "$\\frac{1}{2} \\times 3 \\in E$"


class TestErreursApi:
    """Revue 2, Step B : troncature, 5xx et 404 n'appendent jamais de déchets."""

    def test_tronquee_puis_valide_reessai_sur_messages_originaux(self, monkeypatch):
        reponses = [('{  "titre": "Suite tron', "length"), contenu(SCHEMA)]
        client = installer(monkeypatch, FakeClient(reponses))
        assert chat_json("s", "u", Exercice).titre == "Suites numériques"
        assert len(client.appels_chat) == 2
        messages = client.appels_chat[1]["messages"]
        assert len(messages) == 2  # system + user d'origine, sans la sortie tronquée
        assert all(m["content"] != "Suite tron" for m in messages)

    def test_500_puis_valide_reessai(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([erreur_api(500), contenu(SCHEMA)]))
        assert chat_json("s", "u", Exercice).titre == "Suites numériques"
        assert len(client.appels_chat) == 2
        assert len(client.appels_chat[1]["messages"]) == 2

    def test_500_deux_fois_llmerror(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([erreur_api(500)] * 2))
        with pytest.raises(LLMError, match="a rencontré une erreur"):
            chat_json("s", "u", Exercice)
        assert len(client.appels_chat) == 2

    def test_404_llmerror_apres_un_seul_appel(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([erreur_api(404)]))
        with pytest.raises(LLMError, match="ollama pull"):
            chat_json("s", "u", Exercice)
        assert len(client.appels_chat) == 1

    def test_404_cite_le_nom_du_modele(self, monkeypatch):
        installer(monkeypatch, FakeClient([erreur_api(404)]))
        with pytest.raises(LLMError, match=llm.LLM_MODEL):
            chat_json("s", "u", Exercice)


class TestEmbed:
    def test_liste_vide_appelle_pas_lapi(self, monkeypatch):
        client = installer(monkeypatch, FakeClient([]))
        resultat = embed([])
        assert resultat.shape == (0, 768)
        assert resultat.dtype.name == "float32"
        assert client.appels_embed == []

    def test_lignes_normalisees(self, monkeypatch):
        installer(monkeypatch, FakeClient([]))
        resultat = embed(["pythagore", "théorème de Thalès"])
        assert resultat.shape == (2, 8)
        assert np.linalg.norm(resultat, axis=1) == pytest.approx(1.0)

    def test_decoupage_en_lots(self, monkeypatch):
        from app import llm

        client = installer(monkeypatch, FakeClient([]))
        monkeypatch.setattr(llm, "EMBED_BATCH_SIZE", 2)
        embed(["a", "b", "c"])
        assert [len(lot) for lot in client.appels_embed] == [2, 1]
