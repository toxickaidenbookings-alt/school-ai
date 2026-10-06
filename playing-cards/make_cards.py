"""Draws a 52-card deck in a hand-drawn marker style.

Every line is stamped along a jittered path with a round brush, so no two
cards come out identical. Run: python3 make_cards.py
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter

W, H = 2000, 1414          # same canvas as the original sketch
S = 2                      # supersample, then shrink for soft edges
INK = (13, 13, 13)
PEN = 11                   # brush radius (before supersampling)
OUT = os.path.dirname(os.path.abspath(__file__))

# Rank glyphs as strokes in a 1 x 1.4 box (y down). "s" = smooth curve.
G = {
    'A': [('l', [(0, 1.4), (0.5, 0), (1, 1.4)]), ('l', [(0.22, 0.88), (0.8, 0.85)])],
    '2': [('s', [(0.05, 0.35), (0.25, 0.05), (0.65, 0.0), (0.92, 0.3), (0.75, 0.7), (0.05, 1.38)]),
          ('l', [(0.05, 1.38), (1, 1.33)])],
    '3': [('s', [(0.05, 0.18), (0.45, 0.0), (0.88, 0.22), (0.78, 0.58), (0.35, 0.68)]),
          ('s', [(0.35, 0.68), (0.88, 0.82), (0.95, 1.15), (0.5, 1.4), (0.05, 1.25)])],
    '4': [('l', [(0.75, 0.0), (0.0, 0.95), (1, 0.93)]), ('l', [(0.72, 0.4), (0.7, 1.4)])],
    '5': [('l', [(0.92, 0.0), (0.15, 0.03), (0.1, 0.6)]),
          ('s', [(0.1, 0.6), (0.55, 0.5), (0.93, 0.8), (0.85, 1.25), (0.45, 1.4), (0.05, 1.25)])],
    '6': [('s', [(0.85, 0.05), (0.4, 0.15), (0.08, 0.75), (0.15, 1.25), (0.5, 1.4),
                 (0.88, 1.15), (0.82, 0.78), (0.45, 0.68), (0.1, 0.92)])],
    '7': [('l', [(0.0, 0.0), (0.55, 0.1), (1, 0.12)]), ('l', [(1, 0.12), (0.8, 0.55), (0.55, 0.95), (0.4, 1.35)])],
    '8': [('s', [(0.5, 0.68), (0.12, 0.4), (0.2, 0.05), (0.75, 0.05), (0.85, 0.38), (0.5, 0.68),
                 (0.08, 1.0), (0.25, 1.38), (0.8, 1.35), (0.92, 1.0), (0.5, 0.68)])],
    '9': [('s', [(0.9, 0.45), (0.55, 0.7), (0.12, 0.5), (0.2, 0.08), (0.65, 0.0), (0.9, 0.3),
                 (0.85, 0.9), (0.55, 1.4)])],
    'J': [('l', [(0.3, 0.0), (1, 0.02)]), ('s', [(0.75, 0.0), (0.75, 1.0), (0.55, 1.38), (0.2, 1.35), (0.05, 1.05)])],
    'Q': [('s', [(0.5, 0.0), (0.08, 0.3), (0.05, 1.0), (0.5, 1.38), (0.95, 1.0), (0.92, 0.3), (0.5, 0.0), (0.3, 0.1)]),
          ('l', [(0.55, 0.95), (1.05, 1.45)])],
    'K': [('l', [(0.1, 0.0), (0.12, 1.4)]), ('l', [(0.95, 0.0), (0.12, 0.78)]), ('l', [(0.4, 0.55), (1, 1.4)])],
}
G['10'] = [('l', [(0.0, 0.25), (0.3, 0.0), (0.3, 1.4)])] + \
          [('s', [((x * 0.85) + 0.6, y) for x, y in
                  [(0.5, 0.0), (0.08, 0.3), (0.05, 1.0), (0.5, 1.4), (0.95, 1.0), (0.92, 0.3), (0.5, 0.0), (0.3, 0.1)]])]
WIDTH = {'10': 1.45}
for _r in ('6', '9'):
    G[_r] = G[_r] + [('l', [(0.1, 1.62), (0.9, 1.61)])]


def catmull(pts, n=14):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t +
                                    (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def wobble_line(pts, amp):
    """Break straight segments into a few points nudged sideways, then smooth."""
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        steps = max(2, int(L / 70))
        nx, ny = -(y1 - y0) / (L or 1), (x1 - x0) / (L or 1)
        for k in range(1, steps + 1):
            t = k / steps
            off = 0 if k == steps else random.uniform(-amp, amp)
            out.append((x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off))
    # keep corners sharp: smooth each segment run separately
    return out


def brush(d, path, r):
    """Stamp a round brush densely along the path (variable pressure)."""
    dense = []
    for a, b in zip(path, path[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / 2))
        dense += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    dense.append(path[-1])
    phase = random.uniform(0, 6.28)
    for i, (x, y) in enumerate(dense):
        rr = r * (1 + 0.08 * math.sin(i / 40 + phase))
        d.ellipse([(x - rr) * S, (y - rr) * S, (x + rr) * S, (y + rr) * S], fill=INK)


def draw_rank(d, rank, x, y, h, flip):
    w_unit = h / 1.4
    ang = math.radians(random.uniform(-6, 6) + (180 if flip else 0))
    bw = WIDTH.get(rank, 1) * w_unit
    cx, cy = x + bw / 2, y + h / 2
    ca, sa = math.cos(ang), math.sin(ang)
    for kind, pts in G[rank]:
        pts = [(x + px * w_unit + random.uniform(-4, 4), y + py * w_unit + random.uniform(-4, 4)) for px, py in pts]
        pts = [(cx + (px - cx) * ca - (py - cy) * sa, cy + (px - cx) * sa + (py - cy) * ca) for px, py in pts]
        path = catmull(pts) if kind == 's' else wobble_line(pts, 3)
        brush(d, path, PEN * 0.85)


def card_outline(x0, y0, x1, y1):
    pts = []
    def edge(a, b, n):
        for k in range(n):
            t = k / n
            pts.append((a[0] + (b[0] - a[0]) * t + random.uniform(-3, 3),
                        a[1] + (b[1] - a[1]) * t + random.uniform(-3, 3)))
    r = random.uniform(25, 45)
    corners = [(x0 + r, y0), (x1 - 8, y0 - random.uniform(0, 20)), (x1, y1 - r), (x0, y1 - r)]
    edge((x0 + r, y0 + random.uniform(-5, 15)), (x1 - 10, y0 - 15), 4)        # top (tilts up like the sketch)
    edge((x1 - 5, y0 - 12), (x1 + random.uniform(-5, 10), y1 - r), 5)          # right
    edge((x1 - r * 0.6, y1 + random.uniform(-5, 5)), (x0 + r, y1 + 8), 4)      # bottom
    edge((x0 - random.uniform(0, 12), y1 - r * 1.5), (x0 - 5, y0 + r), 5)      # left
    pts.append(pts[0]); pts.append(pts[1])
    return catmull(pts, 10)


def suit_shape(suit, cx, cy, h):
    """Filled outline for a suit, as a list of points."""
    w = h * random.uniform(0.40, 0.46)
    j = lambda p: (p[0] + random.uniform(-h * .012, h * .012), p[1] + random.uniform(-h * .012, h * .012))
    if suit == 'diamonds':
        raw = [(0, -.5), (.1, -.36), (.2, -.16), (.26, -.02), (.19, .16), (.1, .36), (0, .5),
               (-.1, .37), (-.21, .15), (-.26, -.03), (-.2, -.2), (-.1, -.38)]
        return catmull([j((cx + px * h, cy + py * h)) for px, py in raw + raw[:1]], 8), []
    if suit == 'hearts':
        raw = [(0, -.22), (.12, -.4), (.3, -.38), (.4, -.18), (.32, .08), (.12, .3), (0, .45),
               (-.14, .28), (-.33, .06), (-.4, -.2), (-.28, -.4), (-.1, -.38)]
        return catmull([j((cx + px * h, cy + py * h)) for px, py in raw + raw[:1]], 8), []
    if suit == 'spades':
        raw = [(0, -.48), (.18, -.25), (.38, -.02), (.36, .18), (.2, .25), (.03, .14),
               (-.04, .14), (-.2, .26), (-.37, .16), (-.38, -.04), (-.18, -.26)]
        stem = [(0, .1), (.04, .3), (.13, .45), (0, .47), (-.13, .44), (-.04, .3), (0, .1)]
        return (catmull([j((cx + px * h, cy + py * h)) for px, py in raw + raw[:1]], 8),
                [catmull([j((cx + px * h, cy + py * h)) for px, py in stem], 6)])
    if suit == 'clubs':
        blobs = []
        for bx, by, br in [(0, -.27, .17), (-.2, .04, .17), (.2, .04, .17), (0, -.02, .1)]:
            n = 18
            ring = [j((cx + (bx + br * math.cos(2 * math.pi * k / n)) * h,
                       cy + (by + br * math.sin(2 * math.pi * k / n)) * h)) for k in range(n)]
            blobs.append(catmull(ring + ring[:1], 6))
        stem = [(0, -.05), (.04, .25), (.13, .45), (0, .47), (-.13, .44), (-.04, .25), (0, -.05)]
        blobs.append(catmull([j((cx + px * h, cy + py * h)) for px, py in stem], 6))
        return blobs[0], blobs[1:]


def draw_card(rank, suit, seed):
    random.seed(seed)
    img = Image.new('RGB', (W * S, H * S), 'white')
    d = ImageDraw.Draw(img)
    x0, y0 = 700 + random.uniform(-10, 10), 340 + random.uniform(-15, 15)
    x1, y1 = 1300 + random.uniform(-10, 10), 1100 + random.uniform(-10, 10)
    brush(d, card_outline(x0, y0, x1, y1), PEN)

    rh = random.uniform(160, 180)
    bw = WIDTH.get(rank, 1) * rh / 1.4
    draw_rank(d, rank, x1 - 40 - bw + random.uniform(-10, 5), y0 + 35 + random.uniform(-5, 10), rh, False)
    draw_rank(d, rank, x0 + 75 + random.uniform(-10, 10), y1 - 55 - rh + random.uniform(-10, 5), rh, True)

    main, extra = suit_shape(suit, (x0 + x1) / 2 - 30 + random.uniform(-15, 15),
                             (y0 + y1) / 2 - 15 + random.uniform(-15, 15), random.uniform(320, 350))
    for shape in [main] + extra:
        d.polygon([(px * S, py * S) for px, py in shape], fill=INK)

    img = img.filter(ImageFilter.GaussianBlur(S * 1.6)).resize((W, H), Image.LANCZOS)
    return img


RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = ['spades', 'hearts', 'diamonds', 'clubs']

if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'cards'), exist_ok=True)
    thumbs = []
    for si, suit in enumerate(SUITS):
        for ri, rank in enumerate(RANKS):
            img = draw_card(rank, suit, seed=si * 100 + ri)
            img.save(os.path.join(OUT, 'cards', f'{rank}_of_{suit}.png'), optimize=True)
            thumbs.append(img.crop((620, 260, 1380, 1180)).resize((228, 276), Image.LANCZOS))
    sheet = Image.new('RGB', (228 * 13, 276 * 4), 'white')
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % 13) * 228, (i // 13) * 276))
    sheet.save(os.path.join(OUT, 'all_cards.png'), optimize=True)
    print('done')
