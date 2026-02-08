# Aimz

Multimodal study assistant using the Gemini 3 API. Upload PDFs, images, or code/docs and get:
- Key concepts and definitions
- Likely confusion points
- A timeboxed study plan
- Flashcards
- Quiz with explanations

## Setup
1. Create `.env` (copy `.env.example`) and set `GEMINI_API_KEY`.
   - Optional: set `GEMINI_MODEL` (default `gemini-3-flash-preview`).
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run locally:
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
4. Open `http://127.0.0.1:8000`

## Deploy (Render)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add environment variable `GEMINI_API_KEY` (and optional `GEMINI_MODEL`)

## Demo Script (3 min)
1. Show upload of a PDF or a whiteboard photo.
2. Submit and show structured study output.
3. Highlight the timeboxed study plan and quiz generation.
4. Mention multimodal input and Gemini reasoning.
