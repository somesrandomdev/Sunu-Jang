# Sunu Jàng 🇸🇳

**Sunu Jàng** (« notre savoir » en wolof) est un professeur particulier pour le BAC
sénégalais, qui tourne **entièrement en local** sur votre machine : aucun coût par
exercice, aucune donnée qui sort, aucun abonnement — même sans internet.

🎬 **Démo vidéo (2 min 58) :** https://youtu.be/tdOB__0e2DY

## Le problème

Au Sénégal, préparer le BAC seul est difficile :

- les **cours particuliers coûtent cher** (souvent 10 000 à 25 000 FCFA/mois par matière) ;
- beaucoup d'élèves n'ont qu'un **accès limité à internet**, et les IA en ligne
  demandent une connexion permanente et un paiement en devises ;
- les **annales** existent mais sans correction guidée ni progression adaptée.

## La solution

Une application qui :

1. génère des **exercices neufs** ancrés dans de **vraies annales du BAC sénégalais** (RAG) ;
2. corrige la réponse de l'élève : **note /20**, points forts, erreurs,
   **correction détaillée étape par étape**, et un conseil concret ;
3. propose l'**exercice suivant** adapté : plus facile si note < 10, même niveau si
   10–14, plus difficile si ≥ 15 (progression adaptative).

Sur une machine modeste, si la génération échoue, l'app propose un **exercice de
la banque** — rédigé à la main et clairement étiqueté comme tel, jamais présenté
comme généré — et la correction reste exécutée en direct : le pire cas reste
utilisable.

Matières : Maths, Physique-Chimie, SVT, Philosophie — Niveaux : Seconde, Première, Terminale.

## Captures d'écran

![Sunu Jàng : un exercice de suites (ancré dans `maths_S2_2023.pdf` p.3) et sa
correction — note 4/20 en rouge, points forts, erreurs détaillées](docs/img/capture-correction.png)

## Architecture

```mermaid
flowchart LR
    U[Élève] -->|choisit matière, niveau, difficulté| UI[Interface Gradio]
    UI -->|1. retrieve(query, matiere)| RAG[(Index NumPy\ndata/index/)]
    RAG -->|extraits d'annales| P
    UI -->|2. generate_exercise| P[Prompts français\napp/prompts.py]
    P -->|JSON validé pydantic| LLM[Modèle local via Ollama\nAPI compatible OpenAI]
    LLM --> UI
    UI -->|3. réponse de l'élève| G[grade_answer\nnote /20 + correction]
    G --> LLM
    G -->|note| N[next_difficulty\nexercice suivant adapté]
```

Le RAG : les PDF d'annales sont découpés en chunks (~800 caractères), embeddés avec
`nomic-embed-text`, stockés dans un simple tableau NumPy. La recherche par similarité
cosinus fournit les extraits qui inspirent l'exercice — **jamais recopiés**.

## Démarrage rapide (Docker) — ⚠️ expérimental, non vérifié

> Ce parcours n'a pas encore été validé par un `docker compose up` depuis un
> clone frais (aucune des deux machines du projet n'a Docker au moment de la
> rédaction). En cas de problème, [ouvrez une issue](../../issues/new) — ou
> utilisez le démarrage local ci-dessous, lui aussi testé.

Prérequis : [Docker](https://docs.docker.com/get-docker/).

```bash
git clone https://github.com/somesrandomdev/sunu-jang.git
cd sunu-jang
docker compose up -d            # démarre l'app + Ollama

# un seul coup : télécharger les modèles (~3 Go, à refaire seulement si vous changez de modèle)
docker compose exec ollama ollama pull qwen2.5:3b        # modèle de chat (~2 Go)
docker compose exec ollama ollama pull nomic-embed-text  # embeddings (~0,3 Go)

# (recommandé) ajouter les annales : téléchargez les PDF listés dans data/SOURCES.md
# puis construire l'index
docker compose run --rm app python scripts/ingest.py
```

Ouvrez <http://localhost:7860>. Tout marche aussi **hors ligne** une fois les modèles téléchargés.

## Démarrage rapide (local)

Prérequis : Python 3.11+, [Ollama](https://ollama.com/download).

```bash
ollama pull qwen2.5:3b          # modèle de chat (~2 Go)
ollama pull nomic-embed-text    # embeddings (~0,3 Go)

python -m venv .venv
source .venv/bin/activate       # Windows : .venv\Scripts\activate
pip install -r requirements.txt

python scripts/ingest.py        # après avoir ajouté les annales (voir plus bas)
python -m app.ui                # http://localhost:7860
```

## Utilisation

1. Choisissez **matière**, **niveau**, **difficulté**, et éventuellement un **thème**.
2. « Nouvel exercice » : l'exercice s'affiche avec sa source (« Inspiré de :
   `maths_S2_2023.pdf` p.3 ») quand des annales sont indexées.
3. Rédigez votre réponse, « Corriger » : note /20, points forts, erreurs,
   correction détaillée, conseil.
4. « Exercice suivant » : la difficulté s'ajuste automatiquement à votre note.

## Configuration

| Variable | Défaut | Rôle |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL de l'API Ollama (compatible OpenAI) |
| `LLM_MODEL` | `qwen2.5:3b` | Modèle de chat (génération + correction) ; voir `notes/model_smoke_test.md` |
| `EMBED_MODEL` | `nomic-embed-text` | Modèle d'embeddings du RAG |
| `LLM_API_KEY` | `ollama` | Clé factice pour Ollama ; utile si vous pointez vers une autre API |
| `TOP_K` | `3` | Nombre d'extraits d'annales injectés dans le prompt |

Côté **serveur Ollama** (pas du code de l'app) : la variable
`OLLAMA_CONTEXT_LENGTH=8192` est recommandée. À 4096, un prompt RAG complet
(~2 200 tokens) plus la génération frôlent la limite et peuvent tronquer.
Vérifiez avec `ollama ps` (colonne CONTEXT) pendant une génération.

## Performances et matériel

Mesuré sur un CPU portable 4 cœurs (i7-1065G7, sans GPU) :

- **Correction** d'une réponse : 30 à 60 s.
- **Génération** d'un exercice : 35 s à 3 min selon la charge du CPU — et peut
  échouer (un message clair s'affiche, relancez). Sur une machine avec GPU,
  préférez `LLM_MODEL=qwen2.5:7b` : meilleure qualité de correction, génération
  plus fiable. Voir `notes/model_smoke_test.md` pour la comparaison complète.

## Ajouter des annales

1. Téléchargez les PDF listés dans [`data/SOURCES.md`](data/SOURCES.md)
   (source officielle : Office du Baccalauréat du Sénégal) ou vos propres sujets
   **que vous avez le droit d'utiliser**.
2. Nommez chaque fichier `matiere_serie_annee.pdf`
   (ex. `maths_S2_2023.pdf`, `philo_L_2025.pdf`).
3. Placez-les dans `data/annales/` puis lancez `python scripts/ingest.py`.
   Les pages scannées (sans texte) sont ignorées automatiquement.

Sans index, l'app reste utilisable (bandeau « Mode sans annales ») : les exercices
ne sont simplement pas ancrés dans les annales.

## Qualité : jeu d'évaluation

`scripts/eval.py` exécute 8 cas figés (4 exercices × réponse juste/fausse), 3 fois
chacun. Critères : 8/8 réponses lisibles, bonne réponse ≥ 14/20, réponse fausse ≤ 8/20.

Score réel actuel (voir [`notes/eval_results.md`](notes/eval_results.md)) : **5 cas
sur 8 passés** avec `qwen2.5:3b`, et 24 corrections sur 24 lisibles. Le modèle
corrige correctement les suites et le second degré côté réponses fausses, mais
reste trop laxiste sur une réponse de physique entièrement fausse et trop sévère
sur une bonne introduction de dissertation ; le cas « second degré — bonne
réponse » est instable d'une session à l'autre (dérive du modèle, analysée dans
`notes/eval_results.md`). Conséquence assumée et affichée dans l'application :
**la note est indicative, pas une note officielle** — en cas de doute, l'élève se
reporte à la correction détaillée et à son professeur.

## Feuille de route

- 🗣️ Wolof (bêta), puis **Pulaar** et **Sérère**
- 📄 Export PDF de la correction
- 📚 Plus d'annales : SVT série L, épreuves 2ᵉ groupe, années antérieures
- 👩‍🏫 Tableau de bord enseignant (suivi de classe)
- 📱 Application mobile

## Dépendances principales

- [Ollama](https://ollama.com) — exécution locale des modèles (licence MIT)
- Modèle de chat : `qwen2.5:3b` par défaut ([licence Apache 2.0](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE)) ; changeable via `LLM_MODEL`
- `nomic-embed-text` — embeddings (licence Apache 2.0)
- [Gradio](https://www.gradio.app) — interface (Apache 2.0)
- [pypdf](https://github.com/py-pdf/pypdf) — extraction de texte PDF (BSD)
- [pydantic](https://docs.pydantic.dev) — validation des sorties du modèle (MIT)
- [openai](https://github.com/openai/openai-python) — SDK client, pointé vers Ollama (Apache 2.0)

## Licence

[MIT](LICENSE) — utilisez, modifiez, partagez.

## IA et transparence

Ce projet a été construit avec l'aide d'agents de codage IA. Le rôle exact de l'IA
dans le produit et dans le développement est détaillé dans [`AI.md`](AI.md).
