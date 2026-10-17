"""Logique métier : generate_exercise, grade_answer, next_difficulty."""

from app.llm import chat_json
from app.prompts import (
    CONTEXTE_ANNALE,
    GENERATE_EXERCISE,
    GRADE_ANSWER,
    SYSTEM_FR,
)
from app.schemas import Exercise, Grade

THEME_PAR_DEFAUT = "au choix, conforme au programme"

# Générations : un peu de créativité ; corrections : déterministe (PLAN.md §6 M1).
TEMPERATURE_GENERATION = 0.4
TEMPERATURE_CORRECTION = 0.1
# Bornes de longueur de sortie : les petits modèles locaux ignorent parfois
# les consignes de concision, ce qui fait exploser la latence CPU.
MAX_TOKENS_GENERATION = 900
MAX_TOKENS_CORRECTION = 520

DIFFICULTES = ["facile", "moyen", "difficile"]


def generate_exercise(
    matiere: str,
    niveau: str,
    difficulte: str,
    theme: str = "",
    extraits: list[str] | None = None,
) -> Exercise:
    """Génère un exercice, éventuellement ancré dans des extraits d'annales."""
    if extraits:
        contexte = CONTEXTE_ANNALE.format(extraits="\n\n".join(extraits))
    else:
        contexte = ""  # pas d'en-tête avec un contenu vide (PLAN.md §5)
    theme_effectif = theme.strip() or THEME_PAR_DEFAUT
    systeme = SYSTEM_FR.format(niveau=niveau)
    utilisateur = GENERATE_EXERCISE.format(
        matiere=matiere,
        niveau=niveau,
        difficulte=difficulte,
        theme=theme_effectif,
        contexte_annale=contexte,
    )
    return chat_json(
        systeme,
        utilisateur,
        Exercise,
        TEMPERATURE_GENERATION,
        MAX_TOKENS_GENERATION,
    )


def grade_answer(exercise: Exercise, reponse_eleve: str, niveau: str) -> Grade:
    """Note une réponse d'élève sur 20 à partir du corrigé de référence."""
    if not reponse_eleve.strip():
        raise ValueError("La réponse de l'élève est vide : rien à corriger.")
    systeme = SYSTEM_FR.format(niveau=niveau)
    utilisateur = GRADE_ANSWER.format(
        niveau=niveau,
        enonce=exercise.enonce,
        bareme=exercise.bareme,
        corrige=exercise.corrige,
        reponse_eleve=reponse_eleve,
    )
    return chat_json(
        systeme,
        utilisateur,
        Grade,
        TEMPERATURE_CORRECTION,
        MAX_TOKENS_CORRECTION,
    )


def next_difficulty(note: float, current: str) -> str:
    """Suggestion de difficulté : plus facile si note < 10, pareil si 10–14,
    plus dur si ≥ 15, bornée aux extrêmes de l'échelle."""
    if current not in DIFFICULTES:
        raise ValueError(f"Difficulté inconnue : {current!r}")
    index = DIFFICULTES.index(current)
    if note < 10:
        index -= 1
    elif note >= 15:
        index += 1
    index = max(0, min(len(DIFFICULTES) - 1, index))
    return DIFFICULTES[index]
