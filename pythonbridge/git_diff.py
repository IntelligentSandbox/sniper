from __future__ import annotations  # issues with type hints

from github import Github, PaginatedList, File
from pythonbridge.git_utils import get_installation_token


def get_diff(payload: dict) -> PaginatedList[File]:
    """Returns the diffs from a PR received in a JSON payload from webhook request

    Args:
        payload (dict): The dict representation of the JSON payload
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
