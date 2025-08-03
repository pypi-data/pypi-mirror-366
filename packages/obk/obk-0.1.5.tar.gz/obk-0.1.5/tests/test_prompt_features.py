import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import obk.cli as cli

PYTHON = sys.executable
REPO_ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(REPO_ROOT / "src")


def _run(args, cwd):
    return subprocess.run(
        [PYTHON, "-m", "obk", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=ENV,
    )


def _write_prompt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


VALID_PROMPT = """<?xml version='1.0' encoding='UTF-8'?>\n<gsl-prompt id='20250731T000000+0000'>\n<gsl-header>h</gsl-header>\n<gsl-block>\n<gsl-purpose>p</gsl-purpose>\n<gsl-inputs>i</gsl-inputs>\n<gsl-outputs>o</gsl-outputs>\n<gsl-workflows/>\n<gsl-tdd><gsl-test id='T1'>t</gsl-test></gsl-tdd>\n<gsl-document-spec>d</gsl-document-spec>\n</gsl-block>\n</gsl-prompt>\n"""

BROKEN_PROMPT = "<broken>"


# T1
def test_validate_all(tmp_path):
    prompts = tmp_path / "prompts"
    good = prompts / "good.md"
    bad = prompts / "bad.md"
    _write_prompt(good, VALID_PROMPT)
    _write_prompt(bad, BROKEN_PROMPT)

    result = _run(["validate-all", "--prompts-dir", str(prompts)], cwd=tmp_path)
    assert result.returncode == 1
    assert "bad.md" in (result.stdout + result.stderr)

    bad.unlink()
    result = _run(["validate-all", "--prompts-dir", str(prompts)], cwd=tmp_path)
    assert result.returncode == 0
    assert "All prompt files are valid" in result.stdout


# T2
def test_harmonize_all_and_dry_run(tmp_path):
    prompts = tmp_path / "prompts"
    prompt = prompts / "harm.md"
    content = (
        "<gsl-prompt id='20250731T000000+0000'>\n    <gsl-header>h</gsl-header>\n"
        "<gsl-block>\n    <gsl-purpose>p</gsl-purpose>\n</gsl-block>\n</gsl-prompt>\n"
    )
    _write_prompt(prompt, content)

    result = _run(["harmonize-all", "--prompts-dir", str(prompts)], cwd=tmp_path)
    assert result.returncode == 0
    txt = prompt.read_text()
    assert txt.splitlines()[1].startswith("<gsl-header>")

    _write_prompt(prompt, content)  # reset to original
    result = _run(
        ["harmonize-all", "--prompts-dir", str(prompts), "--dry-run"], cwd=tmp_path
    )
    assert result.returncode == 0
    assert "Would" in result.stdout
    assert content == prompt.read_text()


# T3
def test_commands_any_directory_with_paths(tmp_path):
    prompts = tmp_path / "prompts"
    _write_prompt(prompts / "file.md", VALID_PROMPT)
    sub = tmp_path / "subdir"
    sub.mkdir()

    r1 = _run(["validate-all", "--prompts-dir", str(prompts)], cwd=sub)
    assert r1.returncode == 0

    r2 = _run(["harmonize-all", "--prompts-dir", str(prompts)], cwd=sub)
    assert r2.returncode == 0

    r3 = _run(["trace-id"], cwd=sub)
    assert r3.returncode == 0
    assert re.match(r"\d{8}T\d{6}[+-]\d{4}", r3.stdout.strip())


# T4
def test_trace_id_timezones(tmp_path):
    res = _run(["trace-id", "--timezone", "America/New_York"], cwd=tmp_path)
    assert re.match(r"\d{8}T\d{6}[+-]\d{4}", res.stdout.strip())

    bad = _run(["trace-id", "--timezone", "Invalid/Zone"], cwd=tmp_path)
    assert bad.returncode != 0
    assert "error" in (bad.stderr.lower() or bad.stdout.lower()) or "fatal" in (
        bad.stderr.lower() + bad.stdout.lower()
    )


# Helpers for T5/T6


def _patch_repo_root(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    return cli.get_default_prompts_dir()


# T5
def test_validate_today(monkeypatch, capsys, tmp_path):
    prompts_dir = _patch_repo_root(tmp_path, monkeypatch)
    prompts_dir.mkdir(parents=True)

    cli_obj = cli.ObkCLI()
    with pytest.raises(SystemExit) as exc:
        cli_obj.run(["validate-today"])
    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert "No prompt files found" in captured.out

    _write_prompt(prompts_dir / "bad.md", BROKEN_PROMPT)
    with pytest.raises(SystemExit) as exc:
        cli_obj.run(["validate-today"])
    captured = capsys.readouterr()
    assert exc.value.code == 1
    assert "failed" in captured.out.lower()

    (prompts_dir / "bad.md").unlink()
    _write_prompt(prompts_dir / "good.md", VALID_PROMPT)
    with pytest.raises(SystemExit) as exc:
        cli_obj.run(["validate-today"])
    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert "validated successfully" in captured.out


# T6
def test_harmonize_today(monkeypatch, capsys, tmp_path):
    prompts_dir = _patch_repo_root(tmp_path, monkeypatch)
    prompts_dir.mkdir(parents=True)
    file = prompts_dir / "harm.md"
    content = (
        "<gsl-prompt id='20250731T000000+0000'>\n    <gsl-header>h</gsl-header>\n"
        "<gsl-block>\n    <gsl-purpose>p</gsl-purpose>\n</gsl-block>\n</gsl-prompt>\n"
    )
    _write_prompt(file, content)

    cli_obj = cli.ObkCLI()
    with pytest.raises(SystemExit) as exc:
        cli_obj.run(["harmonize-today"])
    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert "1 file" in captured.out
    assert "Summary" in captured.out

    _write_prompt(file, content)  # reset to original
    with pytest.raises(SystemExit) as exc:
        cli_obj.run(["harmonize-today", "--dry-run"])
    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert "Would" in captured.out
    assert "Dry run" in captured.out


# T7
def test_exit_codes_prompts_not_found(tmp_path):
    r1 = _run(["validate-all"], cwd=tmp_path)
    assert r1.returncode == 2

    r2 = _run(["harmonize-all"], cwd=tmp_path)
    assert r2.returncode == 2


# T8
def test_autolocate_prompts_from_subdir(tmp_path):
    prompts = tmp_path / "prompts"
    _write_prompt(prompts / "good.md", VALID_PROMPT)
    sub = tmp_path / "sub" / "inner"
    sub.mkdir(parents=True)

    r1 = _run(["validate-all"], cwd=sub)
    assert r1.returncode == 0

    r2 = _run(["harmonize-all"], cwd=sub)
    assert r2.returncode == 0


# T9
def test_summary_no_prompts(monkeypatch, capsys, tmp_path):
    prompts_dir = _patch_repo_root(tmp_path, monkeypatch)
    prompts_dir.mkdir(parents=True)

    cli_obj = cli.ObkCLI()
    with pytest.raises(SystemExit) as exc:
        cli_obj.run(["harmonize-today"])
    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert "No prompt files found" in captured.out
    assert "Summary" in captured.out


# T10
def test_harmonize_all_dry_run_summary(tmp_path):
    prompts = tmp_path / "prompts"
    file = prompts / "harm.md"
    _write_prompt(
        file,
        "<gsl-prompt id='20250731T000000+0000'>\n    <gsl-header>h</gsl-header>\n<gsl-block>\n    <gsl-purpose>p</gsl-purpose>\n</gsl-block>\n</gsl-prompt>\n",
    )

    res = _run(
        ["harmonize-all", "--prompts-dir", str(prompts), "--dry-run"], cwd=tmp_path
    )
    assert res.returncode == 0
    assert "Would" in res.stdout
    assert "Summary" in res.stdout
    assert "Dry run" in res.stdout
