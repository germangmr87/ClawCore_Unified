import type { ClawCoreConfig } from "../config/config.js";

export function applyOnboardingLocalWorkspaceConfig(
  baseConfig: ClawCoreConfig,
  workspaceDir: string,
): ClawCoreConfig {
  return {
    ...baseConfig,
    agents: {
      ...baseConfig.agents,
      defaults: {
        ...baseConfig.agents?.defaults,
        workspace: workspaceDir,
      },
    },
    gateway: {
      ...baseConfig.gateway,
      mode: "local",
    },
  };
}
