export type ScopeMode = "single-site" | "multi-site" | "open";

export interface ScopeLimitConfig {
  mode: ScopeMode;
  allowedDomains: string[];
}

export const scopeLimit: ScopeLimitConfig = {
  mode: "open",
  allowedDomains: [],
};
