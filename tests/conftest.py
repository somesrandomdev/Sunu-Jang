"""Fabrique d'un faux client OpenAI : les tests passent avec Ollama arrêté."""

from typing import Any

import httpx
import numpy as np
from openai import APIConnectionError


class _Message:
    def __init__(self, content: str) -> None:
        self.content = content


class _Choice:
    def __init__(self, content: str, finish_reason: str) -> None:
        self.message = _Message(content)
        self.finish_reason = finish_reason


class _ChatResponse:
    def __init__(self, content: str, finish_reason: str = "stop") -> None:
        self.choices = [_Choice(content, finish_reason)]


class _Embedding:
    def __init__(self, vecteur: list[float], index: int) -> None:
        self.embedding = vecteur
        self.index = index
        self.object = "embedding"


class _EmbedResponse:
    def __init__(self, embeddings: list[list[float]]) -> None:
        self.data = [_Embedding(v, i) for i, v in enumerate(embeddings)]


class FakeClient:
    """Client OpenAI factice : renvoie les réponses préparées, dans l'ordre.

    Chaque entrée de `reponses` est :
    - une str : contenu renvoyé (finish_reason "stop") ;
    - un tuple (contenu, finish_reason) : ex. ("...", "length") ;
    - une Exception : levée telle quelle (ex. InternalServerError, NotFoundError).
    `fail_connexion` lève une APIConnectionError au lieu de répondre.
    Chaque appel est enregistré (modèle, température, messages) pour les
    assertions des tests.
    """

    def __init__(
        self,
        reponses: list,
        fail_connexion: bool = False,
        dim_embedding: int = 8,
    ) -> None:
        self._reponses = list(reponses)
        self._fail_connexion = fail_connexion
        self._dim = dim_embedding
        self.appels_chat: list[dict[str, Any]] = []
        self.appels_embed: list[list[str]] = []

        class _Completions:
            @staticmethod
            def create(**kwargs: Any) -> _ChatResponse:
                self.appels_chat.append(kwargs)
                if self._fail_connexion:
                    raise APIConnectionError(
                        request=httpx.Request("POST", "http://test/v1/chat/completions")
                    )
                if not self._reponses:
                    raise AssertionError("plus de réponse préparée que d'appel")
                reponse = self._reponses.pop(0)
                if isinstance(reponse, Exception):
                    raise reponse
                if isinstance(reponse, tuple):
                    contenu, raison = reponse
                    return _ChatResponse(contenu, raison)
                return _ChatResponse(reponse)

        class _Embeddings:
            @staticmethod
            def create(**kwargs: Any) -> _EmbedResponse:
                entrees = kwargs["input"]
                self.appels_embed.append(list(entrees))
                vecteurs = [
                    np.random.default_rng(abs(hash(t)) % 2**32).normal(size=self._dim).tolist()
                    for t in entrees
                ]
                return _EmbedResponse(vecteurs)

        self.chat = type("Chat", (), {"completions": _Completions()})()
        self.embeddings = type("Embeddings", (), {"create": staticmethod(_Embeddings.create)})()


def installer(monkeypatch, client: FakeClient) -> FakeClient:
    """Branche le faux client dans app.llm (get_client le renverra tel quel)."""
    from app import llm

    monkeypatch.setattr(llm, "_client", client)
    return client
