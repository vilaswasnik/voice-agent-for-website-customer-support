import scopeConfig from "./scope-limit.json";

export type ScopeMode = "single-site" | "multi-site" | "open";

export interface ScopeLimitConfig {
  mode: ScopeMode;
  allowedDomains: string[];
}

export const scopeLimit: ScopeLimitConfig = {
  mode: scopeConfig.mode as ScopeMode,
  allowedDomains: scopeConfig.allowedDomains,
};
