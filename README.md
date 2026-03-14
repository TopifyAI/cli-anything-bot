# cli-anything-bot

A GitHub bot that automatically converts any GUI application repository into an
agent-native CLI using the [CLI-Anything](https://github.com/anthropics/CLI-Anything) methodology.

## How it works

```
1. Email chenglinwei@topify.ai to request access
2. Invite @cli-anything-bot to your repo (Settings → Collaborators → Add)
3. Once approved, the operator accepts the invitation
4. Create an issue with: /cli-anything
5. The bot analyzes your codebase and generates a complete CLI harness
6. A PR appears with the generated CLI — review, tweak, merge
```

> **Access is by approval only.** The bot does not auto-accept invitations.
> To request access, email **chenglinwei@topify.ai** with your GitHub
> username and the repository you want to use it on.

## What gets generated

The bot follows the [HARNESS.md](HARNESS.md) methodology to produce a full
CLI package:

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

## Trigger formats

| Command | Behavior |
|---------|----------|
| `/cli-anything` | Uses repo name as software name |
| `/cli-anything build` | Same as above |
| `/cli-anything build gimp` | Uses "gimp" as software name |

The bot responds to triggers in **issue bodies** and **issue comments**.

## Requesting access

1. Email **chenglinwei@topify.ai** with:
   - Your GitHub username
   - The repository you want to use it on
   - A brief description of your use case
2. Invite `@cli-anything-bot` as a collaborator on your repo with **Write** access
3. Once approved, the bot operator accepts the invitation
4. Create an issue with `/cli-anything` in the body
5. The bot comments acknowledging the request, then opens a PR when done

## What happens step by step

1. You create an issue with `/cli-anything`
2. Bot reacts with :eyes: and comments that it's working
3. Bot clones your repo and sends the codebase to Claude API for analysis
4. Claude analyzes the backend engine, data model, and GUI-to-API mappings
5. Claude generates a complete CLI with Click commands, REPL, tests, and packaging
6. Bot commits the generated files to a new branch and opens a PR
7. Bot comments on your issue with a link to the PR

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

## Security and trust

This bot is fully open source. Here's what it does and doesn't do:

**What it does:**
- Reads your repository's source code (public files only)
- Sends file contents to Claude API for analysis
- Creates a new branch and opens a PR (never pushes to main)
- Comments on issues to report status

**What it does NOT do:**
- Modify any existing files in your repo
- Push to your default branch
- Access secrets, environment variables, or CI configurations
- Store your code anywhere (temporary clones are deleted after processing)
- Run any code from your repository
- Auto-accept invitations (operator must manually approve)

**Permissions required:**
- **Read** access: to clone and analyze the repository
- **Write** access: to create branches, open PRs, and post comments

## Operator guide

### Setup

**Prerequisites:** Python 3.12+, a GitHub bot account PAT (`repo` + `notifications` scopes), an [Anthropic API key](https://console.anthropic.com/).

```bash
cp .env.example .env
# Edit .env with your tokens
pip install -r requirements.txt
python main.py
```

### Approving access requests

When someone emails requesting access and invites the bot to their repo:

```bash
python main.py --invites
```

This shows all pending invitations. Select one to accept, or type `all`:

```
  [1] user/their-repo (invited by @user, id: 12345)

Accept which? (number, 'all', or Enter to skip): 1
  Accepted: user/their-repo
```

### Other commands

```bash
python main.py              # Start the bot (polling loop)
python main.py --once       # Single poll cycle (for testing)
python main.py --invites    # List and accept pending invitations
```

### Docker

```bash
docker build -t cli-anything-bot .
docker run -d --restart always --env-file .env cli-anything-bot
```

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
| `DAILY_LIMIT_PER_USER` | No | `3` | Max builds per user per day |
| `DAILY_LIMIT_GLOBAL` | No | `20` | Max builds globally per day |

## License

Same as the parent [CLI-Anything](https://github.com/anthropics/CLI-Anything) project.
