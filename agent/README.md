# Agent service scaffold

This folder contains the Python service and Phase 1 LangGraph skeleton. Its graph
is ordered as `greet → get_website → check_scope → plan_task → run_browser_step
→ confirm_with_user → speak_result`. The graph nodes remain placeholders.
`POST /inspect` is the first implemented website flow: it checks the shared
scope config, opens a headless browser, and returns the page title, headings,
clickable labels, and a short summary. Inspection does not click links or
buttons, read or fill form values, or log in.

The shared scope settings are in `config/scope-limit.json`. Open mode allows
public HTTP(S) sites; single-site and multi-site modes restrict inspected
domains and top-level navigations. Local/private IP destinations and
non-standard ports are blocked. The browser service blocks JavaScript and
service workers during inspection.

Browser and website-catalogue LangChain tools still raise
`NotImplementedError`; they do not make live calls.

`get_chat_model()` in `llm.py` selects a LangChain chat model using
`LLM_PROVIDER`: `openai` (the default), `azure_openai`, or `bedrock`. Model
construction is lazy and does not send requests. Configure the provider's
credentials and model settings in the runtime environment; no API keys are
included in this scaffold.

Install dependencies and run the health endpoint from the repository root:

```bash
python -m pip install -r agent/requirements.txt
python -m playwright install chromium
uvicorn agent.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health`. Later phases
may add CrewAI/AutoGen crews and a separate Copilot Studio business version.

The Next.js server-side route at `/api/inspect` forwards to this service. Set
`AGENT_SERVICE_URL` if it is not running at `http://127.0.0.1:8000`.
