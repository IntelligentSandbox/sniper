from pythonbridge.core.config import load_environment
from pythonbridge.gh.client import get_diff, post_review
from pythonbridge.llm import GraphBuilder


# TODO: Add context input to this function and refactor if needed
def review_pr(payload: dict) -> list[dict]:
    load_environment()

    files = get_diff(payload)
    graph_builder = GraphBuilder()
    agent_graph = graph_builder.build_graph()

    reviews = []
    for file in files:
        result = agent_graph.invoke({"pr_input": file.patch}) if file.patch else None
        review = result.get("pr_review") if result else None
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
    results = review_pr(test_payload)
    for r in results:
        print(r["review"])
