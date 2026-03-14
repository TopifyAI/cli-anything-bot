# cli-anything-bot

A GitHub bot that automatically converts any GUI application repository into an
agent-native CLI using the [CLI-Anything](https://github.com/anthropics/CLI-Anything) methodology.

## How it works

```
1. Email chenglinwei@topify.ai to request access (include your GitHub username)
2. Once approved, invite @cli-anything-bot to your repo (Settings → Collaborators → Add)
3. The bot auto-accepts the invitation
4. Create an issue or comment with: /cli-anything
5. The bot analyzes your codebase and generates a complete CLI harness
6. A PR appears with the generated CLI — review, tweak, merge
```

> **Access is by approval only.** To prevent abuse, the bot only accepts
> invitations and processes requests from approved GitHub users. Email
> **chenglinwei@topify.ai** to request access.

### What gets generated

The bot follows the [HARNESS.md](../cli-anything-plugin/HARNESS.md) methodology
to produce a full CLI package:

```
your-software/agent-harness/
├── YOUR_SOFTWARE.md         # Codebase analysis and architecture doc
├── setup.py                 # PyPI-ready package config
└── cli_anything/your_software/
    ├── your_software_cli.py # Click CLI with interactive REPL
    ├── core/
    │   ├── project.py       # Project create/open/save
    │   ├── session.py       # Undo/redo, state management
    │   └── export.py        # Render pipeline via real software
    ├── utils/
    │   ├── your_software_backend.py  # Subprocess wrapper for real software
    │   └── repl_skin.py     # Interactive REPL interface
    └── tests/
        ├── TEST.md          # Test plan and results
        ├── test_core.py     # Unit tests (no external deps)
        └── test_full_e2e.py # E2E + subprocess tests
```

### Trigger formats

| Command | Behavior |
|---------|----------|
| `/cli-anything` | Uses repo name as software name |
| `/cli-anything build` | Same as above |
| `/cli-anything build gimp` | Uses "gimp" as software name |

The bot responds to triggers in **issue bodies** and **issue comments**.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  GitHub Issue    │────▶│  Bot (polls  │────▶│  Claude API  │
│  /cli-anything   │     │  notifications│     │  (analysis + │
└─────────────────┘     │  every 30s)  │     │  generation) │
                        └──────┬───────┘     └─────────────┘
                               │
                        ┌──────▼───────┐
                        │  Opens PR    │
                        │  with harness │
                        └──────────────┘
```

The bot is a Python service that:
1. **Polls** the bot account's GitHub notifications every 30 seconds
2. **Detects** `/cli-anything` triggers in issues where it's mentioned
3. **Clones** the target repository
4. **Analyzes** the codebase using Claude API (Phases 1-2 of HARNESS.md)
5. **Generates** the full CLI implementation (Phase 3)
6. **Creates** tests (Phases 4-5)
7. **Opens a PR** with all generated files

## Setup

### Prerequisites

- Python 3.12+
- A GitHub bot account with a Personal Access Token (classic) — scopes: `repo`, `notifications`
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Create the bot account

1. Create a new GitHub account (e.g., `cli-anything-bot`)
2. Go to **Settings → Developer settings → Personal access tokens → Tokens (classic)**
3. Generate a token with scopes: `repo`, `notifications`
4. Save the token securely

### 2. Configure environment

```bash
cd bot/
cp .env.example .env
```

Edit `.env`:

```
GITHUB_TOKEN=ghp_your_bot_token_here
BOT_USERNAME=cli-anything-bot
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

### 3. Install and run

```bash
pip install -r requirements.txt
python main.py
```

### 4. Run with Docker

From the repository root:

```bash
docker build -f bot/Dockerfile -t cli-anything-bot .
docker run --env-file bot/.env cli-anything-bot
```

### 5. Test a single poll cycle

```bash
python main.py --once
```

## Using the bot

### For repo owners

1. Go to your repo → **Settings → Collaborators → Add people**
2. Invite the bot account (e.g., `@cli-anything-bot`) with **Write** access
3. The bot must accept the invitation (it does this automatically when it processes notifications)
4. Create an issue with `/cli-anything` in the body
5. The bot will comment acknowledging the request, then open a PR when done

### What happens step by step

1. You post `/cli-anything` in an issue
2. Bot reacts with 👀 and comments that it's working
3. Bot clones your repo and sends the codebase to Claude API for analysis
4. Claude analyzes the backend engine, data model, and GUI-to-API mappings
5. Claude generates a complete CLI with Click commands, REPL, tests, and packaging
6. Bot commits the generated files to a new branch and opens a PR
7. Bot comments on your issue with a link to the PR

### Example issue body

```markdown
Title: Add CLI-Anything harness

/cli-anything

Please generate a CLI harness for this project so AI agents can use it
without a GUI.
```

## Security and trust

This bot is fully open source. Here's what it does and doesn't do:

### What it does
- Reads your repository's source code (public files only)
- Sends file contents to Claude API for analysis
- Creates a new branch and opens a PR (never pushes to main)
- Comments on issues to report status

### What it does NOT do
- Modify any existing files in your repo
- Push to your default branch
- Access secrets, environment variables, or CI configurations
- Store your code anywhere (temporary clones are deleted after processing)
- Run any code from your repository

### Permissions required
- **Read** access: to clone and analyze the repository
- **Write** access: to create branches, open PRs, and post comments

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes | — | Bot account PAT (scopes: repo, notifications) |
| `BOT_USERNAME` | No | `cli-anything-bot` | Bot's GitHub username |
| `ANTHROPIC_API_KEY` | Yes | — | Anthropic API key for Claude |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-20250514` | Claude model to use |
| `POLL_INTERVAL` | No | `30` | Seconds between notification polls |
| `WORK_DIR` | No | `/tmp/cli-anything-bot` | Temp directory for cloned repos |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py

# Run a single poll cycle (useful for testing)
python main.py --once

# Check logs
LOG_LEVEL=DEBUG python main.py
```

## License

Same as the parent [CLI-Anything](https://github.com/anthropics/CLI-Anything) project.
