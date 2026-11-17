# NyayaAI — Indian Consumer Help (MVP)

A small Streamlit prototype for online-shopping refund, non-delivery, defective-product and wrong-item grievances in India.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Open the local URL printed by Streamlit (normally http://localhost:8501).

## Optional AI model
The app works without an API key using deterministic guidance. To enable an OpenAI-compatible chat completion endpoint:
```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o-mini"
# Optional for a compatible provider:
export OPENAI_BASE_URL="https://api.openai.com/v1"
streamlit run app.py
```
The model is used only for a concise plain-language explanation and follow-up questions. Legal references are separately fixed in the application; the model is instructed not to invent legal provisions or case law. A model response is not guaranteed to obey that instruction, so users must verify it.

## Design
- **Structured intake:** issue, platform, dates, amount, order ID, evidence and desired remedy.
- **Rules + AI separation:** deterministic issue classification and complaint draft; optional replaceable model for conversational explanation.
- **Human in the loop:** user verifies facts, edits the draft, submits it, and decides whether to seek professional advice.
- **Source grounding:** official Government of India links are shown in the app.
- **Privacy:** prototype does not save submissions to a database; session data is held by Streamlit while the session is active.

## Test
```bash
python -m unittest discover -s tests -v
```
No credentials or paid API are needed for tests.

## Known limitations
English-only; no voice, OCR, legal filing, deadline calculator, automated jurisdiction determination or legal representation. The AI call is optional and requires the user's own API key. The current fallback is a rules-based assistant, not a full legal reasoning system.
