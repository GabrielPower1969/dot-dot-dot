#!/bin/bash
# Download the open-licence (OFL) display fonts listed in assets/fonts/fonts.json (the ones marked "fetch").
# Sources: google/fonts GitHub mirror + Smiley Sans GitHub release. All OFL-1.1. Run from repo root.
set -e; cd "$(dirname "$0")/../assets/fonts"; G=https://github.com/google/fonts/raw/main/ofl
dl(){ [ -f "$2" ] && { echo "have $2"; return; }; curl -fsSL --max-time 90 -o "$2" "$1" && echo "OK $2" || echo "FAIL $2"; }
dl "$G/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf" PlayfairDisplay-Variable.ttf
dl "$G/inter/Inter%5Bopsz,wght%5D.ttf" Inter-Variable.ttf
dl $G/notosanssc/NotoSansSC%5Bwght%5D.ttf NotoSansSC-Variable.ttf
dl $G/notoserifsc/NotoSerifSC%5Bwght%5D.ttf NotoSerifSC-Variable.ttf
dl $G/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf ZCOOLKuaiLe-Regular.ttf
dl $G/zcoolqingkehuangyou/ZCOOLQingKeHuangYou-Regular.ttf ZCOOLQingKeHuangYou-Regular.ttf
dl $G/mashanzheng/MaShanZheng-Regular.ttf MaShanZheng-Regular.ttf
dl $G/zhimangxing/ZhiMangXing-Regular.ttf ZhiMangXing-Regular.ttf
dl $G/longcang/LongCang-Regular.ttf LongCang-Regular.ttf
dl $G/anton/Anton-Regular.ttf Anton-Regular.ttf
dl $G/bebasneue/BebasNeue-Regular.ttf BebasNeue-Regular.ttf
dl $G/archivoblack/ArchivoBlack-Regular.ttf ArchivoBlack-Regular.ttf
dl "$G/oswald/Oswald%5Bwght%5D.ttf" Oswald-Variable.ttf
if [ ! -f SmileySans-Oblique.ttf ]; then
  U=$(curl -fsSL https://api.github.com/repos/atelier-anchor/smiley-sans/releases/latest | python3 -c "import json,sys;print(next(x['browser_download_url'] for x in json.load(sys.stdin)['assets'] if x['name'].endswith('.zip')))")
  curl -fsSL -o /tmp/smiley.zip "$U" && unzip -o -j -q /tmp/smiley.zip '*.ttf' -d . && echo "OK SmileySans-Oblique.ttf"
fi
echo "fonts ready: $(ls *.ttf *.otf | wc -l | tr -d ' ') files"
