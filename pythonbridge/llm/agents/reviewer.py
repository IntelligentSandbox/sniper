from pathlib import Path

from pythonbridge.llm.groq import GroqLLM
from pythonbridge.llm.agents.base import State

PROMPT_DIR = Path(__file__).parent / "prompts"


class ReviewAgent:
    """Reviewer agent that will generate a review of the PR with extra context"""

    # TODO: Update context here and in State to be joinable with the general system prompt
    def __init__(self, context: str) -> None:
        self.general_system_prompt = (PROMPT_DIR / "reviewer.md").read_text()
        self.context = context
        self.llm = GroqLLM(system_prompt=self.general_system_prompt + self.context)

    def review(self, state: State) -> dict:
        """LangGraph Node function that represents ReviewAgent

        Args:
            state (State): The LangGraph graph state

        Returns:
            dict: The new state that LangGraph will automatically store
        """
        # Generate response from LLM and add response + review context to State
        response = self.llm.invoke(state["pr_input"])

        if response is None:
            raise RuntimeError("ReviewAgent's llm did not respond")

        return {"pr_review": response, "review_context": self.context}
