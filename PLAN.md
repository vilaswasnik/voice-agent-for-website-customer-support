# Voice Agent for Any Website — Product Plan

## 1. The idea in one line
A simple website where **anybody** can type in **any website's address**, and then **talk to a voice agent** that does the work on that website for them — the same things they would normally do by clicking and typing, now done just by speaking.

## 2. What the user sees (front page — keep it very simple)
- A **virtual talking agent** at the top (animated avatar that speaks and listens, shows "Listening… / Thinking… / Speaking…" states).
- Below the agent, **one block / input box**:
  > "Enter the website you want to use — I can help you with it."
  > `[ www.example.com ........................ ] [ Start ]`
- A big **microphone button** — tap and talk.
- Nothing else on the page. No menus, no clutter. An elderly or non-technical person should understand it in 5 seconds.

## 2A. Scope limit — the product stays inside its fence (owner setting)
The product owner can **limit which websites the agent is allowed to work on**:
- **Single-site mode** — the agent works on ONE website only (e.g. a business puts it on their own site as their support agent).
- **Multi-site mode** — the agent works on a fixed list of approved websites.
- **Open mode** — any website the user enters (the public version).

**The agent must never go beyond that point:**
- If a user asks for a site or an action outside the allowed list, the agent politely refuses by voice: *"I can only help you with [allowed site]."*
- The browser worker **hard-blocks** any navigation, link, redirect or popup that leaves the allowed domains — the fence is enforced by the system, not just by asking the AI nicely.
- The allowed list is an **admin setting in the database** — the owner can add/remove sites at any time without changing code.

## 3. How it works (user journey)
1. User opens our site. The agent greets them by voice: *"Hi, which website would you like to use today?"*
2. User types (or says) a website, e.g. `amazon.com` or their bank or a government site.
3. The site is **saved in our database** (per user + a shared catalogue of already-learned sites).
4. Our system **visits and learns the site**: crawls its pages, menus, buttons, forms and links, and builds a "site map of actions" — what can be done there (search, book, buy, check status, fill a form…).
5. The user now **talks to the agent**: *"Find me a red jacket under $50"* / *"Check my appointment"* / *"Book the cheapest ticket for Friday."*
6. The agent **performs the steps on the real site** (clicks, types, navigates) in a secure browser session, narrating what it is doing: *"I found 3 options. The second one is $42. Should I open it?"*
7. For anything sensitive — **login, payment, final submit** — the agent **always stops and asks the user to confirm**, and the user enters passwords/OTP themselves (never stored, never spoken aloud).

## 4. System parts (architecture)
| Part | Job |
|---|---|
| **Front end** | The simple page: avatar, URL box, mic button, live captions of the conversation |
| **Voice in (STT)** | Converts the user's speech to text (e.g. OpenAI Whisper / Deepgram / browser Web Speech API) |
| **Brain (LLM agent)** | Understands the request, plans the steps, decides the next action on the site, asks questions when unsure |
| **Agent orchestration** | LangGraph runs the agent as a step-by-step state machine (plan → act → check → ask/confirm); LangChain provides the tools (browser actions, database lookups); CrewAI / AutoGen provide multi-agent crews for bigger jobs |
| **LLM platform (pluggable)** | OpenAI, Azure OpenAI, or Amazon Bedrock, switchable by configuration; Copilot Studio is the Microsoft-ecosystem route for the Phase 3 business version |
| **Voice out (TTS)** | Speaks the agent's replies in a natural voice (e.g. OpenAI TTS / ElevenLabs) |
| **Site learner (crawler)** | Visits a newly entered site, maps pages, buttons, forms and flows; stores the map in the database |
| **Browser worker** | A real automated browser (Playwright) that carries out the steps on the target site, in an isolated session per user |
| **Database** | Users, saved websites, learned site maps, conversation history, task history |
| **Safety layer** | Confirmation before login/payment/submit; no credential storage; session isolation; blocklist for harmful requests |
| **Scope guard** | Enforces the owner's website limit (one site / approved list / open) — blocks any navigation or action outside the allowed domains |

## 5. Database (main tables)
- `users` — account (optional/guest mode at first)
- `product_settings` — the owner's scope limit: mode (single-site / multi-site / open) and the allowed-domains list
- `websites` — every site ever entered (URL, name, when added, learned or not)
- `site_maps` — the learned structure of each site: pages, actions, forms, common tasks
- `sessions` — one per user visit: which site, what they asked, what the agent did
- `tasks` — each voice request and its step-by-step outcome (success / failed / needs user)

## 6. Build phases
**Phase 1 — MVP (the demo that proves it)**
- Front page with avatar + URL box + mic button
- Voice in/out working in the browser
- Agent can handle **3–5 well-known sites** (pre-learned) and do simple tasks: search, navigate, read out results, fill simple forms
- Sites entered by users are saved in the database (learning them automatically comes in Phase 2)

**Phase 2 — Learn any site**
- Automatic crawler/site-learner for newly entered sites
- Agent handles login flows *with the user* (user types password/OTP themselves)
- Task history per user; "my websites" list

**Phase 3 — Real product**
- Accounts, saved preferences, favourite sites
- Confirmation-by-voice for purchases/bookings, with a strict pay-only-after-confirm rule
- More languages (Hindi/Marathi included), mobile app wrapper
- Business version: website owners can embed this agent on *their own* site as a support agent (this is the money-making version — the repo name's "customer support" angle)

## 7. Tech stack (suggested, all standard)
- Front end: React / Next.js + Web Speech API or streaming audio
- Back end: Python (FastAPI) or Node.js
- Voice: Whisper (STT) + OpenAI/ElevenLabs (TTS), or an all-in-one realtime voice API
- Browser automation: Playwright
- Database: PostgreSQL (Supabase is fine to start)
- Hosting: a small cloud server / Render / Railway to begin
- Agent frameworks: LangChain + LangGraph (core), CrewAI and AutoGen (multi-agent crews)
- LLM platforms: OpenAI / Azure OpenAI / Amazon Bedrock — pluggable by config; Copilot Studio for the Microsoft business version

## 8. Honest challenges (plan for them, don't hide them)
- **Every site is different** — the site-learner will be imperfect at first; start with popular sites and improve.
- **Logins, CAPTCHAs, OTPs** — the agent cannot (and should not) bypass these; design the flow so the user steps in for 10 seconds, then the agent continues.
- **Payments** — never let the agent pay without an explicit spoken "yes" on the exact amount.
- **Speed** — voice + browsing steps must feel fast; stream the voice and show progress on screen.
- **Trust & privacy** — no password storage, clear on-screen note: "We never save your passwords."

## 9. First build order (next steps)
1. Scaffold the project in this repo (front page + stub agent that greets and takes a URL).
2. Wire up voice in/out so the agent can hold a spoken conversation.
3. Connect the browser worker: agent opens the entered site and can search/navigate on **one** test site end-to-end.
4. Add the database: save entered sites + show them back to the user.
5. Then expand site by site.
