# cli-anything-bot

A GitHub bot that automatically converts any software repository into an
agent-native CLI. Powered by [Claude](https://anthropic.com) and the
[CLI-Anything](https://github.com/anthropics/CLI-Anything) methodology.

When triggered, the bot analyzes your codebase, generates a complete CLI
harness (commands, REPL, tests, packaging), and opens a pull request — all
without you writing a single line.

---

## Using the hosted bot

The easiest way to use cli-anything-bot is through the hosted instance at
`@cli-anything-bot`.

### Step 1: Invite the bot

Go to your repo → **Settings → Collaborators → Add people** → invite
`cli-anything-bot` with **Write** access.

The bot operator reviews and approves incoming invitations periodically.
To speed things up, you can email **chenglinwei@topify.ai**.

### Step 2: Trigger the build

Once the invitation is accepted, create an issue in your repo:

Create an issue in your repo with `/cli-anything` in the body:

```
Title: Generate CLI harness

/cli-anything
```

Or comment `/cli-anything` on any existing issue.

### Step 4: Review the PR

The bot will:
1. React with :eyes: and comment that it's working
2. Analyze your codebase (1-2 minutes)
3. Generate the CLI implementation (3-5 minutes)
4. Generate tests (1-2 minutes)
5. Open a PR with all generated files

Review the PR, make adjustments, and merge when ready.

### Trigger formats

| Command | Behavior |
|---------|----------|
| `/cli-anything` | Uses repo name as software name |
| `/cli-anything build` | Same as above |
| `/cli-anything build gimp` | Uses "gimp" as software name |

---

## What gets generated

The bot produces a complete, installable CLI package:

```
your-software/agent-harness/
├── YOUR_SOFTWARE.md              # Codebase analysis and architecture doc
├── setup.py                      # PyPI-ready package (pip install -e .)
└── cli_anything/your_software/
    ├── your_software_cli.py      # Click CLI with interactive REPL
    ├── README.md                 # Installation and usage guide
    ├── core/
    │   ├── project.py            # Project create/open/save
    │   ├── session.py            # Undo/redo, state management
    │   └── export.py             # Render pipeline via real software
    ├── utils/
    │   ├── your_software_backend.py  # Subprocess wrapper for real software
    │   └── repl_skin.py          # Branded interactive REPL
    └── tests/
        ├── TEST.md               # Test plan and results
        ├── test_core.py          # Unit tests (no external deps)
        └── test_full_e2e.py      # E2E + CLI subprocess tests
```

The generated CLI supports:
- **One-shot commands:** `cli-anything-yoursoft project new --name demo --json`
- **Interactive REPL:** Run with no arguments to enter an interactive session
- **JSON output:** `--json` flag on every command for machine consumption
- **Real software backend:** Calls the actual software (not a reimplementation)

---

## Hosting it yourself

You can run your own instance of cli-anything-bot. No dependency on the
CLI-Anything repository is required — the bot is fully self-contained.

### Prerequisites

- Python 3.10+
- A dedicated GitHub account for the bot
- An [Anthropic API key](https://console.anthropic.com/)

### Quick start

```bash
git clone https://github.com/TopifyAI/cli-anything-bot.git
cd cli-anything-bot
cp .env.example .env
# Edit .env with your tokens (see below)
pip install -r requirements.txt
python main.py
```

### Configuration

Edit `.env` with your values:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes | — | Bot account PAT with `repo` and `notifications` scopes |
| `BOT_USERNAME` | No | `cli-anything-bot` | The bot's GitHub username |
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-20250514` | Claude model ID |
| `POLL_INTERVAL` | No | `30` | Seconds between notification polls |
| `WORK_DIR` | No | `/tmp/cli-anything-bot` | Temp directory for cloned repos |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DAILY_LIMIT_PER_USER` | No | `3` | Max builds per user per day (0 = unlimited) |
| `DAILY_LIMIT_GLOBAL` | No | `20` | Max builds globally per day (0 = unlimited) |

### Creating the bot GitHub account

1. Create a new GitHub account (e.g., `my-cli-bot`)
2. Go to **Settings → Developer settings → Personal access tokens → Tokens (classic)**
3. Generate a token with scopes: `repo`, `notifications`
4. Set `GITHUB_TOKEN` and `BOT_USERNAME` in your `.env`

### Managing invitations

The bot **never auto-accepts invitations**. When someone invites your bot
to their repo, approve it manually:

```bash
python main.py --invites
```

```
  [1] user/their-repo (invited by @user, id: 12345)
  [2] org/another-repo (invited by @admin, id: 67890)

Accept which? (number, 'all', or Enter to skip): 1
  Accepted: user/their-repo
```

### Running commands

```bash
python main.py              # Start the bot (continuous polling)
python main.py --once       # Single poll cycle (for testing)
python main.py --invites    # List and accept pending invitations
```

### Docker deployment

```bash
docker build -t cli-anything-bot .
docker run -d --restart always --env-file .env cli-anything-bot
```

### Cost considerations

Each build makes 3 Claude API calls (analysis, implementation, tests). Typical
costs per build:

| Model | Approx. cost per build |
|-------|----------------------|
| `claude-sonnet-4-20250514` | $0.50 – $2.00 |
| `claude-opus-4-20250514` | $3.00 – $10.00 |

Use rate limits (`DAILY_LIMIT_PER_USER`, `DAILY_LIMIT_GLOBAL`) to control
spending. Start with Sonnet for cost efficiency — Opus produces higher quality
but at higher cost.

---

## Privacy and security

### What the bot accesses

- **Source code:** The bot clones your repository and reads source files to
  send as context to the Claude API. Only files matching common code extensions
  are read (see `config.py` for the full list). Files larger than 50KB are
  skipped.
- **Issues/comments:** The bot reads issue bodies and comments to detect the
  `/cli-anything` trigger.

### What the bot does NOT access

- Secrets, environment variables, or `.env` files
- CI/CD configurations or workflow files
- Private keys, credentials, or tokens
- Git history or blame data
- Any files outside the repository

### Where your code goes

- **Claude API:** Source file contents are sent to Anthropic's Claude API for
  analysis and code generation. Anthropic's [data retention policy](https://www.anthropic.com/policies)
  applies. API inputs are not used to train models.
- **Temporary clone:** The repo is cloned to a temp directory and deleted
  immediately after the PR is opened.
- **No storage:** The bot does not store, log, or cache your source code
  anywhere.

### What the bot writes to your repo

- Creates a **new branch** (`cli-anything/<software-name>`) — never touches
  your default branch
- Opens a **pull request** — you review before anything is merged
- Posts **comments** on the triggering issue (status updates only)
- Adds **only new files** — never modifies existing files in your repo

### If you're self-hosting

When you host your own instance, your code is sent to your own Anthropic API
key. No third party (including us) sees your code. The bot is fully open
source — audit the code yourself.

---

## Architecture

```
┌──────────────┐     ┌───────────────┐     ┌─────────────┐
│ GitHub Issue  │────▶│ Bot           │────▶│ Claude API  │
│ /cli-anything │     │ (polls every  │     │ (3 calls:   │
└──────────────┘     │  30 seconds)  │     │  analyze,   │
                     └──────┬────────┘     │  implement, │
                            │              │  test)      │
                     ┌──────▼────────┐     └─────────────┘
                     │ Opens PR with │
                     │ generated CLI │
                     └───────────────┘
```

**How the build works internally:**

1. **Phase 1-2 (Analysis):** Bot sends your repo's file tree and key source
   files to Claude. Claude identifies the backend engine, maps GUI actions to
   API calls, designs the CLI command structure, and produces a `SOFTWARE.md`
   architecture document.

2. **Phase 3 (Implementation):** Claude generates all CLI source files —
   Click commands, REPL interface, core modules (project, session, export),
   backend subprocess wrapper, and `setup.py` for packaging.

3. **Phase 4-5 (Tests):** Claude generates unit tests (synthetic data, no
   external deps), E2E tests (real file generation), and CLI subprocess tests
   with the `_resolve_cli` helper.

All three phases follow the [HARNESS.md](HARNESS.md) methodology, which is
bundled in this repository.

---

## Dependency on CLI-Anything

**None at runtime.** This bot is fully self-contained. It bundles a copy of
`HARNESS.md` (the methodology document) and uses it as a prompt template for
Claude API calls. You do not need to install the CLI-Anything plugin or any
of its harnesses.

The relationship:
- [CLI-Anything](https://github.com/anthropics/CLI-Anything) is the methodology
  and plugin for manual use with Claude Code
- **cli-anything-bot** automates that same methodology via a GitHub bot

If the upstream HARNESS.md is updated with improved techniques, you can pull
the latest copy into this repo to benefit from those improvements.

---

## Does this self-improve?

**Not currently.** The bot produces output based on two things:

1. The Claude model you configure (`CLAUDE_MODEL`)
2. The HARNESS.md methodology bundled in this repo

It does not learn from past builds, incorporate PR review feedback, or update
its own prompts.

**How quality improves over time:**

- **Better Claude models:** When Anthropic releases improved models, update
  `CLAUDE_MODEL` in your `.env` to get better output
- **Updated methodology:** When HARNESS.md is improved upstream (e.g., new
  testing strategies, better architecture patterns), pull the updated file
  into this repo
- **Community contributions:** Submit PRs to improve the prompts in
  `builder.py` or the methodology in `HARNESS.md`

---

## Rate limits

To prevent abuse and control costs:

| Limit | Default | Config variable |
|-------|---------|-----------------|
| Per-user daily | 3 builds | `DAILY_LIMIT_PER_USER` |
| Global daily | 20 builds | `DAILY_LIMIT_GLOBAL` |

Set to `0` for unlimited (not recommended for hosted instances).

---

## License

Same as the parent [CLI-Anything](https://github.com/anthropics/CLI-Anything) project.
