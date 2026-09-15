#!/usr/bin/env node
// Publish queue.  node src/publish/queue.mjs <plan slug | list | login <platform> | run [--now] [--only slug] | confirm <slug> [platform] | clear-done>
// State = src/publish/queue.json (shared with the studio UI). Receipts appended to src/publish/receipts.jsonl.
import fs from "node:fs"; import path from "node:path"; import { ROOT, CFG, openContext, runSteps } from "./adapters/_base.mjs";
const Q = path.join(ROOT, "src/publish/queue.json"); const load = () => fs.existsSync(Q) ? JSON.parse(fs.readFileSync(Q, "utf8")) : []; const save = r => fs.writeFileSync(Q, JSON.stringify(r, null, 1));
const platforms = JSON.parse(fs.readFileSync(path.join(ROOT, "config/platforms.json"), "utf8"));
const [cmd, a1, ...rest] = process.argv.slice(2); const flag = f => process.argv.includes(f); const opt = f => { const i = process.argv.indexOf(f); return i > 0 ? process.argv[i + 1] : null; };
const log = (...m) => { const line = `[${new Date().toISOString().slice(0, 16)}] ${m.join(" ")}`; console.log(line); fs.appendFileSync(path.join(ROOT, "ui/publish.log"), line + "\n"); };

function plan(slug) {
  const proj = path.join(ROOT, "projects", slug); const copy = JSON.parse(fs.readFileSync(path.join(proj, "copy.json"), "utf8"));
  const parsed = copy.schedule ? new Date(copy.schedule.trim().replace(/\s+[A-Z]{2,5}$/, "").replace(" ", "T")) : null;
  const base = parsed && !isNaN(parsed) ? parsed : (() => { const d = new Date(); d.setDate(d.getDate() + 1); d.setHours(CFG.default_hour_local, 0, 0, 0); return d; })();
  const rows = load(); let k = 0;
  for (const pf of copy.publish_order || Object.keys(platforms).filter(x => !x.startsWith("$"))) {
    const p = platforms[pf]; if (!p) continue;
    for (const lang of p.languages) {
      if (!copy[lang]) continue;
      if (rows.some(r => r.slug === slug && r.platform === pf && r.lang === lang && r.status !== "failed")) continue;
      const at = new Date(base.getTime() + k * CFG.stagger_min * 60000); k++;
      rows.push({ slug, platform: pf, lang, at: at.toISOString(), status: "queued", confirmed: !!CFG.auto_confirm, url: null, tries: 0 });
    }
  }
  save(rows); log(`planned ${k} posts for ${slug} starting ${base.toLocaleString()}`); list();
}
function list() { for (const r of load()) console.log(`${r.status.padEnd(9)} ${r.confirmed ? "✓" : "·"} ${r.slug} ${r.platform}/${r.lang} at ${r.at.slice(0, 16)} ${r.url || ""}`); }
function varsFor(r) {
  const proj = path.join(ROOT, "projects", r.slug); const copy = JSON.parse(fs.readFileSync(path.join(proj, "copy.json"), "utf8"));
  const p = platforms[r.platform]; const c = copy[r.lang]; const pc = (copy.platforms || {})[r.platform] || {};
  const aspect = p.aspect === "9:16" ? "9x16" : "16x9"; const [w, h] = p.cover;
  const tags = (pc.hashtags || c.hashtags || []).slice(0, p.tags_max || 30); const at = new Date(r.at);
  return { video: path.join(proj, `output/${r.slug}.${aspect}.${r.lang}.mp4`), cover: path.join(proj, `output/covers/${r.platform}.${r.lang}.${w}x${h}.png`),
    title: (pc.title || c.title || "").slice(0, p.title_max || 999), body: pc.body || c.body || "", hashtags: tags.map(t => "#" + t.replace(/^#/, "")).join(" "), tag1: tags[0] || "",
    date_en: at.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }), time_hm: at.toTimeString().slice(0, 5), at_iso: r.at };
}
async function runRow(r, rows) {
  const vars = varsFor(r); for (const f of ["video", "cover"]) if (!fs.existsSync(vars[f])) { r.status = "failed"; r.error = `missing ${f}: ${vars[f]}`; save(rows); return; }
  const adapter = (await import(`./adapters/${r.platform}.mjs`)).default;
  const shotDir = path.join(ROOT, CFG.screens_dir, `${r.slug}-${r.platform}-${r.lang}`); fs.mkdirSync(shotDir, { recursive: true });
  const { ctx, page } = await openContext(r.platform);
  try {
    const res = await runSteps(page, adapter.steps, vars, { confirmed: r.confirmed, shotDir, log: m => log(`${r.platform}/${r.lang}`, m) });
    if (res.stopped === "prepared") { r.status = "prepared"; r.screens = shotDir; }
    else { r.status = "posted"; r.url = page.url(); r.posted_at = new Date().toISOString(); fs.appendFileSync(path.join(ROOT, CFG.receipts), JSON.stringify({ ...r, vars: { title: vars.title } }) + "\n"); }
  } catch (e) {
    r.tries = (r.tries || 0) + 1; r.error = e.message; r.status = r.tries >= CFG.retry_max ? "needs_human" : "queued"; r.screens = shotDir; log(`${r.platform}/${r.lang} FAILED: ${e.message}`);
  } finally { save(rows); await ctx.close(); }
}
async function run() {
  const rows = load(); const now = Date.now(); const only = opt("--only");
  const due = rows.filter(r => ["queued", "prepared"].includes(r.status) && (flag("--now") || new Date(r.at).getTime() <= now) && (!only || r.slug === only) && !(r.status === "prepared" && !r.confirmed));
  if (!due.length) { log("nothing due"); return; }
  for (const r of due) { log(`run ${r.slug} ${r.platform}/${r.lang} confirmed=${r.confirmed}`); await runRow(r, rows); }
}
async function login(pf) { const adapter = (await import(`./adapters/${pf}.mjs`)).default; const { ctx, page } = await openContext(pf, { headless: false }); await page.goto(adapter.login_url); console.log(`Log in to ${pf} in the window, then close it. The session is saved in ${CFG.profile_dir}/${pf}.`); await new Promise(res => ctx.on("close", res)); }
function confirm(slug, pf) { const rows = load(); let n = 0; for (const r of rows) if (r.slug === slug && (!pf || r.platform === pf) && r.status !== "posted") { r.confirmed = true; n++; } save(rows); console.log(`confirmed ${n} rows`); }
if (cmd === "plan") plan(a1); else if (cmd === "list") list(); else if (cmd === "run") await run(); else if (cmd === "login") await login(a1);
else if (cmd === "confirm") confirm(a1, rest[0]); else if (cmd === "clear-done") { save(load().filter(r => r.status !== "posted")); list(); }
else console.log("usage: queue.mjs plan <slug> | list | login <platform> | run [--now] [--only slug] | confirm <slug> [platform] | clear-done");
