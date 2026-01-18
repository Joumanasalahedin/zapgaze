declare module "*.module.css";

/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_AGENT_URL?: string;
  readonly VITE_FRONTEND_API_KEY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
