from langchain_core.tools import tool


@tool
def navigate_to_website(url: str) -> str:
    """Navigate the controlled browser to an approved website URL."""
    raise NotImplementedError("Browser navigation is not implemented yet.")


@tool
def click_element(selector: str) -> str:
    """Click an element in the controlled browser."""
    raise NotImplementedError("Browser actions are not implemented yet.")


@tool
def fill_input(selector: str, value: str) -> str:
    """Fill an input in the controlled browser."""
    raise NotImplementedError("Browser actions are not implemented yet.")


@tool
def lookup_website(domain: str) -> str:
    """Look up a saved website by its domain."""
    raise NotImplementedError("Website database lookups are not implemented yet.")


@tool
def save_website(url: str) -> str:
    """Save a website to the shared website catalogue."""
    raise NotImplementedError("Website database writes are not implemented yet.")
