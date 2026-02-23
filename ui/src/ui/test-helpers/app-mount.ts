import { afterEach, beforeEach } from "vitest";
import { ClawCoreApp } from "../app.ts";

// oxlint-disable-next-line typescript/unbound-method
const originalConnect = ClawCoreApp.prototype.connect;

export function mountApp(pathname: string) {
  window.history.replaceState({}, "", pathname);
  const app = document.createElement("clawcore-app") as ClawCoreApp;
  document.body.append(app);
  return app;
}

export function registerAppMountHooks() {
  beforeEach(() => {
    ClawCoreApp.prototype.connect = () => {
      // no-op: avoid real gateway WS connections in browser tests
    };
    window.__CLAWCORE_CONTROL_UI_BASE_PATH__ = undefined;
    localStorage.clear();
    document.body.innerHTML = "";
  });

  afterEach(() => {
    ClawCoreApp.prototype.connect = originalConnect;
    window.__CLAWCORE_CONTROL_UI_BASE_PATH__ = undefined;
    localStorage.clear();
    document.body.innerHTML = "";
  });
}
