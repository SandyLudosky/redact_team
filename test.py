import pytest
from unittest.mock import patch, MagicMock
from autogen_core.memory import ListMemory

# Import de ton module
import utils


# =========================
# ✅ TEST get_status
# =========================
def test_get_status_valid():
    msg = {"content": '{"status": "APPROVE"}'}
    assert utils.get_status(msg) == "APPROVE"


def test_get_status_invalid_json():
    msg = {"content": "invalid json"}
    assert utils.get_status(msg) is None


# =========================
# ✅ TEST spell_checker_tool
# =========================
def test_spell_checker_tool():
    text = "Ths is a smple txt"
    result = utils.spell_checker_tool(text)

    assert isinstance(result, str)
    assert "This" in result or "is" in result  # tolérant


# =========================
# ✅ TEST tavily_search_tool (mock API)
# =========================
@patch("utils.tavily.search")
def test_tavily_search_tool(mock_search):
    mock_search.return_value = {
        "results": [
            {"title": "AI Article", "content": "AI is amazing"},
            {"title": "ML Article", "content": "ML is part of AI"},
        ]
    }

    result = utils.tavily_search_tool("AI")

    assert "AI Article" in result
    assert "ML Article" in result


# =========================
# ✅ TEST user_memory_tool
# =========================
def test_user_memory_tool():
    memory = ListMemory()

    result = utils.user_memory_tool("hello", memory)

    assert "added to memory" in result


# =========================
# ✅ TEST generate_image (mock OpenAI)
# =========================
@patch("utils.client.responses.create")
def test_generate_image(mock_create, tmp_path):
    fake_base64 = "aGVsbG8="  # "hello" en base64

    mock_create.return_value = MagicMock(
        output=[
            MagicMock(
                type="image_generation_call",
                result=fake_base64
            )
        ]
    )

    utils.file_path = tmp_path / "test.png"

    result = utils.generate_image("a cat")

    assert result is not None
    assert utils.file_path.exists()


# =========================
# ✅ TEST generate_summary (mock OpenAI)
# =========================
@patch("utils.client.responses.create")
def test_generate_summary(mock_create):
    mock_create.return_value = MagicMock(output_text="Short summary")

    result = utils.generate_summary("Long content")

    assert result == "Short summary"


# =========================
# ✅ TEST pretty_stream (async)
# =========================
@pytest.mark.asyncio
async def test_pretty_stream_text_message():
    from autogen_agentchat.messages import TextMessage

    async def fake_stream():
        yield TextMessage(source="user", content="Hello")

    result = await utils.pretty_stream(fake_stream())

    assert result is None  # pas de summary ici


@pytest.mark.asyncio
async def test_pretty_stream_task_result():
    from autogen_agentchat.base import TaskResult
    from autogen_agentchat.messages import TextMessage

    async def fake_stream():
        yield TaskResult(messages=[
            TextMessage(source="writer", content="Some content")
        ])

    with patch("utils.generate_summary", return_value="Summary"):
        result = await utils.pretty_stream(fake_stream())

        assert result == "Summary"