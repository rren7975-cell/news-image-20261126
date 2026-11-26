#!/usr/bin/env python3
"""Render the 26 November 2026 front page (1024x1024).

Fifty stories that happened, or were first reported, on Thursday
26 November 2026 in any time zone, across nine regions, with thirty-one
drawn pictures (a lead scene plus thirty pictograms), a UTC timeline of
the day's verified times, and attribution on contested claims. Heroes:
the Macy's centenary parade postponed by the Thanksgiving storm (the
first weather postponement in its hundred-year history), the storm
itself, and the Cairo tanker fire that killed thirty-one people.
25 November items (Shenzhou-24, the Hormuz tankers, the Huawei verdict,
the Nvidia selloff) stay out; the Samara refineries appear only as a
continuing 26 November development, fires still burning. Every story
was re-checked against 26 November reporting.

The page is drawn with PIL only (no network, deterministic): masthead,
date, three leads with a drawn lead illustration, thirty briefs and a
seventeen-item "Also on 26 November" strip, then a UTC timeline and
sources. Stories live in data tables at the bottom of this file; the
renderer above them is generic.

Run: python3 render.py  -> writes entry.png next to this file.
"""
import math

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
EDGE = 36
BODY_W = PAGE - 2 * EDGE  # 952

COLORS = {
    "paper": (247, 242, 232),
    "ink": (20, 20, 20),
    "grey": (85, 85, 85),
    "dim": (60, 60, 60),
    "red": (179, 38, 30),
    "blue": (31, 78, 121),
    "green": (46, 125, 50),
    "sea": (46, 98, 130),
    "sea_dark": (28, 68, 96),
    "orange": (214, 110, 30),
    "gold": (212, 160, 40),
    "white": (255, 255, 255),
    "sky": (196, 205, 214),
    "cloud": (110, 118, 128),
    "cloud_dark": (90, 98, 108),
    "rain": (110, 132, 155),
    "street": (150, 148, 140),
    "brick": (120, 96, 78),
    "slate": (96, 110, 128),
    "lit": (232, 220, 180),
}

FONTS = {
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "serif_b": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


def load_font(kind, size):
    return ImageFont.truetype(FONTS[kind], size)


def measure(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def flow_text(draw, text, fnt, width):
    """Greedy word wrap to a pixel width; returns the lines."""
    out, current = [], ""
    for word in text.split(" "):
        joined = (current + " " + word).strip()
        if measure(draw, joined, fnt) <= width or current == "":
            current = joined
        else:
            out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def paint_lines(draw, lines, fnt, x, y, leading, fill=None):
    fill = fill if fill is not None else COLORS["ink"]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def chip(draw, x, y, label, bg, size=13):
    """A small coloured label chip; returns its width."""
    fnt = load_font("sans_b", size)
    tw = measure(draw, label, fnt)
    h = size + 7
    draw.rounded_rectangle([x, y, x + tw + 12, y + h], radius=3, fill=bg)
    draw.text((x + 6, y + 3), label, font=fnt, fill=COLORS["white"])
    return tw + 12


def hline(draw, y, weight=2, x0=None, x1=None):
    x0 = EDGE if x0 is None else x0
    x1 = PAGE - EDGE if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=COLORS["ink"], width=weight)
    return y + weight


# ---- pictograms: each icon is a list of shapes drawn in a 22x22 box ----
# A shape is (kind, box_or_points, colour) where kind is one of
# "ellipse", "rect", "line", "poly". Colours are keys of COLORS.
ICON_SHAPES = {
    "leaf": [("ellipse", (2, 4, 18, 18), "green"),
             ("line", (11, 20, 16, 6), "white")],
    "chip": [("rect", (5, 5, 17, 17), "ink"),
             ("rect", (9, 9, 13, 13), "gold"),
             ("line", (8, 2, 8, 5), "ink"), ("line", (11, 2, 11, 5), "ink"),
             ("line", (14, 2, 14, 5), "ink"), ("line", (8, 17, 8, 20), "ink"),
             ("line", (11, 17, 11, 20), "ink"), ("line", (14, 17, 14, 20), "ink")],
    "chart": [("line", (3, 19, 19, 19), "ink"), ("line", (3, 3, 3, 19), "ink"),
              ("rect", (6, 13, 9, 19), "blue"), ("rect", (11, 8, 14, 19), "blue"),
              ("rect", (16, 3, 19, 19), "blue")],
    "rocket": [("poly", ((11, 1), (16, 9), (6, 9)), "red"),
               ("rect", (7, 9, 15, 17), "blue"),
               ("poly", ((11, 17), (14, 21), (8, 21)), "orange"),
               ("ellipse", (9, 11, 13, 15), "white")],
    "star": [("poly", ((11, 1), (13, 8), (21, 8), (15, 13), (17, 21), (11, 16),
                      (5, 21), (7, 13), (1, 8), (9, 8)), "gold")],
    "flame": [("poly", ((11, 1), (16, 8), (19, 13), (15, 20), (7, 20), (3, 13),
                      (6, 8)), "orange"),
              ("poly", ((11, 10), (14, 14), (12, 18), (9, 18), (8, 14)), "red")],
    "scales": [("line", (11, 2, 11, 18), "ink"), ("line", (3, 5, 19, 5), "ink"),
               ("poly", ((2, 6), (8, 6), (5, 12)), "blue"),
               ("poly", ((14, 6), (20, 6), (17, 12)), "blue"),
               ("rect", (8, 18, 14, 21), "ink")],
    "sun": [("ellipse", (6, 6, 16, 16), "gold"),
            ("line", (11, 1, 11, 4), "gold"), ("line", (11, 18, 11, 21), "gold"),
            ("line", (1, 11, 4, 11), "gold"), ("line", (18, 11, 21, 11), "gold")],
    "alert": [("poly", ((11, 1), (21, 20), (1, 20)), "red"),
              ("line", (11, 7, 11, 14), "white"),
              ("ellipse", (10, 16, 12, 18), "white")],
    "burst": [("poly", tuple(
        (11 + (10 if i % 2 == 0 else 4) * math.cos(math.pi * i / 8 - math.pi / 2),
         11 + (10 if i % 2 == 0 else 4) * math.sin(math.pi * i / 8 - math.pi / 2))
        for i in range(16)), "orange"),
              ("ellipse", (8, 8, 14, 14), "red")],
    "shield": [("poly", ((3, 3), (19, 3), (19, 11), (11, 21), (3, 11)), "blue"),
               ("line", (7, 11, 10, 14), "white"),
               ("line", (10, 14, 15, 7), "white")],
    "arrow": [("line", (11, 20, 11, 5), "green"),
              ("poly", ((11, 1), (17, 8), (5, 8)), "green")],
    "flag": [("line", (5, 2, 5, 20), "ink"),
             ("poly", ((5, 2), (20, 6), (5, 11)), "red")],
    "globe": [("ellipse", (2, 2, 20, 20), "sea"),
              ("ellipse", (5, 5, 11, 10), "green"),
              ("ellipse", (12, 12, 18, 17), "green")],
    "coin": [("ellipse", (3, 3, 19, 19), "gold")],
    "ship": [("poly", ((2, 12), (20, 12), (17, 19), (5, 19)), "ink"),
             ("rect", (8, 5, 14, 12), "blue"),
             ("line", (11, 2, 11, 5), "ink")],
    "balloon": [("ellipse", (4, 1, 18, 14), "red"),
                ("ellipse", (8, 4, 12, 8), "white"),
                ("line", (11, 14, 11, 18), "ink"),
                ("rect", (8, 18, 14, 21), "gold")],
    "heart": [("poly", ((11, 20), (2, 11), (2, 6), (6, 2), (11, 6), (16, 2),
                      (20, 6), (20, 11)), "red")],
    "rain": [("ellipse", (2, 2, 12, 10), "grey"),
             ("ellipse", (9, 1, 20, 10), "cloud"),
             ("line", (5, 12, 5, 16), "blue"), ("line", (11, 12, 11, 16), "blue"),
             ("line", (17, 12, 17, 16), "blue"),
             ("poly", ((11, 17), (17, 21), (5, 21)), "green")],
    "book": [("rect", (3, 3, 19, 19), "blue"),
             ("line", (11, 3, 11, 19), "white"),
             ("line", (5, 7, 9, 7), "white"), ("line", (13, 7, 17, 7), "white"),
             ("line", (5, 11, 9, 11), "white"), ("line", (13, 11, 17, 11), "white"),
             ("line", (5, 15, 9, 15), "white"), ("line", (13, 15, 17, 15), "white")],
    "ball": [("ellipse", (2, 2, 20, 20), "white"),
             ("poly", ((11, 7), (15, 11), (13, 16), (9, 16), (7, 11)), "ink"),
             ("line", (11, 7, 11, 3), "ink"), ("line", (15, 11, 19, 9), "ink"),
             ("line", (7, 11, 3, 9), "ink")],
}


def draw_icon(draw, name, x, y):
    """Draw one pictogram in a 22x22 box at (x, y)."""
    for kind, geom, colour in ICON_SHAPES[name]:
        fill = COLORS[colour]
        if kind == "ellipse":
            draw.ellipse([x + geom[0], y + geom[1], x + geom[2], y + geom[3]],
                         fill=fill)
        elif kind == "rect":
            draw.rectangle([x + geom[0], y + geom[1], x + geom[2], y + geom[3]],
                           fill=fill)
        elif kind == "line":
            draw.line([(x + geom[0], y + geom[1]), (x + geom[2], y + geom[3])],
                      fill=fill, width=2)
        elif kind == "poly":
            draw.polygon([(x + px, y + py) for px, py in geom], fill=fill)
    if name == "coin":
        draw.ellipse([x + 3, y + 3, x + 19, y + 19], outline=COLORS["ink"], width=1)
        draw.text((x + 8, y + 5), "$", font=load_font("sans_b", 12),
                  fill=COLORS["ink"])
    if name == "ball":
        draw.ellipse([x + 2, y + 2, x + 20, y + 20], outline=COLORS["ink"], width=2)
    if name == "globe":
        draw.ellipse([x + 2, y + 2, x + 20, y + 20], outline=COLORS["ink"], width=1)


def parade_scene(draw, x, y, w, h):
    """Lead illustration: the Macy's parade grounded by the Thanksgiving
    storm - a big balloon held low between buildings under rain clouds.
    Every offset is a fraction of the scene height, so nothing pokes
    above the scene's top edge at any height."""
    draw.rectangle([x, y, x + w, y + h], fill=COLORS["sky"])
    # rain clouds along the top, inside the scene
    ch = max(4, int(h * 0.30))
    for cx0 in (x + 10, x + w // 3, x + 2 * w // 3):
        draw.ellipse([cx0, y + 2, cx0 + 150, y + 2 + ch], fill=COLORS["cloud"])
        draw.ellipse([cx0 + 50, y, cx0 + 190, y + ch], fill=COLORS["cloud_dark"])
    # rain streaks, denser and longer
    for rx in range(x + 14, x + w - 8, 24):
        draw.line([(rx, y + int(h * 0.32)), (rx - 5, y + int(h * 0.60))],
                  fill=COLORS["rain"], width=2)
    # street level
    street_y = y + int(h * 0.74)
    draw.rectangle([x, street_y, x + w, y + h], fill=COLORS["street"])
    # buildings left and right, tops inside the scene
    bh = max(6, int(h * 0.52))
    draw.rectangle([x + 6, street_y - bh, x + 150, street_y], fill=COLORS["brick"])
    draw.rectangle([x + w - 150, street_y - bh, x + w - 6, street_y],
                   fill=COLORS["slate"])
    for wx in (x + 26, x + 66, x + 106, x + 126):
        draw.rectangle([wx, street_y - bh + 6, wx + 12, street_y - bh + 16],
                       fill=COLORS["lit"])
    for wx in (x + w - 130, x + w - 90, x + w - 50, x + w - 30):
        draw.rectangle([wx, street_y - bh + 6, wx + 12, street_y - bh + 16],
                       fill=COLORS["lit"])
    # big parade balloon, held low between the buildings
    bx = x + w // 2
    br = max(6, int(h * 0.34))
    by = street_y - br - 2
    draw.ellipse([bx - br - 22, by - br, bx + br + 22, by + br], fill=COLORS["red"])
    draw.ellipse([bx - br // 2, by - br // 2, bx - br // 6, by - br // 6],
                 fill=COLORS["white"])
    # balloon strings down to the street
    draw.line([(bx - 24, by + br), (bx - 34, street_y)], fill=COLORS["ink"], width=2)
    draw.line([(bx + 24, by + br), (bx + 34, street_y)], fill=COLORS["ink"], width=2)
    # small crowd dots on the street
    for px in range(bx - 110, bx + 111, 26):
        draw.ellipse([px, street_y + 3, px + 7, street_y + 10], fill=COLORS["ink"])


# ---- the day's stories: (region, colour, headline, dek, icon) ----
LEAD_ONE = ("LEAD · PARADE", "red", "NEW YORK",
            "Macy's 100th parade postponed by storm",
            "Officials move the centenary parade to Saturday 28 November — the "
            "first weather postponement in its 100-year history.")

LEAD_TWO = ("LEAD · STORM", "red",
            "Thanksgiving storms hit both US coasts",
            "250m people in the path; East Coast storm and king tides flood the "
            "Carolinas to New Jersey; snow falls Missouri to Indiana.")

LEAD_THREE = ("LEAD · DISASTER", "blue",
              "Cairo tanker fire kills 31, injures 21",
              "A fuel tanker overturns on the Ring Road in Giza and bursts into "
              "flames, engulfing 27 vehicles; the toll is preliminary.")

BRIEFS = [
    ("TRADE", "blue", "US proposes tariffs on 14 economies",
     "USTR cites excess capacity; China faces +20%, Vietnam up to 35%.", "chart"),
    ("USA", "blue", "US growth 4.3%, fastest in 3 years",
     "Q3 GDP revised up; October PCE inflation 3.8%, core 3.3%.", "coin"),
    ("USA", "blue", "States sue Musk firms over Grok images",
     "Attorneys general target sexualised AI images of real people.", "scales"),
    ("USA", "blue", "Vance defends Nvidia chief Huang",
     "Vice-president backs the CEO as Washington scrutiny grows.", "chip"),
    ("USA", "blue", "Thanksgiving food costs jump 11%",
     "Holiday dinner is dearer as grocery prices climb.", "coin"),
    ("USA", "blue", "Travellers face long airport lines",
     "Bad weather looms over the Thanksgiving getaway.", "arrow"),
    ("AMERICAS", "red", "Colombia frees ~20 hostages in raid",
     "Police storm a supermarket after a 17-hour siege.", "shield"),
    ("AMERICAS", "red", "Record ~2,000 migrants reach Canaries",
     "A single-day record arrival on Spain's Canary Islands.", "ship"),
    ("AMERICAS", "red", "Venezuela reveals $237.5bn public debt",
     "Government prepares a historic economic restructuring.", "chart"),
    ("AMERICAS", "red", "Petrobras unveils $122bn investment",
     "Brazil's oil giant sets out a five-year strategy.", "coin"),
    ("AMERICAS", "red", "Colombia marks 10 years of peace deal",
     "UN warns of unfinished commitments from the accord.", "flag"),
    ("UK", "red", "Terror monitor blames Sally Rooney",
     "Watchdog links the novelist to a censorship row.", "book"),
    ("MIDEAST", "red", "Daesh attack kills 2 in Hasaka",
     "Syrian security personnel die; five are wounded.", "alert"),
    ("MIDEAST", "red", "Houthis strike Saudi ports",
     "Projectile hits Jazan Port; drones downed near Jeddah.", "burst"),
    ("MIDEAST", "red", "Judges may drop Netanyahu bribery case",
     "Court signals the most serious charges could go.", "scales"),
    ("MIDEAST", "red", "Egypt Suez Canal revenues recovering",
     "Canal income climbs back after the Red Sea disruption.", "ship"),
    ("AFRICA", "green", "Ethiopia backs healthcare independence",
     "Addis Ababa champions home-grown health capacity.", "heart"),
    ("AFRICA", "green", "Tinubu promises peace in northeast",
     "Nigeria's president vows calm in the rebellion-hit region.", "flag"),
    ("AFRICA", "green", "Sudan turns down Ethiopia talks offer",
     "Khartoum calls for neutrality instead of mediation.", "flag"),
    ("AFRICA", "green", "Iraq PM orders troops to oil routes",
     "Deployment aims to close oil-smuggling corridors.", "shield"),
    ("S ASIA", "green", "India marks Constitution Day",
     "New Delhi calls for human control over AI weapons.", "scales"),
    ("S ASIA", "green", "Bangladesh garment staff win 36% rise",
     "Workers secure a big pay increase after talks.", "arrow"),
    ("S ASIA", "green", "Flipkart chief to step down in Dec",
     "Kalyan Krishnamurthy leaves; IPL auction draws 1,220.", "chart"),
    ("PACIFIC", "blue", "Australia–Solomons pact signed",
     "Security deal seen as a check on China's reach.", "ship"),
    ("E ASIA", "blue", "China–Cambodia joint drills held",
     "The two militaries train together, AFP reports.", "shield"),
    ("E ASIA", "blue", "N. Korea expels Swiss office head",
     "Envoy gets 48 hours to leave over sanctions row.", "alert"),
    ("E ASIA", "blue", "Kuala Lumpur sues Google for $146m",
     "Malaysia claims damages over harmful content.", "scales"),
    ("EUROPE", "green", "EU leaders meet on €1.58tn budget",
     "Brussels summit covers the 2028–34 budget and Ukraine.", "globe"),
    ("EUROPE", "green", "Court faults Poland, Latvia pushbacks",
     "European court rules the migrant returns unlawful.", "scales"),
    ("SPORT", "green", "Gukesh faces Sindarov in Game 3",
     "World Chess Championship duel continues in Geneva.", "star"),
]

ALSO = ("Mumbai marks 18 years since the 26/11 attacks · Arsenal host "
        "Borussia Dortmund in the Champions League · Samara refineries "
        "still ablaze after overnight drone strikes · Trump: Iran war "
        "funded through January · Sheikh Hasina seeks return to "
        "Bangladesh on 16 Dec · IPL 2027 auction draws 1,220 players · "
        "Vietnam advances sustainable agriculture · South Korea prepares "
        "to reinforce its EV industry · France seeks independence in "
        "critical-mineral supplies · Britain investigates legacy of "
        "nuclear weapons testing · Russia increases defence allocations · "
        "Ukraine and Hungary pursue renewed economic cooperation · Serbia "
        "aims to curb trash TV and move to a 4-day week · El Salvador "
        "allocates $860m debt financing for year-end spending · European "
        "Parliament socialists and liberals suspend talks with EPP · "
        "Pope Leo calls COP31 failure 'troubling' · NATO envoy visits Cairo")

TIMELINE = ("00:11 Houthi strike hits Jazan Port  ·  00:21 Daesh attack in "
           "Hasaka  ·  02:14 Cairo toll put at 31 dead  ·  02:46 European "
           "court rules on pushbacks  ·  09:00 EU summit opens in Brussels")

FOOTNOTE = ("Sources: Reuters · AP · AFP · Gulf News · Arab News · "
            "Manila Times · Indian Express — Contested claims are labelled "
            "with their source in the text (AFP reports · local sources).")


def render_page():
    img = Image.new("RGB", (PAGE, PAGE), COLORS["paper"])
    d = ImageDraw.Draw(img)
    y = 12

    # masthead
    d.text((EDGE, y), "T H E   W O R L D   I N   O N E   D A Y",
           font=load_font("serif_b", 22), fill=COLORS["red"])
    no = "No. 26 · 2026"
    no_f = load_font("sans_b", 13)
    d.text((PAGE - EDGE - measure(d, no, no_f), y + 5), no, font=no_f,
           fill=COLORS["grey"])
    y += 30
    y = hline(d, y, 3)
    y += 6

    # date line
    d.text((EDGE, y), "Thursday 26 November 2026",
           font=load_font("serif_b", 46), fill=COLORS["ink"])
    y += 50
    y = hline(d, y, 1)
    y += 5
    d.text((EDGE, y),
           "The day's world news in one picture  ·  50 stories  ·  9 regions  ·  "
           "31 drawn  ·  claims labelled  ·  UTC timeline",
           font=load_font("sans", 14), fill=COLORS["grey"])
    y += 20
    y = hline(d, y, 1)
    y += 8

    # ---- lead 1, with the drawn scene ----
    tg, col, kick, head, dek = LEAD_ONE
    chip(d, EDGE, y, tg, COLORS[col])
    d.text((EDGE + 132, y + 3), kick, font=load_font("sans_b", 14),
           fill=COLORS["grey"])
    y += 26
    y = paint_lines(d, flow_text(d, head, load_font("serif_b", 34), BODY_W),
                    load_font("serif_b", 34), EDGE, y, 40)
    y += 3
    y = paint_lines(d, flow_text(d, dek, load_font("serif", 18), BODY_W),
                    load_font("serif", 18), EDGE, y, 23)
    y += 5
    parade_scene(d, EDGE, y, BODY_W, 36)
    y += 36 + 7
    y = hline(d, y, 2)
    y += 6

    # ---- leads 2 and 3, side by side ----
    col_w = (BODY_W - 24) // 2
    col_ends = []
    for i, (tg, col, head, dk) in enumerate((LEAD_TWO, LEAD_THREE)):
        x = EDGE + i * (col_w + 24)
        yy = y
        chip(d, x, yy, tg, COLORS[col])
        yy += 26
        yy = paint_lines(d, flow_text(d, head, load_font("serif_b", 20), col_w),
                         load_font("serif_b", 20), x, yy, 25)
        yy += 3
        yy = paint_lines(d, flow_text(d, dk, load_font("serif", 13), col_w),
                         load_font("serif", 13), x, yy, 16)
        col_ends.append(yy)
    y = max(col_ends) + 5
    y = hline(d, y, 2)
    y += 6

    # ---- 30 briefs, 2 columns x 15 rows ----
    assert len(BRIEFS) == 30, f"briefs: {len(BRIEFS)}"
    row_h = 28
    for r in range(15):
        for c in range(2):
            tg, col, head, dk, icon = BRIEFS[r * 2 + c]
            x = EDGE + c * (col_w + 24)
            yy = y + r * row_h
            tx = x
            if icon:
                draw_icon(d, icon, x, yy - 2)
                tx = x + 28
            tw = chip(d, tx, yy, tg, COLORS[col], size=11)
            fnt = load_font("serif_b", 13)
            while (measure(d, head, fnt) > col_w - (tx - x) - tw - 6
                   and fnt.size > 11):
                fnt = load_font("serif_b", fnt.size - 1)
            d.text((tx + tw + 6, yy + 1), head, font=fnt, fill=COLORS["ink"])
            dek_lines = flow_text(d, dk, load_font("serif", 11), col_w - (tx - x))
            paint_lines(d, dek_lines[:1], load_font("serif", 11), tx, yy + 17, 13,
                        fill=COLORS["dim"])
    y += 15 * row_h
    y = hline(d, y, 2)
    y += 5

    # ---- also strip: 17 items ----
    d.text((EDGE, y), "ALSO ON 26 NOVEMBER", font=load_font("sans_b", 15),
           fill=COLORS["red"])
    y += 17
    also_lines = flow_text(d, ALSO, load_font("serif", 12), BODY_W)
    y = paint_lines(d, also_lines, load_font("serif", 12), EDGE, y, 13)
    y += 4
    y = hline(d, y, 1)
    y += 4

    # ---- UTC timeline ----
    d.text((EDGE, y), "THE DAY IN UTC", font=load_font("sans_b", 12),
           fill=COLORS["red"])
    y += 14
    y = paint_lines(d, flow_text(d, TIMELINE, load_font("serif", 12), BODY_W),
                    load_font("serif", 12), EDGE, y, 14)
    y += 4
    y = hline(d, y, 1)
    y += 4
    d.text((EDGE, y), FOOTNOTE, font=load_font("sans", 11), fill=COLORS["grey"])
    y += 12

    print(f"layout bottom y={y} (canvas {PAGE})")
    print(f"also lines: {len(also_lines)}")
    if y > PAGE - 8:
        print("WARNING: content overflows the page")
    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    render_page()
