# Rapport de checkpoints — pour le reviewer

> Généré le 17 oct 2026 par l'agent implémenteur. Chaque section correspond à un
> CHECKPOINT du plan (`PLAN.md`). Les artefacts cités sont commités.

## CHECKPOINT 1 — Choix du modèle (M0)

**Artefact : [`notes/model_smoke_test.md`](model_smoke_test.md)** — sorties brutes
(6 candidats) + tableau + recommandation.

TL;DR : sur la machine cible (i7-1065G7, 4 cœurs, 16 Go, **pas de GPU**),
seul `qwen2.5:3b` génère un exercice dans le budget de 120 s. Les 7B/8B
dépassement le timeout en génération ; `llama3.2:3b` note 16/20 une réponse
fausse ; `gemma3:4b` timeout partout. **Choix provisoire posé :
`LLM_MODEL=qwen2.5:3b`** (`app/config.py`), à confirmer.

⚠️ Écarts par rapport au plan, à valider :
1. `mistral:7b` non testé (même classe 7B que deux autres déjà rejetés pour
   vitesse ; place disque/bande passante économisée pour les 3-4B).
2. Le reviewer n'ayant pas pu être sollicité en séance, le choix par défaut a
   été posé (environnement `LLM_MODEL` — changeable sans toucher au code).

## CHECKPOINT 2 — Cœur LLM (M1)

- `app/llm.py` : `chat_json` (format json_object, parsing tolérant, 1 réessai,
  LLMError en français, timeout 120 s), `embed` (lots, L2-normalisé).
- `app/tutor.py` : `generate_exercise`, `grade_answer`, `next_difficulty`.
- Tests : **66 passent**, client OpenAI mocké (`pytest -q` avec Ollama arrêté).

```
$ ruff check .
All checks passed!
$ pytest -q
........                                                 [100%]
66 passed
```

Run terminal réel (génération → correction, qwen2.5:3b) : voir
`notes/eval_results.md` et la démo ; exemple enregistré dans
`notes/model_smoke_test.md` (qwen2.5:3b : génération 35 s, correction 49 s,
note 0,0 sur réponse fausse).

## CHECKPOINT 3 — RAG (M3)

- `app/rag.py` + `scripts/ingest.py` ; tests (chunking, parsing des noms,
  retrieve avec index factice, index manquant) : 66 passent.
- Ingestion réelle (13 PDF officiels, Office du BAC, sources dans
  `data/SOURCES.md`) :

```
INFO: Ingestion terminée : 13 fichier(s) lu(s), 0 page(s) scannée(s)/vide(s)
ignorée(s), 187 chunk(s) créé(s).
```

- Vérification retrieve sur l'index réel : requêtes maths/physique/philo/SVT
  retournent les bons PDF + pages (ex. « suites numériques récurrentes » →
  `maths_S1_2026.pdf` p.2).

## CHECKPOINT 4 — Packaging (M5) — ⚠️ vérification partielle

`Dockerfile` + `docker-compose.yml` écrits (ollama + app, healthcheck, volume
modèles, volume `./data`). **Docker n'est pas installé sur cette machine** :
le run « fresh clone → docker compose up » n'a pas pu être exécuté localement.
À faire par le reviewer avant soumission (ou installer Docker Desktop, ce qui
nécessite un redémarrage — non fait sans accord).

Vérifié localement à la place : chemins/comportement applicatif identiques en
local (OLLAMA_BASE_URL paramétrable), `.dockerignore`, README pas-à-pas.

## CHECKPOINT associé M2 — Qualité prompts/éval

**Artefacts : [`notes/prompt_iterations.md`](prompt_iterations.md) +
[`notes/eval_results.md`](eval_results.md)** (dernière table officielle).

TL;DR : 5 itérations de prompts (+2 correctifs de robustesse code) ;
`qwen2.5:3b` est juste sur les maths, biaisé sur 2 cas (physique trop laxiste,
dissertation trop sévère) ; `qwen2.5:7b` corrige juste ces 2 cas mais dépasse
le timeout ~1 fois sur 2 sur cette machine. Trois options tranchables par le
reviewer sont listées en fin de `prompt_iterations.md`.

## M4 — UI bout en bout (vérifié au navigateur)

Câblage complet vérifié (Chrome automatisé) : génération avec affichage
« Inspiré de : … », LaTeX rendu, « Corriger » désactivé jusqu'à exercice +
réponse non vide, correction affichée (note rouge 4/20, points forts, erreurs,
accordéon « Correction détaillée », conseil), « Exercice suivant » pré-règle la
difficulté (4/20 → Facile, puis 17/20 → remontée d'un cran), toasts d'erreur
en français. Capture : `docs/img/capture-correction.png`.

⚠️ Deux limites matérielles mesurées, à trancher :
1. Sur ce CPU (4 cœurs, throttling thermique après ~1 h d'inférence continue),
   la **génération avec RAG** (prompt ~2 200 tokens : 57 s de préfill à
   38 tok/s + ~850 tokens de sortie) dépasse régulièrement le budget et échoue
   (message français affiché, relance possible). La **correction** reste fiable
   (30-60 s). La capture README a été prise avec un grader mocké (contenu réel
   du jeu d'éval) pour être reproductible ; le comportement affiché est celui
   du code.
2. Écart API : `gr.Warning` n'est plus une exception depuis Gradio 5 → toasts
   via `raise gr.Error(...)` (même rendu utilisateur).

## Hors plan, à valider aussi

- Écarts documentés : `max_tokens` borné dans `chat_json` (anti-dérive de
  latence), coercion de types dans `Grade`, réparation d'échappements LaTeX
  dans le JSON, timeout porté de 120 à 180 s (les générations à 900 tokens
  dépassaient 120 s sur ce CPU), timeout non réessayé après dépassement.
  Aucune dépendance nouvelle par rapport à §2.
