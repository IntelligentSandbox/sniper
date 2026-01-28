from github import Github
from pythonbridge.config import load_environment
from pythonbridge.git_diff import get_diff
from pythonbridge.git_utils import get_installation_token
from pythonbridge.llm import GroqLLM


# TODO: Need to move this to a separate file or something.
def post_review(payload: dict, reviews: list[dict]) -> None:
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


def main(payload: dict) -> list[dict]:
    load_environment()

    files = get_diff(payload)
    llm = GroqLLM()

    reviews = []
    for file in files:
        review = llm.review_code(file.patch) if file.patch else None
        reviews.append(
            {
                "filename": file.filename,
                "status": file.status,
                "review": review,
            }
        )

    post_review(payload, reviews)

    return reviews


if __name__ == "__main__":
    test_payload = {
        "number": 1,
        "repository": {"full_name": "owner/repo"},
        "installation": {"id": "12345"},
    }
    results = main(test_payload)
    for r in results:
        print(r["review"])
