from github import GithubIntegration
from pythonbridge.core import config


def get_installation_token(installation_id: str) -> str:
    """Retrieves the installation token for a Github App Installation

    Args:
        installation_id (str): The string representing the specific Github App Installation ID (found in webhook request payload)

    Returns:
        str: The installation token for the Github App Installation
    """
    integration = GithubIntegration(
        integration_id=config.GITHUB_APP_ID, private_key=config.GITHUB_APP_PRIVATE_KEY
    )

    return integration.get_access_token(installation_id).token
