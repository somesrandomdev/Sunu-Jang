"""Interface Gradio (Blocks), en français. Lancement : python -m app.ui"""

import gradio as gr

from app.banque import BANQUE_PAR_MATIERE
from app.config import TOP_K
from app.llm import LLMError
from app.rag import MATIERES_PAR_LIBELLE, charger_index, retrieve
from app.schemas import Exercise, Grade
from app.tutor import (
    generate_exercise,
    grade_answer,
    next_difficulty,
    transcrire_copie,
)

MATIERES = list(MATIERES_PAR_LIBELLE)
NIVEAUX = ["Seconde", "Première", "Terminale"]
CHOIX_DIFFICULTE = [("Facile", "facile"), ("Moyen", "moyen"), ("Difficile", "difficile")]

NOTE_VIDE = "– / 20"


def _note_html(note: float) -> str:
    if note >= 15:
        couleur = "#1a7f37"  # vert
    elif note >= 10:
        couleur = "#b45309"  # orange
    else:
        couleur = "#c62828"  # rouge
    return f"<h1 style='color:{couleur}; margin:0'>Note : {note:g} / 20</h1>"


def _sources_update(chunks: list[dict]):
    vues: list[str] = []
    for chunk in chunks:
        mention = f"**{chunk['source_file']}** p.{chunk['page']}"
        if mention not in vues:
            vues.append(mention)
    if not vues:
        return gr.update(value="", visible=False)
    return gr.update(value="Inspiré de : " + " · ".join(vues), visible=True)


def _exercice_markdown(exercice: Exercise) -> str:
    competences = ", ".join(exercice.competences_evaluees)
    return (
        f"### {exercice.titre}\n\n{exercice.enonce}\n\n"
        f"*Barème : {exercice.bareme}*\n\n*Compétences : {competences}*"
    )


SORTIES_EXERCICE = [
    "enonce",
    "sources",
    "exercice_state",
    "reponse",
    "note",
    "points_forts",
    "erreurs",
    "correction",
    "conseil",
    "resultats",
]


def generer_exercice(matiere: str, niveau: str, difficulte: str, theme: str):
    """Génère un exercice, ancré dans les annales quand l'index existe.

    Si la génération échoue et que la banque a un exercice pour cette matière,
    on montre l'exercice de la banque (clairement étiqueté, jamais présenté
    comme généré) : la correction reste elle exécutée en direct.
    """
    matiere_token = MATIERES_PAR_LIBELLE.get(matiere)
    requete = theme.strip() or f"exercice de {matiere} niveau {niveau}"
    try:
        # retrieve appelle embed() : il peut lever LLMError si Ollama est arrêté
        chunks = retrieve(requete, k=TOP_K, matiere=matiere_token)
        exercice = generate_exercise(
            matiere,
            niveau,
            difficulte,
            theme,
            extraits=[c["texte"] for c in chunks],
        )
    except LLMError as exc:
        exercice_secours = BANQUE_PAR_MATIERE.get(matiere)
        if exercice_secours is None:
            raise gr.Error(str(exc)) from exc
        gr.Warning("Génération indisponible : voici un exercice de la banque.")
        return (
            _exercice_markdown(exercice_secours),
            gr.update(
                value="Exercice de la banque (rédigé à la main, non généré)",
                visible=True,
            ),
            exercice_secours,
            "",  # réponse réinitialisée
            NOTE_VIDE,
            "",
            "",
            "",
            "",
            gr.update(visible=False),
        )
    return (
        _exercice_markdown(exercice),
        _sources_update(chunks),
        exercice,
        "",  # réponse réinitialisée
        NOTE_VIDE,
        "",
        "",
        "",
        "",
        gr.update(visible=False),
    )


def corriger(exercice: Exercise | None, reponse: str, niveau: str, depuis_photo: bool):
    """Note la réponse et affiche le bilan : note, forces, erreurs, conseil."""
    if exercice is None:
        # gr.Error (et non gr.Warning, simple fonction depuis Gradio 5) est
        # l'exception qui affiche un toast sans stack trace côté élève.
        raise gr.Error("Générez d'abord un exercice.")
    try:
        grade: Grade = grade_answer(exercice, reponse, niveau)
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc
    except LLMError as exc:
        raise gr.Error(str(exc)) from exc
    points_forts = "\n".join(f"- ✅ {p}" for p in grade.points_forts) or "- (aucun)"
    erreurs = "\n".join(f"- ❌ {e}" for e in grade.erreurs) or "- (aucune)"
    return (
        _note_html(grade.note),
        points_forts,
        erreurs,
        grade.correction_detaillee,
        f"💡 {grade.conseil}",
        grade.note,  # mémorisée pour la progression adaptative
        gr.update(visible=True),
        gr.update(visible=depuis_photo),
    )


def lire_copie(exercice: Exercise | None, image_chemin: str | None):
    """Transcrit la photo de copie dans la zone « Ta réponse » (modifiable).

    La correction reste inchangée : l'élève vérifie la transcription avant
    de cliquer sur Corriger.
    """
    if exercice is None:
        raise gr.Error("Générez d'abord un exercice.")
    if not image_chemin:
        raise gr.Error("Envoyez d'abord une photo de votre copie.")
    try:
        texte = transcrire_copie(exercice, image_chemin)
    except (ValueError, LLMError) as exc:
        raise gr.Error(str(exc)) from exc
    gr.Info(
        "Transcription automatique : vérifie-la et corrige-la si besoin "
        "avant de cliquer sur Corriger."
    )
    return texte, True  # la réponse vient d'une photo (note dans les résultats)


def _reset_zone_photo():
    """Nouvel exercice : efface la photo, désactive « Lire ma copie »,
    réinitialise l'indicateur « réponse issue d'une photo »."""
    return (
        gr.update(value=None),
        gr.update(interactive=False),
        False,
        gr.update(visible=False),
        gr.update(visible=False),
    )


def preparer_suivant(note: float | None, difficulte_actuelle: str):
    """Difficulté du prochain exercice : plus facile si note < 10, etc."""
    if note is None:
        return gr.update()
    return gr.update(value=next_difficulty(note, difficulte_actuelle))


def construire_demo(mode_sans_annales: bool | None = None):
    """Construit l'app Gradio (séparé de launch pour pouvoir tester)."""
    if mode_sans_annales is None:
        _, meta_index = charger_index()
        mode_sans_annales = not meta_index

    with gr.Blocks(title="Sunu Jàng — Professeur particulier BAC") as demo:
        gr.Markdown(
            "# 🇸🇳 Sunu Jàng\n**Professeur particulier pour le BAC sénégalais — "
            "100 % local.**"
        )
        if mode_sans_annales:
            gr.Markdown(
                "⚠️ **Mode sans annales** : aucun index trouvé dans `data/index/`. "
                "Les exercices ne seront pas ancrés dans les annales réelles. "
                "Ajoutez des PDF dans `data/annales/` puis lancez "
                "`python scripts/ingest.py` (voir `data/SOURCES.md`)."
            )

        exercice_state = gr.State(None)  # Exercise courant ; le corrigé n'est jamais affiché
        note_state = gr.State(None)  # dernière note obtenue
        photo_flag = gr.State(False)  # la réponse actuelle vient d'une photo

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 1. Choisis ton exercice")
                matiere = gr.Dropdown(MATIERES, label="Matière", value="Maths")
                niveau = gr.Dropdown(NIVEAUX, label="Niveau", value="Terminale")
                difficulte = gr.Dropdown(
                    CHOIX_DIFFICULTE, label="Difficulté", value="moyen"
                )
                theme = gr.Textbox(
                    label="Thème (facultatif)",
                    placeholder="ex. suites numériques, mouvement rectiligne…",
                )
                bouton_generer = gr.Button("✨ Nouvel exercice", variant="primary")

            with gr.Column(scale=2):
                gr.Markdown("### 2. Travaille puis fais-toi corriger")
                enonce = gr.Markdown(
                    "*Ton exercice apparaîtra ici.*",
                    latex_delimiters=[
                        {"left": "$", "right": "$", "display": False},
                        {"left": "$$", "right": "$$", "display": True},
                    ],
                )
                sources = gr.Markdown("", visible=False)
                reponse = gr.Textbox(
                    label="Ta réponse",
                    placeholder="Rédige ta solution ici, étape par étape…",
                    lines=8,
                )
                image_copie = gr.Image(
                    type="filepath",
                    sources=["upload", "webcam"],
                    label="…ou envoie une photo de ta copie",
                )
                statut_lecture = gr.Markdown("", visible=False)
                bouton_lire = gr.Button("📷 Lire ma copie", interactive=False)
                bouton_corriger = gr.Button(
                    "📝 Corriger", variant="primary", interactive=False
                )

                with gr.Column(visible=False) as resultats:
                    note = gr.Markdown(NOTE_VIDE)
                    note_photo = gr.Markdown(
                        "📷 Corrigé à partir d'une photo "
                        "(transcription vérifiée par l'élève)",
                        visible=False,
                    )
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### Points forts")
                            points_forts = gr.Markdown()
                        with gr.Column():
                            gr.Markdown("#### Erreurs")
                            erreurs = gr.Markdown()
                    with gr.Accordion("Correction détaillée", open=True):
                        correction = gr.Markdown()
                    conseil = gr.Markdown()
                    bouton_suivant = gr.Button("➡️ Exercice suivant")

        sortie_exercice = [enonce, sources, exercice_state, reponse, note,
                           points_forts, erreurs, correction, conseil, resultats]
        sortie_zone_photo = [image_copie, bouton_lire, photo_flag,
                             note_photo, statut_lecture]

        bouton_generer.click(
            generer_exercice,
            inputs=[matiere, niveau, difficulte, theme],
            outputs=sortie_exercice,
        ).then(
            _reset_zone_photo,
            outputs=sortie_zone_photo,
        )

        # « Corriger » actif seulement si un exercice existe et la réponse est non vide
        reponse.change(
            lambda rep, exo: gr.update(
                interactive=bool(rep.strip()) and exo is not None
            ),
            inputs=[reponse, exercice_state],
            outputs=[bouton_corriger],
        )

        # « Lire ma copie » actif seulement si un exercice existe et une image est chargée
        image_copie.change(
            lambda img, exo: gr.update(interactive=bool(img) and exo is not None),
            inputs=[image_copie, exercice_state],
            outputs=[bouton_lire],
        )

        bouton_lire.click(
            lambda: gr.update(
                visible=True, value="⏳ Lecture de la copie… (~1–2 min)"
            ),
            outputs=[statut_lecture],
        ).then(
            lire_copie,
            inputs=[exercice_state, image_copie],
            outputs=[reponse, photo_flag],
        ).then(
            lambda: gr.update(visible=False),
            outputs=[statut_lecture],
        )

        bouton_corriger.click(
            corriger,
            inputs=[exercice_state, reponse, niveau, photo_flag],
            outputs=[note, points_forts, erreurs, correction, conseil,
                     note_state, resultats, note_photo],
        )

        # Exercice suivant : difficulté adaptée à la note, puis régénération
        bouton_suivant.click(
            preparer_suivant, inputs=[note_state, difficulte], outputs=[difficulte]
        ).then(
            generer_exercice,
            inputs=[matiere, niveau, difficulte, theme],
            outputs=sortie_exercice,
        ).then(
            _reset_zone_photo,
            outputs=sortie_zone_photo,
        )

    return demo


def main() -> None:
    construire_demo().launch()


if __name__ == "__main__":
    main()
