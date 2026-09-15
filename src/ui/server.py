#!/usr/bin/env python3
"""dot-dot-dot local studio UI. stdlib only.  python3 src/ui/server.py [port]
Human and agent share ONE state: the JSON/markdown files in projects/, config/, src/publish/queue.json, ui/inbox.jsonl.
The UI never holds state of its own; it reads files, writes files, runs the same steps the CLI runs."""
import json, os, re, sys, subprocess, threading, time, uuid, mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
ROOT = Path(__file__).resolve().parents[2]
WRITABLE = ("projects/", "config/", "memory/", "src/publish/queue.json", "ui/inbox.jsonl")
STEPS = {"transcribe": ["python3", "src/steps/1-transcribe.py"], "plan": ["python3", "src/steps/2-plan-edit.py"],
         "translate": ["python3", "src/steps/2b-translate.py"], "cards": ["node", "src/steps/3-render-cards.js"],
         "assemble": ["python3", "src/steps/4-assemble.py"], "package": ["node", "src/steps/5-package.js"],
         "speech": [os.environ.get("CM_WHISPER_PYTHON", "python3"), "src/steps/6-speech-report.py"], "titles": ["python3", "src/steps/5b-titles.py"], "build": ["python3", "src/build.py"],
         "queue_plan": ["node", "src/publish/queue.mjs", "plan"], "queue_run_now": ["node", "src/publish/queue.mjs", "run", "--now", "--only"], "queue_login": ["node", "src/publish/queue.mjs", "login"]}
JOBS = {}

def safe(rel):
    p = (ROOT / rel).resolve()
    if ROOT not in p.parents and p != ROOT: raise PermissionError(rel)
    return p

def project_info(d):
    out, work = d / "output", d / "work"
    edit = json.loads((d/"edit.json").read_text()) if (d/"edit.json").exists() else {}
    return {"slug": d.name, "title": edit.get("title", {}), "has": {
        "source": any((d/"source").glob("*.m*")), "script": (d/"script.md").exists(), "voiceover": (d/"voiceover.md").exists(),
        "edit": (d/"edit.json").exists(), "copy": (d/"copy.json").exists(), "cues_en": (d/"cues.en.json").exists(),
        "transcript": (work/"transcript.json").exists(), "plan": (work/"plan.json").exists(), "cards": (work/"cards").exists(),
        "speech": (work/"speech-report.html").exists()},
        "outputs": sorted(p.name for p in out.glob("*.mp4")) if out.exists() else [],
        "covers": sorted(p.name for p in (out/"covers").glob("*.png")) if (out/"covers").exists() else [],
        "posts": {p.name: sorted(x.name for x in p.glob("*.md")) for p in out.iterdir() if p.is_dir() and p.name != "covers"} if out.exists() else {},
        "mtime": max([p.stat().st_mtime for p in d.rglob("*") if p.is_file()] or [0])}

def run_step(slug, step, args):
    jid = uuid.uuid4().hex[:8]; JOBS[jid] = {"status": "running", "log": "", "step": step, "slug": slug, "t0": time.time()}
    def go():
        cmd = [*STEPS[step], (slug if step.startswith("queue_") else f"projects/{slug}"), *args]
        JOBS[jid]["log"] = "$ " + " ".join(cmd) + "\n"
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout: JOBS[jid]["log"] += line
        p.wait(); JOBS[jid]["status"] = "ok" if p.returncode in (0, 2) else f"failed ({p.returncode})"
    threading.Thread(target=go, daemon=True).start(); return jid

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def body(self): return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or b"{}"))
    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query); path = unquote(u.path)
        try:
            if path == "/": return self.send(200, (ROOT/"src/ui/index.html").read_bytes(), "text/html; charset=utf-8")
            if path == "/api/projects":
                return self.send(200, sorted([project_info(d) for d in (ROOT/"projects").iterdir() if d.is_dir()], key=lambda x: x["slug"], reverse=True))
            if path.startswith("/api/project/"):
                d = safe("projects/" + path.split("/")[3]); info = project_info(d)
                for f in ("script.md", "voiceover.md", "edit.json", "copy.json", "cues.en.json", "speech-notes.md"):
                    info[f] = (d/f).read_text() if (d/f).exists() else None
                info["plan"] = json.loads((d/"work/plan.json").read_text()) if (d/"work/plan.json").exists() else None
                info["handoff"] = (d/"output/README.md").read_text() if (d/"output/README.md").exists() else None
                return self.send(200, info)
            if path == "/api/file": return self.send(200, safe(q["path"][0]).read_bytes(), mimetypes.guess_type(q["path"][0])[0] or "text/plain; charset=utf-8")
            if path == "/api/config": return self.send(200, {k: json.loads((ROOT/f"config/{k}.json").read_text()) for k in ("profile", "platforms", "llm")})
            if path == "/api/queue": f = ROOT/"src/publish/queue.json"; return self.send(200, json.loads(f.read_text()) if f.exists() else [])
            if path == "/api/inbox": f = ROOT/"ui/inbox.jsonl"; return self.send(200, [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else [])
            if path == "/api/assets":
                return self.send(200, {k: sorted(x.name for x in (ROOT/"assets"/k).glob("*") if x.suffix.lower() in (".wav",".mp3",".m4a",".mp4",".mov",".png",".jpg") and not x.name.startswith(".")) for k in ("sfx","music","library","broll")}
                                       | {"cards": sorted(x.stem for x in (ROOT/"templates/cards").glob("*.html") if not x.name.startswith(("_","."))), "manifest": json.loads((ROOT/"assets/manifest.json").read_text())})
            if path == "/api/fonts": return self.send(200, json.loads((ROOT/"assets/fonts/fonts.json").read_text()))
            if path == "/api/frames":  # contact sheet: n frames evenly spaced from the cut 16:9 intermediate
                slug = q["slug"][0]; n = int(q.get("n", ["24"])[0]); d = safe("projects/" + slug); inter = d/"work/intermediate/cut.16x9.mov"
                if not inter.exists(): return self.send(400, {"error": "run assemble first (needs work/intermediate/cut.16x9.mov)"})
                fd = d/"work/frames"; fd.mkdir(exist_ok=True)
                dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(inter)],capture_output=True,text=True).stdout.strip() or 0)
                out = []
                for i in range(n):
                    t = round(dur * (i + 0.5) / n, 1); f = fd/f"f{t}.jpg"
                    if not f.exists(): subprocess.run(["ffmpeg","-v","error","-y","-ss",str(t),"-i",str(inter),"-frames:v","1","-vf","scale=480:-1","-q:v","3",str(f)])
                    out.append({"t": t, "url": f"/media/projects/{slug}/work/frames/{f.name}"})
                return self.send(200, out)
            if path == "/api/jobs": return self.send(200, JOBS)
            if path.startswith("/api/jobs/"): return self.send(200, JOBS.get(path.split("/")[3], {"status": "unknown"}))
            if path == "/api/metrics":
                rows = []
                for f in (ROOT/"metrics").glob("*.jsonl"): rows += [json.loads(l) | {"slug": f.stem} for l in f.read_text().splitlines() if l.strip()]
                return self.send(200, rows)
            if path.startswith("/media/"): return self.media(safe(path[7:]))
            self.send(404, {"error": "not found"})
        except Exception as e: self.send(500, {"error": str(e)})
    def media(self, p):
        if not p.is_file(): return self.send(404, {"error": "no file"})
        size = p.stat().st_size; ctype = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        rng = self.headers.get("Range"); start, end = 0, size - 1
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng); a, b = m.groups(); start = int(a) if a else max(0, size - int(b)); end = int(b) if b and a else size - 1
        self.send_response(206 if rng else 200); self.send_header("Content-Type", ctype); self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if rng: self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(p, "rb") as f:
            f.seek(start); left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left));
                if not chunk: break
                try: self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError): return
                left -= len(chunk)
    def do_PUT(self):
        u = urlparse(self.path); q = parse_qs(u.query); rel = q["path"][0]
        if not rel.startswith(WRITABLE): return self.send(403, {"error": "not writable"})
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if rel.endswith(".json"):
            try: json.loads(data)
            except Exception as e: return self.send(400, {"error": f"invalid JSON: {e}"})
        p = safe(rel); p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data); self.send(200, {"ok": True})
    def do_POST(self):
        path = urlparse(self.path).path; b = self.body()
        if path == "/api/run":
            if b["step"] not in STEPS: return self.send(400, {"error": "unknown step"})
            return self.send(200, {"job": run_step(b["slug"], b["step"], b.get("args", []))})
        if path == "/api/inbox":
            row = {"t": time.strftime("%Y-%m-%d %H:%M"), "slug": b.get("slug"), "text": b["text"], "status": "open"}
            with open(ROOT/"ui/inbox.jsonl", "a") as f: f.write(json.dumps(row, ensure_ascii=False) + "\n")
            return self.send(200, row)
        if path == "/api/queue":
            (ROOT/"src/publish/queue.json").write_text(json.dumps(b, ensure_ascii=False, indent=1)); return self.send(200, {"ok": True})
        if path == "/api/project":
            slug = b["slug"]
            if not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$", slug): return self.send(400, {"error": "slug must be yyyy-mm-dd-topic"})
            d = ROOT/"projects"/slug; (d/"source").mkdir(parents=True, exist_ok=True); (d/"script.md").write_text(b.get("script", ""))
            return self.send(200, {"ok": True})
        self.send(404, {"error": "not found"})

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7777
    print(f"dot-dot-dot studio → http://localhost:{port}  (root {ROOT})")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
