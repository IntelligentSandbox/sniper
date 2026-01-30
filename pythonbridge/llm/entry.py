from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from pythonbridge.llm.agents import State, ReviewAgent, ValidateAgent


class GraphBuilder:
    """A class that creates and compiles a LangGraph state graph"""

    def __init__(self) -> None:
        # TODO: Implement memory checkpointing in https://docs.langchain.com/oss/python/langgraph/add-memory
        pass

    def build_graph(
        self, review_context: str = "", validate_context: str = ""
    ) -> CompiledStateGraph:
        """Builds a compiled LangGraph state graph

        Returns:
            CompiledStateGraph: Compiled LangGraph state graph
        """

        # Build workflow (review and validation context passed here)
        workflow = StateGraph(State)

        # Define agents
        review_agent = ReviewAgent(review_context)
        validate_agent = ValidateAgent(validate_context)

        # Add nodes (agents + tools)
        workflow.add_node("review_agent", review_agent.review)
        workflow.add_node("validate_agent", validate_agent.validate)

        # TODO: Add conditional edge from validate to review/END after implementing validate logic
        # Add edges
        workflow.add_edge(START, "review_agent")
        workflow.add_edge("review_agent", "validate_agent")
        workflow.add_edge("validate_agent", END)

        # Compile graph and return
        graph = workflow.compile()
        return graph
