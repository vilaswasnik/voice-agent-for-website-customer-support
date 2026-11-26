"use client";

import { FormEvent, useState } from "react";
import { AgentAvatar } from "@/components/agent-avatar";
import type { AgentState } from "@/types/agent";

export default function Home() {
  const [website, setWebsite] = useState("");
  const [agentState, setAgentState] = useState<AgentState>("listening");
  const [message, setMessage] = useState("");

  function handleStart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const enteredWebsite = website.trim();

    if (!enteredWebsite) {
      setMessage("Enter a website address to get started.");
      return;
    }

    setMessage(`Ready to help you with ${enteredWebsite}. Voice support is coming soon.`);
    setAgentState("thinking");
    window.setTimeout(() => setAgentState("speaking"), 500);
  }

  function handleMicrophoneClick() {
    setAgentState((currentState) =>
      currentState === "listening" ? "thinking" : "listening",
    );
    setMessage("Microphone interaction is a visual placeholder for now.");
  }

  return (
    <main className="home">
      <div className="home__content">
        <AgentAvatar state={agentState} />

        <form className="website-form" onSubmit={handleStart}>
          <label className="website-form__label" htmlFor="website">
            Enter the website you want to use — I can help you with it
          </label>
          <div className="website-form__controls">
            <input
              autoComplete="url"
              id="website"
              name="website"
              onChange={(event) => setWebsite(event.target.value)}
              placeholder="www.example.com"
              type="text"
              value={website}
            />
            <button className="start-button" type="submit">
              Start
            </button>
          </div>
        </form>

        <button
          aria-label="Activate microphone"
          className="microphone-button"
          onClick={handleMicrophoneClick}
          type="button"
        >
          <svg
            aria-hidden="true"
            fill="none"
            height="32"
            viewBox="0 0 24 24"
            width="32"
          >
            <rect
              height="11"
              rx="5.5"
              stroke="currentColor"
              strokeWidth="1.8"
              width="7"
              x="8.5"
              y="2.5"
            />
            <path
              d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3.5M9 21.5h6"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.8"
            />
          </svg>
        </button>
        <p className="microphone-caption">Tap to talk</p>

        {message && (
          <p className="feedback" aria-live="polite">
            {message}
          </p>
        )}
      </div>
    </main>
  );
}
