"""Drive the CLI by feeding scripted keyboard input."""
import main


def run_cli(monkeypatch, capsys, inputs):
    answers = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    main.main()
    return capsys.readouterr().out


def test_full_flow(monkeypatch, capsys):
    out = run_cli(monkeypatch, capsys, [
        "1", "Asha", "Rao", "asha@example.com", "2023-01-10", "Engineering",
        "2", "Website", "2024-01-01", "", "",
        "3", "1", "1", "Developer",
        "4", "1", "Meena", "4", "Teamwork", "Docs", "Nice", "Lead", "mood=happy, bad",
        "5", "1",
        "6", "1",
        "7", "1",
        "7", "2",
        "7", "3",
        "7", "9",
        "8",
    ])
    assert "Employee added with ID 1" in out
    assert "Project added with ID 1" in out
    assert "Review saved" in out
    assert "Developer" in out
    assert "Avg Rating : 4.00" in out
    assert "Goodbye" in out


def test_error_messages(monkeypatch, capsys):
    out = run_cli(monkeypatch, capsys, [
        "x",                      # bad menu choice
        "5", "abc",               # bad ID
        "5", "77",                # missing employee
        "1", "A", "B", "bad", "2023-01-01", "IT",  # bad email
        "8",
    ])
    assert "Please enter a number" in out
    assert "not a valid number" in out
    assert "Employee ID 77 not found" in out
    assert "not a valid email" in out


def test_empty_lists(monkeypatch, capsys):
    out = run_cli(monkeypatch, capsys, ["7", "2", "7", "3", "8"])
    assert out.count("(none)") == 2


def test_unexpected_error_does_not_crash(monkeypatch, capsys):
    monkeypatch.setitem(main.ACTIONS, "1", lambda: 1 / 0)
    out = run_cli(monkeypatch, capsys, ["1", "8"])
    assert "Unexpected error" in out


def test_eof_cancel(monkeypatch, capsys):
    def boom():
        raise EOFError
    monkeypatch.setitem(main.ACTIONS, "1", boom)
    out = run_cli(monkeypatch, capsys, ["1", "8"])
    assert "Cancelled" in out


def test_duplicate_employee_via_cli(monkeypatch, capsys):
    row = ["1", "A", "B", "a@b.com", "2023-01-01", "IT"]
    out = run_cli(monkeypatch, capsys, row + row + ["8"])
    assert "already exists" in out
