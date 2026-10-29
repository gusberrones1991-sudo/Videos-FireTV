# Prepara la app "Videos" (com.gus.videos): logo, nombre y variante de compilacion
import os, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

SS = 4
STOPS = [(0.0, (91, 46, 255)), (0.55, (255, 46, 126)), (1.0, (255, 154, 60))]

def find_font():
    pats = ['/usr/share/fonts/**/Inter*ExtraBold*.otf', '/usr/share/fonts/**/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/**/LiberationSans-Bold.ttf', '/usr/share/fonts/**/*Bold*.ttf']
    for p in pats:
        r = glob.glob(p, recursive=True)
        if r:
            return r[0]
    return None

def gradient(w, h):
    xs = np.linspace(0, 1, w)[None, :]
    ys = np.linspace(0, 1, h)[:, None]
    t = np.clip(xs * 0.6 + (1 - ys) * 0.4, 0, 1)
    out = np.zeros((h, w, 3))
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        m = (t >= t0) & (t <= t1)
        k = ((t - t0) / (t1 - t0))[..., None]
        seg = np.array(c0) + (np.array(c1) - np.array(c0)) * k
        out[m] = seg[m]
    return Image.fromarray(out.astype('uint8'), 'RGB')

def white(S, alpha):
    return Image.merge('RGBA', (Image.new('L', (S, S), 255),) * 3 + (alpha,))

def rounded_triangle(S, cx, cy, r, rad):
    m = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(m)
    pts = [(cx - r * 0.5, cy - r * 0.866), (cx - r * 0.5, cy + r * 0.866), (cx + r, cy)]
    d.polygon(pts, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(rad)).point(lambda v: 255 if v > 160 else 0)
    return m.filter(ImageFilter.GaussianBlur(1))

def icon(px):
    S = px * SS
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=255)
    img.paste(gradient(S, S), (0, 0), mask)
    gloss = Image.new('L', (S, S), 0)
    ImageDraw.Draw(gloss).ellipse([-S * 0.3, -S * 0.55, S * 0.9, S * 0.45], fill=70)
    gloss = ImageChops.multiply(gloss.filter(ImageFilter.GaussianBlur(S * 0.06)), mask)
    img = Image.alpha_composite(img, white(S, gloss))
    cx, cy, r = S * 0.53, S * 0.5, S * 0.27
    back = rounded_triangle(S, cx - S * 0.07, cy, r, S * 0.03).point(lambda v: int(v * 0.30))
    img = Image.alpha_composite(img, white(S, back))
    tri = rounded_triangle(S, cx, cy, r, S * 0.03)
    sh = ImageChops.offset(tri.filter(ImageFilter.GaussianBlur(S * 0.025)).point(lambda v: int(v * 0.35)), 0, int(S * 0.02))
    img = Image.alpha_composite(img, Image.merge('RGBA', (Image.new('L', (S, S), 40),) * 3 + (sh,)))
    img = Image.alpha_composite(img, white(S, tri))
    sp = Image.new('L', (S, S), 0)
    sx, sy, sr = S * 0.77, S * 0.24, S * 0.06
    ImageDraw.Draw(sp).polygon([(sx, sy - sr), (sx + sr * .22, sy - sr * .22), (sx + sr, sy), (sx + sr * .22, sy + sr * .22),
                                (sx, sy + sr), (sx - sr * .22, sy + sr * .22), (sx - sr, sy), (sx - sr * .22, sy - sr * .22)], fill=235)
    img = Image.alpha_composite(img, white(S, sp))
    img.putalpha(ImageChops.multiply(img.getchannel('A'), mask))
    return img.resize((px, px), Image.LANCZOS)

def banner(w, h):
    W, H = w * SS, h * SS
    img = Image.new('RGBA', (W, H), (14, 11, 31, 255))
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).ellipse([-W * 0.1, -H * 0.4, W * 0.6, H * 1.2], fill=90)
    col = Image.new('RGBA', (W, H), (120, 40, 255, 255))
    col.putalpha(glow.filter(ImageFilter.GaussianBlur(H * 0.25)))
    img = Image.alpha_composite(img, col)
    isz = int(H * 0.56)
    ic = icon(isz // SS).resize((isz, isz), Image.LANCZOS)
    ix, iy = int(W * 0.09), (H - isz) // 2
    img.alpha_composite(ic, (ix, iy))
    fp = find_font()
    font = ImageFont.truetype(fp, int(H * 0.27)) if fp else ImageFont.load_default()
    d = ImageDraw.Draw(img)
    tx = ix + isz + int(W * 0.05)
    bb = d.textbbox((0, 0), 'Videos', font=font)
    d.text((tx, (H - (bb[3] - bb[1])) // 2 - bb[1]), 'Videos', font=font, fill=(255, 255, 255, 255))
    return img.resize((w, h), Image.LANCZOS).convert('RGB')

def tint(im, rgb, k):
    s = Image.new('RGBA', im.size, rgb + (255,))
    s.putalpha(im.getchannel('A').point(lambda v: int(v * k)))
    return s

R = 'smarttubetv/src/stvideos/res'
for d in ('mipmap-nodpi', 'mipmap-nodpi-v30', 'values'):
    os.makedirs(f'{R}/{d}', exist_ok=True)
ic = icon(320)
ic.save(f'{R}/mipmap-nodpi/app_icon.png')
ic.save(f'{R}/mipmap-nodpi-v30/app_icon.png')
banner(640, 360).save(f'{R}/mipmap-nodpi/app_banner.png')
lg = icon(180)
lg.save(f'{R}/mipmap-nodpi/app_logo.png')
tint(lg, (255, 46, 126), 0.85).save(f'{R}/mipmap-nodpi/app_logo_semi_red.png')
tint(lg, (180, 180, 180), 0.6).save(f'{R}/mipmap-nodpi/app_logo_semi_grey.png')

open(f'{R}/values/strings.xml', 'w').write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string translatable="false" name="app_name"><![CDATA[Videos]]></string>
    <string translatable="false" name="browse_title"><![CDATA[Videos]]></string>
</resources>
''')

p = 'smarttubetv/build.gradle'
s = open(p).read()
if 'stvideos' not in s:
    a = '        stfdroid {'
    assert a in s, 'flavor anchor not found'
    s = s.replace(a, '''        stvideos {
            applicationId "com.gus.videos"
            targetSdkVersion project.properties.compileSdkVersion
            signingConfig signingConfigs.debug
        }
''' + a, 1)
    s = s.replace('def project = "SmartTube"', 'def project = variant.productFlavors[-1].name == "stvideos" ? "Videos" : "SmartTube"', 1)
    open(p, 'w').write(s)
print('Videos listo')
