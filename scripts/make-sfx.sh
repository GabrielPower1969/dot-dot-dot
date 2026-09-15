#!/bin/bash
# Regenerate the CC0 placeholder SFX + bed music with ffmpeg only (no downloads). Run from repo root.
set -e; cd "$(dirname "$0")/.."
mkdir -p assets/sfx assets/music; cd assets/sfx
ffmpeg -v error -y -f lavfi -i "sine=f=1046.5:d=0.35" -f lavfi -i "sine=f=1568:d=0.35" -filter_complex "[0][1]amix=inputs=2,afade=t=out:st=0.05:d=0.3,volume=0.6" pop.wav
ffmpeg -v error -y -f lavfi -i "sine=f=1318.5:d=0.9" -f lavfi -i "sine=f=2637:d=0.9" -filter_complex "[0]volume=0.5[a];[1]volume=0.15[b];[a][b]amix=inputs=2,afade=t=out:st=0.05:d=0.85" ding.wav
ffmpeg -v error -y -f lavfi -i "anoisesrc=c=pink:d=0.55:a=0.8" -af "highpass=f=400,lowpass=f=3500,afade=t=in:d=0.12,afade=t=out:st=0.25:d=0.3,volume=0.9" whoosh.wav
ffmpeg -v error -y -f lavfi -i "sine=f=1000:d=0.5" -af "volume=0.5" bleep.wav
ffmpeg -v error -y -f lavfi -i "sine=f=196:d=0.12" -af "afade=t=out:st=0.01:d=0.11,volume=0.8" thud.wav
cd ../music
# lo-fi placeholder pad: I–vi–IV–V in A, 4 s per chord, soft tremolo, 160 s
ffmpeg -v error -y -f lavfi -i "aevalsrc='(0.8+0.2*sin(2*PI*0.5*t))*0.09*( if(lt(mod(t,16),4), sin(2*PI*220*t)+sin(2*PI*277.18*t)+sin(2*PI*329.63*t), if(lt(mod(t,16),8), sin(2*PI*185*t)+sin(2*PI*220*t)+sin(2*PI*277.18*t), if(lt(mod(t,16),12), sin(2*PI*146.83*t)+sin(2*PI*185*t)+sin(2*PI*220*t), sin(2*PI*164.81*t)+sin(2*PI*207.65*t)+sin(2*PI*246.94*t)))) )':s=48000:d=160" -af "lowpass=f=900,aecho=0.6:0.3:60:0.25" placeholder-lofi-pad.wav
echo "OK: assets/sfx/*.wav + assets/music/placeholder-lofi-pad.wav"
