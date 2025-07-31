import os
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
