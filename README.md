# spotify-adless

quick python script to block ads on spotify desktop (windows). made this cuz spicetify is annoying to update and proxy dlls keep getting flagged by defender.

doesnt need any pip installs or external junk, just runs on python 3.

## how to use

1. close spotify (or let the script kill it)
2. run:
```bash
python main.py
```
3. open spotify and ads should be gone.

if you wanna launch it right after patching:
```bash
python main.py --launch
```

to revert back to original:
```bash
python main.py --restore
```

## what it does
- opens `xpui.spa` as a zip and strips out the ad checks (`adsEnabled`, `audioAdsEnabled`, etc)
- injects css into index.html to hide banner/upgrade boxes
- blocks ad telemetry requests
- locks `%localappdata%\Spotify\Update` with icacls so spotify doesnt silently update and break the patch
- makes a backup `xpui.spa.bak` automatically on first run

tested on windows 10 and 11. if icacls fails make sure to run your terminal as admin.
