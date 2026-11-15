
from types import SimpleNamespace

import pytest

from app import agent as agent_module
from app.judge import generate_answers, read_jsonl


def test_generate_saves_each_answer_and_can_resume(tmp_path, monkeypatch):
    path = tmp_path / "cases.jsonl"
    cases = [
        {"id": "01", "question": "質問1", "answer": ""},
        {"id": "02", "question": "質問2", "answer": ""},
    ]

    class FakeAgent:
        calls = []

        def run_sync(self, question, model):
            self.calls.append(question)
            if question == "質問2":
                raise RuntimeError("模擬APIエラー")
            return SimpleNamespace(output="回答1")

    fake_agent = FakeAgent()
    monkeypatch.setattr(agent_module, "agent", fake_agent)
    monkeypatch.setattr(agent_module, "build_model", lambda: object())
    monkeypatch.setattr("app.judge.time.sleep", lambda _: None)

    with pytest.raises(RuntimeError, match="模擬APIエラー"):
        generate_answers(cases, path, wait=0)

    saved = read_jsonl(path)
    assert saved[0]["answer"] == "回答1"
    assert saved[1]["answer"] == ""

    class ResumeAgent:
        calls = []

        def run_sync(self, question, model):
            self.calls.append(question)
            return SimpleNamespace(output="回答2")

    resume_agent = ResumeAgent()
    monkeypatch.setattr(agent_module, "agent", resume_agent)

    generate_answers(saved, path, wait=0)

    final = read_jsonl(path)
    assert final[0]["answer"] == "回答1"
    assert final[1]["answer"] == "回答2"
    assert resume_agent.calls == ["質問2"]

