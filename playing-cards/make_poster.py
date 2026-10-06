"""Movie poster: MISSION CARD VAULT, on a busted LED sign. Same marker as the cards.

Run: python3 make_poster.py   (writes poster.png)
"""
import math, os, random
from make_cards import Pen, card, catmull, wobble_line, wobbly_box, write, messy_stack, INK, RED, PEN, OUT, CARD_W, CARD_H

PW, PH = 1414, 2000

LED_ON = (255, 70, 30)
LED_GLOW = (255, 190, 150)
LED_DIM = (120, 45, 35)
DEAD = (95, 95, 95)
SPARK = (255, 200, 0)
WIRE = (150, 150, 160)

# 5x7 sign font ("#" = bulb)
FONT = {
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'S': ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'N': ['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'],
    'C': ['.####', '#....', '#....', '#....', '#....', '#....', '.####'],
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
    'D': ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
    'V': ['#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    ' ': ['...'] * 7,
}


def led_bulbs(text, pitch):
    """(col, row) of every bulb in a line of sign text, plus total width in columns."""
    bulbs, col = [], 0
    for i, ch in enumerate(text):
        rows = FONT[ch]
        for r, line in enumerate(rows):
            for c, on in enumerate(line):
                if on == '#':
                    bulbs.append((col + c, r, i))
        col += len(rows[0]) + 1
    return bulbs, col - 1


def bulb(pen, x, y, pitch, state):
    if state == 'on':
        pen.blob(x, y, pitch * 0.62, LED_GLOW)          # light bleeding out, done with a lighter marker
        pen.blob(x, y, pitch * 0.36, LED_ON)
    elif state == 'dim':
        pen.blob(x, y, pitch * 0.34, LED_DIM)
    else:                                               # dead bulb: just a little grey ring
        ring = [(x + pitch * .28 * math.cos(2 * math.pi * k / 10), y + pitch * .28 * math.sin(2 * math.pi * k / 10)) for k in range(11)]
        pen.stroke(catmull(ring, 4), 2.2, DEAD)


def spark(pen, x, y, size):
    for k in range(7):
        a = random.uniform(0, 2 * math.pi)
        L = size * random.uniform(0.5, 1)
        mid = (x + math.cos(a) * L * .5 + random.uniform(-6, 6), y + math.sin(a) * L * .5 + random.uniform(-6, 6))
        pen.stroke([(x, y), mid, (x + math.cos(a) * L, y + math.sin(a) * L)], 4, SPARK if k % 2 else INK)


def sign(pen):
    """The hanging LED sign. One wire snapped, so it hangs crooked."""
    sx, sy, deg = 110, 175, 4                           # sign's top-left and tilt
    sw, sh = 1190, 470

    # wires from the top of the poster (drawn before the tilt)
    pen.at(0, 0)
    pen.stroke(wobble_line([(230, 52), (sx + 120, sy + 5)], 3), 5, WIRE)
    pen.stroke(wobble_line([(1180, 52), (1165, 110)], 3), 5, WIRE)            # snapped stub at the top
    pen.stroke(catmull([(1165, 110), (1185, 125), (1170, 140)]), 5, WIRE)
    spark(pen, 1172, 142, 40)

    pen.at(sx, sy, 1, deg)
    box = wobbly_box(0, 0, sw, sh, tilt=8, jit=4)
    pen.fill(box, (25, 25, 25))
    # rough scribble on top so the black looks coloured-in, not printed
    y = 22
    while y < sh - 15:
        xs = [30 + random.uniform(-10, 10), sw - 30 + random.uniform(-10, 10)]
        pen.stroke([(xs[0], y), (xs[1], y + random.uniform(4, 12))], 7, INK)
        y += random.uniform(14, 22)
    pen.stroke(box, PEN + 2)
    rim = wobbly_box(14, 14, sw - 14, sh - 14, tilt=6, jit=3)
    pen.stroke(rim, 3, (110, 110, 120))                # metal edge so it shows up against the night
    pen.stroke(wobble_line([(sw - 125, -2), (sw - 115, -45)], 3), 5, WIRE)         # other half of the snapped wire
    for bx, by in [(28, 28), (sw - 30, 30), (30, sh - 30), (sw - 32, sh - 28)]:
        pen.blob(bx, by, 9, (150, 150, 150))

    crack_x = sw - 330                                  # everything right of the crack is flaky
    crack = [(crack_x, -5), (crack_x - 30, 90), (crack_x + 25, 170), (crack_x - 15, 260), (crack_x + 40, 350), (crack_x + 5, sh + 5)]
    pen.stroke(wobble_line(crack, 4), 4.5, (230, 230, 230))

    lines = [('MISSION', 27, 42), ('CARD VAULT', 19.5, 280)]
    flicker_letter = {('MISSION', 5)}                   # the O is on its last legs
    for text, pitch, top in lines:
        bulbs, cols = led_bulbs(text, pitch)
        left = (sw - cols * pitch) / 2 + pitch / 2
        for col, row, li in bulbs:
            x = left + col * pitch + random.uniform(-1.5, 1.5)
            y = top + row * pitch + random.uniform(-1.5, 1.5)
            past_crack = x > crack_x + 20
            r = random.random()
            if (text, li) in flicker_letter:
                state = 'dim' if r < .6 else 'dead'
            elif past_crack:
                state = 'dead' if r < .45 else 'dim' if r < .6 else 'on'
            else:
                state = 'dead' if r < .07 else 'on'
            bulb(pen, x, y, pitch, state)

    spark(pen, crack_x + 40, 350, 55)
    spark(pen, crack_x - 30, 90, 40)
    return pen


POSTER = [(95, 100), (PW - 100, 100), (PW - 100, PH - 95), (95, PH - 95)]
NIGHT = (30, 36, 74)
NIGHT_DARK = (17, 20, 46)
BEAM = (250, 232, 150)
CHALK = (240, 240, 232)
METAL = (138, 144, 156)
METAL_LIGHT = (176, 182, 192)
METAL_DARK = (88, 92, 104)
LASER = (255, 40, 40)
LASER_GLOW = (255, 140, 140)
SACK = (156, 108, 62)


def clip(p0, p1, poly):
    """Part of segment p0-p1 inside a convex polygon, or None."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    t0, t1 = 0.0, 1.0
    for a, b in zip(poly, poly[1:] + poly[:1]):
        side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        s = 1 if side((cx, cy)) >= 0 else -1
        f0, f1 = s * side(p0), s * side(p1)
        if f0 < 0 and f1 < 0:
            return None
        if f0 < 0:
            t0 = max(t0, f0 / (f0 - f1))
        elif f1 < 0:
            t1 = min(t1, f0 / (f0 - f1))
    if t0 >= t1:
        return None
    at = lambda t: (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
    return at(t0), at(t1)


def hatch(pen, poly, color, deg, spacing, r, sloppy=8, inside=None):
    """Colour a convex shape in with parallel marker strokes that overshoot a bit."""
    pen.at(0, 0)
    a = math.radians(deg)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    reach = max(math.hypot(p[0] - cx, p[1] - cy) for p in poly) + 10
    off = -reach
    while off < reach:
        o = off + random.uniform(-spacing * .25, spacing * .25)
        seg = clip((cx + nx * o - dx * reach, cy + ny * o - dy * reach),
                   (cx + nx * o + dx * reach, cy + ny * o + dy * reach), poly)
        if seg:
            (x0, y0), (x1, y1) = seg
            e0, e1 = random.uniform(-sloppy, sloppy), random.uniform(-sloppy, sloppy)
            seg = ((x0 - dx * e0, y0 - dy * e0), (x1 + dx * e1, y1 + dy * e1))
            if inside:                                  # keep the scribble on the poster
                seg = clip(*seg, inside)
            if seg:
                pen.stroke(wobble_line(list(seg), 1.5), r, color)
        off += spacing


def night_sky(pen, border):
    """Fill the poster with dark blue, then scribble darker marker over it."""
    pen.at(0, 0)
    pen.fill(border, NIGHT)
    hatch(pen, [(72, 78), (PW - 78, 78), (PW - 78, PH - 72), (72, PH - 72)], NIGHT_DARK, -32, 17, 5, sloppy=2)
    for x, y in [(90, 120), (1300, 95), (75, 760), (1330, 700), (180, 880), (1250, 880), (100, 1560), (1320, 1500)]:
        for k in range(2):                                         # little hand-drawn stars
            a = math.radians(random.uniform(-10, 10) + 90 * k + 45 * (random.random() < .5))
            L = random.uniform(9, 14)
            pen.stroke([(x - math.cos(a) * L, y - math.sin(a) * L), (x + math.cos(a) * L, y + math.sin(a) * L)], 2.6, CHALK)


def searchlights(pen, target):
    tx, ty = target
    for ox, oy, spread in [(70, PH - 70, 260), (PW - 70, PH - 70, 260)]:
        ang = math.atan2(ty - oy, tx - ox)
        far = 1500
        nx, ny = -math.sin(ang), math.cos(ang)
        end = (ox + math.cos(ang) * far, oy + math.sin(ang) * far)
        cone = [(ox, oy), (end[0] + nx * spread, end[1] + ny * spread), (end[0] - nx * spread, end[1] - ny * spread)]
        hatch(pen, cone, BEAM, math.degrees(ang) + 2, 11, 3.2, sloppy=20, inside=POSTER)


def lasers(pen):
    pen.at(0, 0)
    for (x0, y0), (x1, y1) in [((62, 1180), (PW - 66, 1500)), ((62, 1530), (PW - 66, 1260)),
                               ((62, 1390), (PW - 66, 1610)), ((420, 66 + 1000), (PW - 66, 1080))]:
        line = wobble_line([(x0, y0), (x1, y1)], 2)
        pen.stroke(line, 7, LASER_GLOW)
        pen.stroke(line, 2.6, LASER)


def ring(cx, cy, r, n=16, j=6):
    pts = [(cx + r * math.cos(2 * math.pi * k / n) + random.uniform(-j, j),
            cy + r * math.sin(2 * math.pi * k / n) + random.uniform(-j, j)) for k in range(n)]
    return catmull(pts + pts[:3], 8)


def vault(pen, cx, cy, R):
    pen.at(0, 0)
    for hy in (cy - R * .5, cy + R * .35):              # hinges (behind the door)
        h = [(cx - R - 32, hy), (cx - R - 32, hy + 75), (cx - R + 20, hy + 75), (cx - R + 20, hy)]
        pen.fill(h, METAL_DARK)
        pen.stroke(wobble_line(h + h[:1], 2), 7)
    outer = ring(cx, cy, R)
    pen.fill(outer, METAL)
    # shading: darker crescent bottom right, shine top left
    hatch(pen, [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in range(-20, 120, 10)],
          METAL_DARK, 45, 13, 4, sloppy=3)
    inner = ring(cx, cy, R * .78)
    pen.fill(inner, METAL_LIGHT)
    pen.stroke(outer, PEN + 2)
    pen.stroke(inner, PEN - 2)
    for start in (200, 215):
        arc = [(cx + R * (.86 if start == 200 else .66) * math.cos(math.radians(a)),
                cy + R * (.86 if start == 200 else .66) * math.sin(math.radians(a))) for a in range(start, start + 45, 6)]
        pen.stroke(catmull(arc), 5, (255, 255, 255))
    for k in range(12):                                 # bolts
        a = 2 * math.pi * k / 12 + 0.1
        pen.blob(cx + R * .89 * math.cos(a), cy + R * .89 * math.sin(a), 11)
    for k in range(3):                                  # spinny handle
        a = math.radians(30 + 120 * k)
        end = (cx + R * .52 * math.cos(a), cy + R * .52 * math.sin(a))
        pen.stroke(wobble_line([(cx, cy), end], 3), PEN)
        pen.blob(*end, 20)
    pen.blob(cx, cy, 42)
    pen.blob(cx - 12, cy - 12, 9, METAL_LIGHT)
    dx, dy = cx + R * .42, cy - R * .42                 # dial with tick marks
    dial = ring(dx, dy, 48, n=10, j=2)
    pen.fill(dial, (225, 225, 220))
    pen.stroke(dial, 6)
    for k in range(8):
        a = 2 * math.pi * k / 8
        pen.stroke([(dx + 28 * math.cos(a), dy + 28 * math.sin(a)), (dx + 41 * math.cos(a), dy + 41 * math.sin(a))], 3)
    pen.stroke([(dx, dy), (dx + 20, dy - 18)], 4, RED)


def flying_cards(pen, cx, cy):
    """Cards bursting out of the vault, with motion lines behind them."""
    for (x, y, sc, deg, rank, suit, seed) in [(170, 900, .17, -30, 'K', 'hearts', 501), (300, 760, .15, 20, 'Q', 'spades', 502),
                                              (880, 790, .16, 35, 'J', 'diamonds', 503), (905, 1150, .17, -15, 'A', 'clubs', 504)]:
        a = math.atan2(y - cy, x - cx)
        mx, my = x + CARD_W * sc / 2, y + CARD_H * sc / 2
        pen.at(0, 0)
        for k in (-1, 0, 1):                            # speed lines
            px, py = -math.sin(a) * k * 35, math.cos(a) * k * 35
            L0, L1 = 90 + random.uniform(-10, 10), 170 + random.uniform(-25, 25)
            pen.stroke(wobble_line([(mx + px - math.cos(a) * L0, my + py - math.sin(a) * L0),
                                    (mx + px - math.cos(a) * L1, my + py - math.sin(a) * L1)], 2), 3.5, CHALK)
        pen.at(x, y, sc, deg)
        card(pen, rank, suit, seed=seed, paper=True)
        random.seed(seed + 1)


def thief(pen, x, y):
    """Chalky stick figure tiptoeing over the lasers with a loot sack and a card."""
    pen.at(0, 0)
    hip = (x + 15, y + 230)
    sack = ring(x - 60, y + 120, 70, n=12, j=8)       # loot sack over the shoulder
    pen.fill(sack, SACK)
    pen.stroke(sack, 7)
    pen.stroke(catmull([(x - 70, y + 50), (x - 50, y + 40), (x - 20, y + 55), (x - 45, y + 62)]), 7)
    pen.at(0, 0)
    from make_cards import suit_shape
    for sh in suit_shape('spades', x - 60, y + 125, 70):
        pen.fill(sh, CHALK)
    pen.stroke(wobble_line([(x + 3, y + 60), (x - 40, y + 55)], 2), PEN * .8, CHALK)          # hand on the sack

    head = ring(x, y, 52, n=12, j=3)
    pen.fill(head, CHALK)
    pen.stroke(head, 5)
    pen.fill([(x - 54, y - 18), (x + 54, y - 22), (x + 52, y + 6), (x - 52, y + 8)], INK)   # robber mask
    pen.blob(x - 20, y - 7, 8, 'white')
    pen.blob(x + 18, y - 9, 8, 'white')
    pen.stroke(wobble_line([(x + 52, y - 10), (x + 95, y - 30)], 3), 5, CHALK)                # mask strings
    pen.stroke(wobble_line([(x + 52, y - 4), (x + 90, y + 8)], 3), 5, CHALK)
    pen.stroke(catmull([(x - 15, y + 28), (x, y + 34), (x + 15, y + 27)]), 4)                  # sneaky grin
    pen.stroke(wobble_line([(x + 3, y + 55), hip], 4), PEN, CHALK)                           # body (leaning)
    pen.stroke(wobble_line([hip, (x - 55, y + 300), (x - 95, y + 360)], 4), PEN, CHALK)      # legs, mid tiptoe
    pen.stroke(wobble_line([hip, (x + 70, y + 310), (x + 60, y + 370), (x + 100, y + 372)], 4), PEN, CHALK)
    pen.stroke(wobble_line([(x + 8, y + 110), (x + 80, y + 70), (x + 105, y + 5)], 4), PEN, CHALK)  # arm holding a card up
    pen.at(x + 70, y - 110, 0.2, 10)
    card(pen, 'A', 'spades', seed=999, paper=True)
    random.seed(4242)


def scribble_credits(pen, y):
    """The tiny unreadable credit block at the bottom of every poster."""
    pen.at(0, 0)
    for row in range(3):
        x = 150 + random.uniform(-10, 10)
        while x < PW - 170:
            L = random.uniform(30, 110)
            pts = [(x + t, y + row * 32 + math.sin(t / 5 + x) * 5 + random.uniform(-1, 1)) for t in range(0, int(L), 4)]
            pen.stroke(pts, 2.6, (175, 180, 200))
            x += L + random.uniform(12, 26)


def outlined(pen, text, cx, y, h, r, color, seed):
    """Big poster lettering: drop shadow, fat white outline, then the colour."""
    for dx, dy, rr, c in [(9, 10, r + 7, INK), (0, 0, r + 7, CHALK), (0, 0, r, color)]:
        random.seed(seed)
        write(pen.at(0, 0), text, cx + dx, y + dy, h, r=rr, gap=0.3, color=c, center=True)


if __name__ == '__main__':
    random.seed(4242)
    pen = Pen(PW, PH)
    pen.at(0, 0)
    border = wobbly_box(42, 48, PW - 48, PH - 42, tilt=0, jit=4)
    random.seed(1)
    night_sky(pen, border)
    random.seed(2)
    searchlights(pen, (610, 700))
    random.seed(3)
    pen.at(0, 0)
    pen.stroke(border, PEN + 1)

    random.seed(4242)
    sign(pen)
    random.seed(77)
    for rr, c in [(11, INK), (6, CHALK)]:
        random.seed(77)
        write(pen.at(0, 0), '52 CARDS. 1 VAULT. NO PLAN.', PW / 2, 735, 52, r=rr, gap=0.22, color=c, center=True)

    random.seed(5)
    vault(pen, 610, 1110, 280)
    random.seed(10)
    flying_cards(pen, 610, 1110)
    random.seed(11)
    lasers(pen)
    random.seed(6)
    thief(pen, 1140, 1020)
    messy_stack(pen, 330, 1450, 0.3, 9, seed=31, wide=700, tall=250)
    pen.at(720, 1425, 0.26, 14)                         # the 7 of diamonds, the first card ever drawn
    card(pen, '7', 'diamonds', seed=206, paper=True)

    outlined(pen, 'COMING SOON', PW / 2, 1660, 120, PEN + 1, RED, seed=8)
    random.seed(9)
    scribble_credits(pen, 1845)

    pen.finish().save(os.path.join(OUT, 'poster.png'), optimize=True)
    print('done')
