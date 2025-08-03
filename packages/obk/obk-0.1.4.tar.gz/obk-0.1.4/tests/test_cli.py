import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def test_hello_world():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "hello-world"],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert result.stdout.strip() == "hello world"


def test_help():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "hello-world", "-h"],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert "Print hello world" in result.stdout


def test_entrypoint_any_directory(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "hello-world"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.stdout.strip() == "hello world"


def test_divide_logs(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "divide", "4", "2"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.stdout.strip() == "2.0"
    log_file = tmp_path / "obk.log"
    assert log_file.exists()
    assert "Divide 4.0 by 2.0 = 2.0" in log_file.read_text()


def test_custom_logfile(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    log_file = tmp_path / "custom.log"
    result = subprocess.run(
        [sys.executable, "-m", "obk", "--logfile", str(log_file), "divide", "4", "2"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.stdout.strip() == "2.0"
    assert log_file.exists()


def test_divide_by_zero(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "divide", "1", "0"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.returncode == 2
    assert "cannot divide by zero" in result.stderr.lower()


def test_fail_exits_1(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "fail"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.returncode == 1
    assert "fatal" in result.stderr.lower()


def test_module_invocation(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "divide", "4", "2"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        check=True,
    )
    assert result.stdout.strip() == "2.0"


class MockGreeter:
    def hello(self) -> str:
        return "[mock] hi"


class MockDivider:
    def divide(self, a: float, b: float) -> float:
        return 42


def test_container_override_greeter(tmp_path, capsys):
    from obk.containers import Container
    from obk.cli import ObkCLI

    container = Container()
    container.greeter.override(MockGreeter())
    cli = ObkCLI(container=container, log_file=tmp_path / "log.log")
    cli.run(["hello-world"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "[mock] hi"


def test_container_override_divider(tmp_path, capsys):
    from obk.containers import Container
    from obk.cli import ObkCLI

    container = Container()
    container.divider.override(MockDivider())
    cli = ObkCLI(container=container, log_file=tmp_path / "log.log")
    cli.run(["divide", "1", "3"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "42"


def test_greet_excited(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "greet", "Ada", "--excited"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.stdout.strip() == "Hello, Ada!!!"


def test_greet_default(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "greet", "Ada"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.stdout.strip() == "Hello, Ada."


class MockGreeterGreet:
    def greet(self, name: str, excited: bool = False) -> str:
        return f"[mock greet] {name} {'!!!' if excited else ''}".strip()


def test_container_override_greeter_greet(tmp_path, capsys):
    from obk.containers import Container
    from obk.cli import ObkCLI

    container = Container()
    container.greeter.override(MockGreeterGreet())
    cli = ObkCLI(container=container, log_file=tmp_path / "log.log")
    cli.run(["greet", "Ada", "--excited"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "[mock greet] Ada !!!"


def _write_prompt(file: Path, content: str) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")


def test_trace_id(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "obk", "trace-id"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    assert re.match(r"\d{8}T\d{6}[+-]\d{4}", result.stdout.strip())


def test_validate_all_success(tmp_path):
    prompt = tmp_path / "prompts" / "valid.md"
    _write_prompt(
        prompt,
        """<?xml version='1.0' encoding='UTF-8'?>\n<gsl-prompt id='20250731T000000+0000'>\n<gsl-header>h</gsl-header>\n<gsl-block>\n<gsl-purpose>p</gsl-purpose>\n<gsl-inputs>i</gsl-inputs>\n<gsl-outputs>o</gsl-outputs>\n<gsl-workflows/>\n<gsl-tdd><gsl-test id='T1'>t</gsl-test></gsl-tdd>\n<gsl-document-spec>d</gsl-document-spec>\n</gsl-block>\n</gsl-prompt>\n""",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "obk",
            "validate-all",
            "--prompts-dir",
            str(tmp_path / "prompts"),
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        check=True,
    )
    assert "All prompt files are valid" in result.stdout


def test_validate_all_failure(tmp_path):
    bad = tmp_path / "prompts" / "bad.md"
    _write_prompt(bad, "<broken>")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "obk",
            "validate-all",
            "--prompts-dir",
            str(tmp_path / "prompts"),
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.returncode == 1
    assert "error" in result.stderr.lower() or result.stderr


def test_harmonize_all(tmp_path):
    prompt = tmp_path / "prompts" / "harm.md"
    _write_prompt(
        prompt,
        """<gsl-prompt id='20250731T000000+0000'>\n    <gsl-header>h</gsl-header>\n<gsl-block>\n    <gsl-purpose>p</gsl-purpose>\n</gsl-block>\n</gsl-prompt>\n""",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "obk",
            "harmonize-all",
            "--prompts-dir",
            str(tmp_path / "prompts"),
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        check=True,
    )
    txt = prompt.read_text()
    assert txt.splitlines()[1].startswith("<gsl-header>")


def test_commands_any_directory(tmp_path):
    (tmp_path / "prompts").mkdir()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    subprocess.run(
        [sys.executable, "-m", "obk", "trace-id"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        check=True,
    )
    assert (tmp_path / "prompts").exists()


def _extract_ymd(text: str) -> str:
    text = text.replace("\\", "/")
    match = re.search(r"prompts/(\d{4})/(\d{2})/(\d{2})", text)
    assert match
    return "".join(match.groups())



def test_today_commands_default_timezone(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    trace = subprocess.run(
        [sys.executable, "-m", "obk", "trace-id"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    validate = subprocess.run(
        [sys.executable, "-m", "obk", "validate-today"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    harmonize = subprocess.run(
        [sys.executable, "-m", "obk", "harmonize-today"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    date = trace.stdout.strip()[:8]
    assert date == _extract_ymd(validate.stdout)
    assert date == _extract_ymd(harmonize.stdout)


def test_today_commands_timezone_override(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    tz = "America/New_York"
    trace = subprocess.run(
        [sys.executable, "-m", "obk", "trace-id", "--timezone", tz],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    validate = subprocess.run(
        [sys.executable, "-m", "obk", "validate-today", "--timezone", tz],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    harmonize = subprocess.run(
        [sys.executable, "-m", "obk", "harmonize-today", "--timezone", tz],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    date = trace.stdout.strip()[:8]
    assert date == _extract_ymd(validate.stdout)
    assert date == _extract_ymd(harmonize.stdout)
