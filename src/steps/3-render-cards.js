#!/usr/bin/env node
// Step 3: plan.json inserts + outro -> work/cards/<card>.<lang>.png  (Playwright/Chromium, fully offline)
// Templates: templates/cards/<card>.html with {{var}}, {{#each list}}{{this}}{{/each}}, {{#if x}}…{{else}}…{{/if}}
import fs from "node:fs"; import path from "node:path"; import { fileURLToPath, pathToFileURL } from "node:url";
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const proj = path.resolve(process.argv[2].startsWith("projects/") || fs.existsSync(process.argv[2]) ? process.argv[2] : path.join(ROOT, "projects", process.argv[2]));
const plan = JSON.parse(fs.readFileSync(path.join(proj, "work/plan.json"), "utf8"));
const profile = JSON.parse(fs.readFileSync(path.join(ROOT, "config/profile.json"), "utf8"));
const edit = fs.existsSync(path.join(proj, "edit.json")) ? JSON.parse(fs.readFileSync(path.join(proj, "edit.json"), "utf8")) : {};
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function render(tpl, vars) {
  tpl = tpl.replace(/{{#each (\w+)}}([\s\S]*?){{\/each}}/g, (_, k, body) => (vars[k] || []).map(v => body.replace(/{{this}}/g, esc(v))).join(""));
  tpl = tpl.replace(/{{#if (\w+)}}([\s\S]*?)(?:{{else}}([\s\S]*?))?{{\/if}}/g, (_, k, a, b = "") => vars[k] ? a : b);
  return tpl.replace(/{{(\w+)}}/g, (_, k) => k in vars ? esc(vars[k]) : `[TODO ${k}]`);
}
const { chromium } = await import("playwright");
const browser = await chromium.launch(); const page = await browser.newPage();
await page.route("**/*", r => r.request().url().startsWith("file://") ? r.continue() : r.abort());
const outDir = path.join(proj, "work/cards"); fs.mkdirSync(outDir, { recursive: true });
const langs = profile.creator.languages;
async function shoot(card, lang, vars, size) {
  const tplPath = path.join(ROOT, "templates/cards", card + ".html");
  const html = render(fs.readFileSync(tplPath, "utf8"), vars);
  const tmp = path.join(ROOT, "templates/cards", `.${card}.${lang}.tmp.html`); fs.writeFileSync(tmp, html);
  await page.setViewportSize(size); await page.goto(pathToFileURL(tmp).href); await page.waitForTimeout(150);
  const out = path.join(outDir, `${card}.${lang}.png`);
  await page.screenshot({ path: out, omitBackground: true }); fs.unlinkSync(tmp);
  if (html.includes("[TODO ")) console.log("WARN: missing vars in", card, html.match(/\[TODO \w+\]/g));
  return out;
}
const todo = [];
for (const ins of plan.inserts) for (const lang of langs) {
  const v = (ins.vars || {})[lang] || {}; console.log(" card", await shoot(ins.card, lang, v, { width: 1000, height: 625 }));
  if (ins.todo) todo.push(ins.todo);
}
const logo = fs.existsSync(path.join(ROOT, profile.brand.logo)) ? pathToFileURL(path.join(ROOT, profile.brand.logo)).href : "";
for (const [aspect, w, h, headsize] of [["16x9", 1920, 1080, 96], ["9x16", 1080, 1920, 84]]) for (const lang of langs) {
  const vars = { w, h, headsize, logo, initial: profile.creator.name[0], headline: (edit.outro?.headline || {})[lang] || "", cta: profile.outro[`cta_${lang}`], handle: profile.creator.handle };
  const out = await shoot("outro", lang, vars, { width: w, height: h });
  fs.renameSync(out, path.join(outDir, `outro.${aspect}.${lang}.png`)); console.log(" card", `outro.${aspect}.${lang}.png`);
}
await browser.close();
if (!logo) todo.push(`no logo at ${profile.brand.logo} — outro uses the initial "${profile.creator.name[0]}" as placeholder`);
for (const t of todo) console.log("TODO:", t);
console.log("OK: cards ->", outDir);
