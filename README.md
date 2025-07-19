# Noteist

A script to generate a Markdown report of completed tasks in a Todoist project.


## Features
- Lists completed tasks for a specified project and date range
- Outputs in Markdown format
- Supports sub-tasks and descriptions


## Requirements

1. Get your Todoist API Token
   * Log in to your [Todoist account](https://todoist.com/).
   * Go to **Settings** > **Integrations** > **Developer (tab)**.
   * Copy your **API token** from the "API token" section.
2. Install [UV](https://docs.astral.sh/uv/getting-started/installation/)


## Usage

```
uvx noteist -h                                                               
usage: noteist [-h] --project PROJECT --token TOKEN [--since SINCE] [--until UNTIL] [--debug]

Output a Markdown formatted report of completed tasks in Todoist.

options:
  -h, --help         show this help message and exit
  --project PROJECT  Project name (e.g., Work)
  --token TOKEN      Todoist API token
  --since SINCE      Start date (YYYY-MM-DD, default: one week ago)
  --until UNTIL      End date (YYYY-MM-DD, default: today)
  --debug            Enable debug logging
```

Example:
```sh
uvx noteist --project "Work" --since 2025-07-01 --until 2025-07-15
```

## Development

To run the script locally while in development.

1. Clone the repository.
2. Then run the script with: `uv run -m noteist`


## Formatting Code
To format the codebase using [ruff](https://docs.astral.sh/ruff/):

```sh
just format
```

## License
MIT

