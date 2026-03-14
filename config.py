import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
BOT_USERNAME = os.environ.get("BOT_USERNAME", "cli-anything-bot")
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))
WORK_DIR = Path(os.environ.get("WORK_DIR", "/tmp/cli-anything-bot"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Trigger keyword — users type this in an issue or comment
TRIGGER_KEYWORD = "/cli-anything"

# --- Abuse prevention ---

# Allowlist mode: "open" (anyone), "users" (allowed users only), "repos" (allowed repos only)
ACCESS_MODE = os.environ.get("ACCESS_MODE", "users")

# Comma-separated list of allowed GitHub usernames (when ACCESS_MODE=users)
ALLOWED_USERS = set(
    u.strip().lower()
    for u in os.environ.get("ALLOWED_USERS", "").split(",")
    if u.strip()
)

# Comma-separated list of allowed repos like "owner/repo" (when ACCESS_MODE=repos)
ALLOWED_REPOS = set(
    r.strip().lower()
    for r in os.environ.get("ALLOWED_REPOS", "").split(",")
    if r.strip()
)

# Max builds per user per day (0 = unlimited)
DAILY_LIMIT_PER_USER = int(os.environ.get("DAILY_LIMIT_PER_USER", "3"))

# Max builds globally per day (0 = unlimited)
DAILY_LIMIT_GLOBAL = int(os.environ.get("DAILY_LIMIT_GLOBAL", "20"))

# Max files to send as context to Claude
MAX_CONTEXT_FILES = 80
MAX_FILE_SIZE = 50_000  # bytes

# File extensions to include in repo analysis
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".c", ".cpp", ".h", ".hpp",
    ".java", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
    ".cs", ".lua", ".sh", ".bash", ".zsh", ".pl", ".r", ".m", ".mm",
    ".toml", ".yaml", ".yml", ".json", ".xml", ".ini", ".cfg", ".conf",
}

# Files always worth reading if they exist
PRIORITY_FILES = [
    "README.md", "README.rst", "README.txt", "README",
    "setup.py", "setup.cfg", "pyproject.toml",
    "package.json", "Cargo.toml", "go.mod", "build.gradle",
    "CMakeLists.txt", "Makefile", "meson.build",
    "CONTRIBUTING.md", "ARCHITECTURE.md",
]
