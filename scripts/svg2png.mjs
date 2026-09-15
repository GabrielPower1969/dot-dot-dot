// svg2png.mjs <in.svg> <out.png> <w> <h> — offline SVG rasteriser via Playwright (inlines the SVG, transparent bg)
import { chromium } from "playwright"; import fs from "node:fs";
const [svg, png, w, h] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h } });
await p.setContent(`<style>html,body{margin:0;background:transparent}svg{width:${w}px;height:${h}px;display:block}</style>${fs.readFileSync(svg, "utf8")}`);
await p.waitForTimeout(150); await p.screenshot({ path: png, omitBackground: true }); await b.close(); console.log("wrote", png);
