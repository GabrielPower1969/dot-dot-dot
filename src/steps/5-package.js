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

// 1. frames are extracted per cover (copy.<lang>.cover.frame_s or copy.cover_time_s)
const inter = path.join(proj, "work/intermediate/cut.16x9.mov");

import { loadTheme } from "../lib/theme.js";
const THEME = loadTheme(profile);
const { chromium } = await import("playwright");
const browser = await chromium.launch(); const page = await browser.newPage();
await page.route("**/*", r => r.request().url().startsWith("file://") || r.request().url().startsWith("data:") ? r.continue() : r.abort());
const tpl = fs.readFileSync(path.join(ROOT, "templates/covers/cover.html"), "utf8");
const FONTS = JSON.parse(fs.readFileSync(path.join(ROOT, "assets/fonts/fonts.json"), "utf8"));
const fontOf = id => FONTS.find(f => f.id === id) || FONTS.find(f => f.id === "noto-bold");
const covers = {}, variantFiles = { zh: [], en: [] };
// frame per language may differ (copy.<lang>.cover.frame_s); default cover_time_s
const frameUriFor = (t) => { const f = path.join(proj, `work/cover-frame-${t}.jpg`); if (!fs.existsSync(f)) execFileSync("ffmpeg", ["-v", "error", "-y", "-ss", String(t), "-i", inter, "-frames:v", "1", "-q:v", "2", f]); return "data:image/jpeg;base64," + fs.readFileSync(f).toString("base64"); };
for (const [name, p] of Object.entries(platforms)) {
  if (name.startsWith("$")) continue;
  const [w, h] = p.cover; const portrait = h > w * 1.1; const square = !portrait && h > w * 0.8;
  for (const lang of p.languages) {
    const c = copy[lang]; if (!c) continue;
    const cv = c.cover || {}; const s = Math.min(w, h) / 1080;
    const variants = (cv.variants && cv.variants.length) ? cv.variants : [{ font: lang === "zh" ? "noto-serif" : "playfair", style: "editorial" }, { font: lang === "zh" ? "noto-bold" : "inter", style: "swiss" }, { font: lang === "zh" ? "noto-serif" : "playfair", style: "photo" }];
    const pick = cv.pick ?? 1;
    for (let vi = 1; vi <= variants.length; vi++) {
      const v = variants[vi - 1]; const font = fontOf(v.font);
      const fontFile = fs.existsSync(path.join(ROOT, "assets/fonts", font.file)) ? font.file : "NotoSansSC-Bold.otf";
      const vars = {
        w, h, frame: frameUriFor(cv.frame_s ?? copy.cover_time_s ?? 3), kicker: cv.kicker || c.kicker, title: cv.title_html || c.cover_title_html || esc(c.cover_title), handle: profile.creator.handle,
        focus: portrait ? "20%" : "center", focus_x: portrait || square ? "center" : (cv.face_side === "left" ? "100%" : "0%"), zoom: portrait || square ? "cover" : "auto 150%", grad_dir: portrait ? "to bottom" : "to right", style: v.style || "editorial", orient: portrait ? "portrait" : "landscape", panel_w: Math.round(w * 0.5), panel_h: Math.round(h * 0.36),
        font_url: pathToFileURL(path.join(ROOT, "assets/fonts", fontFile)).href, font_weight: font.weight, stroke: Math.round(4 * s),
        pad: Math.round(56 * s), gap: Math.round(22 * s), txt_w: portrait || square ? w - Math.round(140 * s) : Math.round(w * 0.52),
        txt_pos: portrait ? `top:${Math.round(90 * s)}px` : `top:50%;transform:translateY(-50%)`,
        kicker_fs: Math.round(20 * s), title_fs: Math.round((v.size || (lang === "zh" ? 84 : 80)) * s * (portrait ? 1.05 : 1)), brand_fs: Math.round(24 * s),
      };
      const tmp = path.join(ROOT, "templates/covers", `.cover.${name}.${lang}.${vi}.tmp.html`); fs.writeFileSync(tmp, fill(tpl, vars));
      await page.setViewportSize({ width: w, height: h }); await page.goto(pathToFileURL(tmp).href); await page.waitForTimeout(150);
      const base = `${name}.${lang}.${w}x${h}`; const file = path.join(out, "covers", `${base}.v${vi}.png`);
      await page.screenshot({ path: file }); fs.unlinkSync(tmp);
      if (vi === pick) { fs.copyFileSync(file, path.join(out, "covers", `${base}.png`)); covers[`${name}.${lang}`] = path.relative(proj, path.join(out, "covers", `${base}.png`)); }
      if (name === (portrait ? "douyin" : "youtube")) variantFiles[lang].push({ file, label: `v${vi} ${font.id}/${v.style || "outline"}` });
      console.log(" cover", path.basename(file), vi === pick ? "(pick)" : "");
    }
  }
}
// legibility strip: every variant at 120 px wide, side by side, per language
for (const lang of Object.keys(variantFiles)) {
  const vs = variantFiles[lang]; if (!vs.length) continue;
  const html = `<style>body{margin:0;background:#888;display:flex;gap:14px;padding:14px;font:11px Arimo,sans-serif;color:#fff}div{text-align:center}img{width:120px;display:block;border:1px solid #000}</style>` +
    vs.map(v => `<div><img src="${pathToFileURL(v.file).href}"><span>${esc(v.label)}</span></div>`).join("");
  const tmp = path.join(ROOT, "templates/covers", `.legib.${lang}.tmp.html`); fs.writeFileSync(tmp, html);
  await page.setViewportSize({ width: 40 + vs.length * 134, height: 260 }); await page.goto(pathToFileURL(tmp).href); await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(out, "covers", `legibility-${lang}.png`), fullPage: true }); fs.unlinkSync(tmp);
  console.log(" legibility strip", `legibility-${lang}.png`);
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
