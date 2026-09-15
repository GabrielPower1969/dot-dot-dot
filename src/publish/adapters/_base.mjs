// Adapter runtime: a platform adapter is DATA — an ordered list of steps run against a persistent Playwright context.
// Steps: {goto:url} {click:[locators]} {upload:[locators], file} {fill:[locators], value} {type:[locators], value} {press:key}
//        {wait:ms} {waitFor:[locators]} {shot:name} {check:[locators]} {optional:true} {submit:[locators]}  (submit only runs when row.confirmed)
// A locator is "role=button name=Upload" | "text=发布" | "label=Title" | "placeholder=…" | "css=input[type=file]" | "xpath=…"
import fs from "node:fs"; import os from "node:os"; import path from "node:path"; import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
export const CFG = JSON.parse(fs.readFileSync(path.join(ROOT, "config/publish.json"), "utf8"));
const expand = p => p.replace(/^~/, os.homedir());

export async function openContext(platform, { headless = CFG.headless } = {}) {
  const dir = path.join(expand(CFG.profile_dir), platform); fs.mkdirSync(dir, { recursive: true });
  const ctx = await chromium.launchPersistentContext(dir, { headless, viewport: { width: 1400, height: 900 }, locale: "zh-CN", args: ["--disable-blink-features=AutomationControlled"] });
  const page = ctx.pages()[0] || await ctx.newPage(); return { ctx, page };
}
function locate(page, spec) {
  const [kind, rest] = spec.split(/=(.*)/s);
  if (kind === "role") { const m = rest.match(/^(\S+)\s+name=(.*)$/); return m ? page.getByRole(m[1], { name: new RegExp(m[2], "i") }) : page.getByRole(rest); }
  if (kind === "text") return page.getByText(new RegExp(rest, "i")).first();
  if (kind === "label") return page.getByLabel(new RegExp(rest, "i")).first();
  if (kind === "placeholder") return page.getByPlaceholder(new RegExp(rest, "i")).first();
  if (kind === "css") return page.locator(rest).first();
  if (kind === "xpath") return page.locator("xpath=" + rest).first();
  throw new Error("bad locator " + spec);
}
async function firstVisible(page, specs, timeout = 8000) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) {
    for (const s of specs) { const l = locate(page, s); try { if (await l.isVisible({ timeout: 300 })) return { l, s }; } catch {} }
    await page.waitForTimeout(250);
  }
  return null;
}
export async function runSteps(page, steps, vars, { confirmed, shotDir, log }) {
  const sub = v => typeof v === "string" ? v.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "") : v;
  for (let i = 0; i < steps.length; i++) {
    const st = steps[i]; const name = Object.keys(st).find(k => !["optional", "timeout", "file", "value", "note"].includes(k));
    const specs = Array.isArray(st[name]) ? st[name] : [st[name]]; const to = st.timeout || 8000;
    try {
      if (name === "goto") await page.goto(sub(st.goto), { waitUntil: "domcontentloaded" });
      else if (name === "wait") await page.waitForTimeout(st.wait);
      else if (name === "press") await page.keyboard.press(st.press);
      else if (name === "shot") await page.screenshot({ path: path.join(shotDir, `${i}-${st.shot}.png`), fullPage: false });
      else if (name === "submit") {
        await page.screenshot({ path: path.join(shotDir, `${i}-before-submit.png`) });
        if (!confirmed) { log(`step ${i}: STOP before submit (row not confirmed) — see ${shotDir}`); return { stopped: "prepared" }; }
        const hit = await firstVisible(page, specs, to); if (!hit) throw new Error("submit button not found: " + specs.join(" | "));
        await hit.l.click(); await page.waitForTimeout(4000); await page.screenshot({ path: path.join(shotDir, `${i}-after-submit.png`) });
      } else {
        const hit = await firstVisible(page, specs, to);
        if (!hit) { if (st.optional) { log(`step ${i}: optional ${name} not found, skipped`); continue; } throw new Error(`${name} target not found: ${specs.join(" | ")}`); }
        log(`step ${i}: ${name} ← ${hit.s}`);
        if (name === "click") await hit.l.click();
        else if (name === "check") { try { await hit.l.check(); } catch { await hit.l.click(); } }
        else if (name === "fill") { await hit.l.click(); await hit.l.fill(sub(st.value)); }
        else if (name === "type") { await hit.l.click(); await page.keyboard.press("Control+A").catch(() => {}); await page.keyboard.type(sub(st.value), { delay: 15 }); }
        else if (name === "upload") {
          const file = sub(st.file); if (!fs.existsSync(file)) throw new Error("file missing " + file);
          const tag = await hit.l.evaluate(e => e.tagName).catch(() => "");
          if (tag === "INPUT") await hit.l.setInputFiles(file);
          else { const [fc] = await Promise.all([page.waitForEvent("filechooser", { timeout: to }), hit.l.click()]); await fc.setFiles(file); }
        }
        else if (name === "waitFor") {}
      }
    } catch (e) {
      await page.screenshot({ path: path.join(shotDir, `${i}-FAILED.png`) }).catch(() => {});
      throw new Error(`step ${i} (${name}) failed: ${e.message}`);
    }
  }
  return { stopped: null };
}
export function postUrlFrom(page) { return page.url(); }
