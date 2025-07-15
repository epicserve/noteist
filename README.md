# Todoist Report

A script to generate a Markdown report of completed tasks in a Todoist project.

## Features
- Lists completed tasks for a specified project and date range
- Outputs in Markdown format
- Supports sub-tasks and descriptions

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. If you don't have `uv` installed, follow the instructions on their GitHub page.

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd todoist-report
   ```
2. **Install dependencies:**
   ```sh
   uv sync
   ```

## Configuration

### Get Your Todoist API Token
1. Log in to your [Todoist account](https://todoist.com/).
2. Go to **Settings** > **Integrations** > **Developer (tab)**.
3. Copy your **API token** from the "API token" section.

### Set Up Your `.env` File
Create a file named `.env` in the project root with the following content:

```
TODOIST_API_TOKEN=your_todoist_api_token_here
```

Replace `your_todoist_api_token_here` with your actual Todoist API token.

## Usage

Run the script with Python 3.13 or later:

```sh
uv run todoist_report.py --project "Project Name" [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--debug]
```

- `--project` (required): Name of the Todoist project (e.g., `Work`)
- `--since`: Start date (default: one week ago)
- `--until`: End date (default: today)
- `--debug`: Enable debug logging

Example:
```sh
uv run todoist_report.py --project "Work" --since 2025-07-01 --until 2025-07-15
```

## Output
The script prints a Markdown-formatted list of completed tasks, including sub-tasks and descriptions, for the specified project and date range.

## Formatting Code
To format the codebase using [ruff](https://docs.astral.sh/ruff/):

```sh
just format
```

## License
MIT

