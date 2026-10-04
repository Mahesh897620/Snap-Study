# Demonstration and submission

## A 90-second demonstration

**0–15 seconds — Problem and project choice**

“I chose Snap & Study from the workshop project list. Students often have a photo of a problem but need help understanding it. My app explains that material and turns the conversation into a revision pack.”

**15–40 seconds — Vision input**

In Live AI mode, upload `assets/bfs-sample.png`. Ask: “Explain BFS starting at A; use alphabetical neighbour order.” Point out the visible graph interpretation, queue operations and final traversal. If demonstrating without credentials, explicitly say that the sample is a prewritten offline walkthrough, not AI analysis.

**40–60 seconds — Follow-up and learning modes**

Ask “Why mark nodes visited when enqueuing them?” Then click “Make practice questions.” Explain that the successful conversation is retained in the session.

**60–80 seconds — Useful action**

Open Revision pack, build it, edit one line, and download it. With Gmail configured, confirm an enabled recipient and send the reviewed pack. Do not claim delivery until you check the inbox.

**80–90 seconds — Technical explanation**

“Streamlit handles the interface, Gemini handles vision and conversation, and Python's email tools send a reviewed pack. I separated the prompts, services, validation and UI. The app also handles invalid photos and failed API calls.”

## Before recording or submitting: live acceptance checklist

- [ ] Set Gemini credentials in local or Cloud secrets; choose Live AI.
- [ ] Text question: ask why BFS uses a queue; check against your course notes.
- [ ] Vision: upload the sample graph; verify A, B, C, D, E, F in alphabetical BFS order.
- [ ] Memory: ask “What is the shortest path to E?”; expect A → B → E.
- [ ] Hint first: upload another problem; confirm it does not immediately give the entire answer.
- [ ] Blurry image: use a deliberately unclear crop; confirm the tutor asks for missing information.
- [ ] Error path: in a temporary local setup, use an invalid key and verify a clean error with no fake answer.
- [ ] Build a pack; confirm it reflects the actual conversation and edit a line.
- [ ] Download the pack and verify the edit is present.
- [ ] Configure Gmail and an enabled test recipient; send only after checking the confirmation box.
- [ ] Check the inbox/spam folder and verify the received pack contains the edit.
- [ ] Start a fresh session; confirm old conversation and pack are cleared.

## Submission checklist

- [ ] Create your own GitHub repository and upload the project files.
- [ ] Include `.streamlit/config.toml` and `.streamlit/secrets.toml.example`.
- [ ] Exclude `.streamlit/secrets.toml`, `.env`, virtual environments and keys.
- [ ] Deploy the repository to Streamlit Community Cloud using `app.py` and Python 3.12.
- [ ] Add Gemini/Gmail credentials in Cloud's Secrets panel.
- [ ] Open the deployed link in a fresh browser session and complete the live checklist.
- [ ] Copy the actual repository URL and actual deployed app URL into the submission form.

Guide's submission form: https://forms.ccbp.in/ai-vision-chatbot-last-project-submission

Guide's deadline: 4 October, 11:59 PM. The supplied PDF does not explicitly state a timezone.

## Suggested short project description

Snap & Study is an AI vision study companion built with Streamlit and Gemini. Students upload a photo of notes, a diagram or a problem, receive an explanation or hint, and ask follow-up questions. They can create practice questions and an editable revision pack, download it or email it through Gmail. It includes a clearly labelled offline demo, validated image uploads, session-isolated history and safe error handling.
