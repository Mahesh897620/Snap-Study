"""Run with: python -m streamlit run app.py"""

import hashlib
import os
from pathlib import Path
import time
import streamlit as st
from core import (MAX_IMAGES, MAX_TEXT, MAX_TURNS, prepare_image, valid_email,
                  revision_export, transcript_export)
from demo import QUESTION, EXPLANATION, HINT, PRACTICE, PACK
from prompts import MODE_PROMPTS
from services import ServiceError, generate, send_email

st.set_page_config(page_title="Snap & Study", page_icon="📖", layout="wide")


def setting(name, default=""):
    if os.environ.get(name):
        return os.environ[name]
    try:
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


@st.cache_resource
def get_client(api_key):
    try:
        from google import genai
        from google.genai import types
        # Share the connection pool, never user history. Timeout is in milliseconds.
        return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=45000))
    except Exception as exc:
        raise ServiceError("Gemini could not initialize. Check the installed dependencies, network/proxy settings and API configuration.") from exc


API_KEY = setting("GEMINI_API_KEY")
MODEL = setting("GEMINI_MODEL", "gemini-3.5-flash")
SENDER = setting("GMAIL_ADDRESS")
MAIL_PASSWORD = setting("GMAIL_APP_PASSWORD")
ALLOWED = setting("MAIL_ALLOWED_RECIPIENTS")
ASSETS = Path(__file__).parent / "assets"

st.markdown("""<style>
.block-container {max-width:1180px; padding-top:4.5rem; padding-bottom:4rem;}
h1 {letter-spacing:-.045em; font-weight:750 !important;}
h2,h3 {letter-spacing:-.025em;}
[data-testid="stSidebar"] {border-right:1px solid #dce4d7;}
[data-testid="stChatMessage"] {border:1px solid #e0e6db; border-radius:16px; padding:1.25rem;}
.eyebrow {font-size:.73rem; letter-spacing:.17em; font-weight:750; color:#527560; margin:0 0 .8rem;}
.hero {background:#e8eedf; border:1px solid #d9e2d0; border-radius:22px; padding:2rem; margin:1rem 0 1.4rem;}
.hero h2 {font-size:2.2rem; line-height:1.15; margin:0 0 .8rem; max-width:650px;}
.hero p {max-width:640px; margin-bottom:0; color:#49604f;}
.step {font-size:.8rem; letter-spacing:.1em; color:#58715e; margin-bottom:.4rem;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Snap & Study")
    st.caption("A little clarity. A lot of possibility.")
    st.divider()
    if "profile" in st.session_state:
        profile = st.session_state.profile
        st.write("**Your study space**")
        st.write(profile["name"])
        st.caption("Offline demo" if profile["demo"] else "Live AI mode · Gemini configured")
        st.divider()
        st.markdown("**Your session**")
        count = sum(m["role"] == "user" for m in st.session_state.messages)
        st.metric("Questions explored", count)
        st.caption("Session-only history. Download your work before leaving.")
        if st.button("Start a fresh session", use_container_width=True):
            for key in list(st.session_state):
                del st.session_state[key]
            st.rerun()
    else:
        st.markdown("**01**  Bring a question\n\n**02**  Build understanding\n\n**03**  Keep the key ideas")
    st.divider()
    st.caption("Made for notes, diagrams, code and the question you almost asked in class.")

st.markdown('<p class="eyebrow">YOUR VISUAL STUDY COMPANION</p>', unsafe_allow_html=True)
st.title("Snap & Study")
st.caption("Turn a confusing page into your next ‘I get it’ moment.")

if "profile" not in st.session_state:
    st.markdown('''<div class="hero"><div class="step">FROM PHOTO TO UNDERSTANDING</div>
    <h2>One question.<br>A clearer way forward.</h2>
    <p>Bring your handwritten notes, a diagram or a tricky problem. Get a hint,
    work through an explanation, and take a revision pack with you.</p></div>''', unsafe_allow_html=True)
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        st.subheader("Make yourself a study space")
        with st.form("onboard"):
            name = st.text_input("Your name", placeholder="e.g. Mahesh", max_chars=60)
            email = st.text_input("Your email (optional)", placeholder="For your revision pack", max_chars=254)
            modes = ["Live AI", "Offline demo"] if API_KEY else ["Offline demo"]
            session_mode = st.selectbox("Session mode", modes)
            st.caption("Live mode sends your questions and images to Google Gemini. Email sends only the pack you review. Avoid uploading personal or confidential material.")
            start = st.form_submit_button("Open my study desk →", type="primary", use_container_width=True)
        if start:
            if not name.strip():
                st.error("Add your name to get started.")
            elif email.strip() and not valid_email(email.strip()):
                st.error("Check your email address, or leave it empty.")
            else:
                st.session_state.profile = {"name": name.strip(), "email": email.strip(), "demo": session_mode == "Offline demo"}
                st.session_state.messages = []
                st.session_state.pack = ""
                st.session_state.sent_hashes = []
                st.session_state.last_send = 0.0
                st.rerun()
    with right:
        st.image(str(ASSETS / "bfs-sample.png"), caption="Try the included graph problem. No API key needed for the demo.")
        if not API_KEY:
            st.info("Demo mode uses a prewritten BFS lesson. Add a Gemini key in your app settings to analyse your own photos.")
    st.stop()

profile = st.session_state.profile
demo = profile["demo"]
messages = st.session_state.messages
if demo:
    st.info("OFFLINE DEMO · A prewritten BFS walkthrough. No AI requests, photo analysis or email delivery occur in this mode.")

study, revision, about = st.tabs(["Study desk", "Revision pack", "How it works"])


def add_exchange(question, photo, mode, *, sample=False):
    if sum(m["role"] == "user" for m in messages) >= MAX_TURNS:
        st.warning("This session has reached 20 questions. Download your work and start a fresh session.")
        return
    if len(question) > MAX_TEXT:
        st.warning("Keep each question under 6,000 characters.")
        return
    if photo and sum(bool(m.get("image")) for m in messages) >= MAX_IMAGES:
        st.warning("This session already has three photos. Start a fresh session for more images.")
        return
    if demo and not sample:
        st.warning("Your own questions and photos need Live AI mode. The sample buttons below explore the fixed BFS lesson.")
        return
    user_message = {"role": "user", "text": question, "image": photo, "mode": mode}
    try:
        with st.spinner("Working through your question…"):
            answer = ({"Explain": EXPLANATION, "Hint first": HINT, "Practice": PRACTICE}[mode]
                      if demo else generate(get_client(API_KEY), MODEL, messages + [user_message]))
    except ServiceError as exc:
        st.error(str(exc))
        st.caption("The question was not added to the conversation. Submit it again when ready.")
        return
    messages.extend([user_message, {"role": "assistant", "text": answer}])
    st.session_state.pack = ""
    st.session_state.pop("pack_editor", None)
    st.session_state.pop("email_consent", None)
    st.rerun()


with study:
    main, rail = st.columns([2.2, 1], gap="large")
    with rail:
        with st.container(border=True):
            st.markdown("### Choose your pace")
            mode = st.radio("Learning mode", list(MODE_PROMPTS), label_visibility="collapsed")
            st.caption({"Explain": "Understand the idea, then work through an example.", "Hint first": "A nudge in the right direction. You do the solving.", "Practice": "Try three questions and check the answer key."}[mode])
        with st.container(border=True):
            st.markdown("### A good place to start")
            st.image(str(ASSETS / "bfs-sample.png"))
            st.caption("Data structures · Breadth-first search")
            if st.button("Use sample graph", type="primary", use_container_width=True):
                photo = prepare_image((ASSETS / "bfs-sample.png").read_bytes())
                add_exchange(QUESTION, photo, mode, sample=True)
            if messages:
                if st.button("Give me a hint", use_container_width=True):
                    add_exchange("Give me a hint about the BFS sample." if demo else "Give me one hint about our latest problem.", None, "Hint first", sample=demo)
                if st.button("Make practice questions", use_container_width=True):
                    add_exchange("Make practice questions about the BFS sample." if demo else "Create practice questions based on our conversation.", None, "Practice", sample=demo)
        st.caption("Photo tips: one problem per image, good light, straight-on framing. JPG or PNG, up to 8 MB.")
    with main:
        if not messages:
            st.markdown("### What are we learning today?")
            st.write("Upload a photo with the paperclip below or type your question. You can also start with the sample graph.")
            st.markdown("**Try asking:**\n\n- Explain what this diagram represents.\n- Help me find the error in this code.\n- Give me a hint without the full answer.")
        for message in messages:
            with st.chat_message(message["role"]):
                if message.get("image"):
                    st.image(message["image"], width=430)
                st.markdown(message["text"])
        prompt = st.chat_input("Ask a question or attach a clear photo…", accept_file=True, file_type=["jpg", "jpeg", "png"], key="question")
        if prompt:
            raw_text = prompt if isinstance(prompt, str) else prompt.text
            files = [] if isinstance(prompt, str) else prompt.files
            photo = None
            try:
                if files:
                    photo = prepare_image(files[0].getvalue())
                text = raw_text.strip()
                if text or photo:
                    add_exchange(text or "Help me understand the study material in this photo.", photo, mode)
            except ValueError as exc:
                st.error(str(exc))
        if messages:
            st.download_button("Download conversation", transcript_export(messages), "snap-study-conversation.md", "text/markdown")
        st.caption("AI can misread handwriting or make mistakes. Check key steps against your course material.")

with revision:
    st.subheader("Take the understanding with you")
    st.write("Build a revision pack, review the wording, then download it or email it to an enabled inbox.")
    if not messages:
        st.info("Explore a question on the Study desk first.")
    else:
        if st.button("Build revision pack" if not st.session_state.pack else "Rebuild revision pack", type="primary"):
            try:
                with st.spinner("Collecting the key ideas…"):
                    # Demo pack is explicitly fixed, independent of the selected sample mode.
                    pack = PACK if demo else generate(get_client(API_KEY), MODEL, messages, summary=True)
                st.session_state.pack = pack
                st.session_state.pack_editor = pack
                st.session_state.pop("email_consent", None)
            except ServiceError as exc:
                st.error(str(exc))
        if st.session_state.pack:
            if demo:
                st.caption("This is the complete prewritten BFS example pack, not an AI summary of your session.")
            edited = st.text_area("Review and edit your pack", key="pack_editor", height=350, max_chars=20000)
            exported = revision_export(profile["name"], edited, demo)
            left, right = st.columns(2)
            with left:
                st.download_button("Download revision pack", exported, "snap-study-revision.md", "text/markdown", disabled=not edited.strip(), use_container_width=True)
            with right:
                st.download_button("Download plain text", exported, "snap-study-revision.txt", "text/plain", disabled=not edited.strip(), use_container_width=True)
            with st.expander("Email this revision pack", expanded=False):
                address = st.text_input("Recipient email", value=profile["email"], key="recipient", max_chars=254)
                consent = st.checkbox("I reviewed this pack and want to send it to this address.", key="email_consent")
                ready = bool(SENDER and MAIL_PASSWORD) and not demo
                if demo:
                    st.caption("Email is disabled in the offline demo. Downloads work now.")
                elif not ready:
                    st.caption("Email is not configured. Add Gmail settings in secrets.toml; downloads work without them.")
                else:
                    st.caption("Delivery is limited to inboxes enabled by the app owner.")
                fingerprint = hashlib.sha256((address.strip().lower() + exported).encode()).hexdigest()
                already_sent = fingerprint in st.session_state.sent_hashes
                if st.button("Send reviewed pack", disabled=not (ready and consent and edited.strip()) or already_sent):
                    if time.time() - st.session_state.last_send < 60:
                        st.warning("Wait one minute between email attempts.")
                    else:
                        st.session_state.last_send = time.time()
                        try:
                            with st.spinner("Submitting your email…"):
                                send_email(SENDER, MAIL_PASSWORD, address.strip(), exported, ALLOWED)
                            st.session_state.sent_hashes.append(fingerprint)
                            st.success("Gmail accepted the message. Check the inbox and spam folder; delivery is not guaranteed.")
                        except ServiceError as exc:
                            st.error(str(exc))
                if already_sent:
                    st.caption("This version has already been submitted to this inbox during this session.")

with about:
    st.subheader("From photo to revision, in three steps")
    st.markdown("1. **Bring a question.** Add a clear photo or type a question.\n2. **Work through it.** Pick Explain, Hint first or Practice, then ask follow-ups.\n3. **Keep the essentials.** Build and review a revision pack. Download it or use configured email delivery.")
    st.markdown("### What happens to your work?")
    st.write("Conversation and processed photos stay in server session memory. This app does not write them to a database. Live mode sends the conversation to Google Gemini on each request, including images. Google handles that data under its own terms. Email sends the reviewed pack and recipient address through Gmail. Reloading or disconnecting can lose the session.")
    st.markdown("### Connect live AI")
    st.code('GEMINI_API_KEY = "your-key"\nGEMINI_MODEL = "gemini-3.5-flash"', language="toml")
    st.write("Put these values in .streamlit/secrets.toml locally or the Streamlit Cloud Secrets panel. Restart the app and open a fresh Live AI session. Never commit the real secrets file.")
    st.link_button("Get a Gemini API key", "https://aistudio.google.com/apikey")
    st.caption("Limits: 20 questions and 3 photos per session; 6,000 characters per question. No automatic reminders or background email sends.")
