"""Jeu d'évaluation fixe (PLAN.md §7).

8 cas : 4 exercices figés (Maths Terminale suites, Maths Première second degré,
Physique Terminale mouvement rectiligne, Philosophie Terminale introduction de
dissertation), chacun avec une bonne réponse et une réponse clairement fausse.

Critères de passage :
- les 8 réponses produisent un Grade (après au plus un réessai) ;
- toute bonne réponse obtient ≥ 14/20 ; toute réponse fausse ≤ 8/20 ;
- chaque cas est exécuté 3 fois (min/max affichés pour juger la stabilité).

Usage : python scripts/eval.py [--runs N] [--out notes/eval_results.md]
"""

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.banque import EX_DISSERT, EX_MOUVEMENT, EX_SECOND_DEGRE, EX_SUITES
from app.llm import LLMError
from app.schemas import Exercise
from app.tutor import _note_finale, grade_answer

SEUIL_BONNE = 14.0
SEUIL_FAUSSE = 8.0


@dataclass
class Cas:
    nom: str
    exercice: Exercise
    reponse: str
    bonne: bool


BONNE_SUITES = (
    "1. u_1 = 2*1 + 3 = 5 et u_2 = 2*5 + 3 = 13.\n"
    "2. Par récurrence. Initialisation : pour n = 0, u_0 = 1 et 4*2^0 - 3 = 4 - 3 = 1, "
    "donc la propriété est vraie au rang 0.\n"
    "Hérédité : supposons que u_n = 4*2^n - 3 pour un entier n. Alors "
    "u_{n+1} = 2u_n + 3 = 2(4*2^n - 3) + 3 = 8*2^n - 6 + 3 = 8*2^n - 3 = 4*2^{n+1} - 3. "
    "La propriété est donc héréditaire.\n"
    "Conclusion : pour tout n dans N, u_n = 4*2^n - 3.\n"
    "3. u_10 = 4*2^10 - 3 = 4096 - 3 = 4093."
)

FAUSSE_SUITES = (
    "1. u_1 = 2*1 + 3 = 5 et u_2 = 2*5 + 3 = 11.\n"
    "2. C'est évident : la suite est arithmétique de raison 3, donc u_n = u_0 + 3n = 1 + 3n. "
    "Pas besoin de récurrence.\n"
    "3. u_10 = 1 + 3*10 = 31."
)

BONNE_SECOND_DEGRE = (
    "1. Δ = b² - 4ac = (-5)² - 4×1×6 = 25 - 24 = 1.\n"
    "2. Δ > 0 donc deux racines : x_1 = (5 - 1)/2 = 2 et x_2 = (5 + 1)/2 = 3. "
    "S = {2 ; 3}.\n"
    "3. Factorisation : x² - 5x + 6 = (x - 2)(x - 3).\n"
    "4. Tableau de signes : le trinôme est positif à l'extérieur des racines et négatif "
    "entre les racines : positif sur ]-∞ ; 2[, nul en 2, négatif sur ]2 ; 3[, nul en 3, "
    "positif sur ]3 ; +∞[."
)

FAUSSE_SECOND_DEGRE = (
    "1. Δ = b² + 4ac = 25 + 24 = 49.\n"
    "2. x_1 = (5 + 7)/2 = 6 et x_2 = (5 - 7)/2 = -1. S = {6 ; -1}.\n"
    "3. x² - 5x + 6 = (x - 6)(x + 1).\n"
    "4. Le trinôme est toujours positif car a = 1 > 0."
)

BONNE_MOUVEMENT = (
    "1. x(t) = (1/2)a t² + v_0 t + x_0 = 1,5 t² + 2 t (en mètres).\n"
    "2. v(t) = v_0 + a t = 2 + 3t, donc v(4) = 2 + 12 = 14 m/s.\n"
    "3. x(4) = 1,5 × 16 + 2 × 4 = 24 + 8 = 32 m. Distance parcourue : 32 m."
)

FAUSSE_MOUVEMENT = (
    "1. x(t) = a t² + v_0 t = 3 t² + 2 t.\n"
    "2. v(t) = a t = 3 t, donc v(4) = 12 m/s.\n"
    "3. x(4) = 3 × 16 = 48 m."
)

BONNE_DISSERT = (
    "Introduction.\n"
    "Accroche : quand je choisissais ma filière en terminale, j'avais le sentiment "
    "d'un choix libre ; pourtant mes notes, ma famille et mon environnement ont pesé "
    "sur cette décision.\n"
    "Analyse du sujet : la liberté, c'est le pouvoir de se déterminer soi-même, sans "
    "contrainte. La qualifier d'illusion, c'est supposer qu'elle n'est qu'une apparence. "
    "Le paradoxe : l'expérience commune atteste mon libre arbitre, mais les sciences "
    "humaines et la physique montrent que tout est déterminé par des causes.\n"
    "Problématique : comment concilier le sentiment de liberté avec le déterminisme ? "
    "La liberté est-elle autre chose qu'une illusion nécessaire ?\n"
    "Annonce du plan : d'abord, la liberté comme illusion du déterminisme (Spinoza) ; "
    "ensuite, la liberté comme essence de la conscience (Sartre) ; enfin, une liberté "
    "comprise comme reconnaissance de la nécessité."
)

FAUSSE_DISSERT = (
    "Oui, la liberté est une illusion car tout est déterminé. Je vais d'abord parler "
    "de Spinoza, ensuite de Sartre et enfin je vais conclure. Spinoza dit que les "
    "hommes se croient libres parce qu'ils ignorent les causes. Sartre dit le contraire. "
    "Donc la liberté n'existe pas."
)

CAS: list[Cas] = [
    Cas("Maths T · suites — bonne réponse", EX_SUITES, BONNE_SUITES, True),
    Cas("Maths T · suites — réponse fausse", EX_SUITES, FAUSSE_SUITES, False),
    Cas("Maths 1re · 2nd degré — bonne réponse", EX_SECOND_DEGRE, BONNE_SECOND_DEGRE, True),
    Cas("Maths 1re · 2nd degré — réponse fausse", EX_SECOND_DEGRE, FAUSSE_SECOND_DEGRE, False),
    Cas("Physique T · MRUA — bonne réponse", EX_MOUVEMENT, BONNE_MOUVEMENT, True),
    Cas("Physique T · MRUA — réponse fausse", EX_MOUVEMENT, FAUSSE_MOUVEMENT, False),
    Cas("Philo T · intro dissert — bonne réponse", EX_DISSERT, BONNE_DISSERT, True),
    Cas("Philo T · intro dissert — réponse fausse", EX_DISSERT, FAUSSE_DISSERT, False),
]


def executer(runs: int) -> tuple[list[str], bool]:
    """Exécute les cas ; renvoie (lignes du tableau, succès global)."""
    lignes: list[str] = []
    succes_global = True
    for cas in CAS:
        notes: list[float | None] = []
        sources: list[str] = []
        for _ in range(runs):
            try:
                grade = grade_answer(cas.exercice, cas.reponse, "Terminale")
                notes.append(grade.note)
                sources.append(_note_finale(grade)[1])
            except LLMError:
                notes.append(None)
                sources.append("erreur")
        if all(n is not None for n in notes):
            mini, maxi = min(notes), max(notes)  # type: ignore[type-var]
            passe = mini >= SEUIL_BONNE if cas.bonne else maxi <= SEUIL_FAUSSE
            attendu = f"≥ {SEUIL_BONNE:.0f}" if cas.bonne else f"≤ {SEUIL_FAUSSE:.0f}"
            notes_txt = f"{mini:>4.1f} / {maxi:>4.1f}"
        else:
            passe = False
            attendu = f"≥ {SEUIL_BONNE:.0f}" if cas.bonne else f"≤ {SEUIL_FAUSSE:.0f}"
            notes_txt = "erreur (timeout/parse)"
        succes_global = succes_global and passe
        lignes.append(
            f"| {cas.nom} | {attendu} | {notes_txt} | {' / '.join(sources)} | "
            f"{'✅' if passe else '❌'} |"
        )
    return lignes, succes_global


def main() -> int:
    parseur = argparse.ArgumentParser(description="Jeu d'évaluation fixe de Sunu Jàng")
    parseur.add_argument("--runs", type=int, default=3, help="exécutions par cas")
    parseur.add_argument(
        "--out", default="notes/eval_results.md", help="fichier de résultat"
    )
    args = parseur.parse_args()

    from app.config import LLM_MODEL

    print(f"Jeu d'évaluation Sunu Jàng — modèle : {LLM_MODEL} — {args.runs} runs/cas\n")
    debut = time.time()
    lignes, succes = executer(args.runs)
    duree = time.time() - debut

    entete = [
        f"# Résultats d'évaluation — {time.strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Modèle : `{LLM_MODEL}` · {args.runs} exécutions par cas · durée : {duree:.0f} s",
        "",
        "| Cas | Attendu | min / max | Sources | Pass |",
        "|---|---|---|---|---|",
    ]
    rapport = "\n".join(entete + lignes + ["", f"**Succès global : {'OUI' if succes else 'NON'}**"])
    print(rapport)

    chemin = Path(args.out)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(rapport + "\n", encoding="utf-8")
    print(f"\nRésultats écrits dans {chemin}")
    return 0 if succes else 1


if __name__ == "__main__":
    raise SystemExit(main())
