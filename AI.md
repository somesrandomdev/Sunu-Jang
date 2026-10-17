# AI.md — Transparence sur l'IA

Sunu Jàng est un projet d'IA : ce document explique **quel rôle l'IA joue dans le
produit**, ses limites assumées, et **quels outils d'IA ont servi à construire le
code**.

## 1. L'IA dans le produit

### Quels modèles, pour quoi

| Tâche | Modèle | Exécution |
|---|---|---|
| Génération d'exercices | `LLM_MODEL` (voir `app/config.py`), via [Ollama](https://ollama.com) | 100 % local |
| Correction des réponses (note /20, erreurs, correction détaillée, conseil) | le même modèle | 100 % local |
| Embeddings du RAG | `nomic-embed-text` via Ollama | 100 % local |

Le même modèle de chat fait la génération et la correction ; seule la
température change (0.4 pour générer, 0.1 pour corriger, pour rendre la note
plus stable). Toute la configuration passe par des variables d'environnement :
le code fonctionne sans modification avec toute API compatible OpenAI.

### Pourquoi le RAG

Un petit modèle local invente facilement des sujets hors programme ou hors
niveau. On lui montre donc, avant chaque génération, les `TOP_K` extraits les
plus proches du thème choisi **parmi de vraies annales du BAC sénégalais**
(Office du Baccalauréat, voir `data/SOURCES.md`), avec cette consigne : « inspire-toi
du style et du niveau, ne les recopie pas ». L'élève voit toujours la source qui a
inspiré son exercice (« Inspiré de : maths_S2_2023.pdf p.3 »).

### Comment la sortie du modèle est fiabilisée

- Le modèle doit répondre **uniquement en JSON**, validé par des schémas
  [pydantic](https://docs.pydantic.dev) (`app/schemas.py`) : un exercice sans
  corrigé est refusé, une note hors [0, 20] est ramenée dans les bornes par pas
  de 0,5.
- En cas de JSON cassé ou invalide : **un réessai automatique** avec l'erreur
  renvoyée au modèle ; au second échec, un message d'erreur clair en français.
- Les commandes LaTeX mal échappées dans le JSON (`\times`, `\frac`…) sont
  réparées avant le parsing.
- La réponse de l'élève est isolée entre `<<<` et `>>>` dans le prompt de
  correction, avec l'instruction explicite de la traiter comme une donnée à
  évaluer, jamais comme une instruction à suivre.

### Limites connues

- **Un petit modèle local peut se tromper en corrigeant des maths** : la note est
  **indicative**, pas une note officielle. En cas de doute, l'élève doit se
  référer à la correction détaillée et à son professeur.
- La génération peut produire un énoncé moins profond qu'un vrai sujet de BAC ;
  le RAG limite ce risque sans l'éliminer.
- Le wolof et les autres langues nationales sont en bêta : le modèle garde les
  termes scientifiques en français.

## 2. Les outils d'IA utilisés pour construire le projet

| Outil | Modèle | Ce qu'il a fait |
|---|---|---|
| [ZCode](https://zcode.ai) (agent de codage) | GLM (Z.ai) | Écriture du code, des tests, des prompts et de la documentation, sous la direction du plan du projet (`PLAN.md`) |
| Agent de revue | Claude Opus 5.5 (Claude Code) | Revue à chaque jalon du plan : conformité aux exigences, choix du modèle de chat (`notes/model_smoke_test.md`). À la première revue (17 oct), a trouvé et corrigé trois bugs : la réparation d'échappements LaTeX qui corrompait un JSON *correctement* échappé, l'import `app` impossible quand pytest tourne sans `python -m` (CI rouge), et l'appel `retrieve()` hors du `try` dans l'UI (erreur brute au lieu du toast français) |

Le code reste sous la responsabilité de l'équipe : chaque jalon a été relu, les
tests (`pytest`, 60+ cas, client LLM mocké) tournent en CI à chaque push, et le
jeu d'évaluation fixe (`scripts/eval.py`) mesure la qualité réelle des prompts
sur des cas de correction impossibles à tricher.
