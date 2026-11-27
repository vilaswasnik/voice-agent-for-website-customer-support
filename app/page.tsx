"use client";

import { FormEvent, useState } from "react";
import { AgentAvatar } from "@/components/agent-avatar";
import { isInspectResult, type InspectResult } from "@/types/inspect";
import type { AgentState } from "@/types/agent";

export default function Home() {
  const [website, setWebsite] = useState("");
  const [agentState, setAgentState] = useState<AgentState>("listening");
  const [message, setMessage] = useState("");
  const [inspectResult, setInspectResult] = useState<InspectResult | null>(null);
  const [isInspecting, setIsInspecting] = useState(false);

  async function handleStart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const enteredWebsite = website.trim();

    if (!enteredWebsite) {
      setMessage("Enter a website address to get started.");
      return;
    }

    setMessage("");
    setInspectResult(null);
    setAgentState("thinking");
    setIsInspecting(true);
    setMessage("Inspecting the website. This should only take a moment...");
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 25_000);

    try {
      const response = await fetch("/api/inspect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: enteredWebsite }),
        signal: controller.signal,
      });
      const result: unknown = await response.json();

      if (!response.ok) {
        const detail =
          typeof result === "object" &&
          result !== null &&
          "detail" in result &&
          typeof result.detail === "string"
            ? result.detail
            : "The website could not be inspected.";
        throw new Error(detail);
      }

      if (!isInspectResult(result)) {
        throw new Error("The website inspector returned an invalid response.");
      }

      setInspectResult(result);
      setAgentState("speaking");
      setMessage(result.summary);
      if ("speechSynthesis" in window) {
        const utterance = new SpeechSynthesisUtterance(result.summary);
        window.speechSynthesis.speak(utterance);
      }
    } catch (error) {
      setAgentState("listening");
      setMessage(
        error instanceof DOMException && error.name === "AbortError"
          ? "The website took too long to inspect. Please try another address."
          : error instanceof Error
            ? error.message
          : "The website could not be inspected. Please try again.",
      );
    } finally {
      window.clearTimeout(timeout);
      setIsInspecting(false);
    }
  }

  function handleMicrophoneClick() {
    if (isInspecting) return;
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
            <button className="start-button" disabled={isInspecting} type="submit">
              {isInspecting ? "Inspecting…" : "Start"}
            </button>
          </div>
        </form>

        <button
          aria-label="Activate microphone"
          className="microphone-button"
          onClick={handleMicrophoneClick}
          disabled={isInspecting}
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

        {inspectResult && (
          <section className="inspection-results" aria-live="polite">
            <p className="inspection-results__summary">{inspectResult.summary}</p>
            {inspectResult.headings.length > 0 && (
              <div className="inspection-results__section">
                <h2>Page headings</h2>
                <ul>
                  {inspectResult.headings.map((heading, index) => (
                    <li key={`${heading}-${index}`}>{heading}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="inspection-results__section">
              <h2>Options on this site</h2>
              {inspectResult.options.length > 0 ? (
                <ul>
                  {inspectResult.options.map((option, index) => (
                    <li key={`${option.label}-${index}`}>
                      <span>{option.label}</span>
                      <span className="inspection-results__kind">{option.kind}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No main links or buttons were found.</p>
              )}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
