#!/usr/bin/env python3
"""publish queue (stub): list / add / run. Real submit needs an adapter and row.confirmed == True."""
import json, sys, datetime
from pathlib import Path
Q = Path(__file__).resolve().parent / "queue.json"
rows = json.loads(Q.read_text()) if Q.exists() else []
cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
if cmd == "add":
    slug, platform, lang, at = sys.argv[2:6]; rows.append({"slug": slug, "platform": platform, "lang": lang, "at": at, "status": "queued", "confirmed": False, "url": None})
    Q.write_text(json.dumps(rows, indent=1, ensure_ascii=False)); print("queued")
elif cmd == "run":
    now = datetime.datetime.now().astimezone()
    for r in rows:
        due = datetime.datetime.fromisoformat(r["at"]) <= now
        print(f"{r['slug']} {r['platform']}/{r['lang']} at {r['at']} -> {'DUE' if due else 'wait'} status={r['status']} confirmed={r['confirmed']} (no adapter installed)")
else:
    for r in rows: print(r)
