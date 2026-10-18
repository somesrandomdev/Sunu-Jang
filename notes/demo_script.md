# Script de démo v2 (revue 3) — ≤ 3 min — PLAN.md §11

> Répété 3× de suite avant l'enregistrement final. Exercices et réponses du
> jeu d'éval (`notes/demo_reponses.txt`). Maths uniquement : seule matière où
> le 3b note justement les deux réponses (fausse → 8, juste → 14-15).

## 0. Préparation (avant d'appuyer sur « enregistrer »)

1. Ollama lancé avec les bonnes variables (vérifier `ollama list` non vide) :
   `OLLAMA_MODELS=D:\ollama\models`, `OLLAMA_CONTEXT_LENGTH=8192`
   (déjà persistés via `setx` ; après une mise à jour d'Ollama, redémarrer
   `ollama serve` à la main).
2. Index des annales présent (`data/index/` — sinon bandeau « Mode sans annales »).
3. Deux fenêtres de terminal prêtes :
   - **Prise A (accueil + génération)** : `python -m app.ui` (modèle réel).
   - **Prise B (correction sur exercice de banque)** :
     `LLM_MODEL=qwen2.5:3b EMBED_MODEL=modele-inexistant python -m app.ui`
     → la génération échoue vite (404 embeddings) et la **banque de secours**
     s'affiche aussitôt, étiquetée « Exercice de la banque (rédigé à la main,
     non généré) » — pendant que la **correction tourne en direct** avec le
     vrai modèle (elle n'utilise pas les embeddings).
     ℹ️ Astuce vérifiée par les tests (test_ui.py) ; le toast 404 mentionne
     « qwen2.5:3b » par erreur cosmétique (message commun 404) — ne pas y
     prêter attention à l'écran, le bandeau « banque » est celui qui compte.
4. Réponses à coller dans `notes/demo_reponses.txt`. Police agrandie (Ctrl +).
5. Gradio tourne sur http://localhost:7860 — un seul serveur à la fois.

## 1. (15 s) Le problème + le parti pris local

« Au Sénégal, les cours particuliers coûtent jusqu'à 25 000 FCFA par mois et par
matière. Sunu Jàng est un professeur particulier de BAC qui tourne
**entièrement en local**, sans internet et sans abonnement. »

## 2. (30 s) Génération ancrée RAG — Prise A

- Maths · Terminale · Moyen · thème `suites numériques` → **✨ Nouvel exercice**.
- Filmer JUSQU'À ce qu'une tentative réussisse (couper l'attente au montage) ;
  sous-titre : *« génération : ~2 min sur un portable sans GPU (accéléré) »*.
- Pointer **« Inspiré de : maths_S2_2023.pdf p.X »** (le RAG rendu visible).

## 3. (60 s) Correction reproductible — Prise B (exercice de banque)

- La banque est déjà à l'écran (étiquette visible — le dire à voix haute :
  « ici un exercice de notre banque, rédigé à la main, pour être reproductible »).
- Coller la **mauvaise** réponse (u_2 = 11, suite « arithmétique », u_10 = 31)
  → **📝 Corriger** → **note 8/20 rouge**, erreurs, correction détaillée,
  conseil. (Valeurs validées par le jeu d'éval : 8/8 runs à 8,0.)

## 4. (30 s) Progression adaptative — Prise B

- **➡️ Exercice suivant** → la difficulté **descend à Facile** (note < 10).
- Coller la **bonne** réponse → **Corriger** → 14 ou 15 :
  - si ≥ 15 : « Exercice suivant » passe à **Difficile** — « la progression remonte » ;
  - si 14 : la difficulté **reste Moyen** — dire « même niveau, on consolide ».
  Ne jamais simuler une montée qui n'a pas lieu.

## 5. (15 s) Open source — écran du dépôt GitHub

Licence MIT · CONTRIBUTING · issues « good first issue » (Pulaar, export PDF,
annales SVT) · roadmap : Wolof, Pulaar, modèle 7B sur GPU.

## Après la prise

- [ ] Sous-titre/capture : lien de la vidéo (YouTube non répertoriée) en tête du README.
- [ ] Vérifier audio + lisibilité au téléphone ; export MP4 ≤ 3 min.
- [ ] Garder la vidéo comme secours pour la finale (noter : pas de génération
  en direct à la finale — on montre l'extrait vidéo, puis on corrige en direct
  sur la banque, 30-60 s, en parlant par-dessus).
