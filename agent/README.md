# Agent service scaffold

This folder contains the Phase 1 Python service skeleton. Its LangGraph workflow
is ordered as `greet → get_website → check_scope → plan_task → run_browser_step
→ confirm_with_user → speak_result`. The nodes are placeholders: scope
enforcement, browser automation, confirmation handling, and voice I/O are not
implemented. Browser and website-catalogue LangChain tools raise
`NotImplementedError`; they do not make live calls.

`get_chat_model()` in `llm.py` selects a LangChain chat model using
`LLM_PROVIDER`: `openai` (the default), `azure_openai`, or `bedrock`. Model
construction is lazy and does not send requests. Configure the provider's
credentials and model settings in the runtime environment; no API keys are
included in this scaffold.

Install dependencies and run the health endpoint from the repository root:

```bash
python -m pip install -r agent/requirements.txt
uvicorn agent.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health`. Later phases
may add CrewAI/AutoGen crews and a separate Copilot Studio business version.
