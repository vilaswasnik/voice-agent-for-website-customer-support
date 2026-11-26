# Voice Agent for Website Customer Support

A minimal website voice assistant scaffold. The front page includes a placeholder
agent avatar, website address form, microphone control, and read-only website
inspection. Voice input/output and website task automation are not connected.

## Run locally

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Run the inspection service

In another terminal:

```bash
python -m pip install -r agent/requirements.txt
python -m playwright install chromium
uvicorn agent.main:app --reload
```

The front end forwards inspection requests through its server-side `/api/inspect`
route to `http://127.0.0.1:8000`. Set `AGENT_SERVICE_URL` to use another service
address.

## Website scope

Configure the owner-selected scope in [`config/scope-limit.json`](./config/scope-limit.json):

- `single-site`: one entry in `allowedDomains`
- `multi-site`: multiple approved entries in `allowedDomains`
- `open`: any entered website (`allowedDomains` is ignored)

Inspection is read-only: it does not click links or buttons, read or fill form
values, or log in. The service blocks local/private IP targets, non-standard
ports, and top-level navigation outside the configured scope. Only public HTTP(S)
websites can be inspected.
