"""Builds the KoolHub asset set from source/original-logo.png.
Usage: python3 source/build_assets.py   (needs pillow numpy scipy opencv-python-headless playwright+chromium)
Mark = background-removed 4x raster cutout (embedded in SVGs). Wordmark = Poppins Bold, tagline = Poppins Regular, both converted to vector outlines (needs fonttools)."""
import base64, io, os, json, shutil
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi

CHROME = next(p for p in ('/opt/pw-browsers/chromium', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome') if os.path.isfile(p))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SRC = Image.open('source/original-logo.png').convert('RGB')
a = np.array(SRC); H, W = a.shape[:2]
S = 4  # mark upscale

# ---------- mark cutout ----------
rgb = a.astype(np.float32); sat = rgb.max(2) - rgb.min(2)
top = np.zeros((H, W), bool); top[:440] = True
raw = np.clip((sat - 10) / 18, 0, 1) * top
m = raw > .5
lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1))
m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 200])
core = ndi.binary_erosion(m, iterations=2)
idx = ndi.distance_transform_edt(~core, return_distances=False, return_indices=True)
col = np.where(core[..., None], a, a[idx[0], idx[1]]).astype(np.float32)
soft = np.where(ndi.binary_dilation(m), np.clip((sat - 6) / 20, 0, 1), 0)
soft = np.maximum(soft, core.astype(np.float32))
colU = cv2.resize(col, (W * S, H * S), interpolation=cv2.INTER_LANCZOS4)
aU = cv2.GaussianBlur(cv2.resize(soft.astype(np.float32), (W * S, H * S), interpolation=cv2.INTER_CUBIC), (0, 0), 1.2)
aU = np.clip((aU - .5) * 2.2 + .5, 0, 1)
mark = Image.fromarray(np.dstack([np.clip(colU, 0, 255), aU * 255]).astype(np.uint8), 'RGBA')
mark = mark.crop(mark.getchannel('A').point(lambda v: 255 if v > 5 else 0).getbbox())
MW, MH = mark.size  # ~1740x1690
def b64(img):
    b = io.BytesIO(); img.save(b, 'PNG', optimize=True); return base64.b64encode(b.getvalue()).decode()
def silhouette(rgb_):
    s = Image.new('RGBA', mark.size, rgb_ + (0,)); s.putalpha(mark.getchannel('A')); return s

# ---------- text outlines (Poppins Bold wordmark, Poppins Regular tagline) ----------
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
def outline(weight, text, size=100, tracking=0):
    f = TTFont(f'source/fonts/poppins-latin-{weight}-normal.woff'); gs = f.getGlyphSet(); cm = f.getBestCmap(); s = size / f['head'].unitsPerEm
    x = 0; pen = SVGPathPen(gs); bp = BoundsPen(gs)
    for ch in text:
        g = cm[ord(ch)]
        for p_ in (pen, bp): gs[g].draw(TransformPen(p_, (s, 0, 0, -s, x, 0)))
        x += gs[g].width * s + tracking
    x0, y0, x1, y1 = bp.bounds  # y is flipped (SVG space)
    return pen.getCommands(), (x0, x1, y0, y1)
word_d, wb = outline(700, 'KoolHub')
tag_d, tb = outline(400, 'Integrated Multi-Sector Management Platform')
INK = '#3f4152'; INK_DARK = '#f2f4fa'; TAG = '#4b4d5e'; TAG_DARK = '#c9cddc'
# text geometry in source px (word 'KoolHub' and tagline)
ww, wh = wb[1] - wb[0], wb[3] - wb[2]; tw, th = tb[1] - tb[0], tb[3] - tb[2]

def T(d, x, y, scale, fill, ox, oy):  # place traced path so its bbox top-left lands at (x,y)
    return f'<path transform="translate({x - ox * scale:.2f} {y - oy * scale:.2f}) scale({scale:.5f})" fill="{fill}" fill-rule="evenodd" d="{d}"/>'

MARK_IMG = b64(mark.resize((MW // 2, MH // 2), Image.LANCZOS))
def mark_el(x, y, w):
    h = w * MH / MW
    return f'<image x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" href="data:image/png;base64,{MARK_IMG}"/>', h
def svg(w, h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">{body}</svg>'

def primary(dark=False, tagline=True):
    # stacked: mark, wordmark, tagline (tagline stretched to wordmark width like the source, which is slightly wider)
    ink, tag = (INK_DARK, TAG_DARK) if dark else (INK, TAG)
    Wd = 520; el, mh = mark_el((Wd - 400) / 2, 0, 400)
    y = mh + 34; sc = 440 / ww; body = el + T(word_d, (Wd - 440) / 2, y, sc, ink, wb[0], wb[2])
    y += wh * sc
    if tagline:
        ts = 440 / max(tw, ww) * (ww / max(tw, ww)) if False else 500 / tw
        ts = min(ts, 500 / tw); y += 26
        body += T(tag_d, (Wd - tw * ts) / 2, y, ts, tag, tb[0], tb[2]); y += th * ts
    return svg(Wd, y + 8, body)

def horizontal(dark=False, tagline=True):
    ink, tag = (INK_DARK, TAG_DARK) if dark else (INK, TAG)
    mw = 200; el, mh = mark_el(0, 0, mw); x = mw + 36
    sc = 300 / ww; block = wh * sc; ts = 300 / tw if tagline else 0
    total = block + (18 + th * ts if tagline else 0)
    y = (mh - total) / 2
    body = el + T(word_d, x, y, sc, ink, wb[0], wb[2])
    if tagline: body += T(tag_d, x, y + block + 18, ts, tag, tb[0], tb[2])
    return svg(x + 300, mh, body)

def mark_svg(kind='color'):
    if kind == 'color': el, h = mark_el(0, 0, 400); return svg(400, h, el)
    rgb_ = (255, 255, 255) if kind == 'white' else (17, 17, 17)
    s = silhouette(rgb_).resize((MW // 2, MH // 2), Image.LANCZOS)
    h = 400 * MH / MW
    return svg(400, h, f'<image width="400" height="{h:.2f}" href="data:image/png;base64,{b64(s)}"/>')

os.makedirs('svg', exist_ok=True)
files = {
 'koolhub-logo-primary': primary(), 'koolhub-logo-primary-dark': primary(True),
 'koolhub-logo-primary-notagline': primary(False, False), 'koolhub-logo-primary-notagline-dark': primary(True, False),
 'koolhub-logo-horizontal': horizontal(), 'koolhub-logo-horizontal-dark': horizontal(True),
 'koolhub-logo-horizontal-notagline': horizontal(False, False), 'koolhub-logo-horizontal-notagline-dark': horizontal(True, False),
 'koolhub-mark': mark_svg(), 'koolhub-mark-white': mark_svg('white'), 'koolhub-mark-black': mark_svg('black'),
}

# icons (rounded squares): light + dark
def icon_svg(dark=False, size=512, pad=.2, radius=.225):
    bg = '#141a33' if dark else '#ffffff'
    stroke = '' if dark else ' stroke="#e5e7eb"'
    mw = size * (1 - 2 * pad); el, mh = mark_el((size - mw) / 2, 0, mw)
    el, mh = mark_el((size - mw) / 2, (size - mw * MH / MW) / 2, mw)
    return svg(size, size, f'<rect x=".5" y=".5" width="{size - 1}" height="{size - 1}" rx="{size * radius:.1f}" fill="{bg}"{stroke}/>' + el)
files['koolhub-icon'] = icon_svg(); files['koolhub-icon-dark'] = icon_svg(True)
def fav_svg():
    mw = 512 * .78; el, _ = mark_el((512 - mw) / 2, (512 - mw * MH / MW) / 2, mw)
    return svg(512, 512, el)
files['favicon'] = fav_svg()
for k, v in files.items(): open(f'svg/{k}.svg', 'w').write(v)

# ---------- render PNGs with chromium ----------
from playwright.sync_api import sync_playwright
os.makedirs('png/logo', exist_ok=True); os.makedirs('png/icon', exist_ok=True)
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path=CHROME); pg = br.new_page()
    def r(svgname, out, w, bg=None):
        # use a data page loading svg via file:// requires allow; embed inline instead
        s = open(f'svg/{svgname}.svg').read()
        import re
        vw, vh = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s).groups()); h = round(w * vh / vw)
        pg.set_viewport_size({'width': w, 'height': h})
        sized = s.replace("<svg ", "<svg style='width:%dpx;height:%dpx;display:block' " % (w, h), 1)
        pg.set_content('<html><body style="margin:0;background:%s">%s</body></html>' % (bg or 'transparent', sized))
        pg.screenshot(path=out, omit_background=bg is None)
    for k in files:
        if k.startswith('koolhub-logo'):
            for w in (256, 512, 1024, 2048): r(k, f'png/logo/{k}-{w}w.png', w)
        elif k.startswith('koolhub-mark'):
            for w in (128, 256, 512, 1024): r(k, f'png/logo/{k}-{w}w.png', w)
        elif k in ('koolhub-icon', 'koolhub-icon-dark'):
            for w in (64, 128, 192, 256, 512, 1024): r(k, f'png/icon/{k}-{w}.png', w)
    # favicons
    os.makedirs('favicon', exist_ok=True)
    for w in (16, 32, 48, 180, 192, 512): r('favicon', f'favicon/_f{w}.png', w)
    r('favicon', 'favicon/_big.png', 1024)
    br.close()

# post-process rasters with PIL
def fl(path): return Image.open(path).convert('RGBA')
shutil.copy('svg/favicon.svg', 'favicon/favicon.svg')
for w, n in ((16, 'favicon-16x16'), (32, 'favicon-32x32'), (48, 'favicon-48x48'), (192, 'android-chrome-192x192'), (512, 'android-chrome-512x512')):
    os.replace(f'favicon/_f{w}.png', f'favicon/{n}.png')
def on_white(im, size, pad=0):
    bg = Image.new('RGBA', (size, size), (255, 255, 255, 255)); im = im.resize((size - 2 * pad, size - 2 * pad), Image.LANCZOS); bg.alpha_composite(im, (pad, pad)); return bg.convert('RGB')
big = fl('favicon/_big.png')
on_white(big, 180, 20).save('favicon/apple-touch-icon.png')
on_white(big, 512, 100).save('favicon/maskable-512x512.png')   # safe-zone padding
Image.open('favicon/favicon-48x48.png').save('favicon/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)]) if False else fl('favicon/_big.png').resize((256, 256), Image.LANCZOS).save('favicon/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
os.remove('favicon/_big.png')

# mobile
sq = fl('png/icon/koolhub-icon-1024.png')
def flat(dark, size, pad):  # opaque square, mark centered
    bg = Image.new('RGB', (size, size), (20, 26, 51) if dark else (255, 255, 255))
    mk = mark.resize((int(size * (1 - 2 * pad)), int(size * (1 - 2 * pad) * MH / MW)), Image.LANCZOS)
    bg.paste(mk, ((size - mk.width) // 2, (size - mk.height) // 2), mk); return bg
os.makedirs('mobile/ios', exist_ok=True)
flat(False, 1024, .2).save('mobile/ios/AppIcon-1024.png'); flat(True, 1024, .2).save('mobile/ios/AppIcon-dark-1024.png')
dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for d, f in dens.items():
    o = f'mobile/android/mipmap-{d}'; os.makedirs(o, exist_ok=True)
    s = int(48 * f); fs = int(108 * f)
    flat(False, s, .15).save(f'{o}/ic_launcher.png')
    r_ = flat(False, s, .2).convert('RGBA'); mask = Image.new('L', (s, s), 0)
    from PIL import ImageDraw; ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255); r_.putalpha(mask); r_.save(f'{o}/ic_launcher_round.png')
    # adaptive foreground: mark inside the 66/108 safe zone
    fg = Image.new('RGBA', (fs, fs), (0, 0, 0, 0)); mw_ = int(fs * .52); mk = mark.resize((mw_, int(mw_ * MH / MW)), Image.LANCZOS)
    fg.alpha_composite(mk, ((fs - mk.width) // 2, (fs - mk.height) // 2)); fg.save(f'{o}/ic_launcher_foreground.png')
flat(False, 512, .18).save('mobile/android/play-store-512.png')

# social OG 1200x630 (light bg, horizontal logo)
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path=CHROME); pg = br.new_page(viewport={'width': 1200, 'height': 630})
    s = open('svg/koolhub-logo-horizontal.svg').read().replace('<svg ', "<svg style='width:900px;display:block' ", 1)
    pg.set_content(f'<html><body style="margin:0;width:1200px;height:630px;background:#fff;display:flex;align-items:center;justify-content:center">{s}</body></html>')
    os.makedirs('social', exist_ok=True); pg.screenshot(path='social/og-image-1200x630.png'); br.close()

# manifest + head snippet
json.dump({"name": "KoolHub", "short_name": "KoolHub", "description": "Integrated Multi-Sector Management Platform",
 "icons": [{"src": "/favicon/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
           {"src": "/favicon/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
           {"src": "/favicon/maskable-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
 "theme_color": "#5b57d1", "background_color": "#ffffff", "display": "standalone"}, open('favicon/site.webmanifest', 'w'), indent=2)
open('favicon/head-snippet.html', 'w').write(open('../KoolKamp/favicon/head-snippet.html').read().replace('#7840d2', '#5b57d1'))
print('done')
