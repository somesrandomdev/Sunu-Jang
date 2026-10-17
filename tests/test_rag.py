"""Tests de app.rag : découpage, parsing des noms, retrieve avec index factice."""

import numpy as np
import pytest

import app.rag as rag
from app.rag import (
    charger_index,
    construire_index,
    decouper_texte,
    parser_nom_fichier,
    retrieve,
)


class TestDecouperTexte:
    def test_texte_vide(self):
        assert decouper_texte("") == []

    def test_texte_blanc(self):
        assert decouper_texte("   \n \n  ") == []

    def test_texte_plus_court_qu_un_chunk(self):
        assert decouper_texte("Bonjour la classe.", taille=100, chevauchement=20) == [
            "Bonjour la classe."
        ]

    def test_paragraphes_regroupes_sous_la_taille(self):
        texte = "\n\n".join("Paragraphe " + "a" * 40 for _ in range(4))
        chunks = decouper_texte(texte, taille=100, chevauchement=20)
        assert len(chunks) >= 2
        assert all(len(c) <= 100 for c in chunks)
        assert "".join(chunks).count("a" * 40) >= 4  # chaque paragraphe est couvert

    def test_paragraphe_geant_coupe_avec_recouvrement(self):
        texte = "x" * 250
        chunks = decouper_texte(texte, taille=100, chevauchement=20)
        assert chunks[0] == "x" * 100
        assert chunks[1].startswith("x" * 20)  # début = 80 -> recouvrement de 20
        assert "".join(chunks).count("x") >= 250  # tout le texte est couvert

    def test_multiple_exact_du_pas(self):
        texte = "x" * 160  # 2 × (taille - chevauchement)
        chunks = decouper_texte(texte, taille=100, chevauchement=20)
        assert len(chunks) == 2
        assert chunks[0] == "x" * 100
        assert chunks[1] == "x" * 80

    def test_chevauchement_invalide_refuse(self):
        with pytest.raises(ValueError):
            decouper_texte("abc", taille=10, chevauchement=10)


class TestParserNomFichier:
    def test_nom_complet(self):
        assert parser_nom_fichier("maths_S2_2023.pdf") == {
            "matiere": "maths",
            "serie": "S2",
            "annee": 2023,
        }

    def test_annee_non_numerique(self):
        assert parser_nom_fichier("philo_S2_inconnu.pdf")["annee"] is None

    def test_nom_hors_convention(self):
        assert parser_nom_fichier("annales_bac.pdf") == {
            "matiere": None,
            "serie": None,
            "annee": None,
        }


def vecteur_unitaire(valeurs: list[float]) -> np.ndarray:
    v = np.asarray(valeurs, dtype=np.float32)
    return v / np.linalg.norm(v)


@pytest.fixture
def index_factice():
    vecteurs = np.stack(
        [
            vecteur_unitaire([1, 0, 0]),  # maths 2023
            vecteur_unitaire([0, 1, 0]),  # philo
            vecteur_unitaire([0.95, 0.05, 0]),  # maths 2022
            vecteur_unitaire([0, 0, 1]),  # svt
        ]
    )
    meta = [
        {"source_file": "maths_S2_2023.pdf", "page": 1, "matiere": "maths",
         "serie": "S2", "annee": 2023, "texte": "suites numériques"},
        {"source_file": "philo_S2_2022.pdf", "page": 2, "matiere": "philo",
         "serie": "S2", "annee": 2022, "texte": "la liberté"},
        {"source_file": "maths_S1_2022.pdf", "page": 3, "matiere": "maths",
         "serie": "S1", "annee": 2022, "texte": "second degré"},
        {"source_file": "svt_S2_2021.pdf", "page": 4, "matiere": "svt",
         "serie": "S2", "annee": 2021, "texte": "génétique"},
    ]
    return vecteurs, meta


class TestRetrieve:
    def test_classement_par_similarite(self, monkeypatch, index_factice):
        vecteurs, meta = index_factice
        monkeypatch.setattr(
            rag, "embed",
            lambda textes: np.stack([vecteur_unitaire([1, 0.02, 0])] * len(textes)),
        )
        resultats = retrieve("suites", k=2, vecteurs=vecteurs, metadonnees=meta)
        assert [r["texte"] for r in resultats] == ["suites numériques", "second degré"]

    def test_filtre_matiere(self, monkeypatch, index_factice):
        vecteurs, meta = index_factice
        monkeypatch.setattr(
            rag, "embed",
            lambda textes: np.stack([vecteur_unitaire([0, 1, 0])] * len(textes)),
        )
        resultats = retrieve(
            "liberté", k=3, matiere="maths", vecteurs=vecteurs, metadonnees=meta
        )
        assert {r["matiere"] for r in resultats} == {"maths"}

    def test_filtre_sans_resultat_repli_sur_tout(self, monkeypatch, index_factice):
        vecteurs, meta = index_factice
        monkeypatch.setattr(
            rag, "embed",
            lambda textes: np.stack([vecteur_unitaire([0, 0, 1])] * len(textes)),
        )
        resultats = retrieve(
            "génétique", k=2, matiere="chimie", vecteurs=vecteurs, metadonnees=meta
        )
        assert resultats[0]["texte"] == "génétique"
        assert len(resultats) == 2

    def test_index_vide(self, monkeypatch):
        monkeypatch.setattr(
            rag, "embed", lambda textes: np.zeros((len(textes), 3), dtype=np.float32)
        )
        assert retrieve("x", vecteurs=np.zeros((0, 0)), metadonnees=[]) == []

    def test_requete_vide(self, monkeypatch, index_factice):
        vecteurs, meta = index_factice
        monkeypatch.setattr(
            rag, "embed", lambda textes: np.zeros((len(textes), 3), dtype=np.float32)
        )
        assert retrieve("   ", vecteurs=vecteurs, metadonnees=meta) == []


class TestChargerIndex:
    def test_index_absent(self, tmp_path):
        vecteurs, meta = charger_index(tmp_path)
        assert meta == []
        assert vecteurs.shape == (0, 0)

    def test_index_present(self, tmp_path, index_factice):
        vecteurs, meta = index_factice
        np.save(tmp_path / "vectors.npy", vecteurs)
        import json

        (tmp_path / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )
        vecs2, meta2 = charger_index(tmp_path)
        assert vecs2.shape == vecteurs.shape
        assert meta2 == meta


class TestConstruireIndex:
    def test_dossier_vide_ne_plante_pas(self, tmp_path):
        (tmp_path / "annales").mkdir()
        stats = construire_index(tmp_path / "annales", tmp_path / "index")
        assert stats == {"fichiers": 0, "pages_ignorees": 0, "chunks": 0}
        assert not (tmp_path / "index" / "vectors.npy").exists()

    def test_ingestion_complete(self, tmp_path, monkeypatch, index_factice):
        _, meta = index_factice
        pdfs = [tmp_path / "maths_S2_2023.pdf", tmp_path / "corrompu.pdf"]
        for p in pdfs:
            p.write_bytes(b"%PDF-1.4 faux pdf")

        def faux_extraire_pages(pdf):
            if pdf.name == "corrompu.pdf":
                raise ValueError("fichier corrompu")
            return ([(1, "page une " * 30), (2, "x" * 49)], 1)  # p.2 quasi vide

        def faux_embed(textes):
            return np.stack(
                [vecteur_unitaire([1, 0, 0])] * len(textes)
            ).astype(np.float32)

        monkeypatch.setattr(rag, "extraire_pages", faux_extraire_pages)
        monkeypatch.setattr(rag, "embed", faux_embed)
        stats = construire_index(tmp_path, tmp_path / "index")
        assert stats == {"fichiers": 1, "pages_ignorees": 1, "chunks": 2}
        vecs = np.load(tmp_path / "index" / "vectors.npy")
        assert vecs.shape == (2, 3)
        import json

        meta_ecrite = json.loads(
            (tmp_path / "index" / "meta.json").read_text(encoding="utf-8")
        )
        assert len(meta_ecrite) == 2
        assert meta_ecrite[0]["source_file"] == "maths_S2_2023.pdf"
        assert meta_ecrite[0]["page"] == 1
        assert meta_ecrite[0]["texte"].startswith("page une")
