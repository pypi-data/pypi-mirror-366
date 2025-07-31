import datetime
import pathlib
import sys

import dateparser
from git import Repo


def rebase_sequence_editor():
    """
    This function serves as the GIT_SEQUENCE_EDITOR, which is a hacky
    way to programatically set all commits to edit in an interactive rebase
    """
    rebase_todo = pathlib.Path(sys.argv[1])
    rebase_todo.write_text(rebase_todo.read_text().replace("pick", "edit"))


def make_backup_branch(repo: Repo):
    backup_name = f"_redate-backup_{repo.active_branch.name}"
    try:
        backup_branch = repo.heads[backup_name]
    except IndexError:
        backup_branch = None
    if backup_branch is not None:
        if backup_branch.commit == repo.head.commit:
            print("Backup branch exists and is up to date.")
        else:
            user_input = input(
                "Backup branch is out of date! Do you want to [c]ontinue with the old backup, [f]orce update the backup, or [A]bort? "
            ).lower()
            if user_input == "c":
                pass
            elif user_input == "f":
                backup_branch = None
            else:
                print("Aborted!")
                sys.exit(1)
    if backup_branch is None:
        repo.create_head(backup_name, repo.head.commit, force=True)
        print("Created back branch")


def parse_datetime_str(datetime_str: str) -> datetime.datetime | None:
    if not datetime_str:
        return None
    return dateparser.parse(datetime_str, settings={"RETURN_AS_TIMEZONE_AWARE": True})


def parse_time_str(time_str: str) -> datetime.time:
    parts = time_str.lower().replace("h", ":").split(":")
    return datetime.time(*[int(part) for part in parts])


def remap(value, old_min, old_max, new_min=0, new_max=1):
    return (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min


def fmt(dt: datetime.datetime):
    return f"{dt.astimezone():%d %b %y %H:%M %z}"
