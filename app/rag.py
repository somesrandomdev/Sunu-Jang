"""RAG : ingestion des annales PDF -> chunks -> embeddings -> index NumPy ; retrieve().

L'index tient dans quelques centaines de chunks : un tableau NumPy et un JSON
de métadonnées suffisent, pas besoin d'une base vectorielle.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
from pypdf import PdfReader

from app.config import TOP_K
from app.llm import embed

logger = logging.getLogger(__name__)

RACINE_DATA = Path(__file__).resolve().parents[1] / "data"
DOSSIER_ANNALES = RACINE_DATA / "annales"
DOSSIER_INDEX = RACINE_DATA / "index"

TAILLE_CHUNK = 800
CHEVAUCHEMENT = 150
# Une page qui donne moins de caractères est considérée scannée/vide.
MIN_CARACTERES_PAGE = 50

# Correspondance libellé UI -> token de nommage des fichiers (maths_S2_2023.pdf).
MATIERES_PAR_LIBELLE = {
    "Maths": "maths",
    "Physique-Chimie": "physique",
    "SVT": "svt",
    "Philosophie": "philo",
}


def parser_nom_fichier(nom: str) -> dict[str, Any]:
    """Extrait {matiere, serie, annee} du nom `matiere_serie_annee.pdf` (null si absent)."""
    parties = Path(nom).stem.split("_")
    if len(parties) == 3:
        matiere, serie, annee = parties
        return {
            "matiere": matiere or None,
            "serie": serie or None,
            "annee": int(annee) if annee.isdigit() else None,
        }
    return {"matiere": None, "serie": None, "annee": None}


def decouper_texte(
    texte: str, taille: int = TAILLE_CHUNK, chevauchement: int = CHEVAUCHEMENT
) -> list[str]:
    """Découpe un texte en morceaux d'environ `taille` caractères.

    On regroupe les paragraphes tant que possible ; un paragraphe trop long
    est coupé brutalement avec `chevauchement` caractères de recouvrement.
    """
    texte = texte.strip()
    if not texte:
        return []
    if chevauchement >= taille:
        raise ValueError("chevauchement doit être inférieur à taille")
    paragraphes = [p.strip() for p in re.split(r"\n+", texte) if p.strip()]
    chunks: list[str] = []
    courant = ""
    for para in paragraphes:
        if len(para) > taille:  # paragraphe géant : découpe glissante
            if courant:
                chunks.append(courant)
                courant = ""
            pas = taille - chevauchement
            i = 0
            while True:
                chunks.append(para[i : i + taille])
                if i + taille >= len(para):
                    break
                i += pas
            continue
        if courant and len(courant) + 1 + len(para) > taille:
            chunks.append(courant)
            courant = courant[-chevauchement:]
        courant = f"{courant} {para}" if courant else para
    if courant:
        chunks.append(courant)
    return chunks


def extraire_pages(pdf: Path) -> tuple[list[tuple[int, str]], int]:
    """Renvoie (pages exploitables [(numéro, texte)], pages ignorées).

    Une page qui donne moins de MIN_CARACTERES_PAGE caractères est considérée
    scannée ou vide et est ignorée avec un avertissement.
    """
    lecteur = PdfReader(str(pdf))
    pages: list[tuple[int, str]] = []
    ignorees = 0
    for numero, page in enumerate(lecteur.pages, start=1):
        texte = (page.extract_text() or "").strip()
        if len(texte) < MIN_CARACTERES_PAGE:
            logger.warning("Page scannée ou vide, ignorée : %s (page %d)", pdf.name, numero)
            ignorees += 1
            continue
        pages.append((numero, texte))
    return pages, ignorees


def construire_index(
    dossier_annales: Path = DOSSIER_ANNALES, dossier_index: Path = DOSSIER_INDEX
) -> dict[str, int]:
    """Ingestion complète : PDFs -> chunks -> embeddings -> vectors.npy + meta.json."""
    fichiers = sorted(dossier_annales.glob("*.pdf"))
    if not fichiers:
        logger.warning("Aucun PDF dans %s", dossier_annales)
    chunks: list[str] = []
    metadonnees: list[dict[str, Any]] = []
    pages_ignorees = 0
    fichiers_lus = 0
    for fichier in fichiers:
        try:
            pages, ignorees = extraire_pages(fichier)
        except Exception as exc:  # un PDF corrompu ne doit jamais casser l'ingestion
            logger.warning("PDF illisible, ignoré : %s (%s)", fichier.name, exc)
            continue
        fichiers_lus += 1
        pages_ignorees += ignorees
        for numero, texte in pages:
            for morceau in decouper_texte(texte):
                chunks.append(morceau)
                metadonnees.append(
                    {
                        "source_file": fichier.name,
                        "page": numero,
                        **parser_nom_fichier(fichier.name),
                        # le texte du chunk est stocké avec ses métadonnées
                        # pour que retrieve() puisse renvoyer des extraits
                        "texte": morceau,
                    }
                )
    if chunks:
        vecteurs = embed(chunks)
        dossier_index.mkdir(parents=True, exist_ok=True)
        np.save(dossier_index / "vectors.npy", vecteurs)
        (dossier_index / "meta.json").write_text(
            json.dumps(metadonnees, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    return {
        "fichiers": fichiers_lus,
        "pages_ignorees": pages_ignorees,
        "chunks": len(chunks),
    }


def charger_index(
    dossier_index: Path = DOSSIER_INDEX,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Charge (vecteurs, métadonnées) ; index absent ou vide -> ((0, 0), [])."""
    chemin_vecteurs = dossier_index / "vectors.npy"
    chemin_meta = dossier_index / "meta.json"
    if not chemin_vecteurs.exists() or not chemin_meta.exists():
        return np.zeros((0, 0), dtype=np.float32), []
    vecteurs = np.load(chemin_vecteurs)
    metadonnees = json.loads(chemin_meta.read_text(encoding="utf-8"))
    if not metadonnees or vecteurs.shape[0] == 0:
        return np.zeros((0, 0), dtype=np.float32), []
    return vecteurs, metadonnees


def retrieve(
    query: str,
    k: int = TOP_K,
    matiere: str | None = None,
    vecteurs: np.ndarray | None = None,
    metadonnees: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Chunks les plus proches de `query` (similarité cosinus).

    Filtre par matière d'abord ; si le filtre ne laisse rien, cherche parmi
    tous les chunks. Index absent -> [] (l'app reste utilisable sans annales).
    """
    if vecteurs is None or metadonnees is None:
        vecteurs, metadonnees = charger_index()
    if not query.strip() or not metadonnees:
        return []
    if matiere is not None:
        indices = [i for i, m in enumerate(metadonnees) if m.get("matiere") == matiere]
        if not indices:
            indices = list(range(len(metadonnees)))
    else:
        indices = list(range(len(metadonnees)))
    vec_requete = embed([query])[0]
    similarites = vecteurs[indices] @ vec_requete
    ordre = np.argsort(similarites)[::-1][:k]
    return [metadonnees[indices[i]] for i in ordre]
