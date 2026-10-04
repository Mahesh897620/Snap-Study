# Validation record

Date: 4 October 2026. Runtime: Python 3.12, Streamlit 1.65.0, google-genai 1.75.0, Pillow 12.3.0.

## Automated result

`python -m pytest -q` — **26 passed**.

| Area | Verified |
|---|---|
| Onboarding | Blank names rejected; offline session starts without a Gemini key |
| Offline study flow | Sample graph opens, pack builds, practice adds turns, new session clears state |
| Live UI with mocks | Photo reaches provider payload; summary requested separately; reviewed edit reaches email payload |
| Email UI | Explicit confirmation required; repeat submission of the same pack is disabled |
| Failed requests | A failed AI response adds neither a question nor an answer to history |
| Images | Resize, JPEG conversion, white background for transparency, no EXIF; reject invalid, empty, oversized and wrong-format uploads |
| Email addresses | Reject malformed addresses, header injection and multiple recipients |
| Gemini boundary | Correct user/model roles and image MIME; summary does not mutate history |
| Output failures | Reject blank/truncated generation and hide raw provider error details |
| Gmail boundary | Expected reviewed body and recipient; reject non-enabled inboxes; handle authentication failure |

Gemini and Gmail provider calls were mocked. **No real message was sent and no live model accuracy was measured.**

## Browser checks

Used a headless Chromium browser against the running Streamlit server:

- Desktop onboarding, sample lesson and revision-pack pages loaded.
- Edited a pack in the browser, downloaded it, and verified the file contained the edit.
- At a 390 px mobile viewport, document width was 390 px: no page-level horizontal overflow.
- No JavaScript page errors were recorded in that workflow.
- Inspected screenshots of desktop onboarding, the lesson and the mobile layout. Adjusted top spacing to keep the heading below Streamlit's toolbar.

Browser tests used offline mode. They do not establish real-device compatibility across all browsers. The preview included in `assets/app-preview.png` is an actual local app screenshot.

## Remaining live acceptance checks

1. Gemini authentication, model availability and quota for the user's project.
2. Real image interpretation, math/code correctness, unclear-photo handling and prompt adherence.
3. Gmail App Password validity, enabled recipient and actual inbox receipt.
4. GitHub repository creation and Streamlit Community Cloud deployment.

Follow `DEMO_AND_SUBMISSION.md` to complete these checks. The package is a tested local build with external integrations implemented; it is not a claim of successful public deployment or complete live end-to-end verification.
