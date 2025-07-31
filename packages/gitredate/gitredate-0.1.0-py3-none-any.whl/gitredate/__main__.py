import sys

import typer

if len(sys.argv) > 1 and sys.argv[1] == "edit-todo":
    del sys.argv[1]
    from .utils import rebase_sequence_editor

    typer.run(rebase_sequence_editor)
else:
    from .main import redate

    typer.run(redate)
