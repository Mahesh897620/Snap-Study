"""Gemini and Gmail boundaries. Never turn provider errors into study content."""

from email.message import EmailMessage
import smtplib
import ssl
from core import valid_email
from prompts import SYSTEM_PROMPT, MODE_PROMPTS, SUMMARY_PROMPT


class ServiceError(RuntimeError):
    pass


def make_contents(messages):
    from google.genai import types
    contents = []
    for message in messages:
        parts = []
        if message.get("image"):
            parts.append(types.Part.from_bytes(data=message["image"], mime_type="image/jpeg"))
        text = message["text"]
        if message["role"] == "user":
            text = MODE_PROMPTS.get(message.get("mode"), MODE_PROMPTS["Explain"]) + "\n\nStudent material/question:\n" + text
        parts.append(types.Part.from_text(text=text))
        contents.append(types.Content(role="model" if message["role"] == "assistant" else "user", parts=parts))
    return contents


def generate(client, model, messages, *, summary=False):
    from google.genai import types
    contents = make_contents(messages)
    if summary:
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=SUMMARY_PROMPT)]))
    try:
        response = client.models.generate_content(
            model=model, contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT, temperature=0.3, max_output_tokens=4096
            ),
        )
        result = (response.text or "").strip()
        if not result:
            raise ServiceError("No readable answer was returned. Try a clearer photo or rephrase the question.")
        # A truncated response is not a complete answer or revision pack.
        candidates = getattr(response, "candidates", None)
        if candidates and str(candidates[0].finish_reason).endswith("MAX_TOKENS"):
            raise ServiceError("The answer was too long. Ask about a smaller section and try again.")
        return result
    except ServiceError:
        raise
    except Exception as exc:
        code = str(getattr(exc, "code", ""))
        if code == "429":
            message = "Gemini's quota or rate limit was reached. Wait a moment or check your API quota."
        elif code in {"401", "403"}:
            message = "Gemini access was denied. Check the configured API key and project permissions."
        elif code == "404":
            message = "The configured model is unavailable. Set GEMINI_MODEL to one supported by your account."
        else:
            message = "Gemini could not complete this request. Check the connection, model and API settings, then retry."
        raise ServiceError(message) from exc


def allowed_recipients(sender, configured):
    return {item.strip().lower() for item in (configured or sender).split(",") if valid_email(item.strip())}


def send_email(sender, password, recipient, body, allowed=""):
    if not valid_email(sender) or not valid_email(recipient):
        raise ServiceError("Enter a valid single email address.")
    if recipient.lower() not in allowed_recipients(sender, allowed):
        raise ServiceError("This inbox is not enabled by the app owner. Download the pack, or ask the owner to enable your inbox.")
    if not password or not body.strip():
        raise ServiceError("Email setup or the revision pack is missing.")
    message = EmailMessage()
    message["Subject"] = "Your Snap & Study revision pack"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=20) as server:
            server.login(sender, password.replace(" ", ""))
            refused = server.send_message(message)
            if refused:
                raise ServiceError("The mail server rejected the recipient. Check the address.")
    except smtplib.SMTPAuthenticationError as exc:
        raise ServiceError("Gmail sign-in failed. Check the sender's App Password and 2-Step Verification.") from exc
    except ServiceError:
        raise
    except (smtplib.SMTPException, OSError) as exc:
        raise ServiceError("Email submission could not be confirmed. Check your inbox before retrying.") from exc
