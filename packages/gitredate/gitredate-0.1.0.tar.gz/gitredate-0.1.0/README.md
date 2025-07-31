# GitRedate

Rewrite commit dates and times in your git history to business hours.

Features:
- sets date during working hours
- keeps more or less delta time between commits
- preserves consistency with merge commits

## Usage

This requires UV, if you don't have it yet, install with `pip install uv`.

```bash
uvx gitredate --help
```

```
Usage: gitredate.exe [OPTIONS] [BASE_REF]

╭─ Arguments ──────────────────────────────────────────────────────────────────────────╮
│   base_ref      [BASE_REF]  Base ref at which redating starts. If empty, will redate │
│                             the last commit only. Set `root` the redate the whole    │
│                             history.                                                 │
│                             [default: HEAD~1]                                        │
╰──────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────╮
│ --min-date                  YYYY-MM-DD(THH:MM(:SS))  Custom start date and time      │
│                                                      [default: None]                 │
│ --max-date                  YYYY-MM-DD(THH:MM(:SS))  Custom end date and time        │
│                                                      [default: None]                 │
│ --working-days              TEXT                     Working days, provide this      │
│                                                      argument for each working day   │
│                                                      (monday=1)                      │
│                                                      [default: 1,2,3,4,5]            │
│ --working-hour-start        HH:MM(:SS)               Work day starting hour          │
│                                                      [default: 8:00]                 │
│ --working-hour-end          HH:MM(:SS)               Work day ending hour            │
│                                                      [default: 18:00]                │
│ --repository                PATH                     Path to the git repository      │
│                                                      [default: .]                    │
│ --help                                               Show this message and exit.     │
╰──────────────────────────────────────────────────────────────────────────────────────╯
```
