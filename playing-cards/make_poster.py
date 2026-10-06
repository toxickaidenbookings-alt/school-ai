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
    pen.stroke(wobble_line([(230, 52), (sx + 120, sy + 5)], 3), 5)
    pen.stroke(wobble_line([(1180, 52), (1165, 110)], 3), 5)                  # snapped stub at the top
    pen.stroke(catmull([(1165, 110), (1185, 125), (1170, 140)]), 5)
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
    pen.stroke(wobble_line([(sw - 125, -2), (sw - 115, -45)], 3), 5)         # other half of the snapped wire
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


def vault(pen, cx, cy, R):
    pen.at(0, 0)
    ring = lambda r, n=16, j=6: catmull([(cx + r * math.cos(2 * math.pi * k / n) + random.uniform(-j, j),
                                          cy + r * math.sin(2 * math.pi * k / n) + random.uniform(-j, j))
                                         for k in range(n)], 8)
    outer = ring(R)
    pen.stroke(outer + outer[:2], PEN + 2)
    inner = ring(R * .78)
    pen.stroke(inner + inner[:2], PEN - 2)
    for k in range(12):                                 # bolts
        a = 2 * math.pi * k / 12 + 0.1
        pen.blob(cx + R * .89 * math.cos(a), cy + R * .89 * math.sin(a), 11)
    for hy in (cy - R * .5, cy + R * .35):              # hinges
        pen.stroke(wobble_line([(cx - R - 28, hy), (cx - R - 28, hy + 70), (cx - R + 8, hy + 70), (cx - R + 8, hy), (cx - R - 28, hy)], 2), 8)
    for k in range(3):                                  # spinny handle
        a = math.radians(30 + 120 * k)
        end = (cx + R * .52 * math.cos(a), cy + R * .52 * math.sin(a))
        pen.stroke(wobble_line([(cx, cy), end], 3), PEN)
        pen.blob(*end, 20)
    pen.blob(cx, cy, 42)
    # dial with tick marks, top right
    dx, dy = cx + R * .42, cy - R * .42
    dial = catmull([(dx + 48 * math.cos(2 * math.pi * k / 10), dy + 48 * math.sin(2 * math.pi * k / 10)) for k in range(11)], 5)
    pen.stroke(dial, 6)
    for k in range(8):
        a = 2 * math.pi * k / 8
        pen.stroke([(dx + 30 * math.cos(a), dy + 30 * math.sin(a)), (dx + 42 * math.cos(a), dy + 42 * math.sin(a))], 3)


def thief(pen, x, y):
    """Stick figure sneaking up on the vault with a card."""
    pen.at(0, 0)
    head = catmull([(x + 52 * math.cos(2 * math.pi * k / 12) + random.uniform(-3, 3),
                     y + 55 * math.sin(2 * math.pi * k / 12) + random.uniform(-3, 3)) for k in range(13)], 6)
    pen.stroke(head, PEN)
    pen.fill([(x - 54, y - 18), (x + 54, y - 22), (x + 52, y + 6), (x - 52, y + 8)], INK)   # robber mask
    pen.blob(x - 20, y - 7, 8, 'white')
    pen.blob(x + 18, y - 9, 8, 'white')
    pen.stroke(wobble_line([(x + 52, y - 10), (x + 95, y - 30)], 3), 6)                       # mask strings
    pen.stroke(wobble_line([(x + 52, y - 4), (x + 90, y + 8)], 3), 6)
    hip = (x + 15, y + 230)
    pen.stroke(wobble_line([(x + 3, y + 55), hip], 4), PEN)                                  # body (leaning)
    pen.stroke(wobble_line([hip, (x - 55, y + 300), (x - 95, y + 360)], 4), PEN)             # legs, mid tiptoe
    pen.stroke(wobble_line([hip, (x + 70, y + 310), (x + 60, y + 370), (x + 100, y + 372)], 4), PEN)
    pen.stroke(wobble_line([(x + 6, y + 110), (x - 80, y + 150), (x - 140, y + 120)], 4), PEN)   # arm reaching
    pen.stroke(wobble_line([(x + 8, y + 110), (x + 80, y + 70), (x + 105, y + 5)], 4), PEN)      # arm holding a card up
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
            pen.stroke(pts, 2.6, INK)
            x += L + random.uniform(12, 26)


if __name__ == '__main__':
    random.seed(4242)
    pen = Pen(PW, PH)
    pen.at(0, 0)
    border = wobbly_box(42, 48, PW - 48, PH - 42, tilt=0, jit=4)
    pen.stroke(border, PEN + 1)

    sign(pen)
    pen.at(0, 0)
    random.seed(77)
    write(pen, '52 CARDS. 1 VAULT. NO PLAN.', PW / 2, 735, 52, r=6, gap=0.22, center=True)

    random.seed(5)
    vault(pen, 610, 1110, 280)
    random.seed(6)
    thief(pen, 1140, 1020)
    messy_stack(pen, 330, 1450, 0.3, 9, seed=31, wide=700, tall=250)
    # a 7 of diamonds flying off (the first card ever drawn)
    pen.at(720, 1425, 0.26, 14)
    card(pen, '7', 'diamonds', seed=206, paper=True)

    random.seed(8)
    pen.at(0, 0)
    write(pen, 'COMING SOON', PW / 2, 1660, 120, r=PEN + 1, gap=0.3, color=RED, center=True)
    random.seed(9)
    scribble_credits(pen, 1845)

    pen.finish().save(os.path.join(OUT, 'poster.png'), optimize=True)
    print('done')
