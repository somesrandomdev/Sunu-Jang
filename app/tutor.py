"""Logique métier : generate_exercise, grade_answer, next_difficulty."""

import logging
import re

from app.copie import preparer_image
from app.llm import chat_json, chat_vision
from app.prompts import (
    CONTEXTE_ANNALE,
    GENERATE_EXERCISE,
    GRADE_ANSWER,
    SYSTEM_FR,
    TRANSCRIRE_COPIE,
)
from app.schemas import Exercise, Grade

logger = logging.getLogger(__name__)

THEME_PAR_DEFAUT = "au choix, conforme au programme"

# Générations : un peu de créativité ; corrections : déterministe (PLAN.md §6 M1).
TEMPERATURE_GENERATION = 0.4
TEMPERATURE_CORRECTION = 0.1
# Bornes de longueur de sortie : les petits modèles locaux ignorent parfois
# les consignes de concision, ce qui fait exploser la latence CPU.
MAX_TOKENS_GENERATION = 900
MAX_TOKENS_CORRECTION = 620  # le champ points_par_question coûte ~60 tokens

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


# Ligne « Total : n/20 » demandée au modèle dans correction_detaillee ; la note
# JSON est parfois incohérente avec cette somme détaillée, on s'y fie en priorité.
_MOTIF_TOTAL = re.compile(r"Total\s*:\s*(\d+(?:[.,]\d+)?)\s*/\s*20", re.IGNORECASE)
# Lignes « Q1 : 4/4 » : le modèle détaille souvent un barème juste (somme 20/20)
# mais met une autre note dans le JSON (Gate 2) — on refait la somme nous-mêmes.
_MOTIF_QUESTION = re.compile(r"Q\s*(\d+)\s*:\s*(\d+(?:[.,]\d+)?)\s*/\s*(\d+(?:[.,]\d+)?)")


def _nombre(texte: str) -> float:
    return float(texte.replace(",", "."))


def _note_finale(grade: Grade) -> tuple[float, str]:
    """Note finale et sa source, par ordre de fiabilité décroissante.

    - "points" : le champ points_par_question du JSON, si exploitable
      (≥ 1 entrée, questions uniques, somme des max = 20) → somme des obtenu ;
    - "lignes" : les lignes « Qn : a/b » de la correction détaillée
      (dernière occurrence de chaque Qn, chaque a ≤ b, somme des b = 20) ;
    - "total" : la dernière ligne « Total : n/20 » ;
    - "json" : le champ note du modèle (dernier recours, le plus bruité :
      12/20 pour une copie à 20/20 — voir notes/vision_smoke_test.md).
    """
    entrees = grade.points_par_question
    if (
        entrees
        and len({entree.question for entree in entrees}) == len(entrees)
        and abs(sum(entree.max for entree in entrees) - 20) <= 0.01
    ):
        return sum(entree.obtenu for entree in entrees), "points"
    questions: dict[str, tuple[float, float]] = {}
    for numero, points, sur in _MOTIF_QUESTION.findall(grade.correction_detaillee):
        questions[numero] = (_nombre(points), _nombre(sur))
    if (
        questions
        and all(points <= sur for points, sur in questions.values())
        and abs(sum(sur for _, sur in questions.values()) - 20) <= 0.01
    ):
        return sum(points for points, _ in questions.values()), "lignes"
    totaux = _MOTIF_TOTAL.findall(grade.correction_detaillee)
    if totaux:
        return _nombre(totaux[-1]), "total"
    return grade.note, "json"


def grade_answer(exercise: Exercise, reponse_eleve: str, niveau: str) -> Grade:
    """Note une réponse d'élève sur 20 à partir du corrigé de référence.

    La note vient de _note_finale (points_par_question, puis lignes « Qn »,
    puis « Total : n/20 », puis note JSON) ; toujours bornée [0, 20].
    """
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
    grade = chat_json(
        systeme,
        utilisateur,
        Grade,
        TEMPERATURE_CORRECTION,
        MAX_TOKENS_CORRECTION,
    )
    note, source = _note_finale(grade)
    logger.info("Note %.1f/20 — source : %s", note, source)
    return Grade.model_validate({**grade.model_dump(), "note": note})


def transcrire_copie(exercise: Exercise, chemin: str) -> str:
    """Transcrit une photo de copie manuscrite avec le modèle vision.

    Renvoie le texte brut (jamais du JSON). ValueError avec message français
    si l'image ne contient pas de copie ou est trop peu lisible.
    """
    image_png = preparer_image(chemin)
    # PAS d'énoncé dans le prompt (Gate 1b : le modèle le recopiait pour les
    # questions non traitées) — v2 : liste des questions seulement.
    texte = chat_vision(
        "Tu transcris fidèlement des copies manuscrites d'élèves.",
        TRANSCRIRE_COPIE,
        image_png,
    )
    if texte.strip().upper().startswith("AUCUNE_COPIE"):
        raise ValueError("Aucune copie détectée sur l'image.")
    lignes = [ligne for ligne in texte.splitlines() if ligne.strip()]
    illisibles = sum(1 for ligne in lignes if "[illisible]" in ligne)
    if lignes and illisibles > len(lignes) / 2:
        raise ValueError(
            "Copie trop peu lisible : reprends la photo à plat, bien éclairée."
        )
    return texte.strip()


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
