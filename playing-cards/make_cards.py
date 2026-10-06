"""Draws a 52-card deck in a hand-drawn marker style.

Every line is stamped along a jittered path with a round brush, so no two
cards come out identical. Run: python3 make_cards.py
(make_poster.py reuses the pen and letters from here.)
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter

W, H = 2000, 1414          # same canvas as the original sketch
S = 2                      # supersample, then shrink for soft edges
INK = (13, 13, 13)
RED = (206, 32, 36)
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
WIDTH = {'10': 1.45, 'I': 0.6, '1': 0.5, '.': 0.25, ' ': 0.55}
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



# Handwritten capitals for poster text, same 1 x 1.4 box.
OVAL = [(0.5, 0.0), (0.08, 0.3), (0.05, 1.0), (0.5, 1.4), (0.95, 1.0), (0.92, 0.3), (0.5, 0.0), (0.3, 0.1)]
G.update({
    'C': [('s', [(0.95, 0.2), (0.55, 0.0), (0.1, 0.35), (0.08, 1.0), (0.5, 1.4), (0.95, 1.2)])],
    'O': [('s', OVAL)],
    'M': [('l', [(0, 1.4), (0.1, 0), (0.5, 0.8), (0.9, 0), (1, 1.4)])],
    'I': [('l', [(0.3, 0), (0.3, 1.4)]), ('l', [(0.0, 0.0), (0.6, 0.02)]), ('l', [(0.0, 1.4), (0.6, 1.38)])],
    'N': [('l', [(0.05, 1.4), (0.05, 0), (0.95, 1.4), (0.95, 0)])],
    'G': [('s', [(0.95, 0.2), (0.55, 0.0), (0.1, 0.35), (0.08, 1.0), (0.5, 1.4), (0.95, 1.1), (0.95, 0.8)]),
          ('l', [(0.95, 0.8), (0.55, 0.8)])],
    'S': [('s', [(0.92, 0.18), (0.5, 0.0), (0.1, 0.25), (0.2, 0.6), (0.8, 0.8), (0.92, 1.15), (0.5, 1.4), (0.05, 1.2)])],
    'T': [('l', [(0, 0), (1, 0.02)]), ('l', [(0.5, 0), (0.5, 1.4)])],
    'H': [('l', [(0.05, 0), (0.05, 1.4)]), ('l', [(0.95, 0), (0.95, 1.4)]), ('l', [(0.05, 0.7), (0.95, 0.7)])],
    'E': [('l', [(0.95, 0), (0.05, 0), (0.05, 1.4), (0.95, 1.4)]), ('l', [(0.05, 0.7), (0.75, 0.7)])],
    'R': [('l', [(0.08, 1.4), (0.08, 0)]), ('s', [(0.08, 0), (0.7, 0.02), (0.92, 0.35), (0.7, 0.68), (0.08, 0.7)]),
          ('l', [(0.4, 0.7), (0.95, 1.4)])],
    'P': [('l', [(0.08, 1.4), (0.08, 0)]), ('s', [(0.08, 0), (0.7, 0.02), (0.92, 0.35), (0.7, 0.68), (0.08, 0.7)])],
    'D': [('l', [(0.08, 0), (0.08, 1.4)]), ('s', [(0.08, 0), (0.6, 0.05), (0.95, 0.5), (0.9, 1.0), (0.55, 1.38), (0.08, 1.4)])],
    'U': [('s', [(0.05, 0), (0.05, 1.0), (0.5, 1.4), (0.95, 1.0), (0.95, 0)])],
    'L': [('l', [(0.05, 0), (0.05, 1.4), (0.9, 1.38)])],
    'V': [('l', [(0, 0), (0.5, 1.4), (1, 0)])],
    '1': [('l', [(0.0, 0.25), (0.3, 0.0), (0.3, 1.4)])],
    '.': [('l', [(0.1, 1.33), (0.12, 1.38)])],
    ' ': [],
})


class Pen:
    """A supersampled sheet of paper plus a transform for where we're drawing."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new('RGB', (w * S, h * S), 'white')
        self.d = ImageDraw.Draw(self.img)
        self.xf = (0, 0, 1, 0)                          # offset x, offset y, scale, angle

    def at(self, ox, oy, sc=1, deg=0):
        self.xf = (ox, oy, sc, math.radians(deg))
        return self

    def pt(self, x, y):
        ox, oy, sc, a = self.xf
        return (ox + sc * (x * math.cos(a) - y * math.sin(a)), oy + sc * (x * math.sin(a) + y * math.cos(a)))

    def stroke(self, path, r=PEN, color=INK):
        path = [self.pt(*p) for p in path]
        r *= self.xf[2]
        dense = []
        for a, b in zip(path, path[1:]):
            n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 2))
            dense += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
        dense.append(path[-1])
        phase = random.uniform(0, 6.28)
        for i, (x, y) in enumerate(dense):
            rr = r * (1 + 0.08 * math.sin(i / 40 + phase))     # marker pressure
            self.d.ellipse([(x - rr) * S, (y - rr) * S, (x + rr) * S, (y + rr) * S], fill=color)

    def fill(self, pts, color=INK):
        self.d.polygon([(x * S, y * S) for x, y in (self.pt(*p) for p in pts)], fill=color)

    def blob(self, x, y, r, color=INK):
        n = 14
        ring = [(x + r * math.cos(2 * math.pi * k / n) + random.uniform(-r, r) * .08,
                 y + r * math.sin(2 * math.pi * k / n) + random.uniform(-r, r) * .08) for k in range(n)]
        self.fill(catmull(ring + ring[:1], 5), color)

    def finish(self):
        return self.img.filter(ImageFilter.GaussianBlur(S * 1.6)).resize((self.w, self.h), Image.LANCZOS)


def wobble_line(pts, amp):
    """Break straight segments into a few points nudged sideways (hand shake)."""
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        steps = max(2, int(L / 70))
        nx, ny = -(y1 - y0) / (L or 1), (x1 - x0) / (L or 1)
        for k in range(1, steps + 1):
            t = k / steps
            off = 0 if k == steps else random.uniform(-amp, amp)
            out.append((x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off))
    return out


def glyph(pen, ch, x, y, h, deg=0, r=PEN * 0.85, color=INK):
    """Write one character with its box's top-left at (x, y); returns its width."""
    w_unit = h / 1.4
    bw = WIDTH.get(ch, 1) * w_unit
    cx, cy = x + bw / 2, y + h / 2
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    shake = h * 0.022
    for kind, pts in G[ch]:
        pts = [(x + px * w_unit + random.uniform(-shake, shake), y + py * w_unit + random.uniform(-shake, shake)) for px, py in pts]
        pts = [(cx + (px - cx) * ca - (py - cy) * sa, cy + (px - cx) * sa + (py - cy) * ca) for px, py in pts]
        pen.stroke(catmull(pts) if kind == 's' else wobble_line(pts, shake * .8), r, color)
    return bw


def write(pen, text, x, y, h, r=PEN * 0.85, color=INK, gap=0.25, center=False):
    """Write a line of handwritten text, each letter a little crooked."""
    if center:
        x -= sum(WIDTH.get(c, 1) * h / 1.4 + gap * h for c in text) / 2
    for ch in text:
        x += glyph(pen, ch, x, y + random.uniform(-h * .04, h * .04), h, random.uniform(-5, 5), r, color) + gap * h


def wobbly_box(x0, y0, x1, y1, tilt=15, jit=3):
    """Closed, slightly crooked rectangle like the sketch (top-right pokes up)."""
    pts = []
    def edge(a, b, n):
        for k in range(n):
            t = k / n
            pts.append((a[0] + (b[0] - a[0]) * t + random.uniform(-jit, jit),
                        a[1] + (b[1] - a[1]) * t + random.uniform(-jit, jit)))
    r = random.uniform(25, 45)
    edge((x0 + r, y0 + random.uniform(-5, 15)), (x1 - 10, y0 - tilt), 4)
    edge((x1 - 5, y0 - tilt * .8), (x1 + random.uniform(-5, 10), y1 - r), 5)
    edge((x1 - r * 0.6, y1 + random.uniform(-5, 5)), (x0 + r, y1 + 8), 4)
    edge((x0 - random.uniform(0, 12), y1 - r * 1.5), (x0 - 5, y0 + r), 5)
    pts.append(pts[0]); pts.append(pts[1])
    return catmull(pts, 10)


def suit_shape(suit, cx, cy, h):
    """Filled outline(s) for a suit."""
    j = lambda p: (p[0] + random.uniform(-h * .012, h * .012), p[1] + random.uniform(-h * .012, h * .012))
    closed = lambda raw, n=8: catmull([j((cx + px * h, cy + py * h)) for px, py in raw + raw[:1]], n)
    stem = [(0, .1), (.04, .3), (.13, .45), (0, .47), (-.13, .44), (-.04, .3)]
    if suit == 'diamonds':
        return [closed([(0, -.5), (.1, -.36), (.2, -.16), (.26, -.02), (.19, .16), (.1, .36), (0, .5),
                        (-.1, .37), (-.21, .15), (-.26, -.03), (-.2, -.2), (-.1, -.38)])]
    if suit == 'hearts':
        return [closed([(0, -.22), (.12, -.4), (.3, -.38), (.4, -.18), (.32, .08), (.12, .3), (0, .45),
                        (-.14, .28), (-.33, .06), (-.4, -.2), (-.28, -.4), (-.1, -.38)])]
    if suit == 'spades':
        return [closed([(0, -.48), (.18, -.25), (.38, -.02), (.36, .18), (.2, .25), (.03, .14),
                        (-.04, .14), (-.2, .26), (-.37, .16), (-.38, -.04), (-.18, -.26)]), closed(stem, 6)]
    if suit == 'clubs':
        rings = [[(bx + br * math.cos(2 * math.pi * k / 18), by + br * math.sin(2 * math.pi * k / 18)) for k in range(18)]
                 for bx, by, br in [(0, -.27, .17), (-.2, .04, .17), (.2, .04, .17), (0, -.02, .1)]]
        return [closed(r, 6) for r in rings] + [closed([(x, y - .15 if y == .1 else y) for x, y in stem], 6)]


CARD_W, CARD_H = 600, 760     # card size in its own coordinates


def card(pen, rank, suit, seed, paper=False):
    """Draw a card at pen's current transform; (0,0) is its top-left corner."""
    random.seed(seed)
    color = RED if suit in ('hearts', 'diamonds') else INK
    x0, y0 = random.uniform(-10, 10), random.uniform(-15, 15)
    x1, y1 = CARD_W + random.uniform(-10, 10), CARD_H + random.uniform(-10, 10)
    edge = wobbly_box(x0, y0, x1, y1)
    if paper:
        pen.fill(edge, 'white')                     # so cards underneath are hidden
    pen.stroke(edge)

    rh = random.uniform(160, 180)
    bw = WIDTH.get(rank, 1) * rh / 1.4
    for ch_x, ch_y, deg in [(x1 - 40 - bw + random.uniform(-10, 5), y0 + 35 + random.uniform(-5, 10), random.uniform(-6, 6)),
                            (x0 + 75 + random.uniform(-10, 10), y1 - 55 - rh + random.uniform(-10, 5), 180 + random.uniform(-6, 6))]:
        glyph(pen, rank, ch_x, ch_y, rh, deg, color=color)

    for shape in suit_shape(suit, (x0 + x1) / 2 - 30 + random.uniform(-15, 15),
                            (y0 + y1) / 2 - 15 + random.uniform(-15, 15), random.uniform(320, 350)):
        pen.fill(shape, color)


RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = ['spades', 'hearts', 'diamonds', 'clubs']
DECK = [(r, s, si * 100 + ri) for si, s in enumerate(SUITS) for ri, r in enumerate(RANKS)]


def messy_stack(pen, cx, cy, sc, n, seed, wide=1100, tall=520):
    """A pile of cards dropped on top of each other, bottom card first."""
    rnd = random.Random(seed)
    picks = rnd.sample(DECK, n)
    for i, (rank, suit, s) in enumerate(picks):
        spread = 1 - 0.6 * i / n                      # bottom cards wander further
        x = cx + rnd.uniform(-1, 1) * wide * sc * spread
        y = cy + rnd.uniform(-1, 1) * tall * sc * spread
        deg = rnd.uniform(-35, 35) * spread + rnd.uniform(-6, 6)
        a = math.radians(deg)
        # place so the card's centre lands on (x, y)
        hx, hy = CARD_W / 2 * sc, CARD_H / 2 * sc
        pen.at(x - (hx * math.cos(a) - hy * math.sin(a)), y - (hx * math.sin(a) + hy * math.cos(a)), sc, deg)
        card(pen, rank, suit, s, paper=True)


if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'cards'), exist_ok=True)
    thumbs = []
    for rank, suit, seed in DECK:
        pen = Pen(W, H).at(700, 340)
        card(pen, rank, suit, seed)
        img = pen.finish()
        img.save(os.path.join(OUT, 'cards', f'{rank}_of_{suit}.png'), optimize=True)
        thumbs.append(img.crop((620, 260, 1380, 1180)).resize((228, 276), Image.LANCZOS))
    sheet = Image.new('RGB', (228 * 13, 276 * 4), 'white')
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % 13) * 228, (i // 13) * 276))
    sheet.save(os.path.join(OUT, 'all_cards.png'), optimize=True)

    pen = Pen(W, H)
    messy_stack(pen, W / 2, H / 2 + 20, 0.62, 52, seed=7)
    pen.finish().save(os.path.join(OUT, 'stack.png'), optimize=True)
    print('done')
