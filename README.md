# glassfrog-cli

A command-line tool for read-only access to the [GlassFrog](https://www.glassfrog.com/) API. Browse your organization's circles, roles, people, projects, assignments, and meeting data from the terminal.

> **This is a vibe coded project.** It was built with AI assistance and has not yet undergone a thorough manual review. There are no guarantees of correctness, completeness, or stability. **Only read-only API operations are supported** -- no mutations will be added until the author has time for a proper review of the codebase. Use at your own risk.

## Features

- Browse circles, roles, people, projects, assignments, and meeting data
- Render circle hierarchy as an indented tree
- Table output with rich terminal formatting (default) or JSON
- Three-tier API token resolution (CLI flag, environment variable, config file)
- Friendly error messages for auth failures, rate limits, and network issues

## Installation

### From source (pip)

```
pip install -e .
```

### Nix

```
# Run directly
nix run github:rschaffar/glassfrog-cli

# Development shell
nix develop
```

## Configuration

The CLI needs a GlassFrog API token. It is resolved in this order:

1. `--token` / `-t` flag
2. `GLASSFROG_API_TOKEN` environment variable
3. `~/.config/glassfrog/config.toml`

Config file example:

```toml
[auth]
token = "your-api-token-here"
```

## Usage

```
gf [OPTIONS] COMMAND [ARGS]
```

### Global options

| Option | Description |
|---|---|
| `-t`, `--token` | GlassFrog API token |
| `-o`, `--output` | Output format: `table` (default) or `json` |
| `--no-color` | Disable colored output |
| `--version` | Show version |
| `--help` | Show help |

### Commands

| Command | Subcommands | Description |
|---|---|---|
| `circles` | `list`, `show <id>`, `tree` | Browse circles and view hierarchy |
| `roles` | `list [--circle ID]`, `show <id>` | Browse roles, optionally filter by circle |
| `people` | `list`, `show <id>` | Browse people |
| `projects` | `list [--circle ID]` | Browse projects, optionally filter by circle |
| `assignments` | `list [--role ID] [--person ID]` | Browse role assignments with optional filters |
| `meetings` | `checklist --circle ID`, `metrics --circle ID`, `actions [--circle ID]` | Browse checklists, metrics, and actions |

### Examples

```
# List all circles
gf circles list

# Show circle hierarchy as a tree
gf circles tree

# Show details for a specific role
gf roles show 42

# List projects for a circle in JSON format
gf -o json projects list --circle 123

# List role assignments for a person
gf assignments list --person 456

# Show checklist items for a circle
gf meetings checklist --circle 123
```

## Development

```
# Clone and enter dev shell (Nix)
git clone git@github.com:rschaffar/glassfrog-cli.git
cd glassfrog-cli
nix develop

# Or install with dev dependencies (pip)
pip install -e ".[dev]"

# Run tests
pytest

# Lint and format check
ruff check src/ tests/
ruff format --check src/ tests/
```

CI runs lint and tests on every push to `main` and on pull requests. Dependabot checks for outdated dependencies daily and GitHub Actions updates weekly.

## License

MIT -- see [LICENSE](LICENSE).
