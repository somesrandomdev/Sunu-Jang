"""Construit data/index/ à partir des PDF de data/annales/ (PLAN.md §3).

Usage : python scripts/ingest.py
Nécessite Ollama lancé (embeddings via `EMBED_MODEL`).
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag import construire_index  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ingest")


def main() -> int:
    stats = construire_index()
    logger.info(
        "Ingestion terminée : %d fichier(s) lu(s), %d page(s) scannée(s)/vide(s) "
        "ignorée(s), %d chunk(s) créé(s).",
        stats["fichiers"],
        stats["pages_ignorees"],
        stats["chunks"],
    )
    if stats["chunks"] == 0:
        logger.warning(
            "Index vide : placez des PDF dans data/annales/ (voir data/SOURCES.md)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
