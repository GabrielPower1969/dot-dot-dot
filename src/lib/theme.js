// Same as theme.py for the node steps: writes templates/cards/_theme.css and returns the token set.
import fs from "node:fs"; import path from "node:path"; import { fileURLToPath } from "node:url";
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
export function loadTheme(profile) {
  const themes = JSON.parse(fs.readFileSync(path.join(ROOT, "config/themes.json"), "utf8"));
  const name = profile.brand.theme || "ink-classic"; const t = { ...themes[name], name };
  fs.writeFileSync(path.join(ROOT, "templates/cards/_theme.css"),
    `:root{--paper:${t.paper};--paper-2:${t.paper2};--ink:${t.ink};--muted:${t.muted};--line:${t.line};--accent:${t.accent};--accent-soft:${t.accentSoft};--accent-on:${t.accentOn}}\n`);
  return t;
}
