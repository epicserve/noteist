# Noteist

Print out a report of completed tasks in a Todoist project in Markdown.


## Features
- Lists completed tasks for a specified project and date range
- Outputs in Markdown format
- Supports sub-tasks and descriptions


## Requirements

1. Get your Todoist API Token
   * Log in to your [Todoist account](https://todoist.com/).
   * Go to **Settings** > **Integrations** > **Developer (tab)**.
   * Copy your **API token** from the "API token" section.
2. A Python Interpreter


## Install

It's recommended you use [UV](https://docs.astral.sh/uv/) and either install as a tool
(`uv tool install noteist`) or run it with `uvx noteist`. You can also install it with
`pip` if you prefer.


## Usage

Print help:
```sh
noteist --help
```

Print out completed tasks for the Todoist project Work with the default of two weeks:
```sh
noteist --project "Work" --token <TOKEN>
```

Save the project "Work" as the default:
```sh
noteist config set project Work
```

Save the token "example-token" as the default:
```sh
noteist config set token example-token
```

List saved defaults:
```sh
noteist config list
```

Unset a saved default:
```sh
noteist config unset project
```

Specify the time range:
```sh
noteist --since 2025-07-01 --until 2025-07-15
```

Use relative dates, with anything [dateparser](https://dateparser.readthedocs.io/en/latest/#) supports:
```sh
noteist --since "-7d" --until "-3d"
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

