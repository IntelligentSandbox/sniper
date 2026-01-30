from __future__ import annotations  # issues with type hints

from github import Github, PaginatedList, File
from pythonbridge.gh.auth import get_installation_token


def get_diff(payload: dict) -> PaginatedList[File]:
    """Get the changed files from a pull request.

    Args:
        payload: GitHub webhook payload containing PR details.
            Expected keys: "number", "repository.full_name", "installation.id"

    Returns:
        PaginatedList of File objects representing changed files in the PR.
    """
    # Get installation token
    pr_number = payload.get("number")
    repo_full_name = payload.get("repository").get("full_name")
    installation_id = payload.get("installation").get("id")
    installation_token = get_installation_token(installation_id)

    # Create Github client and get changed files from PR
    github_client = Github(installation_token)
    repo = github_client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    files = pr.get_files()

    return files


def post_review(payload: dict, reviews: list[dict]) -> None:
    """Post code review comments to a pull request.

    Formats review comments and posts them as a single issue comment on the PR.
    Only includes files that have non-empty review content.

    Args:
        payload: GitHub webhook payload containing PR details.
            Expected keys: "number", "repository.full_name", "installation.id"
        reviews: List of review dicts with keys "filename" and "review".
    """
    pr_number = payload.get("number")
    repo_full_name = payload.get("repository").get("full_name")
    installation_id = payload.get("installation").get("id")
    installation_token = get_installation_token(installation_id)

    github_client = Github(installation_token)
    repo = github_client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)

    body = ""
    for r in reviews:
        if r["review"]:
            body += f"**{r['filename']}**\n{r['review']}\n\n"

    if body:
        pr.create_issue_comment(body)


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
