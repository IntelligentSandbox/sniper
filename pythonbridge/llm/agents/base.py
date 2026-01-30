from typing import TypedDict


# TODO: See if need to append any state using Annotated[list, operator.add]
class State(TypedDict):
    """A class that represents the state of the LangGraph graph

    Args:
        TypedDict: Langgraph's required base data type for States
    """

    pr_input: str
    pr_review: str
    pr_review_validation: str
    review_context: str
    validate_context: str
