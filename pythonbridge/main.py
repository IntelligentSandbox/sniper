from pythonbridge.config import load_environment
from pythonbridge.git_diff import get_diff
from pythonbridge.llm import GroqLLM

# TODO: Post reviews back to GitHub as PR comments


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
