"""Client LLM : chat_json(system, user, schema) et embed(texts) via Ollama.

Le client parle le protocole compatible OpenAI exposé par Ollama
(`OLLAMA_BASE_URL/v1`). Le même code fonctionne donc avec toute API
compatible OpenAI, via les variables d'environnement uniquement.
"""

import json
import re
from collections.abc import Sequence
from typing import TypeVar

import numpy as np
from openai import APIConnectionError, APITimeoutError, OpenAI
from pydantic import BaseModel, ValidationError

from app.config import EMBED_MODEL, LLM_API_KEY, LLM_MODEL, OLLAMA_BASE_URL

# Délai maximal d'une requête au modèle (PLAN.md §6 M1).
TIMEOUT_S = 120.0

# Taille d'un lot d'embeddings envoyé à l'API.
EMBED_BATCH_SIZE = 32

# Dimension des vecteurs de nomic-embed-text (sert uniquement pour
# renvoyer une forme (0, dim) sur une liste d'entrées vide).
EMBED_DIM = 768

ModelT = TypeVar("ModelT", bound=BaseModel)

_client: OpenAI | None = None


class LLMError(RuntimeError):
    """Erreur à montrer à l'élève (message en français, jamais de stack trace)."""


def get_client() -> OpenAI:
    """Client OpenAI pointé vers Ollama (créé au premier appel ; mockable en test)."""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=f"{OLLAMA_BASE_URL.rstrip('/')}/v1",
            api_key=LLM_API_KEY,
            timeout=TIMEOUT_S,
            max_retries=0,  # les réessais JSON sont gérés par chat_json
        )
    return _client


# 1) Antislashs LaTeX qui n'ouvrent PAS un échappement JSON valide (\in, \Delta,
#    \pi…) : json.loads les refuse, on les double dans le texte brut.
_ECHAP_INVALIDES = re.compile(r'\\(?![\\/"bfnrtu])')

# 2) Commandes LaTeX dont l'initiale forme AUSSI un échappement JSON valide
#    (\times est décodé « tab + imes », \bbr « retour arrière + br »…).
#    La limite (?![a-z]) évite de doubler un vrai \n devant un mot (ex. \nnuage).
_LATEX_ECHAP_JSON = re.compile(
    r"\\(?=(?:times|tau|theta|therefore|text|tfrac|frac|forall|flat|begin|bar|beta"
    r"|boldsymbol|neq|nabla|notin|nu|nmid|right|rho|rightarrow|rangle|underline"
    r"|underbrace|unit)(?![a-z]))"
)


def _extraire_json(texte: str) -> dict:
    r"""Extrait l'objet JSON d'une réponse du modèle.

    Gère : blancs autour, balises ```json ... ```, prose avant/après le JSON
    (on prend alors le premier objet équilibré), et commandes LaTeX mal
    échappées dans les chaînes (\times, \frac, \in, \Delta…).
    """
    nettoye = texte.strip()
    if nettoye.startswith("```"):
        premiere_ligne, *reste = nettoye.splitlines()
        if "```" not in premiere_ligne or not reste:
            raise ValueError("bloc de code mal formé")
        nettoye = "\n".join(reste).rsplit("```", 1)[0].strip()
    nettoye = _ECHAP_INVALIDES.sub(r"\\\\", nettoye)
    nettoye = _LATEX_ECHAP_JSON.sub(r"\\\\", nettoye)
    try:
        return json.loads(nettoye)
    except json.JSONDecodeError:
        pass
    # Prose autour du JSON : chercher le premier objet { ... } équilibré.
    debut, profondeur = nettoye.find("{"), 0
    if debut == -1:
        raise ValueError("aucun objet JSON trouvé")
    for i in range(debut, len(nettoye)):
        if nettoye[i] == "{":
            profondeur += 1
        elif nettoye[i] == "}":
            profondeur -= 1
            if profondeur == 0:
                return json.loads(nettoye[debut : i + 1])
    raise ValueError("objet JSON non fermé")


def chat_json(
    system: str,
    user: str,
    schema: type[ModelT],
    temperature: float = 0.4,
    max_tokens: int | None = None,
) -> ModelT:
    """Interroge le modèle et renvoie la réponse validée par `schema`.

    Un échec de parsing/validation déclenche exactement un réessai ;
    au second échec, lève LLMError avec un message en français.
    `max_tokens` borne la longueur de sortie (les petits modèles locaux
    ignorent parfois les consignes de concision).
    """
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    derniere_erreur: str = ""
    for _tentative in (1, 2):
        try:
            reponse = get_client().chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
            )
        except APITimeoutError as exc:  # sous-classe de APIConnectionError
            raise _erreur_connexion() from exc
        except APIConnectionError as exc:
            raise _erreur_connexion() from exc
        contenu = reponse.choices[0].message.content or ""
        try:
            donnees = _extraire_json(contenu)
            return schema.model_validate(donnees)
        except (ValueError, json.JSONDecodeError, ValidationError) as exc:
            derniere_erreur = str(exc)[:500]
            messages = messages + [
                {"role": "assistant", "content": contenu},
                {
                    "role": "user",
                    "content": (
                        "Ta réponse précédente était invalide : "
                        f"{derniere_erreur}. Renvoie uniquement le JSON corrigé."
                    ),
                },
            ]
    raise LLMError(
        "Le modèle n'a pas renvoyé de réponse exploitable après deux essais. "
        "Relancez la génération."
    )


def embed(texts: Sequence[str]) -> np.ndarray:
    """Embeddings float32, lignes L2-normalisées. Liste vide -> forme (0, dim)."""
    if not texts:
        return np.zeros((0, EMBED_DIM), dtype=np.float32)
    vecteurs: list[list[float]] = []
    for debut in range(0, len(texts), EMBED_BATCH_SIZE):
        lot = texts[debut : debut + EMBED_BATCH_SIZE]
        try:
            reponse = get_client().embeddings.create(model=EMBED_MODEL, input=lot)
        except APITimeoutError as exc:  # sous-classe de APIConnectionError
            raise _erreur_connexion() from exc
        except APIConnectionError as exc:
            raise _erreur_connexion() from exc
        vecteurs.extend(item.embedding for item in reponse.data)
    matrice = np.asarray(vecteurs, dtype=np.float32)
    normes = np.linalg.norm(matrice, axis=1, keepdims=True)
    return matrice / np.maximum(normes, 1e-12)


def _erreur_connexion() -> LLMError:
    return LLMError(
        "Le modèle local ne répond pas. Vérifiez qu'Ollama est lancé."
    )
