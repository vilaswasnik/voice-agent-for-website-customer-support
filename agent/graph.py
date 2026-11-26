from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict, total=False):
    website: str
    user_request: str
    scope_allowed: bool
    task_plan: str
    browser_result: str
    user_confirmation: bool
    response: str


def greet(_state: AgentState) -> AgentState:
    """Return a placeholder greeting; voice output is not connected yet."""
    return {"response": "Hi, which website would you like to use today?"}


def get_website(_state: AgentState) -> AgentState:
    """TODO: obtain and validate the user's target website."""
    return {}


def check_scope(_state: AgentState) -> AgentState:
    """TODO: enforce the configured website scope before planning."""
    return {}


def plan_task(_state: AgentState) -> AgentState:
    """TODO: create a task plan with the configured chat model."""
    return {}


def run_browser_step(_state: AgentState) -> AgentState:
    """TODO: execute one approved browser action."""
    return {}


def confirm_with_user(_state: AgentState) -> AgentState:
    """TODO: pause for user confirmation before sensitive actions."""
    return {}


def speak_result(_state: AgentState) -> AgentState:
    """TODO: return the result through the voice output service."""
    return {}


def build_agent_graph():
    """Compile the placeholder voice-agent workflow."""
    graph = StateGraph(AgentState)
    graph.add_node("greet", greet)
    graph.add_node("get_website", get_website)
    graph.add_node("check_scope", check_scope)
    graph.add_node("plan_task", plan_task)
    graph.add_node("run_browser_step", run_browser_step)
    graph.add_node("confirm_with_user", confirm_with_user)
    graph.add_node("speak_result", speak_result)

    graph.add_edge(START, "greet")
    graph.add_edge("greet", "get_website")
    graph.add_edge("get_website", "check_scope")
    graph.add_edge("check_scope", "plan_task")
    graph.add_edge("plan_task", "run_browser_step")
    graph.add_edge("run_browser_step", "confirm_with_user")
    graph.add_edge("confirm_with_user", "speak_result")
    graph.add_edge("speak_result", END)

    return graph.compile()
