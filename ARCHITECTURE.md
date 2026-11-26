# Architecture — How the Technologies Connect and the Logic Flows

```
                        THE USER
                          │  ▲
              speaks      │  │  hears the agent speak
                          ▼  │
┌──────────────────────────────────────────────────────────────┐
│  FRONT PAGE  (Next.js + React + TypeScript)                  │
│  ┌─────────────┐   ┌──────────────────┐   ┌───────────────┐  │
│  │ Agent Avatar │   │ Website URL box  │   │ Mic button    │  │
│  │ Listening /  │   │ "Enter website…" │   │ "Tap to talk" │  │
│  │ Thinking /   │   └──────────────────┘   └───────────────┘  │
│  │ Speaking     │                                            │
│  └─────────────┘                                             │
└────────┬───────────────────────────────────────▲─────────────┘
         │ typed URL +                captions / │ spoken reply
         │ speech-to-text (Whisper)              │ text-to-speech
         ▼                                       │
┌──────────────────────────────────────────────────────────────┐
│  BACK END  (Python + FastAPI)                                │
│                                                              │
│   ┌────────────────────────────────────────────────────┐     │
│   │  SCOPE GUARD  (config/scope-limit)                 │     │
│   │  Mode: single-site / multi-site / open             │     │
│   │  Is this website allowed? ── NO ──► agent refuses  │     │
│   └──────────────────────┬─────────────────────────────┘     │
│                          │ YES                               │
│   ┌──────────────────────▼─────────────────────────────┐     │
│   │  LANGGRAPH  — the agent's brain (state machine)    │     │
│   │                                                    │     │
│   │  greet ─► get_website ─► check_scope ─► plan_task  │     │
│   │                              │              │      │     │
│   │                              ▼              ▼      │     │
│   │                       run_browser_step ─► confirm  │     │
│   │                              │        _with_user   │     │
│   │                              ▼              │      │     │
│   │                        speak_result ◄───────┘      │     │
│   └──────┬──────────────────────────┬──────────────────┘     │
│          │ uses                     │ asks for intelligence  │
│          ▼                          ▼                        │
│   ┌───────────────┐      ┌─────────────────────────────┐     │
│   │  LANGCHAIN    │      │  LLM PLATFORM (one switch)  │     │
│   │  tools:       │      │  LLM_PROVIDER =             │     │
│   │  • browser    │      │   openai        ─► OpenAI   │     │
│   │    actions    │      │   azure_openai  ─► Azure    │     │
│   │  • DB lookups │      │   bedrock       ─► AWS      │     │
│   └──────┬────────┘      └─────────────────────────────┘     │
│          │ commands                                          │
└──────────┼───────────────────────────────────────────────────┘
           ▼
┌──────────────────────┐        ┌──────────────────────────────┐
│  BROWSER WORKER      │        │  DATABASE (PostgreSQL)       │
│  (Playwright)        │        │  • users                     │
│  opens the real site,│        │  • product_settings (scope)  │
│  clicks, types,      │        │  • websites (entered sites)  │
│  reads the page      │        │  • site_maps (learned sites) │
└──────────┬───────────┘        │  • sessions / tasks          │
           │                    └──────────────▲───────────────┘
           ▼                                   │ stores what
┌──────────────────────┐                       │ it learns
│  TARGET WEBSITE      │───────────────────────┘
│  e.g. policybazaar   │   SITE LEARNER (crawler) maps its
│  .com — or ANY site  │   pages, buttons, forms ─► site_maps
│  inside the scope    │
└──────────────────────┘

  Later phases:  CrewAI / AutoGen = crews of agents for big jobs
                 Copilot Studio  = business version inside Teams/M365
```

## The logic, step by step
1. The user speaks → the front page turns the voice into text (speech-to-text).
2. The **Scope Guard** checks first: is this website inside the owner's limit (single-site / approved list / open)? If not, the agent stops there and refuses politely.
3. **LangGraph** runs the brain as fixed steps — it cannot skip the confirm step, which guarantees the agent always asks before login, payment or final submit.
4. When the brain needs to think, it calls the **LLM** — one config switch (`LLM_PROVIDER`) decides whether that is OpenAI, Azure OpenAI or Amazon Bedrock.
5. When the brain needs to act, it uses **LangChain tools** to order the **Playwright browser worker** to click, type and read on the real website.
6. Everything learned about a site is stored in the **database** (`site_maps`), so the second visit is faster than the first.
7. The result travels back up and the agent **speaks it to the user** (text-to-speech), with the avatar in its Speaking state.
