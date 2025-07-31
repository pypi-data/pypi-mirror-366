import pathlib
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
import typer
from git import Repo
from typer.testing import CliRunner

from gitredate.main import redate

app = typer.Typer()
app.command()(redate)
runner = CliRunner()


TEST_DATA = [
    ##################################################################
    # base_ref                                                       #
    ##################################################################
    # Without argument, only the last commit is affected
    (
        "--min-date 1999-12-31 --max-date 1999-12-31 --yes",
        {"delta": timedelta()},
        [
            ("2000-01-01", "1999-12-31"),
            ("2000-01-01", "2000-01-01"),
            ("2000-01-01", "2000-01-01"),
            ("2000-01-01", "2000-01-01"),
            ("2000-01-01", "2000-01-01"),
        ],
    ),
    # 3 last commits affected
    (
        "HEAD~3 --min-date 1999-12-31 --max-date 1999-12-31 --yes",
        {"delta": timedelta()},
        [
            ("2000-01-01", "1999-12-31"),
            ("2000-01-01", "1999-12-31"),
            ("2000-01-01", "1999-12-31"),
            ("2000-01-01", "2000-01-01"),
            ("2000-01-01", "2000-01-01"),
        ],
    ),
    # Affect the whole history
    (
        "root --min-date 1999-12-31 --max-date 1999-12-31 --yes",
        {"delta": timedelta()},
        [
            ("2000-01-01", "1999-12-31"),
            ("2000-01-01", "1999-12-31"),
            ("2000-01-01", "1999-12-31"),
            ("2000-01-01", "1999-12-31"),
            ("2000-01-01", "1999-12-31"),
        ],
    ),
    ##################################################################
    # hours                                                          #
    ##################################################################
    # Hours are redated according to working hours
    (
        "root --yes",
        {
            "count": 6,
            "start": datetime(2010, 1, 1, 6, tzinfo=timezone.utc),
            "delta": timedelta(hours=3),
            "format": "%H:%M",
        },
        [
            ("21:00", "18:00"),
            ("18:00", "16:00"),
            ("15:00", "14:00"),
            ("12:00", "12:00"),
            ("09:00", "10:00"),
            ("06:00", "08:00"),
        ],
    ),
]


@pytest.mark.parametrize("cmd,repo_args,expected", TEST_DATA)
def test_redate(cmd: str, repo_args: dict[str, Any], expected: list[str]):
    repo_start = repo_args.get("start", datetime(2000, 1, 1, tzinfo=timezone.utc))
    repo_count = repo_args.get("count", 5)
    repo_delta = repo_args.get("delta", timedelta(days=1))
    format = repo_args.get("format", "%Y-%m-%d")

    with tempfile.TemporaryDirectory(delete=False) as temp_dir:
        # Initialise the repo
        repo_path = pathlib.Path(temp_dir)
        file_path = repo_path.joinpath("file.txt")
        repo = Repo.init(repo_path)
        repo.config_writer().set_value("user", "name", "tester").release()
        repo.config_writer().set_value("user", "email", "tester@localhost").release()

        # Create commits
        dt = repo_start
        for i in range(repo_count):
            file_path.write_text(f"{i + 1}")
            repo.index.add([file_path.relative_to(repo_path).as_posix()])
            repo.index.commit(f"commit {i + 1}", author_date=dt, commit_date=dt)
            dt += repo_delta

        # Check results
        before = [
            f"{c.committed_datetime.strftime(format)}" for c in repo.iter_commits()
        ]

        # Run the command
        result = runner.invoke(
            app, [*cmd.split(" "), "--repository", str(repo.working_dir)]
        )
        if result.exception:
            result.exception.add_note(result.stderr)
            raise result.exception

        # Check results
        after = [
            f"{c.committed_datetime.strftime(format)}" for c in repo.iter_commits()
        ]

        assert list(zip(before, after)) == expected
