"""Harness builder: uses Claude API to analyze a repo and generate CLI harness files."""

import logging
import re
from pathlib import Path

import anthropic

import config
import github_ops

logger = logging.getLogger(__name__)

# Try multiple possible locations for HARNESS.md
_HARNESS_CANDIDATES = [
    Path(__file__).parent / "HARNESS.md",
    Path(__file__).parent.parent / "cli-anything-plugin" / "HARNESS.md",
]


def _load_harness_md() -> str:
    """Load the HARNESS.md methodology document."""
    for p in _HARNESS_CANDIDATES:
        if p.is_file():
            return p.read_text()
    logger.warning("HARNESS.md not found, using embedded summary")
    return (
        "Follow the CLI-Anything methodology: analyze the codebase, design CLI architecture, "
        "implement Click-based CLI with REPL, write tests, create setup.py for PyPI packaging. "
        "See https://github.com/anthropics/CLI-Anything for full methodology."
    )


def _collect_repo_context(local_path: Path) -> str:
    """Build a context string from the repo's structure and key files."""
    parts = []

    # File tree
    tree = github_ops.get_file_tree(local_path, max_depth=3)
    parts.append(f"## Repository file tree\n```\n{tree}\n```")

    # Priority files (READMEs, build configs)
    priority = github_ops.read_priority_files(local_path)
    for name, content in priority.items():
        if len(content) > 15_000:
            content = content[:15_000] + "\n... (truncated)"
        parts.append(f"## {name}\n```\n{content}\n```")

    # Code files (up to budget)
    remaining_budget = config.MAX_CONTEXT_FILES - len(priority)
    code_files = github_ops.read_code_files(local_path, budget=max(remaining_budget, 20))
    for name, content in code_files.items():
        if len(content) > 10_000:
            content = content[:10_000] + "\n... (truncated)"
        parts.append(f"## {name}\n```\n{content}\n```")

    return "\n\n".join(parts)


def _parse_generated_files(response_text: str) -> dict[str, str]:
    """Parse Claude's response to extract generated files.

    Expects files wrapped in <file path="...">...</file> tags.
    """
    pattern = r'<file\s+path="([^"]+)">\s*\n?(.*?)\s*</file>'
    matches = re.findall(pattern, response_text, re.DOTALL)

    files = {}
    for path, content in matches:
        files[path.strip()] = content.strip() + "\n"

    return files


def _stream_message(client, **kwargs) -> str:
    """Send a message using streaming and return the full response text."""
    collected = []
    with client.messages.stream(**kwargs) as stream:
        for text in stream.text_stream:
            collected.append(text)
    return "".join(collected)


def build_harness(local_path: Path, software_name: str) -> tuple[dict[str, str], str]:
    """Run the full harness build pipeline via Claude API.

    Returns (generated_files, summary) where generated_files is a dict of
    relative_path -> file_content, and summary is a human-readable description.
    """
    harness_md = _load_harness_md()
    repo_context = _collect_repo_context(local_path)

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # Phase 1-2: Analysis and Architecture
    logger.info("Phase 1-2: Analyzing codebase and designing CLI architecture...")
    analysis_text = _stream_message(
        client,
        model=config.CLAUDE_MODEL,
        max_tokens=16_000,
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are an expert software architect building a CLI harness for a GUI application.\n\n"
                    f"# Methodology\n{harness_md}\n\n"
                    f"# Target Software: {software_name}\n\n"
                    f"# Repository Contents\n{repo_context}\n\n"
                    f"# Task: Phase 1-2\n"
                    f"Perform Phase 1 (Codebase Analysis) and Phase 2 (CLI Architecture Design) "
                    f"from the methodology above.\n\n"
                    f"Provide:\n"
                    f"1. Backend engine identification\n"
                    f"2. GUI-to-API action mapping\n"
                    f"3. Data model and file format analysis\n"
                    f"4. Existing CLI tools found\n"
                    f"5. Command group design\n"
                    f"6. State model design\n"
                    f"7. The complete <SOFTWARE>.md document\n\n"
                    f"Output the analysis document inside:\n"
                    f'<file path="{software_name}/agent-harness/{software_name.upper()}.md">...content...</file>'
                ),
            }
        ],
    )
    analysis_files = _parse_generated_files(analysis_text)
    logger.info("Phase 1-2 complete: %d files", len(analysis_files))

    # Phase 3: Implementation
    logger.info("Phase 3: Generating CLI implementation...")
    impl_text = _stream_message(
        client,
        model=config.CLAUDE_MODEL,
        max_tokens=64_000,
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are building a CLI harness following the CLI-Anything methodology.\n\n"
                    f"# Methodology\n{harness_md}\n\n"
                    f"# Software: {software_name}\n\n"
                    f"# Analysis from Phase 1-2\n{analysis_text}\n\n"
                    f"# Task: Phase 3 — Implementation\n"
                    f"Generate ALL implementation files for the CLI harness. Follow the directory "
                    f"structure from the methodology exactly.\n\n"
                    f"Required files:\n"
                    f"- `{software_name}/agent-harness/setup.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/__init__.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/__main__.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/{software_name}_cli.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/README.md`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/core/__init__.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/core/project.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/core/session.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/core/export.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/utils/__init__.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/utils/{software_name}_backend.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/utils/repl_skin.py`\n\n"
                    f"IMPORTANT:\n"
                    f"- Use Click for the CLI framework\n"
                    f"- Support both one-shot subcommands and interactive REPL\n"
                    f"- Every command must support --json output\n"
                    f"- The backend module MUST call the real software via subprocess\n"
                    f"- Use PEP 420 namespace packages (NO __init__.py in cli_anything/ root)\n"
                    f"- REPL must be default behavior (invoke_without_command=True)\n\n"
                    f"Output each file inside <file path=\"...\">...content...</file> tags."
                ),
            }
        ],
    )
    impl_files = _parse_generated_files(impl_text)
    logger.info("Phase 3 complete: %d files", len(impl_files))

    # Phase 4-5: Test Planning and Implementation
    logger.info("Phase 4-5: Generating tests...")
    test_text = _stream_message(
        client,
        model=config.CLAUDE_MODEL,
        max_tokens=32_000,
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are building tests for a CLI harness following the CLI-Anything methodology.\n\n"
                    f"# Methodology (testing sections)\n{harness_md}\n\n"
                    f"# Software: {software_name}\n\n"
                    f"# Implementation files generated\n"
                    + "\n".join(f"- {p}" for p in impl_files.keys())
                    + f"\n\n# Key implementation code\n"
                    + "\n\n".join(
                        f"## {p}\n```python\n{c[:5000]}\n```"
                        for p, c in impl_files.items()
                        if p.endswith(".py") and "test" not in p
                    )
                    + f"\n\n# Task: Phase 4-5 — Test Planning and Implementation\n"
                    f"Generate:\n"
                    f"1. TEST.md with the test plan\n"
                    f"2. test_core.py with unit tests (synthetic data, no external deps)\n"
                    f"3. test_full_e2e.py with E2E tests and subprocess tests\n\n"
                    f"Include the _resolve_cli helper in test_full_e2e.py.\n"
                    f"Include TestCLISubprocess class.\n\n"
                    f"Output each file inside <file path=\"...\">...content...</file> tags.\n"
                    f"Paths should be relative, e.g.:\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/tests/TEST.md`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/tests/test_core.py`\n"
                    f"- `{software_name}/agent-harness/cli_anything/{software_name}/tests/test_full_e2e.py`\n"
                ),
            }
        ],
    )
    test_files = _parse_generated_files(test_text)
    logger.info("Phase 4-5 complete: %d files", len(test_files))

    # Merge all generated files
    all_files = {}
    all_files.update(analysis_files)
    all_files.update(impl_files)
    all_files.update(test_files)

    # Build summary
    summary = (
        f"Analyzed the `{software_name}` codebase and generated a complete CLI harness "
        f"with {len(all_files)} files following the CLI-Anything HARNESS.md methodology.\n\n"
        f"**Phases completed:**\n"
        f"- Phase 1: Codebase analysis (backend engine, data model, GUI-to-API mapping)\n"
        f"- Phase 2: CLI architecture design (command groups, state model, output format)\n"
        f"- Phase 3: Implementation (Click CLI, REPL, core modules, backend wrapper)\n"
        f"- Phase 4-5: Test planning and implementation (unit + E2E + subprocess tests)\n"
    )

    logger.info("Build complete: %d files generated", len(all_files))
    return all_files, summary
