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

Print help:

```sh
uvx noteist --help                                                               
```

Out completed tasks for the Todoist project Work with the default of two weeks:
```sh
uvx noteist --project "Work" --token <TOKEN>
```

Save the project "Work" and your token as the defaults:
```sh
uvx noteist --project "Work" --token <TOKEN> --save-project --save-token
```

Specify the time range:
```sh
uvx noteist --since 2025-07-01 --until 2025-07-15
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

