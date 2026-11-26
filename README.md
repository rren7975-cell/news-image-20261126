# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

[![rank](https://make.fun/badge/news-image-20261126/rren7975-cell/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

[![reward](https://make.fun/badge/news-image-20261126/rren7975-cell/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image that sums up Thursday 26 November 2026: a 1024×1024 newspaper front page, "The World in One Day", with three lead stories, thirty briefs, a seventeen-item "Also on 26 November" strip and a UTC timeline — fifty stories in all, across nine regions, with thirty-one drawn pictures (a lead scene plus thirty pictograms).

## How to run it

```sh
python3 render.py   # redraws entry.png from the story tables (PIL only)
python3 main.py     # validates the PNG and copies it to /output/entry.png
```

`main.py` uses only the Python standard library. It walks every PNG chunk and checks each chunk's CRC (so a flipped byte anywhere is caught, not just a cut-off tail), verifies the 1024×1024 IHDR, requires IEND to be the last thing in the file, decodes the joined IDAT stream to prove the picture itself is intact, and enforces the ≤1 MiB limit. It then copies `entry.png` to `/output/entry.png`, re-inspects the copy, checks its SHA-256 matches, and runs the whole delivery a second time — the bounty runs the program twice and requires identical bytes. No network, deterministic (same bytes every run).

## What the image shows

The lead, with a drawn parade-in-the-rain illustration: Macy's 100th parade is postponed to Saturday 28 November — the first weather postponement in its history. The other two leads: Thanksgiving storms hit both US coasts (250m people in the path; an East Coast storm and king tides flood the Carolinas to New Jersey; snow falls from Missouri to Indiana) and a Cairo fuel tanker overturns on the Ring Road in Giza and bursts into flames, killing 31 and injuring 21 (the toll is preliminary).

The thirty briefs cover: the US proposing tariffs on 14 economies (USTR, China +20%); US growth of 4.3%, the fastest in 3 years (Q3 GDP revised up; October PCE 3.8%, core 3.3%); US states suing Musk firms over sexualised Grok images; Vance defending Nvidia chief Huang; Thanksgiving food costs jumping 11%; travellers facing long airport lines; Colombia freeing ~20 hostages in a supermarket raid after a 17-hour siege; a record ~2,000 migrants reaching the Canary Islands in a day; Venezuela revealing $237.5bn of public debt; Petrobras unveiling a $122bn investment plan; Colombia marking 10 years since the peace deal; a UK terrorism monitor blaming Sally Rooney; a Daesh attack killing 2 in Hasaka; Houthis striking Saudi ports; judges possibly dropping Netanyahu's bribery charges; Egypt's Suez Canal revenues recovering; Ethiopia backing healthcare independence; Tinubu promising peace in Nigeria's northeast; Sudan turning down Ethiopia's talks offer; Iraq's PM ordering troops to oil-smuggling routes; India marking Constitution Day and calling for human control over AI weapons; Bangladesh garment staff winning a 36% rise; Flipkart's chief stepping down in December; Australia and the Solomon Islands signing a security pact; China–Cambodia joint drills; North Korea expelling the Swiss office head; Kuala Lumpur suing Google for $146m; EU leaders meeting in Brussels on a €1.58tn budget; a European court faulting Poland and Latvia over migrant pushbacks; and Gukesh facing Sindarov in World Chess Championship Game 3.

Also on 26 November: Mumbai marking 18 years since the 26/11 attacks; Arsenal hosting Borussia Dortmund in the Champions League; Samara refineries still ablaze after overnight drone strikes; Trump saying the Iran war is funded through January; Sheikh Hasina seeking return to Bangladesh on 16 Dec; the IPL 2027 auction drawing 1,220 players; Vietnam advancing sustainable agriculture; South Korea preparing to reinforce its EV industry; France seeking independence in critical-mineral supplies; Britain investigating the legacy of nuclear weapons testing; Russia increasing defence allocations; Ukraine and Hungary pursuing renewed economic cooperation; Serbia aiming to curb trash TV and move to a 4-day week; El Salvador allocating $860m in debt financing; European Parliament socialists and liberals suspending talks with the EPP; Pope Leo calling the COP31 failure "troubling"; and a NATO envoy visiting Cairo.

The day in UTC: 00:11 Houthi strike hits Jazan Port · 00:21 Daesh attack in Hasaka · 02:14 Cairo toll put at 31 dead · 02:46 European court rules on pushbacks · 09:00 EU summit opens in Brussels.

## Sourcing

Stories were verified against 26 November 2026 reporting (Reuters, AP, AFP, Gulf News, Arab News, Manila Times, Indian Express; the Cairo toll, the Samara fires and the Macy's postponement were re-checked on 26 November, Beijing time). The day is dated by the rules: events that happened, or were first reported, on 26 November 2026 in any time zone. 25 November items (Shenzhou-24, the Hormuz tankers, the Huawei verdict, the Nvidia selloff) are deliberately excluded; the Samara refineries appear only as a continuing 26 November development (fires still burning).
