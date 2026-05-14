from __future__ import annotations  # issues with type hints

from github import Github, PaginatedList, File
from pythonbridge.gh.auth import get_installation_token


def create_reaction(payload: dict, reaction_type: str = "eyes") -> None:
    """Add a reaction to the triggering comment.

    Args:
        payload: GitHub webhook payload containing PR details.
            Expected keys: "comment_id", "repository.full_name", "installation.id"
        reaction_type: The reaction to add (default "eyes").
    """
    repo_full_name = payload.get("repository").get("full_name")
    installation_id = payload.get("installation").get("id")
    comment_id = payload.get("comment_id")
    installation_token = get_installation_token(installation_id)

    pr_number = payload.get("number")
    github_client = Github(installation_token)
    repo = github_client.get_repo(repo_full_name)
    comment = repo.get_issue(pr_number).get_comment(comment_id)
    comment.create_reaction(reaction_type)


def get_pr(payload: dict) -> tuple:
    """Get PR metadata and changed files.

    Args:
        payload: GitHub webhook payload containing PR details.
            Expected keys: "number", "repository.full_name", "installation.id"

    Returns:
        Tuple of (files, title, body, head_sha).
    """
    # Get installation token
    pr_number = payload.get("number")
    repo_full_name = payload.get("repository").get("full_name")
    installation_id = payload.get("installation").get("id")
    installation_token = get_installation_token(installation_id)

    # Create Github client and get PR metadata + changed files
    github_client = Github(installation_token)
    repo = github_client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)

    return pr.get_files(), pr.title, pr.body or "", pr.head.sha


def post_review(payload: dict, comments: list[dict], head_sha: str) -> None:
    """Post inline review comments to a pull request.

    Args:
        payload: GitHub webhook payload containing PR details.
            Expected keys: "number", "repository.full_name", "installation.id"
        comments: List of dicts with keys "path", "line", and "body".
        head_sha: The commit SHA to attach the review to.
    """
    pr_number = payload.get("number")
    repo_full_name = payload.get("repository").get("full_name")
    installation_id = payload.get("installation").get("id")
    installation_token = get_installation_token(installation_id)

    github_client = Github(installation_token)
    repo = github_client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    commit = repo.get_commit(head_sha)

    if not comments:
        pr.create_issue_comment("No issues found in this PR.")
        return

    pr.create_review(
        commit=commit,
        event="COMMENT",
        comments=[
            {"path": c["path"], "line": c["line"], "body": c["body"]}
            for c in comments
        ],
    )


def post_comment(payload: dict, body: str) -> None:
    """Post a comment on a pull request.

    Args:
        payload: GitHub webhook payload containing PR details.
            Expected keys: "number", "repository.full_name", "installation.id"
        body: The comment body to post.
    """
    pr_number = payload.get("number")
    repo_full_name = payload.get("repository").get("full_name")
    installation_id = payload.get("installation").get("id")
    installation_token = get_installation_token(installation_id)

    github_client = Github(installation_token)
    repo = github_client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)
