import os, sys, shutil, zipfile

appdata = os.environ.get('APPDATA')
local = os.environ.get('LOCALAPPDATA')

if not appdata or not local:
    print('[-] env vars missing')
    sys.exit(1)

sp_dir = os.path.join(appdata, 'Spotify')
spa = os.path.join(sp_dir, 'Apps', 'xpui.spa')
bak = os.path.join(sp_dir, 'Apps', 'xpui.spa.bak')
upd = os.path.join(local, 'Spotify', 'Update')

if not os.path.exists(spa):
    print('[-] spotify xpui.spa not found at', spa)
    sys.exit(1)

if '--restore' in sys.argv:
    if os.path.exists(bak):
        print('[*] killing spotify')
        os.system('taskkill /F /IM Spotify.exe >nul 2>&1')
        shutil.copy2(bak, spa)
        if os.path.exists(upd):
            os.system(f'icacls "{upd}" /remove:d *S-1-1-0 >nul 2>&1')
        print('[+] restored clean xpui.spa & unlocked updates')
    else:
        print('[-] no backup found')
    sys.exit(0)

print('[*] killing spotify')
os.system('taskkill /F /IM Spotify.exe >nul 2>&1')

if not os.path.exists(bak):
    print('[*] backing up xpui.spa -> xpui.spa.bak')
    shutil.copy2(spa, bak)

css_payload = b'<style>[data-testid*="ad-"],[data-testid="upgrade-button"],.sponsor-container,a[href*="spotify.com/premium"]{display:none!important;height:0!important;width:0!important;pointer-events:none!important}</style>'
js_payload = b'<script>(function(){const _f=window.fetch;window.fetch=function(u,o){const s=typeof u==="string"?u:(u&&u.url?u.url:"");if(/(\\/ads\\/|\\/ad-logic\\/|audio-sp-ads|sp:\\/\\/ads)/i.test(s)){return Promise.resolve(new Response("{}",{status:200,headers:{"Content-Type":"application/json"}}));}return _f.apply(this,arguments);};})();</script></head>'
head_hook = css_payload + js_payload

patterns = [
    (b'adsEnabled:!0', b'adsEnabled:!1'),
    (b'adsEnabled:true', b'adsEnabled:false'),
    (b'isAdsEnabled:!0', b'isAdsEnabled:!1'),
    (b'showAds:!0', b'showAds:!1'),
    (b'audioAdsEnabled:!0', b'audioAdsEnabled:!1'),
    (b'enableAudioAds:!0', b'enableAudioAds:!1'),
    (b'enableVideoAds:!0', b'enableVideoAds:!1'),
    (b'enableBillboard:!0', b'enableBillboard:!1'),
    (b'enableLeaderboard:!0', b'enableLeaderboard:!1'),
    (b'displayAdsEnabled:!0', b'displayAdsEnabled:!1'),
    (b'sp://ads/v1/adslots', b'sp://ads/v1/blocked'),
    (b'spclient.wg.spotify.com/ads/', b'127.0.0.1/blocked-ads/'),
    (b'spclient.wg.spotify.com/ad-logic/', b'127.0.0.1/blocked-logic/'),
    (b'isSkipNextRestricted:!0', b'isSkipNextRestricted:!1'),
    (b'isSkipPrevRestricted:!0', b'isSkipPrevRestricted:!1'),
    (b'isSeekRestricted:!0', b'isSeekRestricted:!1'),
    (b'upgradeButtonText', b'upgradeButtonHidden'),
]

print('[*] patching xpui.spa')
tmp_spa = spa + '.tmp'
zin = zipfile.ZipFile(bak, 'r')
zout = zipfile.ZipFile(tmp_spa, 'w', zipfile.ZIP_DEFLATED)

mods = 0
for item in zin.infolist():
    data = zin.read(item.filename)
    name = item.filename.lower()

    if name.endswith('.html') and b'</head>' in data:
        data = data.replace(b'</head>', head_hook, 1)
        mods += 1
    elif name.endswith('.js'):
        for old, new in patterns:
            if old in data:
                data = data.replace(old, new)
                mods += 1

    zout.writestr(item, data)

zin.close()
zout.close()

if mods > 0:
    os.replace(tmp_spa, spa)
    print(f'[+] applied {mods} patches')
else:
    print('[-] no patches applied')
    if os.path.exists(tmp_spa):
        os.remove(tmp_spa)

if upd and sys.platform == 'win32':
    os.makedirs(upd, exist_ok=True)
    os.system(f'icacls "{upd}" /deny *S-1-1-0:(OI)(CI)(W,D,X) >nul 2>&1')
    print('[+] update directory locked with icacls')

if '--launch' in sys.argv:
    exe = os.path.join(sp_dir, 'Spotify.exe')
    if os.path.exists(exe):
        print('[*] launching spotify')
        os.startfile(exe)

print('[+] done!')
