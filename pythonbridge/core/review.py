import json
import logging

from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

from pythonbridge.core.config import load_environment
from pythonbridge.core.diff_parser import parse_patch, clamp_to_valid
from pythonbridge.gh.client import get_pr, get_file_log, post_review, create_reaction
from pythonbridge.llm import GraphBuilder

logger = logging.getLogger(__name__)


_SEVERITY_EMOJI = {
    "critical": "🔴 **[CRITICAL]**",
    "high": "🟠 **[HIGH]**",
    "medium": "🟡 **[MEDIUM]**",
    "low": "🔵 **[LOW]**",
}


def _severity_emoji(severity: str) -> str:
    return _SEVERITY_EMOJI.get(severity.lower(), "")


def _detect_language(filename: str) -> str:
    try:
        return get_lexer_for_filename(filename).name
    except ClassNotFound:
        return "Unknown"


def _build_pr_context(title: str, body: str) -> str:
    return f"\n\n## PR Context\n\n**Title:** {title}\n\n**Description:**\n{body or '_No description provided._'}\n"


def _parse_comments(raw: str, filename: str) -> list[dict]:
    """Extract JSON comment array from LLM output, attaching the file path."""
    try:
        # Strip markdown code fences if the model wrapped the JSON
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        comments = json.loads(text)
        if not isinstance(comments, list):
            return []
        return [
            {
                "path": filename,
                "line": c["line"],
                "body": f"{_severity_emoji(c['severity'])} {c['body']}" if c.get("severity") else c["body"],
            }
            for c in comments
            if isinstance(c.get("line"), int) and c.get("body")
        ]
    except Exception:
        logger.warning("Failed to parse LLM output for %s", filename)
        return []


def review_pr(payload: dict) -> list[dict]:
    load_environment()

    create_reaction(payload)

    files, pr_title, pr_body, head_sha = get_pr(payload)
    pr_context = _build_pr_context(pr_title, pr_body)

    graph_builder = GraphBuilder()
    agent_graph = graph_builder.build_graph(review_context=pr_context)

    all_comments = []
    reviews = []
    for file in files:
        if not file.patch:
            continue

        # Annotate the diff with real line numbers so the LLM can reference them accurately
        annotated_patch, valid_lines = parse_patch(file.patch)
        language = _detect_language(file.filename)
        file_log = get_file_log(payload, file.filename)
        log_str = "\n".join(f"  {c['sha']} {c['author']}: {c['message']}" for c in file_log)
        llm_input = f"Language: {language}\nFile: {file.filename}\nRecent commits:\n{log_str}\n\n{annotated_patch}"

        result = agent_graph.invoke({"pr_input": llm_input})
        raw_review = result.get("pr_review") if result else None
        comments = _parse_comments(raw_review, file.filename) if raw_review else []

        # Drop any comments where the LLM referenced a line outside the diff
        comments = clamp_to_valid(comments, valid_lines)

        all_comments.extend(comments)
        reviews.append(
            {
                "filename": file.filename,
                "status": file.status,
                "comments": comments,
            }
        )

    post_review(payload, all_comments, head_sha)

    return reviews


if __name__ == "__main__":
    test_payload = {
        "number": 1,
        "repository": {"full_name": "owner/repo"},
        "installation": {"id": "12345"},
    }
    results = review_pr(test_payload)
    for r in results:
        print(r["comments"])
