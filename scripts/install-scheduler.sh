#!/bin/bash
# macOS launchd job: run the publish queue every 15 minutes (user session, so the persistent browser profiles are yours).
set -e; R="$(cd "$(dirname "$0")/.." && pwd)"; P=~/Library/LaunchAgents/com.dotdotdot.publish.plist; NODE="$(which node)"
cat > "$P" <<PLIST
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
 <key>Label</key><string>com.dotdotdot.publish</string>
 <key>ProgramArguments</key><array><string>$NODE</string><string>$R/src/publish/queue.mjs</string><string>run</string></array>
 <key>WorkingDirectory</key><string>$R</string>
 <key>StartInterval</key><integer>900</integer>
 <key>StandardOutPath</key><string>$R/ui/publish.log</string><key>StandardErrorPath</key><string>$R/ui/publish.err</string>
 <key>EnvironmentVariables</key><dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
</dict></plist>
PLIST
launchctl unload "$P" 2>/dev/null || true; launchctl load "$P"; echo "installed: $P (every 15 min). Remove: launchctl unload $P && rm $P"
