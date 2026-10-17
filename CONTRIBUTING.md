# Contribuer à Sunu Jàng

Merci de votre intérêt ! Sunu Jàng est un projet libre (MIT) conçu pour les
élèves sénégalais qui préparent le BAC. Toute contribution est bienvenue :
code, annales, corrections de français, documentation, idées.

## Comment contribuer

1. Forkez le dépôt puis créez une branche :
   `git checkout -b ma-fonctionnalite`
2. Installez l'environnement :
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows : .venv\Scripts\activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```
3. Vérifiez avant de committer :
   ```bash
   ruff check .
   pytest -q
   ```
4. Commitez avec des messages clairs à l'impératif
   (ex. `Ajoute le filtre par série dans retrieve`), puis ouvrez une Pull Request.

## Bonnes pratiques

- **Langue de l'interface et des prompts : français.** Le code (identifiants,
  commentaires) peut être en anglais ou en français.
- Les prompts vivent uniquement dans `app/prompts.py` ; les contrats de données
  dans `app/schemas.py`. Toute sortie du modèle doit passer par une validation
  pydantic.
- Chaque fonction qui touche le LLM, les fichiers ou la saisie utilisateur doit
  gérer : entrée vide, sortie malformée du modèle, modèle hors ligne, fichiers
  absents.
- Pas de nouvelle dépendance sans discussion d'abord (ouverture d'une issue).
- N'engagez **jamais** de PDF d'annales dont la licence interdit la
  redistribution : ajoutez plutôt l'URL publique dans `data/SOURCES.md`.

## Bon premier contributeur ?

Les issues marquées [`good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
sont faites pour vous : ajouter une langue (Pulaar, Sérère), un export PDF de la
correction, de nouvelles annales…

## Signaler un bug

Ouvrez une issue avec : ce que vous avez fait, ce que vous attendiez, ce qui
s'est passé, votre OS, la version d'Ollama et le modèle utilisé
(`echo $LLM_MODEL`).
