export type SearchResultItem = {
  title: string;
  url: string;
};

export type SearchResult = {
  url: string;
  query: string;
  site: string;
  title: string;
  results: SearchResultItem[];
  summary: string;
};

export function isSearchResult(value: unknown): value is SearchResult {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.url === "string" &&
    typeof candidate.query === "string" &&
    typeof candidate.site === "string" &&
    typeof candidate.title === "string" &&
    typeof candidate.summary === "string" &&
    Array.isArray(candidate.results) &&
    candidate.results.every(
      (item) =>
        typeof item === "object" &&
        item !== null &&
        typeof (item as Record<string, unknown>).title === "string" &&
        typeof (item as Record<string, unknown>).url === "string",
    )
  );
}
