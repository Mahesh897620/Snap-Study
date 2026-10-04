from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import smtplib
import pytest
from services import ServiceError, generate, make_contents, send_email


def test_vision_and_follow_up_payload():
    history = [{"role": "user", "text": "Explain", "image": b"jpeg", "mode": "Hint first"},
               {"role": "assistant", "text": "Use a queue."},
               {"role": "user", "text": "Why?"}]
    payload = make_contents(history)
    assert [c.role for c in payload] == ["user", "model", "user"]
    assert payload[0].parts[0].inline_data.mime_type == "image/jpeg"
    assert "only one useful hint" in payload[0].parts[1].text
    assert "Why?" in payload[-1].parts[0].text


def test_summary_does_not_mutate_history():
    history = [{"role": "user", "text": "BFS"}, {"role": "assistant", "text": "Queue"}]
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(text="Revision", candidates=[])
    assert generate(client, "model", history, summary=True) == "Revision"
    assert len(history) == 2
    assert len(client.models.generate_content.call_args.kwargs["contents"]) == 3


@pytest.mark.parametrize("response", [SimpleNamespace(text="", candidates=[]),
    SimpleNamespace(text="Partial", candidates=[SimpleNamespace(finish_reason="MAX_TOKENS")])])
def test_rejects_empty_or_truncated_response(response):
    client = MagicMock()
    client.models.generate_content.return_value = response
    with pytest.raises(ServiceError):
        generate(client, "model", [])


def test_error_does_not_leak_provider_secrets():
    client = MagicMock()
    client.models.generate_content.side_effect = RuntimeError("SECRET-key-in-raw-error")
    with pytest.raises(ServiceError) as caught:
        generate(client, "model", [])
    assert "SECRET" not in str(caught.value)


def test_email_real_payload_using_mock_transport():
    with patch("services.smtplib.SMTP_SSL") as smtp:
        server = smtp.return_value.__enter__.return_value
        server.send_message.return_value = {}
        send_email("owner@example.com", "app pass", "student@example.com", "Reviewed pack", "student@example.com")
        server.login.assert_called_once_with("owner@example.com", "apppass")
        message = server.send_message.call_args.args[0]
        assert message["To"] == "student@example.com"
        assert "Reviewed pack" in message.get_content()


def test_no_open_email_relay():
    with patch("services.smtplib.SMTP_SSL") as smtp:
        with pytest.raises(ServiceError, match="not enabled"):
            send_email("owner@example.com", "pw", "stranger@example.com", "pack")
        smtp.assert_not_called()


def test_email_authentication_failure():
    with patch("services.smtplib.SMTP_SSL") as smtp:
        smtp.return_value.__enter__.return_value.login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad password")
        with pytest.raises(ServiceError, match="App Password"):
            send_email("owner@example.com", "pw", "owner@example.com", "pack")
