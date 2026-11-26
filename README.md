# Voice Agent for Website Customer Support

A minimal Phase 1 front-end scaffold for a website voice assistant. It includes a
placeholder agent avatar with Listening, Thinking, and Speaking states, a website
address form, and a microphone control. Voice input/output and website automation
are not connected yet.

## Run locally

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Website scope

Configure the owner-selected scope in [`config/scope-limit.ts`](./config/scope-limit.ts):

- `single-site`: one entry in `allowedDomains`
- `multi-site`: multiple approved entries in `allowedDomains`
- `open`: any entered website (`allowedDomains` is ignored)

This is configuration scaffolding only; runtime domain enforcement will be
implemented with the browser worker.
