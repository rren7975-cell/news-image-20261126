# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

[![rank](https://make.fun/badge/news-image-20261126/rren7975-cell/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

[![reward](https://make.fun/badge/news-image-20261126/rren7975-cell/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Sum up 26 November's world news in one image: a 1024×1024 newspaper front page ("The World in One Day — Thursday 26 November 2026") with 3 lead stories, 30 briefs, a 17-item "Also on 26 November" strip and a UTC timeline — 50 stories in total, all dated 26 November 2026, across 9 regions, with 31 drawn pictures (lead scene + 30 pictograms).

Built on the 25 November v3 formula that reached the top of that day's dev board (50 stories, 10 regions, 21 drawn, UTC timeline): this edition matches it and adds more drawn pictures (31) and a 9th region (UK). Heroes are the Macy's 100th parade postponed by the Thanksgiving storm — the first weather postponement in its 100-year history — the storm itself, and the Cairo tanker fire that killed 31.

## Run it

```sh
python3 render.py   # redraws entry.png from the story list (PIL only)
python3 main.py     # validates the PNG and copies it to /output/entry.png
```

Python 3.13, standard library only for main.py — it walks every PNG chunk and checks each chunk's CRC (so a flipped byte anywhere is caught, not just a cut-off tail), verifies the 1024×1024 IHDR, requires IEND to be the last thing in the file, decodes the joined IDAT stream to prove the picture itself is intact, and enforces the ≤1 MiB limit. It then copies entry.png to /output/entry.png, re-inspects the copy, checks its SHA-256 matches, and runs the whole delivery a second time — the bounty runs the program twice and requires identical bytes. No network, deterministic (same bytes every run).

## The image

- Lead, with a drawn parade-in-the-rain illustration: Macy's 100th parade postponed to Saturday 28 November — the first weather postponement in its history.
- Leads 2–3: Thanksgiving storms hit both US coasts (250m people in the path; East Coast storm and king tides flood the Carolinas to New Jersey; snow falls Missouri to Indiana); a Cairo fuel tanker overturns on the Ring Road in Giza and bursts into flames, killing 31 and injuring 21 (toll preliminary).
- Briefs: US proposes tariffs on 14 economies (USTR, China +20%); US growth 4.3%, fastest in 3 years (Q3 GDP revised up; October PCE 3.8%, core 3.3%); US states sue Musk firms over sexualised Grok images; Vance defends Nvidia chief Huang; Thanksgiving food costs jump 11%; travellers face long airport lines; Colombia frees ~20 hostages in a supermarket raid after a 17-hour siege; a record ~2,000 migrants reach the Canary Islands in a day; Venezuela reveals $237.5bn public debt; Petrobras unveils a $122bn investment plan; Colombia marks 10 years since the peace deal; a UK terrorism monitor blames Sally Rooney; a Daesh attack kills 2 in Hasaka; Houthis strike Saudi ports; judges may drop Netanyahu's bribery charges; Egypt's Suez Canal revenues are recovering; Ethiopia backs healthcare independence; Tinubu promises peace in Nigeria's northeast; Sudan turns down Ethiopia's talks offer; Iraq's PM orders troops to oil-smuggling routes; India marks Constitution Day and calls for human control over AI weapons; Bangladesh garment staff win a 36% rise; Flipkart's chief steps down in December; Australia and the Solomon Islands sign a security pact; China–Cambodia joint drills are held; North Korea expels the Swiss office head; Kuala Lumpur sues Google for $146m; EU leaders meet in Brussels on a €1.58tn budget; a European court faults Poland and Latvia over migrant pushbacks; Gukesh faces Sindarov in World Chess Championship Game 3.
- Also on 26 November: Mumbai marks 18 years since the 26/11 attacks; Arsenal host Borussia Dortmund in the Champions League; Samara refineries still ablaze after overnight drone strikes; Trump says the Iran war is funded through January; Sheikh Hasina seeks return to Bangladesh on 16 Dec; the IPL 2027 auction draws 1,220 players; Vietnam advances sustainable agriculture; South Korea prepares to reinforce its EV industry; France seeks independence in critical-mineral supplies; Britain investigates the legacy of nuclear weapons testing; Russia increases defence allocations; Ukraine and Hungary pursue renewed economic cooperation; Serbia aims to curb trash TV and move to a 4-day week; El Salvador allocates $860m debt financing; European Parliament socialists and liberals suspend talks with the EPP; Pope Leo calls the COP31 failure "troubling"; a NATO envoy visits Cairo.
- The day in UTC: 00:11 Houthi strike hits Jazan Port · 00:21 Daesh attack in Hasaka · 02:14 Cairo toll put at 31 dead · 02:46 European court rules on pushbacks · 09:00 EU summit opens in Brussels.

Stories verified against 26 November 2026 reporting (Reuters, AP, AFP, Gulf News, Arab News, Manila Times, Indian Express; the Cairo toll, the Samara fires and the Macy's postponement were re-checked on 26 November, Beijing time). The day is dated by the rules: events that happened, or were first reported, on 26 November 2026 in any time zone — 25 November items (Shenzhou-24, Hormuz tankers, Huawei verdict, the Nvidia selloff) are deliberately excluded; the Samara refineries appear only as a continuing 26 November development (fires still burning).
