# Snap & Study

**Turn a confusing page into your next “I get it” moment.**

A Streamlit study companion built from **Project 1: Snap & Study** in the supplied *Build Your AI Vision ChatBot* workshop guide. Upload notes, a diagram or a problem; explore it with Gemini; review and download or email a revision pack.

## What is included

- Image + text questions and follow-up conversation with Gemini.
- Explain, Hint first and Practice modes.
- Revision packs generated separately from chat, editable before export.
- Markdown/text downloads and optional Gmail delivery.
- A labelled, offline BFS walkthrough that needs no credentials.
- Image validation, orientation correction, resizing and metadata removal.
- Source-backed research, implementation plan, tests and submission checklist.

**Status:** implemented and locally tested. The offline demo works without credentials. Live AI and real email delivery require your accounts and a final live check. Source repository: https://github.com/Mahesh897620/Snap-Study. Streamlit Cloud deployment and live service verification are pending.

## 1. Run on your Mac

Install **Python 3.12** if needed. Extract the ZIP, open Terminal in the extracted `snap-and-study` folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open `http://localhost:8501`. Enter your name, leave the email blank if you prefer, and start the offline demo. Click **Use sample graph**, then open **Revision pack → Build revision pack**.

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`. Windows Command Prompt: `.venv\Scripts\activate.bat`.

## 2. Enable Gemini vision and chat

1. Create an API key at [Google AI Studio](https://aistudio.google.com/apikey).
2. Copy the settings template:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

3. Edit `.streamlit/secrets.toml`:

   ```toml
   GEMINI_API_KEY = "your-real-key"
   GEMINI_MODEL = "gemini-3.5-flash"
   ```

4. Restart Streamlit, start a fresh session, and choose **Live AI**.
5. Try a text question, then upload `assets/bfs-sample.png` using the chat paperclip. Ask a follow-up such as “Why does this use a queue?”

The default model follows the supplied guide and was listed in Google's model catalog during research. Model access and quotas vary by account. If unavailable, set `GEMINI_MODEL` to a supported text-and-image model from your account. No API call is made in demo mode. The app does not promise free or unlimited Gemini usage.

## 3. Enable email delivery (optional)

Downloads work without email setup. To enable the guide's external action:

1. Enable 2-Step Verification on the sending Google account.
2. Create an [App Password](https://support.google.com/accounts/answer/185833). Some organizational or protected accounts do not offer this option. Do not use your normal account password.
3. Add to `.streamlit/secrets.toml`:

   ```toml
   GMAIL_ADDRESS = "your-address@gmail.com"
   GMAIL_APP_PASSWORD = "your-16-character-app-password"
   MAIL_ALLOWED_RECIPIENTS = "your-address@gmail.com"
   ```

4. For another test inbox, add its address to the comma-separated allowlist. If the allowlist is empty, only the sender's inbox is permitted. This avoids exposing an unrestricted email relay when the app is shared.
5. In a **Live AI** session, build a revision pack, review/edit it, expand **Email this revision pack**, enter an enabled recipient, check the confirmation box and click **Send reviewed pack**.

The service uses TLS on `smtp.gmail.com:465`. A success message means Gmail accepted submission, not proof that it arrived. Check spam too. There is a session-level one-minute cooldown and duplicate prevention; these are convenience guards, not global abuse prevention. Demo mode never sends email.

## 4. Project files

| File | Purpose |
|---|---|
| `app.py` | Streamlit onboarding, chat, revision and email interface |
| `prompts.py` | Tutor scope, learning modes and summary instructions |
| `services.py` | Gemini payloads, error handling and Gmail transport |
| `core.py` | Image validation, mailbox validation and exports |
| `demo.py` | Clearly labelled prewritten BFS lesson |
| `assets/bfs-sample.png` | Original sample graph for the demo and vision tests |
| `.streamlit/config.toml` | Theme and upload-size limit |
| `.streamlit/secrets.toml.example` | Empty credential template |
| `docs/RESEARCH_AND_PLAN.md` | Research findings, scope, architecture and build sequence |
| `docs/DEMO_AND_SUBMISSION.md` | Demo script and deployment checklist |
| `docs/VALIDATION.md` | Tested behaviour and unverified boundaries |
| `tests/` | Validation, mocked service and Streamlit workflow tests |

## 5. Test

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Unit tests and the offline Streamlit AppTest need no API keys and send no messages. Mocked service tests verify request construction and transport handling; they do not demonstrate live model accuracy or email delivery.

## 6. Publish for submission

1. Use the source repository at https://github.com/Mahesh897620/Snap-Study.
2. Upload this folder's contents, including `.streamlit/config.toml` and `.streamlit/secrets.toml.example`. **Never upload `.streamlit/secrets.toml`, `.env`, `.venv` or credentials.**
3. At [Streamlit Community Cloud](https://share.streamlit.io), choose your repository and `app.py` as the entry point. Select Python 3.12 in deployment settings.
4. Paste the real secret values into the Cloud Secrets panel, not GitHub.
5. Deploy. Run the live checklist in `docs/DEMO_AND_SUBMISSION.md`.
6. Submit your actual GitHub and live app URLs using the form linked in the workshop guide.

The guide states a **4 October, 11:59 PM** deadline. Check the event's stated timezone if it differs from yours. A ZIP and an offline demo alone do not satisfy the guide's two-link submission requirement.

## Data and limits

No database or login system is included. History and processed images live in Streamlit session memory and can disappear on refresh/disconnection. A fresh session clears app state. Live requests send the conversation and images to Google under its provider terms; emailing sends the reviewed pack through Gmail. The app does not log raw provider errors, API keys or image contents.

Each session allows 20 questions and 3 photos, with an 8 MB upload limit and 20-megapixel decoded-image limit. Photos are resized to 1600 pixels on the longest side and re-encoded as JPEG. Small handwriting may need a closer crop. Photos are retained in context; long sessions can cost more than one-off questions.

This is a workshop MVP, not a production learning platform. Future deployment at scale needs authentication, per-user quota enforcement, global mail controls and a storage/retention design. AI answers can be incorrect; the prompt requests uncertainty and clarification but cannot guarantee correctness or resist every prompt injection.

## Credits and sources

Concept and build pattern: the user-supplied workshop PDF. Implementation, sample graph and demo lesson: created for this project. Official technical references are recorded in `docs/RESEARCH_AND_PLAN.md`.
