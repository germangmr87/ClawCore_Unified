import type {
  AnyAgentTool,
  ClawCorePluginApi,
  ClawCorePluginToolFactory,
} from "../../src/plugins/types.js";
import { createLobsterTool } from "./src/lobster-tool.js";

export default function register(api: ClawCorePluginApi) {
  api.registerTool(
    ((ctx) => {
      if (ctx.sandboxed) {
        return null;
      }
      return createLobsterTool(api) as AnyAgentTool;
    }) as ClawCorePluginToolFactory,
    { optional: true },
  );
}
