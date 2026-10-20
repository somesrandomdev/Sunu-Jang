"""Tests de app.copie — préparation d'une photo de copie (revue 4, §4)."""

import io
from pathlib import Path

import pytest
from PIL import Image

from app import copie
from app.copie import preparer_image


def creer_jpeg(chemin: Path, taille: tuple[int, int], orientation: int | None = None) -> None:
    image = Image.new("RGB", taille, color=(240, 240, 240))
    if orientation is None:
        image.save(chemin, format="JPEG")
        return
    exif = Image.Exif()
    exif[274] = orientation  # tag Orientation
    image.save(chemin, format="JPEG", exif=exif)


def taille_png(donnees: bytes) -> tuple[int, int]:
    return Image.open(io.BytesIO(donnees)).size


class TestPreparerImage:
    def test_exif_pivote_redresse(self, tmp_path):
        chemin = tmp_path / "photo.jpg"
        creer_jpeg(chemin, (300, 500), orientation=6)  # 6 = pivoter 90° CW
        sorti = taille_png(preparer_image(str(chemin)))
        assert sorti == (500, 300)  # redressée : largeur/hauteur inversées

    def test_grande_image_reduite_a_1024(self, tmp_path):
        chemin = tmp_path / "grande.jpg"
        creer_jpeg(chemin, (3000, 4000))
        grand, haut = taille_png(preparer_image(str(chemin)))
        assert max(grand, haut) == copie.IMAGE_MAX_PX
        assert (grand, haut) == (768, 1024)

    def test_petite_image_pas_agrandie(self, tmp_path):
        chemin = tmp_path / "petite.jpg"
        creer_jpeg(chemin, (300, 200))
        assert taille_png(preparer_image(str(chemin))) == (300, 200)

    def test_fichier_texte_renome_png_refuse(self, tmp_path):
        chemin = tmp_path / "fausse.png"
        chemin.write_text("ceci n'est pas une image", encoding="utf-8")
        with pytest.raises(ValueError, match="pas une image"):
            preparer_image(str(chemin))

    def test_image_trop_petite_refusee(self, tmp_path):
        chemin = tmp_path / "minuscule.jpg"
        creer_jpeg(chemin, (100, 100))
        with pytest.raises(ValueError, match="trop petite"):
            preparer_image(str(chemin))

    def test_fichier_trop_lourd_refuse(self, tmp_path, monkeypatch):
        monkeypatch.setattr(copie, "TAILLE_MAX_FICHIER", 100)
        chemin = tmp_path / "lourde.jpg"
        creer_jpeg(chemin, (300, 200))
        with pytest.raises(ValueError, match="volumineuse"):
            preparer_image(str(chemin))
