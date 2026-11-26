export interface InspectOption {
  label: string;
  kind: "link" | "button";
}

export interface InspectResult {
  url: string;
  title: string;
  headings: string[];
  options: InspectOption[];
  summary: string;
}

export function isInspectResult(value: unknown): value is InspectResult {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const result = value as Record<string, unknown>;
  return (
    typeof result.url === "string" &&
    typeof result.title === "string" &&
    typeof result.summary === "string" &&
    Array.isArray(result.headings) &&
    result.headings.every((heading) => typeof heading === "string") &&
    Array.isArray(result.options) &&
    result.options.every(
      (option) =>
        typeof option === "object" &&
        option !== null &&
        "label" in option &&
        typeof option.label === "string" &&
        "kind" in option &&
        (option.kind === "link" || option.kind === "button"),
    )
  );
}
