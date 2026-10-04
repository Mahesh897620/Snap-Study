from pathlib import Path
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock
from services import ServiceError

APP = str(Path(__file__).parents[1] / "app.py")


def click(at, label):
    next(button for button in at.button if button.label == label).click().run()
    assert not at.exception


def test_offline_workflow(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    at = AppTest.from_file(APP, default_timeout=20).run()
    assert not at.exception
    click(at, "Open my study desk →")
    assert at.error
    at.text_input[0].set_value("Mahesh")
    click(at, "Open my study desk →")
    click(at, "Use sample graph")
    assert len(at.session_state["messages"]) == 2
    click(at, "Build revision pack")
    assert "Breadth-first search" in at.session_state["pack"]
    assert next(b for b in at.button if b.label == "Send reviewed pack").disabled
    click(at, "Make practice questions")
    assert len(at.session_state["messages"]) == 4
    assert not at.session_state["pack"]
    click(at, "Start a fresh session")
    assert "profile" not in at.session_state


def test_live_ui_with_mock_providers(monkeypatch):
    monkeypatch.setattr("google.genai.Client", MagicMock())
    monkeypatch.setenv("GEMINI_API_KEY", "unit-test-placeholder")
    monkeypatch.setenv("GMAIL_ADDRESS", "owner@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "unit-test-placeholder")
    generate = MagicMock(side_effect=["BFS uses a queue.", "## Revision\nUse a queue."])
    send = MagicMock()
    monkeypatch.setattr("services.generate", generate)
    monkeypatch.setattr("services.send_email", send)
    at = AppTest.from_file(APP, default_timeout=20).run()
    at.text_input[0].set_value("Student")
    at.text_input[1].set_value("owner@example.com")
    click(at, "Open my study desk →")
    assert not at.session_state["profile"]["demo"]
    click(at, "Use sample graph")
    assert generate.call_args.args[2][-1]["image"]
    click(at, "Build revision pack")
    assert generate.call_args.kwargs["summary"] is True
    at.text_area[0].set_value("My reviewed pack").run()
    assert next(b for b in at.button if b.label == "Send reviewed pack").disabled
    at.checkbox[0].check().run()
    click(at, "Send reviewed pack")
    assert "My reviewed pack" in send.call_args.args[3]
    at.run()
    assert next(b for b in at.button if b.label == "Send reviewed pack").disabled
    send.assert_called_once()


def test_failed_live_request_does_not_enter_history(monkeypatch):
    monkeypatch.setattr("google.genai.Client", MagicMock())
    monkeypatch.setenv("GEMINI_API_KEY", "unit-test-placeholder")
    monkeypatch.setattr("services.generate", MagicMock(side_effect=ServiceError("Quota reached")))
    at = AppTest.from_file(APP, default_timeout=20).run()
    at.text_input[0].set_value("Student")
    click(at, "Open my study desk →")
    click(at, "Use sample graph")
    assert not at.session_state["messages"]
    assert not at.session_state["pack"]
    assert at.error[0].value == "Quota reached"
