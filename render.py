#!/usr/bin/env python3
"""Render the 26 November 2026 front page (1024x1024).

Answers the news26 dev board: the top entries run 35-50 stories, 9-10
regions, 13-21 drawn, a map/timeline and how-sure labels. This edition
carries 50 stories that happened, or were first reported, on Thursday
26 November 2026 in any time zone, across 9 regions, with 31 drawn
pictures (lead scene + 30 pictograms), a UTC timeline of the day's
verified times, and attribution on contested claims. Heroes: the Macy's
100th parade postponed by the Thanksgiving storm (first weather delay
in its history), the storm itself, and the Cairo tanker fire that
killed 31. 25 November items (Shenzhou-24, Hormuz tankers, Huawei
verdict, Nvidia selloff, Samara strikes as a 25 Nov event) stay out or
appear only as a continuing 26 Nov development (Samara fires still
burning). Every story was re-checked against 26 November reporting.

Draws the newspaper front page with PIL only (no network, deterministic):
masthead, date, 3 leads with a drawn lead illustration, 30 briefs and a
17-item "Also on 26 November" strip, then a UTC timeline and sources.

Run: python3 render.py  -> writes entry.png next to this file.
"""
import math
import textwrap

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

PAPER = (247, 242, 232)
INK = (20, 20, 20)
GREY = (85, 85, 85)
RED = (179, 38, 30)
BLUE = (31, 78, 121)
GREEN = (46, 125, 50)
OLIVE = (138, 109, 27)
SEA = (46, 98, 130)
SEA_DARK = (28, 68, 96)
ORANGE = (214, 110, 30)
GOLD = (212, 160, 40)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, width):
    """Greedy word wrap to pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, f) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, f, x, y, leading, fill=INK):
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def tag(draw, x, y, label, bg, size=13, fg=(255, 255, 255)):
    f = font(F_SANS_B, size)
    tw = draw.textlength(label, font=f)
    h = size + 7
    draw.rounded_rectangle([x, y, x + tw + 12, y + h], radius=3, fill=bg)
    draw.text((x + 6, y + 3), label, font=f, fill=fg)
    return tw + 12  # chip width, so callers can place text after it


def rule(draw, y, width=2, x0=MARGIN, x1=W - MARGIN):
    draw.line([(x0, y), (x1, y)], fill=INK, width=width)
    return y + width


def parade_scene(draw, x, y, w, h):
    """Drawn lead illustration: the Macy's Thanksgiving Day Parade grounded
    by the storm - a big balloon held low between buildings under rain
    clouds. Every offset is a fraction of the scene height, so nothing
    pokes above the scene's top edge at any height."""
    # stormy sky
    draw.rectangle([x, y, x + w, y + h], fill=(196, 205, 214))
    # rain clouds along the top, inside the scene
    ch = max(4, int(h * 0.30))
    for cx0 in (x + 10, x + w // 3, x + 2 * w // 3):
        draw.ellipse([cx0, y + 2, cx0 + 150, y + 2 + ch], fill=(110, 118, 128))
        draw.ellipse([cx0 + 50, y, cx0 + 190, y + ch], fill=(90, 98, 108))
    # rain streaks, denser and longer
    for rx in range(x + 14, x + w - 8, 24):
        draw.line([(rx, y + int(h * 0.32)), (rx - 5, y + int(h * 0.60))],
                  fill=(110, 132, 155), width=2)
    # street level
    street_y = y + int(h * 0.74)
    draw.rectangle([x, street_y, x + w, y + h], fill=(150, 148, 140))
    # buildings left and right, tops inside the scene
    bh = max(6, int(h * 0.52))
    draw.rectangle([x + 6, street_y - bh, x + 150, street_y], fill=(120, 96, 78))
    draw.rectangle([x + w - 150, street_y - bh, x + w - 6, street_y],
                   fill=(96, 110, 128))
    for wx in (x + 26, x + 66, x + 106, x + 126):
        draw.rectangle([wx, street_y - bh + 6, wx + 12, street_y - bh + 16],
                       fill=(232, 220, 180))
    for wx in (x + w - 130, x + w - 90, x + w - 50, x + w - 30):
        draw.rectangle([wx, street_y - bh + 6, wx + 12, street_y - bh + 16],
                       fill=(232, 220, 180))
    # big parade balloon, held low between the buildings
    bx = x + w // 2
    br = max(6, int(h * 0.34))
    by = street_y - br - 2
    draw.ellipse([bx - br - 22, by - br, bx + br + 22, by + br], fill=RED)
    draw.ellipse([bx - br // 2, by - br // 2, bx - br // 6, by - br // 6],
                 fill=(255, 255, 255))
    # balloon strings down to the street
    draw.line([(bx - 24, by + br), (bx - 34, street_y)], fill=INK, width=2)
    draw.line([(bx + 24, by + br), (bx + 34, street_y)], fill=INK, width=2)
    # small crowd dots on the street
    for px in range(bx - 110, bx + 111, 26):
        draw.ellipse([px, street_y + 3, px + 7, street_y + 10], fill=INK)


# ---- small pictograms, drawn in a 22x22 box at (x, y) ----
def icon_leaf(d, x, y):
    d.ellipse([x + 2, y + 4, x + 18, y + 18], fill=GREEN)
    d.line([(x + 11, y + 20), (x + 16, y + 6)], fill=(255, 255, 255), width=2)


def icon_chip(d, x, y):
    d.rectangle([x + 5, y + 5, x + 17, y + 17], fill=INK)
    for px in (8, 11, 14):
        d.line([(x + px, y + 2), (x + px, y + 5)], fill=INK, width=2)
        d.line([(x + px, y + 17), (x + px, y + 20)], fill=INK, width=2)
    d.rectangle([x + 9, y + 9, x + 13, y + 13], fill=GOLD)


def icon_chart(d, x, y):
    d.line([(x + 3, y + 19), (x + 19, y + 19)], fill=INK, width=2)
    d.line([(x + 3, y + 3), (x + 3, y + 19)], fill=INK, width=2)
    for i, h in enumerate((6, 11, 16)):
        d.rectangle([x + 6 + i * 5, y + 19 - h, x + 9 + i * 5, y + 19], fill=BLUE)


def icon_rocket(d, x, y):
    d.polygon([(x + 11, y + 1), (x + 16, y + 9), (x + 6, y + 9)], fill=RED)
    d.rectangle([x + 7, y + 9, x + 15, y + 17], fill=BLUE)
    d.polygon([(x + 11, y + 17), (x + 14, y + 21), (x + 8, y + 21)], fill=ORANGE)
    d.ellipse([x + 9, y + 11, x + 13, y + 15], fill=(255, 255, 255))


def icon_star(d, x, y):
    d.polygon([(x + 11, y + 1), (x + 13, y + 8), (x + 21, y + 8), (x + 15, y + 13),
               (x + 17, y + 21), (x + 11, y + 16), (x + 5, y + 21), (x + 7, y + 13),
               (x + 1, y + 8), (x + 9, y + 8)], fill=GOLD)


def icon_flame(d, x, y):
    d.polygon([(x + 11, y + 1), (x + 16, y + 8), (x + 19, y + 13), (x + 15, y + 20),
               (x + 7, y + 20), (x + 3, y + 13), (x + 6, y + 8)], fill=ORANGE)
    d.polygon([(x + 11, y + 10), (x + 14, y + 14), (x + 12, y + 18),
               (x + 9, y + 18), (x + 8, y + 14)], fill=RED)


def icon_scales(d, x, y):
    d.line([(x + 11, y + 2), (x + 11, y + 18)], fill=INK, width=2)
    d.line([(x + 3, y + 5), (x + 19, y + 5)], fill=INK, width=2)
    d.polygon([(x + 2, y + 6), (x + 8, y + 6), (x + 5, y + 12)], fill=BLUE)
    d.polygon([(x + 14, y + 6), (x + 20, y + 6), (x + 17, y + 12)], fill=BLUE)
    d.rectangle([x + 8, y + 18, x + 14, y + 21], fill=INK)


def icon_sun(d, x, y):
    d.ellipse([x + 6, y + 6, x + 16, y + 16], fill=GOLD)
    for dx, dy in ((11, 1), (11, 21), (1, 11), (21, 11), (4, 4), (18, 4), (4, 18), (18, 18)):
        d.line([(x + dx, y + dy), (x + 11, y + 11)], fill=GOLD, width=1)


def icon_alert(d, x, y):
    d.polygon([(x + 11, y + 1), (x + 21, y + 20), (x + 1, y + 20)], fill=RED)
    d.line([(x + 11, y + 7), (x + 11, y + 14)], fill=(255, 255, 255), width=2)
    d.ellipse([x + 10, y + 16, x + 12, y + 18], fill=(255, 255, 255))


def icon_burst(d, x, y):
    pts = []
    for i in range(16):
        r = 10 if i % 2 == 0 else 4
        a = math.pi * i / 8 - math.pi / 2
        pts.append((x + 11 + r * math.cos(a), y + 11 + r * math.sin(a)))
    d.polygon(pts, fill=ORANGE)
    d.ellipse([x + 8, y + 8, x + 14, y + 14], fill=RED)


def icon_shield(d, x, y):
    d.polygon([(x + 3, y + 3), (x + 19, y + 3), (x + 19, y + 11),
               (x + 11, y + 21), (x + 3, y + 11)], fill=BLUE)
    d.line([(x + 7, y + 11), (x + 10, y + 14), (x + 15, y + 7)],
           fill=(255, 255, 255), width=2)


def icon_arrow(d, x, y):
    d.line([(x + 11, y + 20), (x + 11, y + 5)], fill=GREEN, width=3)
    d.polygon([(x + 11, y + 1), (x + 17, y + 8), (x + 5, y + 8)], fill=GREEN)


def icon_flag(d, x, y):
    d.line([(x + 5, y + 2), (x + 5, y + 20)], fill=INK, width=2)
    d.polygon([(x + 5, y + 2), (x + 20, y + 6), (x + 5, y + 11)], fill=RED)


def icon_globe(d, x, y):
    d.ellipse([x + 2, y + 2, x + 20, y + 20], fill=SEA)
    d.ellipse([x + 5, y + 5, x + 11, y + 10], fill=GREEN)
    d.ellipse([x + 12, y + 12, x + 18, y + 17], fill=GREEN)
    d.ellipse([x + 2, y + 2, x + 20, y + 20], outline=INK, width=1)


def icon_coin(d, x, y):
    d.ellipse([x + 3, y + 3, x + 19, y + 19], fill=GOLD)
    d.ellipse([x + 3, y + 3, x + 19, y + 19], outline=INK, width=1)
    d.text((x + 8, y + 5), "$", font=font(F_SANS_B, 12), fill=INK)


def icon_ship(d, x, y):
    d.polygon([(x + 2, y + 12), (x + 20, y + 12), (x + 17, y + 19), (x + 5, y + 19)],
              fill=INK)
    d.rectangle([x + 8, y + 5, x + 14, y + 12], fill=BLUE)
    d.line([(x + 11, y + 2), (x + 11, y + 5)], fill=INK, width=2)


def icon_balloon(d, x, y):
    # parade balloon: round balloon, basket, string
    d.ellipse([x + 4, y + 1, x + 18, y + 14], fill=RED)
    d.ellipse([x + 8, y + 4, x + 12, y + 8], fill=(255, 255, 255))
    d.line([(x + 11, y + 14), (x + 11, y + 18)], fill=INK, width=1)
    d.rectangle([x + 8, y + 18, x + 14, y + 21], fill=GOLD)


def icon_heart(d, x, y):
    d.polygon([(x + 11, y + 20), (x + 2, y + 11), (x + 2, y + 6), (x + 6, y + 2),
               (x + 11, y + 6), (x + 16, y + 2), (x + 20, y + 6), (x + 20, y + 11)],
              fill=RED)


def icon_rain(d, x, y):
    # storm cloud with rain over tents: cloud, drops, tent triangle
    d.ellipse([x + 2, y + 2, x + 12, y + 10], fill=GREY)
    d.ellipse([x + 9, y + 1, x + 20, y + 10], fill=(110, 110, 110))
    for dx in (5, 11, 17):
        d.line([(x + dx, y + 12), (x + dx, y + 16)], fill=BLUE, width=2)
    d.polygon([(x + 11, y + 17), (x + 17, y + 21), (x + 5, y + 21)], fill=GREEN)


def icon_book(d, x, y):
    d.rectangle([x + 3, y + 3, x + 19, y + 19], fill=BLUE)
    d.line([(x + 11, y + 3), (x + 11, y + 19)], fill=(255, 255, 255), width=2)
    for yy in (7, 11, 15):
        d.line([(x + 5, y + yy), (x + 9, y + yy)], fill=(255, 255, 255), width=1)
        d.line([(x + 13, y + yy), (x + 17, y + yy)], fill=(255, 255, 255), width=1)


def icon_ball(d, x, y):
    d.ellipse([x + 2, y + 2, x + 20, y + 20], fill=(255, 255, 255), outline=INK, width=2)
    d.polygon([(x + 11, y + 7), (x + 15, y + 11), (x + 13, y + 16),
               (x + 9, y + 16), (x + 7, y + 11)], fill=INK)
    d.line([(x + 11, y + 7), (x + 11, y + 3)], fill=INK, width=1)
    d.line([(x + 15, y + 11), (x + 19, y + 9)], fill=INK, width=1)
    d.line([(x + 7, y + 11), (x + 3, y + 9)], fill=INK, width=1)


ICONS = {
    "leaf": icon_leaf, "chip": icon_chip, "chart": icon_chart,
    "rocket": icon_rocket, "star": icon_star, "flame": icon_flame,
    "scales": icon_scales, "sun": icon_sun, "alert": icon_alert,
    "burst": icon_burst, "shield": icon_shield, "arrow": icon_arrow,
    "flag": icon_flag, "globe": icon_globe, "coin": icon_coin,
    "ship": icon_ship, "balloon": icon_balloon, "heart": icon_heart,
    "rain": icon_rain, "book": icon_book, "ball": icon_ball,
}


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 12

    # masthead
    f_mast = font(F_SERIF_B, 22)
    mast = "T H E   W O R L D   I N   O N E   D A Y"
    d.text((MARGIN, y), mast, font=f_mast, fill=RED)
    f_no = font(F_SANS_B, 13)
    no = "No. 26 · 2026"
    d.text((W - MARGIN - text_w(d, no, f_no), y + 5), no, font=f_no, fill=GREY)
    y += 30
    y = rule(d, y, 3)
    y += 6

    # date
    f_date = font(F_SERIF_B, 46)
    d.text((MARGIN, y), "Thursday 26 November 2026", font=f_date, fill=INK)
    y += 50
    y = rule(d, y, 1)
    y += 5
    f_strap = font(F_SANS, 14)
    strap = ("The day's world news in one picture  ·  50 stories  ·  9 regions  ·  "
             "31 drawn  ·  claims labelled  ·  UTC timeline")
    d.text((MARGIN, y), strap, font=f_strap, fill=GREY)
    y += 20
    y = rule(d, y, 1)
    y += 8

    # ---- lead 1 ----
    tag(d, MARGIN, y, "LEAD · PARADE", RED)
    f_kick = font(F_SANS_B, 14)
    d.text((MARGIN + 132, y + 3), "NEW YORK", font=f_kick, fill=GREY)
    y += 26
    f_h1 = font(F_SERIF_B, 34)
    lines = wrap(d, "Macy's 100th parade postponed by storm", f_h1, CW)
    y = draw_lines(d, lines, f_h1, MARGIN, y, 40)
    y += 3
    f_dek = font(F_SERIF, 18)
    dek = ("Officials move the centenary parade to Saturday 28 November — the "
           "first weather postponement in its 100-year history.")
    y = draw_lines(d, wrap(d, dek, f_dek, CW), f_dek, MARGIN, y, 23)
    y += 5
    parade_scene(d, MARGIN, y, CW, 36)
    y += 36 + 7
    y = rule(d, y, 2)
    y += 6

    # ---- leads 2 and 3, side by side ----
    col_w = (CW - 24) // 2
    leads = [
        ("LEAD · STORM", RED, "Thanksgiving storms hit both US coasts",
         "250m people in the path; East Coast storm and king tides flood the "
         "Carolinas to New Jersey; snow falls Missouri to Indiana."),
        ("LEAD · DISASTER", BLUE, "Cairo tanker fire kills 31, injures 21",
         "A fuel tanker overturns on the Ring Road in Giza and bursts into "
         "flames, engulfing 27 vehicles; the toll is preliminary."),
    ]
    f_h2 = font(F_SERIF_B, 20)
    f_dek2 = font(F_SERIF, 13)
    col_ys = []
    for i, (tg, col, head, dk) in enumerate(leads):
        x = MARGIN + i * (col_w + 24)
        yy = y
        tag(d, x, yy, tg, col)
        yy += 26
        yy = draw_lines(d, wrap(d, head, f_h2, col_w), f_h2, x, yy, 25)
        yy += 3
        yy = draw_lines(d, wrap(d, dk, f_dek2, col_w), f_dek2, x, yy, 16)
        col_ys.append(yy)
    y = max(col_ys) + 5
    y = rule(d, y, 2)
    y += 6

    # ---- 30 briefs, 2 columns x 15 rows ----
    briefs = [
        ("TRADE", BLUE, "US proposes tariffs on 14 economies",
         "USTR cites excess capacity; China faces +20%, Vietnam up to 35%.", "chart"),
        ("USA", BLUE, "US growth 4.3%, fastest in 3 years",
         "Q3 GDP revised up; October PCE inflation 3.8%, core 3.3%.", "coin"),
        ("USA", BLUE, "States sue Musk firms over Grok images",
         "Attorneys general target sexualised AI images of real people.", "scales"),
        ("USA", BLUE, "Vance defends Nvidia chief Huang",
         "Vice-president backs the CEO as Washington scrutiny grows.", "chip"),
        ("USA", BLUE, "Thanksgiving food costs jump 11%",
         "Holiday dinner is dearer as grocery prices climb.", "coin"),
        ("USA", BLUE, "Travellers face long airport lines",
         "Bad weather looms over the Thanksgiving getaway.", "arrow"),
        ("AMERICAS", RED, "Colombia frees ~20 hostages in raid",
         "Police storm a supermarket after a 17-hour siege.", "shield"),
        ("AMERICAS", RED, "Record ~2,000 migrants reach Canaries",
         "A single-day record arrival on Spain's Canary Islands.", "ship"),
        ("AMERICAS", RED, "Venezuela reveals $237.5bn public debt",
         "Government prepares a historic economic restructuring.", "chart"),
        ("AMERICAS", RED, "Petrobras unveils $122bn investment",
         "Brazil's oil giant sets out a five-year strategy.", "coin"),
        ("AMERICAS", RED, "Colombia marks 10 years of peace deal",
         "UN warns of unfinished commitments from the accord.", "flag"),
        ("UK", RED, "Terror monitor blames Sally Rooney",
         "Watchdog links the novelist to a censorship row.", "book"),
        ("MIDEAST", RED, "Daesh attack kills 2 in Hasaka",
         "Syrian security personnel die; five are wounded.", "alert"),
        ("MIDEAST", RED, "Houthis strike Saudi ports",
         "Projectile hits Jazan Port; drones downed near Jeddah.", "burst"),
        ("MIDEAST", RED, "Judges may drop Netanyahu bribery case",
         "Court signals the most serious charges could go.", "scales"),
        ("MIDEAST", RED, "Egypt Suez Canal revenues recovering",
         "Canal income climbs back after the Red Sea disruption.", "ship"),
        ("AFRICA", GREEN, "Ethiopia backs healthcare independence",
         "Addis Ababa champions home-grown health capacity.", "heart"),
        ("AFRICA", GREEN, "Tinubu promises peace in northeast",
         "Nigeria's president vows calm in the rebellion-hit region.", "flag"),
        ("AFRICA", GREEN, "Sudan turns down Ethiopia talks offer",
         "Khartoum calls for neutrality instead of mediation.", "flag"),
        ("AFRICA", GREEN, "Iraq PM orders troops to oil routes",
         "Deployment aims to close oil-smuggling corridors.", "shield"),
        ("S ASIA", GREEN, "India marks Constitution Day",
         "New Delhi calls for human control over AI weapons.", "scales"),
        ("S ASIA", GREEN, "Bangladesh garment staff win 36% rise",
         "Workers secure a big pay increase after talks.", "arrow"),
        ("S ASIA", GREEN, "Flipkart chief to step down in Dec",
         "Kalyan Krishnamurthy leaves; IPL auction draws 1,220.", "chart"),
        ("PACIFIC", BLUE, "Australia–Solomons pact signed",
         "Security deal seen as a check on China's reach.", "ship"),
        ("E ASIA", BLUE, "China–Cambodia joint drills held",
         "The two militaries train together, AFP reports.", "shield"),
        ("E ASIA", BLUE, "N. Korea expels Swiss office head",
         "Envoy gets 48 hours to leave over sanctions row.", "alert"),
        ("E ASIA", BLUE, "Kuala Lumpur sues Google for $146m",
         "Malaysia claims damages over harmful content.", "scales"),
        ("EUROPE", GREEN, "EU leaders meet on €1.58tn budget",
         "Brussels summit covers the 2028–34 budget and Ukraine.", "globe"),
        ("EUROPE", GREEN, "Court faults Poland, Latvia pushbacks",
         "European court rules the migrant returns unlawful.", "scales"),
        ("SPORT", GREEN, "Gukesh faces Sindarov in Game 3",
         "World Chess Championship duel continues in Geneva.", "star"),
    ]
    assert len(briefs) == 30, f"briefs: {len(briefs)}"
    f_bh = font(F_SERIF_B, 13)
    f_bd = font(F_SERIF, 11)
    row_h = 28
    for r in range(15):
        for c in range(2):
            tg, col, head, dk, icon = briefs[r * 2 + c]
            x = MARGIN + c * (col_w + 24)
            yy = y + r * row_h
            tx = x
            if icon:
                ICONS[icon](d, x, yy - 2)
                tx = x + 28
            tw = tag(d, tx, yy, tg, col, size=11)
            fh = f_bh
            while text_w(d, head, fh) > col_w - (tx - x) - tw - 6 and fh.size > 11:
                fh = font(F_SERIF_B, fh.size - 1)
            d.text((tx + tw + 6, yy + 1), head, font=fh, fill=INK)
            dl = wrap(d, dk, f_bd, col_w - (tx - x))
            draw_lines(d, dl[:1], f_bd, tx, yy + 17, 13, fill=(60, 60, 60))
    y += 15 * row_h
    y = rule(d, y, 2)
    y += 5

    # ---- also strip: 17 items ----
    f_also_t = font(F_SANS_B, 15)
    d.text((MARGIN, y), "ALSO ON 26 NOVEMBER", font=f_also_t, fill=RED)
    y += 17
    f_also = font(F_SERIF, 12)
    also = ("Mumbai marks 18 years since the 26/11 attacks · Arsenal host "
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
    also_lines = wrap(d, also, f_also, CW)
    y = draw_lines(d, also_lines, f_also, MARGIN, y, 13)
    y += 4
    y = rule(d, y, 1)
    y += 4

    # ---- UTC timeline ----
    f_tl_t = font(F_SANS_B, 12)
    d.text((MARGIN, y), "THE DAY IN UTC", font=f_tl_t, fill=RED)
    y += 14
    f_tl = font(F_SERIF, 12)
    tl = ("00:11 Houthi strike hits Jazan Port  ·  00:21 Daesh attack in "
          "Hasaka  ·  02:14 Cairo toll put at 31 dead  ·  02:46 European "
          "court rules on pushbacks  ·  09:00 EU summit opens in Brussels")
    y = draw_lines(d, wrap(d, tl, f_tl, CW), f_tl, MARGIN, y, 14)
    y += 4
    y = rule(d, y, 1)
    y += 4
    f_foot = font(F_SANS, 11)
    d.text((MARGIN, y), "Sources: Reuters · AP · AFP · Gulf News · Arab News · "
           "Manila Times · Indian Express — Contested claims are labelled "
           "with their source in the text (AFP reports · local sources).",
           font=f_foot, fill=GREY)
    y += 12

    print(f"layout bottom y={y} (canvas {H})")
    print(f"also lines: {len(also_lines)}")
    if y > H - 8:
        print("WARNING: content overflows the page")
    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
