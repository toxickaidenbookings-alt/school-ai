"""Movie poster: MISSION CARD VAULT, on a busted LED sign.

Drawn like the original 7 of diamonds sketch: white paper, one fat black marker,
shaky hand, and a few coloured markers to fill bits in. No shading.

Run: python3 make_poster.py   (writes poster.png)
"""
import math, os, random
import make_cards
from make_cards import Pen, card, catmull, wobble_line, wobbly_box, write, messy_stack, suit_shape, INK, RED, PEN, OUT, CARD_W, CARD_H

PW, PH = 1414, 2000

LED_ON = (255, 70, 30)
LED_DIM = (120, 45, 35)
DEAD = (200, 200, 200)
SPARK = (255, 200, 0)
YELLOW = (255, 214, 40)
LASER = (235, 30, 30)
POSTER = [(95, 100), (PW - 100, 100), (PW - 100, PH - 95), (95, PH - 95)]
BEAM_BOX = [(95, 100), (PW - 100, 100), (PW - 100, 1700), (95, 1700)]    # beams come up from behind the title

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
    """One bulb, coloured in with a marker dot, never quite the same size twice."""
    x += random.uniform(-.12, .12) * pitch
    y += random.uniform(-.12, .12) * pitch
    if state == 'on':
        pen.blob(x, y, pitch * random.uniform(.3, .44), LED_ON)
    elif state == 'dim':
        pen.blob(x, y, pitch * random.uniform(.25, .35), LED_DIM)
    else:                                               # dead bulb: a scratchy little circle
        ring = [(x + pitch * .27 * math.cos(2 * math.pi * k / 7) + random.uniform(-2, 2),
                 y + pitch * .27 * math.sin(2 * math.pi * k / 7) + random.uniform(-2, 2)) for k in range(8)]
        pen.stroke(catmull(ring, 4), 2.5, DEAD)


def spark(pen, x, y, size):
    for k in range(6):
        a = random.uniform(0, 2 * math.pi)
        L = size * random.uniform(0.5, 1)
        pen.stroke(wobble_line([(x + math.cos(a) * L * .25, y + math.sin(a) * L * .25),
                                (x + math.cos(a) * L, y + math.sin(a) * L)], 2), 5, YELLOW if k % 2 else INK)


def sign(pen):
    """The hanging LED sign. One wire snapped, so it hangs crooked."""
    sx, sy, deg = 110, 150, 3.5
    sw, sh = 1190, 420
    pen.at(0, 0)
    pen.stroke(wobble_line([(230, 52), (sx + 120, sy + 5)], 3), 7)
    pen.stroke(wobble_line([(1180, 52), (1170, 115)], 3), 7)                  # snapped stub at the top
    spark(pen, 1170, 125, 45)

    pen.at(sx, sy, 1, deg)
    box = wobbly_box(0, 0, sw, sh, tilt=12, jit=5)
    # coloured in like the diamond on the sketch: solid black, a bit uneven
    pen.fill(box, INK)
    y = 25
    while y < sh - 20:                                  # scribble marks that show the colouring direction
        pen.stroke([(40 + random.uniform(-15, 15), y), (sw - 40 + random.uniform(-15, 15), y + random.uniform(-6, 10))], 3, (45, 45, 45))
        y += random.uniform(30, 55)
    pen.stroke(box, PEN + 3)
    pen.stroke(wobble_line([(sw - 125, -2), (sw - 118, -40)], 3), 7)          # other half of the wire

    crack_x = sw - 330
    crack = [(crack_x, -5), (crack_x - 30, 90), (crack_x + 25, 170), (crack_x - 15, 260), (crack_x + 40, 350), (crack_x + 5, sh + 5)]
    pen.stroke(wobble_line(crack, 4), 5, (240, 240, 240))

    lines = [('MISSION', 27, 36), ('CARD VAULT', 19.5, 250)]
    for text, pitch, top in lines:
        bulbs, cols = led_bulbs(text, pitch)
        left = (sw - cols * pitch) / 2 + pitch / 2
        for col, row, li in bulbs:
            x, y = left + col * pitch, top + row * pitch
            r = random.random()
            if (text, li) == ('MISSION', 5):            # the O is on its last legs
                state = 'dim' if r < .6 else 'dead'
            elif x > crack_x + 20:
                state = 'dead' if r < .45 else 'dim' if r < .6 else 'on'
            else:
                state = 'dead' if r < .07 else 'on'
            bulb(pen, x, y, pitch, state)
    spark(pen, crack_x + 40, 350, 60)
    spark(pen, crack_x - 30, 90, 45)


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


def colour_in(pen, poly, color, deg, spacing, r):
    """Back-and-forth zigzag scribble, like colouring with a marker in a hurry."""
    pen.at(0, 0)
    a = math.radians(deg)
    dx, dy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    reach = max(math.hypot(p[0] - cx, p[1] - cy) for p in poly) + 10
    zig, off, flip = [], -reach, False
    while off < reach:
        seg = clip((cx + nx * off - dx * reach, cy + ny * off - dy * reach),
                   (cx + nx * off + dx * reach, cy + ny * off + dy * reach), poly)
        if seg:
            seg = [(p[0] + random.uniform(-12, 12), p[1] + random.uniform(-12, 12)) for p in seg]
            zig += seg[::-1] if flip else seg
            flip = not flip
        elif zig:
            pen.stroke(zig, r, color); zig = []
        off += spacing * random.uniform(.7, 1.3)
    if zig:
        pen.stroke(zig, r, color)


def searchlights(pen, target):
    """Two beams: a black outline each, quickly coloured in yellow."""
    tx, ty = target
    for ox, oy in [(40, PH - 40), (PW - 40, PH - 40)]:   # lights sit just off the bottom corners
        ang = math.atan2(ty - oy, tx - ox)
        far = math.hypot(tx - ox, ty - oy)              # beams stop on the vault
        nx, ny = -math.sin(ang), math.cos(ang)
        end = (ox + math.cos(ang) * far, oy + math.sin(ang) * far)
        left = clip((ox, oy), (end[0] + nx * 170, end[1] + ny * 170), BEAM_BOX)
        right = clip((ox, oy), (end[0] - nx * 170, end[1] - ny * 170), BEAM_BOX)
        colour_in(pen, [left[0], left[1], right[1], right[0]], YELLOW, math.degrees(ang) + 90, 34, 6)
        for side in (left, right):
            pen.stroke(wobble_line(list(side), 4), 6)


def lasers(pen):
    pen.at(0, 0)
    for (x0, y0), (x1, y1) in [((75, 1300), (PW - 80, 1470)), ((75, 1480), (PW - 80, 1310))]:   # an X across the floor
        pen.stroke(wobble_line([(x0, y0), (x1, y1)], 3), 5, LASER)
        for x, y in ((x0, y0), (x1, y1)):                                                      # little emitters on the walls
            pen.blob(x, y, 11, LASER)


def ring(cx, cy, r, n=16, j=6):
    pts = [(cx + r * math.cos(2 * math.pi * k / n) + random.uniform(-j, j) * make_cards.SHAKE,
            cy + r * math.sin(2 * math.pi * k / n) + random.uniform(-j, j) * make_cards.SHAKE) for k in range(n)]
    return catmull(pts + pts[:3], 8)


def vault(pen, cx, cy, R):
    pen.at(0, 0)
    for hy in (cy - R * .5, cy + R * .35):              # hinges
        h = [(cx - R - 38, hy), (cx - R - 38, hy + 70), (cx - R + 20, hy + 70), (cx - R + 20, hy)]
        pen.fill(h, 'white')
        pen.stroke(wobble_line(h + h[:1], 2), 8)
    outer = ring(cx, cy, R, j=3)
    pen.fill(outer, 'white')                            # covers the searchlight scribble behind it
    pen.stroke(outer, PEN + 3)
    pen.stroke(ring(cx, cy, R * .78, j=3), PEN)
    for k in range(10):                                 # bolts
        a = 2 * math.pi * k / 10 + 0.1
        pen.blob(cx + R * .89 * math.cos(a), cy + R * .89 * math.sin(a), 12)
    for k in range(3):                                  # spinny handle
        a = math.radians(30 + 120 * k + random.uniform(-6, 6))
        end = (cx + R * .52 * math.cos(a), cy + R * .52 * math.sin(a))
        pen.stroke(wobble_line([(cx, cy), end], 3), PEN + 2)
        pen.blob(*end, 24)
    pen.blob(cx, cy, 45)
    dx, dy = cx + R * .42, cy - R * .42                 # dial
    pen.stroke(ring(dx, dy, 48, n=9, j=1.2), 8)
    pen.stroke(wobble_line([(dx, dy), (dx + 22, dy - 20)], 2), 6, RED)


def flying_cards(pen, cx, cy):
    """Cards bursting out of the vault, with scribbly speed lines."""
    for (x, y, sc, deg, rank, suit, seed) in [(150, 960, .17, -30, 'K', 'hearts', 501), (250, 830, .15, 20, 'Q', 'spades', 502),
                                              (905, 860, .16, 35, 'J', 'diamonds', 503), (905, 1150, .17, -15, 'A', 'clubs', 504)]:
        a = math.atan2(y - cy, x - cx)
        mx, my = x + CARD_W * sc / 2, y + CARD_H * sc / 2
        pen.at(0, 0)
        for k in (-1, 1):
            px, py = -math.sin(a) * k * 30, math.cos(a) * k * 30
            L0, L1 = 85 + random.uniform(-10, 10), 150 + random.uniform(-25, 25)
            pen.stroke(wobble_line([(mx + px - math.cos(a) * L0, my + py - math.sin(a) * L0),
                                    (mx + px - math.cos(a) * L1, my + py - math.sin(a) * L1)], 3), 5)
        pen.at(x, y, sc, deg)
        card(pen, rank, suit, seed=seed, paper=True)
        random.seed(seed + 1)


def thief(pen, x, y):
    """Stick figure tiptoeing over the lasers with a loot sack and a card."""
    pen.at(0, 0)
    hip = (x + 15, y + 230)
    sack = ring(x - 95, y + 95, 58, n=10, j=5)        # slung over his back
    pen.fill(sack, 'white')
    pen.stroke(sack, PEN)
    pen.stroke(wobble_line([(x - 115, y + 38), (x - 70, y + 36)], 3), PEN)                 # tied-up top
    for sh in suit_shape('spades', x - 95, y + 100, 62):
        pen.fill(sh, INK)
    head = ring(x, y, 52, n=10, j=4)
    pen.fill(head, 'white')
    pen.stroke(head, PEN)
    pen.fill([(x - 54, y - 18), (x + 54, y - 24), (x + 52, y + 6), (x - 52, y + 10)], INK)   # robber mask
    pen.blob(x - 20, y - 7, 9, 'white')
    pen.blob(x + 18, y - 9, 9, 'white')
    pen.stroke(catmull([(x - 15, y + 26), (x, y + 33), (x + 17, y + 24)]), 5)                # grin
    pen.stroke(wobble_line([(x + 3, y + 55), hip], 4), PEN)
    pen.stroke(wobble_line([hip, (x - 55, y + 300), (x - 95, y + 360)], 4), PEN)
    pen.stroke(wobble_line([hip, (x + 70, y + 310), (x + 60, y + 370), (x + 100, y + 372)], 4), PEN)
    pen.stroke(wobble_line([(x + 3, y + 95), (x - 45, y + 60), (x - 75, y + 40)], 3), PEN)  # hand holding the sack
    pen.stroke(wobble_line([(x + 8, y + 110), (x + 80, y + 70), (x + 105, y + 5)], 4), PEN)
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
            pts = [(x + t, y + row * 34 + math.sin(t / 5 + x) * 6 + random.uniform(-2, 2)) for t in range(0, int(L), 4)]
            pen.stroke(pts, 3.5, INK)
            x += L + random.uniform(12, 26)


if __name__ == '__main__':
    make_cards.SHAKE = 2.0          # shakier hand than the cards
    make_cards.LINE_KEEP = 0.55     # small cards still get a fat marker
    random.seed(4242)
    pen = Pen(PW, PH)
    random.seed(2)
    searchlights(pen, (610, 1080))       # beams end hidden behind the vault
    random.seed(3)
    pen.at(0, 0)
    pen.stroke(wobbly_box(42, 48, PW - 48, PH - 42, tilt=0, jit=4), PEN + 2)

    random.seed(4242)
    sign(pen)
    random.seed(77)
    make_cards.SHAKE = 1.1                              # steadier hand so the words stay readable
    write(pen.at(0, 0), "SOME CARDS AREN'T", PW / 2, 672, 44, r=6.5, gap=0.24, center=True)
    write(pen.at(0, 0), 'MEANT TO BE PLAYED.', PW / 2, 742, 44, r=6.5, gap=0.24, center=True)
    make_cards.SHAKE = 2.0

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

    random.seed(8)
    write(pen.at(0, 0), 'COMING SOON', PW / 2, 1660, 120, r=PEN + 3, gap=0.3, color=RED, center=True)
    random.seed(9)
    scribble_credits(pen, 1845)

    pen.finish().save(os.path.join(OUT, 'poster.png'), optimize=True)
    print('done')
