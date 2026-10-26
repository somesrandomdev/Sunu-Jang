# Feature spec — Correction d'une copie scannée (photo / PNG)

> Reviewer spec. Same rules as PLAN.md §12. Work on a branch: `git checkout -b feat/copie-scannee`.
> **`main` must stay exactly as submitted until this branch passes Gate 1 and Gate 2 below.**

## 0. Design (read before coding)

The flow has two stages. The image is never sent to the grader:

```
photo/PNG ──► vision model (qwen2.5vl:3b) ──► transcription text ──► shown in "Ta réponse" (editable)
                                                                         │
                                         student checks / fixes it ──► "Corriger" (existing grading, unchanged)
```

Why two stages:
- **The grading is already validated.** Its eval, the "Total" parsing and the bank all stay
  untouched. A vision model grading directly would need a new eval from zero.
- **Handwriting OCR by a 3B model will make mistakes.** If the student can see and fix the
  transcription, they are never penalised for a misread. This matters for fairness and in front
  of judges.
- **The demo shows AI at work.** Judges watch the photo become text, then get graded.

The text answer path doesn't change: students can still type or paste.

## Gate 1 — Smoke test before any app code (≤ 45 min, hard stop)

1. Run `ollama pull qwen2.5vl:3b` and record `ollama --version`.
2. Ask the user to handwrite the **suites** exercise answers from `notes/demo_reponses.txt` on
   paper: one correct copy and one wrong copy, plus one deliberately messy copy. Photograph them
   with a phone. Save them as `tests/fixtures/copies/` `suites_bonne.jpg`, `suites_fausse.jpg` and
   `suites_brouillon.jpg`. Commit these files: they are the user's own handwriting, fine to publish.
3. Use a scratch script that **doesn't get committed**. Resize each photo so the longest side is
   1024 px, then send it to `/v1/chat/completions` as a base64 `image_url` data URL with the
   transcription prompt from §2. Record the time and the raw output for each photo.
4. Write `notes/vision_smoke_test.md` with the 3 outputs, the times, and your verdict.

**Pass:** on the two clean copies, the formulas and numbers survive (u₁=5, u₂=13, 4×2ⁿ−3, u₁₀=4093),
and each photo takes **≤ 120 s** on the laptop.
**Fail:** stop, don't write app code, and report to the reviewer. The fallback is to document the
feature as roadmap. Don't go model shopping (`llama3.2-vision` is 11B, which is too big for this CPU).

## 1. Config (`app/config.py`)

- `VISION_MODEL = os.getenv("VISION_MODEL", "qwen2.5vl:3b")`
- `IMAGE_MAX_PX = int(os.getenv("IMAGE_MAX_PX", "1024"))`

Add both to `.env.example` and to the README configuration table.

## 2. Prompt (`app/prompts.py`)

```python
TRANSCRIRE_COPIE = """Cette image est la copie manuscrite d'un élève qui répond à l'exercice suivant :

{enonce}

Transcris FIDÈLEMENT ce que l'élève a écrit, question par question, sans rien corriger,
sans rien ajouter et sans compléter ce qui manque. Recopie aussi les erreurs.
Écris les formules en LaTeX entre $...$.
Si un passage est illisible, écris [illisible] à sa place.
Si l'image ne contient pas de copie d'élève, réponds uniquement : AUCUNE_COPIE
Réponds uniquement avec la transcription, sans commentaire."""
```

Return **plain text, not JSON**. Transcriptions are full of LaTeX, and JSON escaping is exactly
the bug class we already fixed once.

## 3. LLM client (`app/llm.py`) — extend, don't duplicate

1. Move the existing exception mapping out of `chat_json` into a shared helper:
   connection/timeout → existing French message, 404 → "modèle introuvable / ollama pull",
   5xx → one retry. Keep its current behaviour exactly; the existing tests must still pass unchanged.
2. Add `chat_vision(system: str, user: str, image_png: bytes, max_tokens: int = 700) -> str`:
   - The user message `content` is a list:
     `[{"type": "text", "text": user}, {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}]`
   - It uses `VISION_MODEL` and `temperature=0`.
   - It returns the stripped text. An empty result → `LLMError("Impossible de lire la copie. Reprenez la photo plus nette, à plat et bien éclairée.")`.
   - `finish_reason == "length"`: return the text anyway. The student sees a cut-off
     transcription and can complete it themselves.

## 4. Image handling (`app/copie.py`, new and small)

`preparer_image(chemin: str) -> bytes`:
- Open it with Pillow. Pillow is already installed as a Gradio dependency; **I approve adding
  `pillow` to `requirements.txt` explicitly**, pinned to the installed version.
- Apply `ImageOps.exif_transpose` (phone photos are often rotated) and convert to RGB.
- Resize so the longest side is ≤ `IMAGE_MAX_PX` (keep the ratio; never upscale), then encode as PNG.
- Error cases → `ValueError` with a French message: unreadable or non-image file, image smaller
  than 200 px on its shortest side ("photo trop petite"), file > 15 MB.

`transcrire_copie(exercise: Exercise, chemin: str) -> str` in `app/tutor.py`:
- Call `preparer_image`, then `chat_vision`.
- Output `AUCUNE_COPIE` → `ValueError("Aucune copie détectée sur l'image.")`.
- If more than half the lines are `[illisible]` → `ValueError("Copie trop peu lisible…")`.

## 5. UI (`app/ui.py`)

Under "Ta réponse":
- `gr.Image(type="filepath", sources=["upload", "webcam"], label="…ou envoie une photo de ta copie")`
- Button "📷 Lire ma copie". It's disabled until an exercise exists **and** an image is loaded.
  While it runs, show a spinner and the text "Lecture de la copie… (~1–2 min)".
- On success, put the transcription **into the existing `reponse` textbox** with an info line:
  "Transcription automatique : vérifie-la et corrige-la si besoin avant de cliquer sur Corriger."
  The existing `reponse.change` handler then enables "Corriger" as it already does.
- `ValueError`/`LLMError` → `gr.Error` with the French message. Never show a stack trace.
- A new exercise clears the image.
- In the results area, show a small "Corrigé à partir d'une photo (transcription vérifiée par l'élève)"
  note whenever the answer came from a photo. Keep this in a `gr.State` flag.

## 6. Tests (mock everything; Ollama off)

- `preparer_image`: an EXIF-rotated JPEG comes out upright; a 3000×4000 image becomes ≤ 1024 px;
  a small image is not upscaled; a text file renamed `.png` → ValueError; a 100×100 image → ValueError.
  Generate the images in the test with Pillow; no binary fixtures are needed for unit tests.
- `chat_vision`: the request contains an `image_url` data URL and the vision model name; empty
  output → LLMError; 404 → LLMError naming `VISION_MODEL`; `length` → text returned.
- `transcrire_copie`: AUCUNE_COPIE → ValueError; mostly `[illisible]` → ValueError; normal text returned.
- UI: the transcription fills `reponse`; an LLMError → gr.Error.
- **All existing 83 tests still pass unchanged.**

## Gate 2 — End-to-end before merging

On the laptop, with the real models, run each of the 3 photos through the UI: read → (no edits) →
Corriger. Record the transcription time, the note and the total time in `notes/vision_smoke_test.md`.

**Merge to `main` only if:** `suites_bonne` gets ≥ 14, `suites_fausse` gets ≤ 8, the brouillon
gives a clean French error or a usable transcription, and CI is green. Otherwise the branch stays
open and the README roadmap gets a line "Correction de copies manuscrites (branche `feat/copie-scannee`)".

## 7. Docs (only once merged)

- README features: a short paragraph and a screenshot of the photo → transcription → note flow.
- AI.md: name `qwen2.5vl:3b` as the second model and its role (transcription only, never grading),
  why the two-stage design, and its known limits (handwriting, formulas, ~1–2 min on CPU).
- Dependencies list: add Pillow and `qwen2.5vl:3b` with its license (check the license on the
  Ollama model page; don't guess it).

## Out of scope

No direct image grading. No PDF scans. No multi-page copies (one photo = one copy for now).
No prompt changes to grading.
