"""CLI-Anything Bot: polls GitHub notifications and builds CLI harnesses via PR."""

import logging
import sys
import time
import traceback
from collections import defaultdict
from datetime import date

from github import Auth, Github

import config
import github_ops
from builder import build_harness

# Rate limiting: track builds per user per day and global per day
_user_builds: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
_global_builds: dict[str, int] = defaultdict(int)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cli-anything-bot")


def _extract_trigger(text: str) -> str | None:
    """Check if text contains the trigger keyword. Returns software name or None.

    Supported formats:
        /cli-anything              -> uses repo name as software name
        /cli-anything build        -> uses repo name as software name
        /cli-anything build gimp   -> uses 'gimp' as software name
    """
    text_lower = text.lower().strip()
    if config.TRIGGER_KEYWORD not in text_lower:
        return None

    # Find the trigger and extract optional software name
    idx = text_lower.index(config.TRIGGER_KEYWORD) + len(config.TRIGGER_KEYWORD)
    rest = text_lower[idx:].strip()

    # Remove optional "build" keyword
    if rest.startswith("build"):
        rest = rest[len("build"):].strip()

    # Filter out @mentions — they're not software names
    words = [w for w in rest.split() if not w.startswith("@")]

    # Return explicit name or empty string (caller will use repo name)
    return words[0] if words else ""


def _check_access(username: str, repo_full_name: str) -> str | None:
    """Check if a user/repo is allowed. Returns denial reason or None if allowed."""
    if config.ALLOWED_USERS and username.lower() not in config.ALLOWED_USERS:
        return (
            f"User `@{username}` is not approved to use this bot.\n\n"
            f"To request access, email **chenglinwei@topify.ai** with:\n"
            f"- Your GitHub username\n"
            f"- The repository you want to use it on\n"
            f"- A brief description of your use case\n\n"
            f"Once approved, the bot will accept your invitation and be ready to use."
        )

    # Rate limiting
    today = date.today().isoformat()

    if config.DAILY_LIMIT_PER_USER > 0:
        if _user_builds[username][today] >= config.DAILY_LIMIT_PER_USER:
            return f"User `@{username}` has reached the daily limit of {config.DAILY_LIMIT_PER_USER} builds."

    if config.DAILY_LIMIT_GLOBAL > 0:
        if _global_builds[today] >= config.DAILY_LIMIT_GLOBAL:
            return "The bot has reached its global daily build limit."

    return None


def _record_build(username: str):
    """Record a build for rate limiting."""
    today = date.today().isoformat()
    _user_builds[username][today] += 1
    _global_builds[today] += 1


def _derive_software_name(repo_full_name: str) -> str:
    """Derive a software name from the repo's full name."""
    return repo_full_name.split("/")[-1].lower().replace("-", "_")


def _process_notification(notification):
    """Process a single GitHub notification that contains a trigger."""
    subject = notification.subject
    repo_full_name = notification.repository.full_name

    logger.info(
        "Processing trigger in %s: %s (#%s)",
        repo_full_name, subject.title, subject.type,
    )

    # Extract issue/PR number from the subject URL
    issue_number = None
    if subject.url:
        try:
            issue_number = int(subject.url.rstrip("/").split("/")[-1])
        except (ValueError, IndexError):
            pass

    # Read the actual issue/comment body to extract the trigger
    gh = Github(auth=Auth.Token(config.GITHUB_TOKEN))
    gh_repo = gh.get_repo(repo_full_name)
    trigger_text = ""
    comment_id = None

    if subject.type == "Issue":
        if issue_number:
            issue = gh_repo.get_issue(issue_number)
            # Check issue body first
            trigger_text = issue.body or ""
            if config.TRIGGER_KEYWORD not in trigger_text.lower():
                # Check latest comments
                comments = list(issue.get_comments())
                for c in reversed(comments):
                    if config.TRIGGER_KEYWORD in (c.body or "").lower():
                        trigger_text = c.body
                        comment_id = c.id
                        break
    elif subject.type == "PullRequest":
        if issue_number:
            pr = gh_repo.get_pull(issue_number)
            trigger_text = pr.body or ""
            if config.TRIGGER_KEYWORD not in trigger_text.lower():
                comments = list(pr.get_issue_comments())
                for c in reversed(comments):
                    if config.TRIGGER_KEYWORD in (c.body or "").lower():
                        trigger_text = c.body
                        comment_id = c.id
                        break

    software_name_override = _extract_trigger(trigger_text)
    if software_name_override is None:
        logger.info("No trigger found in body/comments, skipping")
        return

    software_name = software_name_override or _derive_software_name(repo_full_name)
    logger.info("Software name: %s", software_name)

    # Determine who triggered the build
    trigger_user = notification.repository.owner.login
    if subject.type == "Issue" and issue_number:
        trigger_user = gh_repo.get_issue(issue_number).user.login
    elif subject.type == "PullRequest" and issue_number:
        trigger_user = gh_repo.get_pull(issue_number).user.login

    # Access check
    denial = _check_access(trigger_user, repo_full_name)
    if denial:
        logger.info("Access denied for %s on %s: %s", trigger_user, repo_full_name, denial)
        if issue_number:
            github_ops.post_comment(
                repo_full_name, issue_number,
                f"⛔ **cli-anything-bot** cannot process this request.\n\n{denial}\n\n"
                f"Contact the bot operator to request access.",
            )
        return

    # Acknowledge with reaction and comment
    if comment_id:
        github_ops.add_reaction(repo_full_name, comment_id, "eyes")
    if issue_number:
        github_ops.post_comment(
            repo_full_name, issue_number,
            f"👀 **cli-anything-bot** is analyzing this repository and building a CLI harness "
            f"for `{software_name}`.\n\nThis may take a few minutes. I'll open a PR when ready.",
        )

    # Clone, build, PR
    local_path = None
    try:
        local_path = github_ops.clone_repo(repo_full_name, config.WORK_DIR)

        generated_files, summary = build_harness(local_path, software_name)

        if not generated_files:
            if issue_number:
                github_ops.post_comment(
                    repo_full_name, issue_number,
                    "❌ **cli-anything-bot** could not generate any files. "
                    "The repository may not contain a recognizable GUI application.",
                )
            return

        _record_build(trigger_user)

        branch = github_ops.create_branch_and_commit(local_path, generated_files, software_name)
        pr_url = github_ops.push_and_open_pr(
            repo_full_name, local_path, branch, software_name, summary, issue_number,
        )

        if issue_number:
            github_ops.post_comment(
                repo_full_name, issue_number,
                f"✅ **cli-anything-bot** has opened a PR with the generated CLI harness:\n\n"
                f"🔗 {pr_url}\n\n"
                f"Please review the generated code and tests. The harness follows the "
                f"[CLI-Anything HARNESS.md](https://github.com/anthropics/CLI-Anything/blob/main/cli-anything-plugin/HARNESS.md) methodology.",
            )

    except Exception:
        logger.error("Failed to process %s:\n%s", repo_full_name, traceback.format_exc())
        if issue_number:
            github_ops.post_comment(
                repo_full_name, issue_number,
                "❌ **cli-anything-bot** encountered an error while building the harness. "
                "Please check the bot logs or try again.",
            )
    finally:
        if local_path:
            github_ops.cleanup(local_path)


def poll_loop():
    """Main polling loop: check GitHub notifications for triggers."""
    gh = Github(auth=Auth.Token(config.GITHUB_TOKEN))
    bot_user = gh.get_user()
    logger.info("Bot started as @%s — polling every %ds", bot_user.login, config.POLL_INTERVAL)

    seen = set()

    while True:
        try:
            # Only accept invitations from approved users
            try:
                for invite in gh.get_user().get_invitations():
                    inviter = invite.inviter.login if invite.inviter else ""
                    repo_owner = invite.repository.owner.login if invite.repository else ""
                    # Accept if the inviter or repo owner is on the allowed list
                    allowed = not config.ALLOWED_USERS or (
                        inviter.lower() in config.ALLOWED_USERS
                        or repo_owner.lower() in config.ALLOWED_USERS
                    )
                    if allowed:
                        gh._Github__requester.requestJsonAndCheck(
                            "PATCH", f"/user/repository_invitations/{invite.id}"
                        )
                        logger.info("Accepted invitation from @%s: %s", inviter, invite.repository.full_name)
                    else:
                        logger.info(
                            "Ignored invitation from @%s (%s) — not approved",
                            inviter, invite.repository.full_name,
                        )
            except Exception:
                logger.debug("Could not check invitations: %s", traceback.format_exc())

            notifications = gh.get_user().get_notifications(all=False)
            for n in notifications:
                if n.id in seen:
                    continue
                seen.add(n.id)

                def _safe_mark_read(notif):
                    try:
                        notif.mark_as_read()
                    except Exception:
                        pass  # May lack admin rights on some repos

                # Only process issues and PRs where we might be mentioned
                if n.subject.type not in ("Issue", "PullRequest"):
                    _safe_mark_read(n)
                    continue

                if n.reason not in ("mention", "team_mention", "subscribed", "assign"):
                    _safe_mark_read(n)
                    continue

                try:
                    _process_notification(n)
                except Exception:
                    logger.error("Error processing notification %s:\n%s", n.id, traceback.format_exc())
                finally:
                    _safe_mark_read(n)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception:
            logger.error("Poll error:\n%s", traceback.format_exc())

        time.sleep(config.POLL_INTERVAL)


def main():
    """Entry point."""
    config.WORK_DIR.mkdir(parents=True, exist_ok=True)

    if "--once" in sys.argv:
        # Single poll for testing
        gh = Github(auth=Auth.Token(config.GITHUB_TOKEN))
        notifications = gh.get_user().get_notifications(all=False)
        for n in notifications:
            if n.subject.type in ("Issue", "PullRequest"):
                _process_notification(n)
                n.mark_as_read()
        return

    poll_loop()


if __name__ == "__main__":
    main()
