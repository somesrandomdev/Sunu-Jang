"""Préparation d'une photo de copie manuscrite avant transcription.

Rotation EXIF (les téléphones orientent souvent mal), conversion RGB,
redimensionnement au plus grand côté ≤ IMAGE_MAX_PX, encodage PNG.
"""

import io
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import IMAGE_MAX_PX

# Une copie photographiée de trop près n'est pas exploitable
TAILLE_MIN = 200
TAILLE_MAX_FICHIER = 15 * 1024 * 1024


def preparer_image(chemin: str) -> bytes:
    """Charge, redresse et compresse l'image. Lève ValueError avec un message
    français si le fichier est illisible, trop lourd ou trop petit."""
    try:
        taille = Path(chemin).stat().st_size
    except OSError as exc:
        raise ValueError("Fichier introuvable ou illisible.") from exc
    if taille > TAILLE_MAX_FICHIER:
        raise ValueError("Photo trop volumineuse (15 Mo maximum).")
    try:
        image = Image.open(chemin)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Fichier illisible : ce n'est pas une image valide.") from exc
    image = ImageOps.exif_transpose(image).convert("RGB")
    if min(image.size) < TAILLE_MIN:
        raise ValueError(
            "Photo trop petite : rapproche-toi de la copie avant de photographier."
        )
    cote = max(image.size)
    if cote > IMAGE_MAX_PX:
        ratio = IMAGE_MAX_PX / cote
        image = image.resize((round(image.width * ratio), round(image.height * ratio)))
    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    return tampon.getvalue()
