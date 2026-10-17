# Script de démo (≤ 3 min) — PLAN.md §11

> Répété 3× de suite avant enregistrement. Utiliser les exercices et réponses
> du jeu d'évaluation (`scripts/eval.py`) pour être reproductible.

## 0. Avant d'enregistrer

- [ ] Ollama lancé, `qwen2.5:3b` chargé (faire un appel à vide avant)
- [ ] Index des annales présent (`data/index/`)
- [ ] Interface ouverte : `python -m app.ui` → http://localhost:7860
- [ ] Réponses prêtes à coller (fichier `notes/demo_reponses.txt`)
- [ ] Enregistreur lancé, plein écran, police agrandie (Ctrl+ dans le navigateur)

## 1. (15 s) Le problème + le parti pris local

Phrase : « Au Sénégal, les cours particuliers coûtent jusqu'à 25 000 FCFA par mois
et par matière. Sunu Jàng est un professeur particulier de BAC qui tourne
**entièrement en local**, sans internet et sans abonnement. »
→ montrer le bandeau, puis couper le Wi-Fi si possible pour appuyer « 100 % local ».

## 2. (45 s) Générer un exercice ancré RAG

- Matière **Maths**, Niveau **Terminale**, Difficulté **Moyen**,
  Thème : `suites numériques` → **✨ Nouvel exercice**
- Pointer la ligne **« Inspiré de : maths_S2_2023.pdf p.X »** (RAG visible)
- Lire l'énoncé à voix haute (récurrence).

## 3. (50 s) Une mauvaise réponse, corrigée sévèrement

- Coller la **réponse fausse** (celle du jeu d'éval : u_2 = 11, suite « arithmétique
  de raison 3 », u_10 = 31) → **📝 Corriger**
- Pointer : **note rouge ≤ 8 /20**, les erreurs détectées une à une, la
  **correction détaillée** (accordion), le **conseil**.

## 4. (45 s) Progression adaptative

- **➡️ Exercice suivant** → la difficulté passe à **Facile** automatiquement
- Répondre **juste** (réponse correcte du jeu d'éval) → **note verte ≥ 15**
- **➡️ Exercice suivant** → la difficulté remonte (**Difficile**)
- Phrase : « L'élève progresse à son rythme, comme avec un vrai professeur. »

## 5. (25 s) Open source

- Repo GitHub : licence MIT, CONTRIBUTING, issues « good first issue »
  (Pulaar, export PDF, annales SVT)
- Roadmap : Pulaar, Sérère, mobile, tableau de bord enseignant
- Phrase finale : « Le code, les modèles et les données sont ouverts — construisons
  ensemble le tuteur BAC de nos frères et sœurs. »

## Après la prise

- [ ] Vérifier audio + lisibilité au téléphone
- [ ] Exporter en MP4 ≤ 3 min, ≤ 100 Mo
