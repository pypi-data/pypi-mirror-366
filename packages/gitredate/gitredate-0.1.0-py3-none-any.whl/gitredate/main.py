import datetime
import os
import sys
from itertools import count
from pathlib import Path

import pytz
import typer
from businesstimedelta import BusinessTimeDelta, WorkDayRule
from git import Commit, Repo
from typing_extensions import Annotated
from tzlocal import get_localzone_name

from .chart import chart
from .utils import (
    fmt,
    make_backup_branch,
    parse_datetime_str,
    parse_time_str,
    remap,
)

local_tz = pytz.timezone(get_localzone_name())
Commit.min_datetime = property(
    lambda self: min(self.authored_datetime, self.committed_datetime)
)
Commit.max_datetime = property(
    lambda self: max(self.authored_datetime, self.committed_datetime)
)


def redate(
    base_ref: Annotated[
        str,
        typer.Argument(
            help="Base ref at which redating starts. If empty, will redate the last commit only. Set `root` the redate the whole history.",
        ),
    ] = "HEAD~1",
    min_date: Annotated[
        datetime.datetime | None,
        typer.Option(
            help="Custom start date and time",
            parser=parse_datetime_str,
            metavar="YYYY-MM-DD(THH:MM(:SS))",
        ),
    ] = None,
    max_date: Annotated[
        datetime.datetime | None,
        typer.Option(
            help="Custom end date and time",
            parser=parse_datetime_str,
            metavar="YYYY-MM-DD(THH:MM(:SS))",
        ),
    ] = None,
    work_days: Annotated[
        # TODO: once https://github.com/fastapi/typer/pull/800 is merged, switch to list[int] with separator ","
        str,
        typer.Option(
            help="Working days, provide this argument for each working day (monday=1)",
        ),
    ] = "1,2,3,4,5",
    work_hour_start: Annotated[
        # TODO: try to create a datetime.time type
        str,
        typer.Option(
            help="Work day starting hour",
            metavar="HH:MM(:SS)",
        ),
    ] = "8:00",
    work_hour_end: Annotated[
        str,
        typer.Option(
            help="Work day ending hour",
            metavar="HH:MM(:SS)",
        ),
    ] = "18:00",
    repository: Annotated[
        Path,
        typer.Option(help="Path to the git repository"),
    ] = Path("."),
    show_chart: Annotated[
        bool,
        typer.Option(help="Display the debug chart"),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(help="Do not prompt for confirmation"),
    ] = False,
):
    # TODO: parse with Typer (add a datetime.time type and wait for https://github.com/fastapi/typer/pull/800)
    parsed_work_days = [int(d) - 1 for d in work_days.split(",")]
    parsed_work_hour_start = parse_time_str(work_hour_start)
    parsed_work_hour_end = parse_time_str(work_hour_end)

    repo = Repo(repository)
    current_commit = repo.head.commit
    if base_ref == "root":
        commit_range = "HEAD"
        rebase_ref = "--root"
    else:
        commit_range = f"{base_ref}..HEAD"
        rebase_ref = base_ref
    print(f"Will redate range {commit_range}")

    # Get date ranges
    print()
    commits = list(repo.iter_commits(commit_range))

    if not commits:
        raise RuntimeError(f"The given range (`{commit_range}`) is empty")

    old_min_date = min(c.min_datetime for c in commits)
    old_max_date = max(c.max_datetime for c in commits)
    print(f"Old range: {fmt(old_min_date)} - {fmt(old_max_date)}")
    new_min_date = min_date or old_min_date
    new_max_date = max_date or old_max_date
    print(f"New range: {fmt(new_min_date)} - {fmt(new_max_date)}")

    # Setup the rules
    work_rule = WorkDayRule(
        start_time=parsed_work_hour_start,
        end_time=parsed_work_hour_end,
        working_days=[int(d) - 1 for d in work_days.split(",")],
        tz=local_tz,
    )
    new_work_range = work_rule.difference(new_min_date, new_max_date)
    new_work_seconds = new_work_range.hours * 3600 + new_work_range.seconds

    # Compute new dates
    redates = {}
    for commit in commits:
        old_date = commit.min_datetime
        if old_min_date == old_max_date:
            work_seconds = 0
        else:
            work_seconds = remap(
                old_date, old_min_date, old_max_date, 0, new_work_seconds
            )
        new_date = new_min_date + BusinessTimeDelta(work_rule, seconds=work_seconds)
        redates[commit.hexsha] = (old_date, new_date)
        print(f"Redating {commit.hexsha[:7]}:    {fmt(old_date)} → {fmt(new_date)}")

    if show_chart:
        chart(
            redates,
            old_min_date,
            old_max_date,
            new_min_date,
            new_max_date,
            parsed_work_days,
            parsed_work_hour_start,
            parsed_work_hour_end,
        )

    print()
    if not (yes or input("Do you want to apply these changes ? [yN] ").lower() == "y"):
        print("Operation cancelled by user")
        sys.exit(1)

    # Make a backup branch if needed
    make_backup_branch(repo)

    # Start rebase
    os.environ["GIT_SEQUENCE_EDITOR"] = "gitredate-rebase-sequence-editor"
    repo.git.rebase("--interactive", rebase_ref)

    # Ammend each commit
    print()
    for i in count():
        rebase_commit = repo.commit("REBASE_HEAD")
        new_date = redates[rebase_commit.hexsha][1]
        print(f"Processing {rebase_commit.hexsha[:7]} ({i}/{len(redates)})")
        repo.git.commit(
            "--amend",
            "--no-edit",
            f'--date="{new_date}"',
            env={"GIT_COMMITTER_DATE": str(new_date)},
        )
        repo.git.rebase("--continue")
        if rebase_commit == current_commit:
            break
