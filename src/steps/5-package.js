#!/usr/bin/env node
// Step 5: covers for every platform size + per-platform post copy + hand-off README.
// Inputs: config/platforms.json, projects/<slug>/copy.json (agent-written), work/intermediate frame for the cover.
import fs from "node:fs"; import path from "node:path"; import { execFileSync } from "node:child_process"; import { fileURLToPath, pathToFileURL } from "node:url";
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const proj = path.resolve(fs.existsSync(process.argv[2]) ? process.argv[2] : path.join(ROOT, "projects", process.argv[2]));
const slug = path.basename(proj);
const platforms = JSON.parse(fs.readFileSync(path.join(ROOT, "config/platforms.json"), "utf8"));
const profile = JSON.parse(fs.readFileSync(path.join(ROOT, "config/profile.json"), "utf8"));
const copy = JSON.parse(fs.readFileSync(path.join(proj, "copy.json"), "utf8"));
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fill = (tpl, v) => tpl.replace(/{{{(\w+)}}}/g, (_, k) => v[k] ?? `[TODO ${k}]`).replace(/{{(\w+)}}/g, (_, k) => k in v ? esc(v[k]) : `[TODO ${k}]`);
const out = path.join(proj, "output"); fs.mkdirSync(path.join(out, "covers"), { recursive: true });

// 1. freeze frame -> data URI (cover_time_s from copy.json, default 3s into the cut)
const inter = path.join(proj, "work/intermediate/cut.16x9.mov");
const frame = path.join(proj, "work/cover-frame.jpg");
execFileSync("ffmpeg", ["-v", "error", "-y", "-ss", String(copy.cover_time_s ?? 3), "-i", inter, "-frames:v", "1", "-q:v", "2", frame]);
const frameUri = "data:image/jpeg;base64," + fs.readFileSync(frame).toString("base64");

const { chromium } = await import("playwright");
const browser = await chromium.launch(); const page = await browser.newPage();
await page.route("**/*", r => r.request().url().startsWith("file://") || r.request().url().startsWith("data:") ? r.continue() : r.abort());
const tpl = fs.readFileSync(path.join(ROOT, "templates/covers/cover.html"), "utf8");
const covers = {};
for (const [name, p] of Object.entries(platforms)) {
  if (name.startsWith("$")) continue;
  const [w, h] = p.cover; const portrait = h > w * 1.1; const square = !portrait && h > w * 0.8;
  for (const lang of p.languages) {
    const c = copy[lang]; if (!c) continue;
    const s = Math.min(w, h) / 1080;
    const vars = {
      w, h, frame: frameUri, kicker: c.kicker, title: c.cover_title_html || esc(c.cover_title), handle: profile.creator.handle,
      focus: portrait ? "30%" : "center", grad_dir: portrait ? "to bottom" : "to right",
      pad: Math.round(70 * s), gap: Math.round(26 * s), txt_w: portrait || square ? w - Math.round(140 * s) : Math.round(w * 0.55),
      txt_pos: portrait ? `top:${Math.round(90 * s)}px` : `top:50%;transform:translateY(-50%)`,
      kicker_fs: Math.round((lang === "zh" ? 44 : 38) * s), title_fs: Math.round((lang === "zh" ? 128 : 104) * s * (portrait ? 0.95 : 1)), brand_fs: Math.round(34 * s),
    };
    const tmp = path.join(ROOT, "templates/covers", `.cover.${name}.${lang}.tmp.html`); fs.writeFileSync(tmp, fill(tpl, vars));
    await page.setViewportSize({ width: w, height: h }); await page.goto(pathToFileURL(tmp).href); await page.waitForTimeout(120);
    const file = path.join(out, "covers", `${name}.${lang}.${w}x${h}.png`); await page.screenshot({ path: file }); fs.unlinkSync(tmp);
    covers[`${name}.${lang}`] = path.relative(proj, file); console.log(" cover", path.basename(file));
  }
}
await browser.close();

// 2. copy per platform
const postTpl = fs.readFileSync(path.join(ROOT, "templates/copy/post.md"), "utf8"); const rows = [];
for (const [name, p] of Object.entries(platforms)) {
  if (name.startsWith("$")) continue;
  for (const lang of p.languages) {
    const c = copy[lang]; if (!c) continue;
    const pc = (copy.platforms || {})[name] || {};
    const tags = (pc.hashtags || c.hashtags || []).slice(0, p.tags_max || 30).map(t => "#" + t.replace(/^#/, "")).join(" ");
    const aspect = p.aspect === "9:16" ? "9x16" : "16x9";
    const video = `output/${slug}.${aspect}.${lang}.mp4`;
    const title = (pc.title || c.title || "").slice(0, p.title_max || 999);
    const v = { platform: name, lang, title, hook: c.hook, body: pc.body || c.body, cta: c.cta, hashtags: tags, video, cover: covers[`${name}.${lang}`] || "", schedule: pc.schedule || copy.schedule || "TBD" };
    const dir = path.join(out, name); fs.mkdirSync(dir, { recursive: true });
    const file = path.join(dir, `${name}-post-${copy.topic}-${slug.slice(0, 10)}.${lang}.md`); fs.writeFileSync(file, fill(postTpl, v));
    if (p.title_max && (pc.title || c.title || "").length > p.title_max) console.log(`WARN: ${name} title truncated to ${p.title_max} chars`);
    rows.push(`| ${name} | ${lang} | ${p.aspect} | ${video} | ${v.cover} | ${path.relative(proj, file)} | ${v.schedule} |`);
  }
}
fs.writeFileSync(path.join(out, "README.md"), `# ${slug} — hand-off\n\n| platform | lang | aspect | video | cover | copy | schedule |\n|---|---|---|---|---|---|---|\n${rows.join("\n")}\n\nPublish order: ${copy.publish_order?.join(" → ") || "see copy.json"}\n`);
console.log("OK: covers + copy ->", out);
