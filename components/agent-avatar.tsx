import type { AgentState } from "@/types/agent";

interface AgentAvatarProps {
  state: AgentState;
}

const stateLabels: Record<AgentState, string> = {
  listening: "Listening",
  thinking: "Thinking",
  speaking: "Speaking",
};

export function AgentAvatar({ state }: AgentAvatarProps) {
  const greeting =
    state === "thinking"
      ? "Inspecting the website..."
      : state === "speaking"
        ? "Here is what I found."
        : "Hi, which website would you like to use today?";

  return (
    <section className={`agent agent--${state}`} aria-label="Virtual agent">
      <div className="agent__portrait" aria-hidden="true">
        <div className="agent__hair" />
        <div className="agent__face">
          <span className="agent__eye agent__eye--left" />
          <span className="agent__eye agent__eye--right" />
          <span className="agent__smile" />
        </div>
        <div className="agent__shoulders" />
      </div>
      <p className="agent__status" aria-live="polite">
        <span className="agent__status-dot" />
        {stateLabels[state]}
      </p>
      <p className="agent__greeting">{greeting}</p>
    </section>
  );
}
