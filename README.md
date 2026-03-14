<h1 align="center">🤖&nbsp; CLI-Anything Bot</h1>

<p align="center">
  <strong>Invite the bot. Post a command. Get a CLI harness — as a PR.</strong><br>
  Automates the <a href="https://github.com/HKUDS/CLI-Anything">CLI-Anything</a> methodology via a GitHub bot.
</p>

<p align="center">
  <a href="#-get-started"><img src="https://img.shields.io/badge/Get_Started-3_Steps-blue?style=for-the-badge" alt="Get Started"></a>
  <a href="#-self-hosting"><img src="https://img.shields.io/badge/Self--Host-Your_Instance-green?style=for-the-badge" alt="Self-Host"></a>
  <a href="#-privacy--security"><img src="https://img.shields.io/badge/Privacy-Transparent-orange?style=for-the-badge" alt="Privacy"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-≥3.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Claude_API-Powered-blueviolet?logo=anthropic" alt="Claude">
  <img src="https://img.shields.io/badge/GitHub-Bot_Account-black?logo=github" alt="GitHub">
  <img src="https://img.shields.io/badge/output-Pull_Request-brightgreen" alt="Output">
</p>

---

## 🤔 What Is This?

CLI-Anything Bot brings the [CLI-Anything](https://github.com/HKUDS/CLI-Anything) methodology to any GitHub repository — without installing plugins or running commands yourself.

| Without the bot | With the bot |
|-----------------|--------------|
| Install Claude Code | Just invite the bot |
| Install the CLI-Anything plugin | Just post `/cli-anything` |
| Run the 7-phase pipeline manually | Bot does it automatically |
| Copy files into your repo | Bot opens a PR for you |

**One issue comment → full CLI harness as a pull request.**

---

## 🚀 Get Started

### Step 1: Invite the bot

Go to your repo → **Settings → Collaborators → Add people** → invite `cli-anything-bot` with **Write** access.

> Invitations are reviewed and approved manually. Most are accepted within 24 hours.
> To speed things up, email **chenglinwei@topify.ai**.

### Step 2: Trigger a build

Once the invitation is accepted, create an issue:

```
Title: Generate CLI harness

/cli-anything
```

Or comment `/cli-anything` on any existing issue.

### Step 3: Review the PR

The bot will:

1. 👀 React and comment that it's working
2. 🔍 Analyze your codebase (1-2 min)
3. 🔨 Generate the full CLI implementation (3-5 min)
4. 🧪 Generate tests (1-2 min)
5. 📬 Open a PR with all generated files

Review the PR, tweak if needed, and merge.

### Trigger formats

| Command | Behavior |
|---------|----------|
| `/cli-anything` | Uses repo name as software name |
| `/cli-anything build` | Same as above |
| `/cli-anything build gimp` | Uses "gimp" as software name |

---

## 📦 What Gets Generated

The bot produces a complete, installable CLI package following the [HARNESS.md](HARNESS.md) methodology:

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

| Feature | Description |
|---------|-------------|
| **One-shot commands** | `cli-anything-yoursoft project new --name demo` |
| **Interactive REPL** | Run with no arguments to enter interactive mode |
| **JSON output** | `--json` flag on every command for agent consumption |
| **Real software backend** | Calls the actual software via subprocess — not a reimplementation |
| **PyPI packaging** | `pip install -e .` puts it on PATH instantly |

---

## ⚙️ How It Works

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────┐
│ GitHub Issue  │────▶│  cli-anything-bot │────▶│  Claude API  │
│ /cli-anything │     │  (polls every     │     │  (3 phases:  │
└──────────────┘     │   30 seconds)     │     │   analyze,   │
                     └────────┬──────────┘     │   implement, │
                              │                │   test)      │
                     ┌────────▼──────────┐     └──────────────┘
                     │  Opens PR with    │
                     │  generated CLI    │
                     └───────────────────┘
```

### The 3-phase build pipeline

| Phase | What happens | Claude API call |
|-------|-------------|-----------------|
| **Phase 1-2: Analysis** | Identifies backend engine, maps GUI actions to APIs, designs CLI command groups, produces `SOFTWARE.md` | 1 call (~1 min) |
| **Phase 3: Implementation** | Generates all CLI source files — Click commands, REPL, core modules, backend wrapper, `setup.py` | 1 call (~3-5 min) |
| **Phase 4-5: Tests** | Creates `TEST.md` plan, unit tests (synthetic data), E2E tests, CLI subprocess tests with `_resolve_cli` | 1 call (~1-2 min) |

All phases follow the [HARNESS.md](HARNESS.md) methodology — the same standard used by the [CLI-Anything](https://github.com/HKUDS/CLI-Anything) plugin.

---

## 🔒 Privacy & Security

<table>
<tr>
<td width="50%">

### ✅ What the bot does
- Reads your repo's source code (common code extensions only, files <50KB)
- Sends file contents to Claude API for analysis
- Creates a **new branch** — never touches your default branch
- Opens a **pull request** — you review before merging
- Posts comments on issues (status updates only)

</td>
<td width="50%">

### ❌ What the bot does NOT do
- Modify any existing files in your repo
- Push to your default branch
- Access secrets, `.env` files, or CI configurations
- Store or cache your code anywhere
- Run any code from your repository
- Auto-accept invitations (operator approves manually)

</td>
</tr>
</table>

### Where your code goes

| Destination | Details |
|-------------|---------|
| **Claude API** | Source files are sent to Anthropic's API. [Anthropic's data policy](https://www.anthropic.com/policies) applies. API inputs are not used to train models. |
| **Temp clone** | Repo is cloned to a temp directory and **deleted immediately** after the PR is opened. |
| **No storage** | The bot does not log, store, or cache your source code. |

### If you self-host

When you run your own instance, your code is sent only to **your own Anthropic API key**. No third party sees your code. The bot is fully open source — audit every line.

---

## 🏠 Self-Hosting

You can run your own instance. **No dependency on CLI-Anything** — the bot is fully self-contained (bundles its own copy of HARNESS.md).

### Prerequisites

- Python 3.10+
- A dedicated GitHub account for the bot
- An [Anthropic API key](https://console.anthropic.com/)

### Quick start

```bash
git clone https://github.com/TopifyAI/cli-anything-bot.git
cd cli-anything-bot
cp .env.example .env
# Edit .env with your tokens
pip install -r requirements.txt
python main.py
```

### Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes | — | Bot account PAT (`repo` + `notifications` scopes) |
| `BOT_USERNAME` | No | `cli-anything-bot` | The bot's GitHub username |
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-20250514` | Claude model ID |
| `POLL_INTERVAL` | No | `30` | Seconds between notification polls |
| `WORK_DIR` | No | `/tmp/cli-anything-bot` | Temp directory for cloned repos |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `DAILY_LIMIT_PER_USER` | No | `3` | Max builds per user per day |
| `DAILY_LIMIT_GLOBAL` | No | `20` | Max builds globally per day |

### Creating the bot GitHub account

1. Create a new GitHub account (e.g., `my-cli-bot`)
2. **Settings → Developer settings → Personal access tokens → Tokens (classic)**
3. Generate with scopes: `repo`, `notifications`
4. Set `GITHUB_TOKEN` and `BOT_USERNAME` in `.env`

### Commands

```bash
python main.py              # Start the bot (continuous polling)
python main.py --once       # Single poll cycle (for testing)
python main.py --invites    # List and accept pending invitations
```

### Managing invitations

The bot **never auto-accepts** invitations. When someone invites your bot:

```bash
$ python main.py --invites

  [1] user/their-repo (invited by @user, id: 12345)
  [2] org/cool-project (invited by @dev, id: 67890)

Accept which? (number, 'all', or Enter to skip): 1
  Accepted: user/their-repo
```

### Docker

```bash
docker build -t cli-anything-bot .
docker run -d --restart always --env-file .env cli-anything-bot
```

### Cost estimates

Each build makes 3 Claude API calls. Approximate cost per build:

| Model | Cost per build |
|-------|---------------|
| `claude-sonnet-4-20250514` | $0.50 – $2.00 |
| `claude-opus-4-20250514` | $3.00 – $10.00 |

Use `DAILY_LIMIT_PER_USER` and `DAILY_LIMIT_GLOBAL` to control spending.

---

## 🔗 Relationship to CLI-Anything

| | [CLI-Anything](https://github.com/HKUDS/CLI-Anything) | cli-anything-bot |
|---|---|---|
| **What** | Plugin + methodology for manual use | GitHub bot that automates it |
| **How** | You run `/cli-anything` in Claude Code | Anyone posts `/cli-anything` in an issue |
| **Output** | Files generated in your local workspace | PR opened on the repo |
| **Runtime dependency** | Requires Claude Code | Standalone — just Python + API keys |

The bot bundles [HARNESS.md](HARNESS.md) and uses it as a prompt template. No installation of the CLI-Anything plugin is needed.

---

## 🔄 Does This Self-Improve?

**Not currently.** Output quality depends on two things:

1. **The Claude model** — set via `CLAUDE_MODEL` in `.env`
2. **The methodology** — the bundled [HARNESS.md](HARNESS.md)

The bot does not learn from past builds or incorporate PR feedback.

### How quality improves over time

| Method | How |
|--------|-----|
| **Better models** | Update `CLAUDE_MODEL` when Anthropic releases improved models |
| **Updated methodology** | Pull the latest HARNESS.md from upstream CLI-Anything |
| **Community PRs** | Improve prompts in `builder.py` or methodology in HARNESS.md |

---

## 📂 Project Structure

```
cli-anything-bot/
├── 📄 README.md           # You are here
├── 📄 LICENSE             # MIT License
├── 📄 HARNESS.md          # Bundled methodology (from CLI-Anything)
├── 📄 requirements.txt    # Python dependencies
├── 📄 .env.example        # Environment variable template
├── 📄 Dockerfile          # Container deployment
├── 🐍 main.py             # Entry point — polling, notifications, orchestration
├── 🐍 builder.py          # Claude API harness generation (3-phase pipeline)
├── 🐍 github_ops.py       # Git/GitHub operations — clone, branch, commit, PR
└── 🐍 config.py           # Configuration from environment variables
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

**cli-anything-bot** — *Invite. Trigger. Get a CLI.*

<sub>Powered by <a href="https://github.com/HKUDS/CLI-Anything">CLI-Anything</a> methodology and <a href="https://anthropic.com">Claude</a></sub>

</div>
