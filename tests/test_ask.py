from types import SimpleNamespace

from app import ask


def _response(text: str, input_tokens: int, output_tokens: int):
    return SimpleNamespace(
        text=text,
        usage_metadata=SimpleNamespace(
            prompt_token_count=input_tokens,
            candidates_token_count=output_tokens,
        ),
    )


def test_chat_reuses_one_session_and_prints_usage(monkeypatch, capsys):
    responses = [_response("最初の回答", 3, 5), _response("続きの回答", 7, 11)]

    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return responses.pop(0)

    sessions = []

    def create_chat(*, model):
        assert model == ask.MODEL
        session = FakeChat()
        sessions.append(session)
        return session

    client = SimpleNamespace(chats=SimpleNamespace(create=create_chat))

    def create_client(*, api_key):
        assert api_key == "test-key"
        return client

    monkeypatch.setattr(ask.genai, "Client", create_client)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    inputs = iter(["最初の質問", "続けて質問", "exit"])
    monkeypatch.setattr("sys.argv", ["app.ask", "--chat"])

    ask.main()

    output = capsys.readouterr().out
    assert len(sessions) == 1
    assert sessions[0].questions == ["最初の質問", "続けて質問"]
    assert "[model] " in output
    assert "最初の回答" in output
    assert "続きの回答" in output
    assert "入力: 3, 出力: 5" in output
    assert "入力: 7, 出力: 11" in output


def test_chat_exits_on_quit(monkeypatch, capsys):
    sessions = []

    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return _response("回答", 1, 1)

    def create_chat(*, model):
        assert model == ask.MODEL
        session = FakeChat()
        sessions.append(session)
        return session

    client = SimpleNamespace(chats=SimpleNamespace(create=create_chat))

    def create_client(*, api_key):
        assert api_key == "test-key"
        return client

    monkeypatch.setattr(ask.genai, "Client", create_client)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("builtins.input", lambda _: "quit")
    monkeypatch.setattr("sys.argv", ["app.ask", "--chat"])

    ask.main()

    output = capsys.readouterr().out
    assert len(sessions) == 1
    assert sessions[0].questions == []
    assert "対話を終了します。" in output


def test_single_question_mode_is_preserved(monkeypatch, capsys):
    response = _response("回答", 2, 4)

    def generate_content(*, model, contents):
        assert model == ask.MODEL
        assert contents == "単発の質問"
        return response

    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))

    def create_client(*, api_key):
        assert api_key == "test-key"
        return client

    monkeypatch.setattr(ask.genai, "Client", create_client)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("sys.argv", ["app.ask", "単発の質問"])

    ask.main()

    output = capsys.readouterr().out
    assert "[質問] 単発の質問" in output
    assert "回答" in output
    assert "入力: 2, 出力: 4" in output
