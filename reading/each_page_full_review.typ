// A page-by-page guide to the dashboard: what is on screen, what it means, what to say, and how to answer questions.
// Compile: typst compile each_page_full_review.typ   (needs the Manrope font; Newsreader is optional for headings)

#set document(title: "Each Page, Fully Reviewed: Presenting the Rain and Vegetable Prices Dashboard")
#set page(paper: "a4", margin: (x: 2.3cm, top: 2.3cm, bottom: 2.2cm), numbering: "1", number-align: center)
#set text(font: "Manrope", size: 10.5pt, weight: 450, lang: "en", region: "gb")
#set par(justify: false, leading: 0.72em, spacing: 1.05em)
#set heading(numbering: "1.1")
#show heading: set text(font: ("Newsreader", "Newsreader 36pt", "Manrope"), weight: 600, fill: rgb("#002941"))
#show heading.where(level: 1): set text(size: 17pt)
#show heading.where(level: 1): set block(above: 1.8em, below: 0.9em)
#show heading.where(level: 2): set text(size: 13pt)
#show heading.where(level: 2): set block(above: 1.4em, below: 0.7em)
#set table(stroke: 0.5pt + rgb("#c9d6de"), inset: 6pt)
#show table.cell.where(y: 0): set text(weight: 700)
#show link: set text(fill: rgb("#1155cc"))

#let note(body) = block(breakable: false, fill: rgb("#fff4e5"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#f5a33b")), body)
#let key(body) = block(breakable: false, fill: rgb("#e8f3f8"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#2f7292")), body)
#let say(body) = block(breakable: false, fill: rgb("#eef6f1"), inset: 12pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#23936f")), [#text(weight: 700)[What to say]#v(0.2em)#emph(body)])
#let dont(body) = block(breakable: false, fill: rgb("#fdecec"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#d9534f")), [*What not to claim.* #body])
#let qa(q, a) = block(breakable: false, above: 0.9em, below: 0.9em)[#text(weight: 700, fill: rgb("#002941"))[Q. #q] \ #a]

#let shot(path, cap) = figure(block(stroke: 0.5pt + rgb("#c9d6de"), image(path, width: 100%)), caption: cap, supplement: [Screenshot], kind: image)
#let part(path, title, shows, tell, w: 100%) = block(breakable: false, above: 1.3em, below: 1.3em)[
  #text(weight: 700, size: 11.5pt, fill: rgb("#002941"))[#title]
  #v(0.2em)
  #align(center, block(stroke: 0.5pt + rgb("#c9d6de"), image(path, width: w)))
  #v(0.2em)
  *What it shows.* #shows

  #block(fill: rgb("#eef6f1"), inset: 8pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#23936f")))[*What to tell people here.* #emph(tell)]
]

// ---------------------------------------------------------------- title
#text(font: ("Newsreader", "Newsreader 36pt", "Manrope"), size: 26pt, weight: 600, fill: rgb("#002941"))[Each page, fully reviewed]
#v(-0.4em)
#text(size: 13pt, fill: rgb("#52707f"))[A guide for presenting the dashboard: what every part of every page shows, what it means, what to say, and how to answer the questions people ask.]
#line(length: 100%, stroke: 0.6pt + rgb("#c9d6de"))

*Who this is for.* Anyone presenting the dashboard at the DST Data Gallery Walk, including someone who has never seen the project before. If you read only one of the three documents before presenting, read this one. For the background story see `full_story.typ`; for the full method and code see `analysis.typ`.

*How each page section is built.* Purpose; a screenshot of the whole page, then each part cropped out with what it shows and what to tell people about it; where each number comes from; what the page proves in the argument; what to click; *what to say* (a script in a green box, written to be spoken); questions you may be asked, with answers; and what not to claim. No abbreviations are used without being spelled out.

#outline(title: [Contents], depth: 1, indent: 1em)

= Before you start

== Starting the dashboard

Open a terminal in the `research-story` folder and run `uv run streamlit run app.py`. The browser opens at `http://localhost:8501`. The first run downloads Python and the packages, so do it once with internet before the event; after that it works offline. For a 40-inch television, use the browser's full-screen mode and check that all text can be read from two metres away.

== How every page is laid out

#table(
  columns: (1.1fr, 2.4fr),
  table.header([Part of the screen], [What it is]),
  [Left sidebar], [The project name ("Rain & vegetable prices"), a dark *Start from page 1* button (hidden on page 1), and the five pages grouped into three acts: *The problem* (pages 1 and 2), *The test* (page 3), *The bigger picture* (pages 4 and 5). Click any page name to jump to it.],
  [Small label above the title], [The page number and act, for example "01 · The problem".],
  [Title and one-line description], [The headline of the page, and one sentence explaining what the viewer can do.],
  [Controls], [Buttons, switches and sliders the viewer can use. Every number and chart on the page reacts to them.],
  [Coloured cards], [Four (or three) headline numbers. Each card has a small icon, a label, a large value and a small chip underneath that explains the value.],
  [Charts], [Interactive. Hovering over a point shows its exact value.],
  [Source bar], [A white bar with a dark *SOURCE* badge naming the data behind the page, and the reminder "Exploratory · not proof of cause" on the right.],
  [Control bar at the bottom], [A progress line, the act name, "page n / 5", and *Previous* and *Next* buttons. The right arrow or Page Down key also goes forward; the left arrow or Page Up goes back.],
)

#grid(columns: (1fr, 2fr), gutter: 12pt, align: horizon,
  block(stroke: 0.5pt + rgb("#c9d6de"), image("images/p1_sidebar.png", width: 100%)),
  [*The sidebar* (left). The three acts are "The problem", "The test" and "The bigger picture". The highlighted row is the page you are on. On every page except page 1, a dark *Start from page 1* button appears above the list; use it to reset between visitors.])

#block(stroke: 0.5pt + rgb("#c9d6de"), image("images/p1_bar.png", width: 100%))
*The control bar* (bottom of every page). The line fills up as you move through the five pages. "The problem" on the left is the current act, "1 / 5" in the middle is the page number, and the buttons on the right move back and forward. *Previous* is greyed out on page 1 and *Next* on page 5.

== The whole story in one minute

If someone gives you one minute, say this:

#say["Vegetable prices in Sri Lanka swing wildly. Cabbage at Dambulla has gone from about 16 rupees a kilo to about 452. We asked whether last month's rain can help forecast next month's price, once you already know past prices. We made two forecasts every month for five years, one from past prices only and one that also knew the rain, and checked which missed by less. For cabbage, brinjal and carrot, adding rain clearly helped: errors were 8 to 20 percent smaller, and that survived strict statistical checks. For the other four vegetables it did not help. Even the best forecasts still miss by about a quarter of the price, so this tells us where rain carries useful information. It is not a price prediction app, and it does not prove rain causes the price changes."]

== Numbers worth memorising

#table(
  columns: (2fr, 1fr),
  table.header([Fact], [Value]),
  [Cabbage at Dambulla: cheapest and dearest month], [Rs 16 (January 2017), Rs 452 (January 2024)],
  [Gap between them], [about 28 times],
  [Months where cabbage moved more than 20%], [6 in 10],
  [Link between rain and cabbage price change, one month later], [correlation +0.60],
  [Forecasts tested per vegetable], [62 (September 2021 to October 2026)],
  [Cabbage typical miss: prices only, then with rain], [Rs 52, then Rs 42 per kilo],
  [Overall error reduction with rain], [cabbage 19.7%, brinjal 12.4%, carrot 8.2%, tomato 4.8%, snake gourd 1.8%, pumpkin 1.8%, beans −1.5%],
  [Typical miss even with rain], [about a quarter of the price (24.8%, median over seven vegetables)],
  [Rain and rice harvest share, Yala season], [correlation +0.68 over 16 seasons],
  [Peak share of rice imported], [about 30% (2017)],
  [Rupee price of one US dollar], [about Rs 333 now, up 75% since January 2021],
)

= Page 1: Vegetable prices swing wildly

*Act:* The problem. *Time:* about one and a half minutes.

== Purpose

To make the problem felt. Before any statistics, the viewer should see that vegetable prices jump around enormously, that every vegetable behaves differently, and that rain falls unevenly across the island. The page ends by asking the question the whole dashboard answers.

== The page, part by part

#shot("images/p1_full.png", [Page 1 as it appears when the dashboard opens (cabbage selected, latest month on the map).])

#part("images/p1_header.png", [1. The label, title and vegetable buttons],
  [The small label "01 · The problem" tells you where you are in the story. The headline states the problem. The sentence under it says what the prices are (wholesale, at Dambulla) and what the viewer can do. The row of buttons picks one of the seven vegetables; every card and chart below follows it.],
  ["These are wholesale prices at Dambulla, one of the main vegetable markets. Pick any vegetable and watch how far its price moves."])

#part("images/p1_cards.png", [2. The four cards],
  [Blue: the *cheapest month* (Rs 16 a kilo, January 2017). Pink: the *most expensive month* (Rs 452, January 2024). Orange: the *biggest one-month move*, 158%, a rise into November 2023. Purple: *months with a swing over 20%*: in 6 of every 10 months, the price moved more than a fifth up or down from the previous month; the chip says the dearest month was 28 times the cheapest.],
  ["In its cheapest month cabbage sold for about 16 rupees a kilo; in its dearest, about 452. That is a 28-times gap. And in six months out of ten the price moved by more than a fifth from one month to the next."])

#part("images/p1_chart.png", [3. The price and rain chart],
  [The dark line (with light fill) is the monthly average cabbage price in rupees per kilo since 2016. The blue bars underneath are monthly rain in millimetres for the area chosen with the buttons above (here the whole island). Both share the same time axis, so a wet spell can be lined up with what the price did afterwards. The switch on the left turns the rain bars on and off; the four buttons choose whole island, Dambulla, Nuwara Eliya or Colombo rain.],
  ["The line is the price, the bars are the rain, on the same timeline. Look at the end of 2023: very heavy rain, and the price climbs to its peak in January 2024. Rain and price are side by side here, but this chart alone does not prove anything; that is what the next pages test."])

#part("images/p1_map.png", [4. The rain map], w: 75%,
  [Each small square is one weather grid square, about 11 km across, coloured by rain: darker blue means more rain (scale 0 to 600 mm). The slider picks the month; the two round buttons switch between one specific month and the long-term average for a calendar month (2010 to 2026). The dotted squares are the areas around Dambulla, Nuwara Eliya and Colombo; the area chosen with the rain buttons is drawn solid. The small white square is Colombo (Pettah) market.],
  ["This is where the rain falls. Darker blue is more rain. It is very uneven: the south-west is soaked during the May monsoon, while the dry zone around Dambulla gets much less. Dambulla and Nuwara Eliya are the two areas whose rain we also tested; Colombo is there just for comparison."])

#part("images/p1_bottom.png", [5. The question and the source bar],
  [The coral line asks the question the whole dashboard answers. The source bar names the data on this page: Central Bank of Sri Lanka daily wholesale prices (monthly average) and ERA5-Land rainfall. "Exploratory · not proof of cause" on the right is a standing reminder.],
  ["So here is our question: can last month's rain warn us about next month's price? Let's look for a pattern."])

== Where the numbers come from

*Prices.* The Central Bank of Sri Lanka publishes daily wholesale prices, which we obtained through Macro Lab. For each month we average the daily Dambulla prices, but only when the month has at least 10 days of prices; otherwise the month is left empty. Prices are in rupees per kilo and are not adjusted for inflation. Each vegetable has 123 monthly prices.

*The cards* are calculated live from those monthly prices. The "biggest move" compares each month only with the month directly before it, so a gap in the data never creates a false jump.

*Rain.* ERA5-Land is a weather dataset from the European Copernicus programme. It combines a weather computer model with real observations to give rainfall for every square of a grid covering Sri Lanka, every hour, since 2010. We add up each month's rain. Sri Lanka has 541 land squares. The "whole island" bars are the average over all of them; the area bars average a box about 0.3 degrees (roughly 33 km) each way around each place.

*Values for each vegetable* (so you know what the cards will say):

#table(
  columns: (1.15fr, 1fr, 1fr, 1.15fr, 0.8fr, 0.6fr),
  align: (left, center, center, center, center, center),
  table.header([Vegetable], [Cheapest], [Dearest], [Biggest move], [Swings over 20%], [Gap]),
  [Cabbage], [Rs 16, Jan 2017], [Rs 452, Jan 2024], [158% rise, Nov 2023], [6 in 10], [28×],
  [Brinjal], [Rs 24, Mar 2017], [Rs 462, Jan 2024], [163% rise, May 2019], [6 in 10], [19×],
  [Carrot], [Rs 52, Feb 2017], [Rs 1,038, Jan 2024], [196% rise, Jan 2024], [5 in 10], [20×],
  [Tomato], [Rs 17, Sep 2018], [Rs 557, Feb 2024], [362% rise, Jun 2024], [7 in 10], [34×],
  [Snake gourd], [Rs 22, Aug 2016], [Rs 344, Dec 2025], [174% rise, May 2022], [6 in 10], [16×],
  [Pumpkin], [Rs 13, Jan 2019], [Rs 240, Feb 2024], [165% rise, Jun 2021], [6 in 10], [18×],
  [Beans], [Rs 53, Jan 2017], [Rs 718, Dec 2025], [179% rise, May 2024], [5 in 10], [14×],
)

== What this page supports

It establishes that the swings are large, frequent, and different for each vegetable. That makes forecasting both worthwhile and hard. It also shows that rain is uneven in place and time, which is why rain *might* carry information about supply. It does not show any link yet; that is page 2.

== How to demonstrate it

+ Leave *Cabbage* selected and let people read the four cards.
+ Click *Beans*, then *Tomato*. Every card and the chart change. Point out that every vegetable swings, by different amounts.
+ Turn *Show rainfall underneath* off and on, so people see rain and price on the same timeline.
+ Click *Dambulla*, *Nuwara Eliya* and *Colombo*: the rain bars change and the square on the map becomes solid.
+ On the map, drag the slider through a few months. Then choose *Long-term monthly average* and slide from May to October. The south-west turns dark blue in the May to September monsoon; the north and east get their rain later in the year.
+ Finish on the coral question.

== What to say

#say["This is the wholesale price of cabbage at Dambulla, one of the country's main vegetable markets, every month since 2016. Look at the cards. In its cheapest month, cabbage sold for about 16 rupees a kilo. In its dearest month, about 452. That is roughly a 28-times gap. And in six months out of ten, the price moved by more than a fifth from one month to the next.

Let me switch to beans... and tomato. Every vegetable swings, but each in its own way.

On the right is where the rain falls. Darker blue means more rain. It is not even: the south-west is soaked during the May monsoon, while the dry zone around Dambulla gets much less. The squares mark Dambulla, Nuwara Eliya and Colombo. Dambulla and Nuwara Eliya are the two areas whose rain we also tested in our study; Colombo is there for comparison.

Underneath the price I have put the rain. So here is our question: can last month's rain warn us about next month's price? Let's look for a pattern."]

== Questions you may be asked

#qa[Why Dambulla?][It is one of Sri Lanka's main wholesale collection points for vegetables from the growing regions, so its prices react quickly to changes in supply. We also checked our main result on Pettah market in Colombo (page 3).]

#qa[Why monthly averages and not daily prices?][Daily prices are noisy: a single late truck can move a day's price. Rain affects crops over weeks. Monthly averages smooth out the noise and match monthly rainfall totals. A month is only used if it has at least 10 days of prices.]

#qa[Are these prices adjusted for inflation?][No. They are the prices as published. We did not have a consumer price index in the project. This does not affect our main test, because both forecasts we compare predict the same unadjusted prices. But it does mean the 28-times gap is not all a "real" price rise; the period includes the 2022 economic crisis and high inflation.]

#qa[Why was January 2024 so expensive?][We did not model the causes of individual months. What we can say is that October to December 2023 were much wetter than usual across the island, and our forecast that used rain predicted much of the January jump while the prices-only forecast did not. That is consistent with a supply effect, but it is not proof of cause.]

#qa[What is ERA5-Land? Is it real data?][It is a "reanalysis" from the Copernicus Climate Data Store: a weather model that is continuously corrected using real observations. It gives complete, gap-free rainfall for every grid square every hour. It is widely used in research. It is not the same as a rain gauge on a farm, which is one of our stated limitations.]

#qa[Why do some coastal areas look blocky or missing on the map?][Each square is about 11 km across, and the dataset decides for each square whether it is land or sea. Its coastline is coarser than the real one. We hide squares that are entirely over the sea, so the map shows only land, but the edges are still blocky.]

#qa[Why is Colombo on the map if you did not test it?][It was added so viewers can compare the wet south-west with the drier areas. The Colombo rainfall was not used in any forecasting test, and we do not draw any conclusion from it.]

#qa[Did you check the rainfall data?][Yes, carefully. The first processed rainfall file was wrong by a factor of 12 to 21, because the dataset stores rain as a running total through each day and the original script added up the running totals. We rebuilt every rainfall series with the correct method and only use the corrected data. An automated test checks that the map reproduces our rainfall series to within half a millimetre.]

#dont[That rain *causes* these swings (the chart only puts them side by side). That the 28-times gap is a real price rise (prices are not adjusted for inflation). That Colombo rainfall was part of the study.]

= Page 2: Spot the pattern yourself

*Act:* The problem. *Time:* about two minutes. A good page to hand the mouse to a visitor.

== Purpose

To let the viewer *find a clue themselves*: for some vegetables, a wetter-than-usual month tends to come before a price rise about a month later. The page also teaches caution: a pattern is a clue, not proof.

== The page, part by part

#shot("images/p2_full.png", [Page 2 with cabbage selected and rain from one month earlier.])

#part("images/p2_controls.png", [1. The vegetable buttons and the "Rain from" slider],
  [Pick a vegetable, then choose how long before the price change the rain is taken from: the same month, or one, two or three months earlier. It starts at one month earlier.],
  ["Here you choose how long rain takes to show up in the price. Let's start with the rain from one month earlier."])

#part("images/p2_cards.png", [2. The four cards],
  [Blue: the *strength* of the link in a word, here "Strong", with the correlation in the chip, r = +0.60 on a scale from −1 to +1. Orange: the *direction*, "Wetter → dearer", meaning wetter months come before higher prices. Purple: the *delay with the strongest link* for this vegetable, one month earlier. Green: the *number of months compared*, 122, from September 2016 to October 2026.],
  ["For cabbage, with the rain from a month earlier, the link is strong: about 0.6 on a scale where 1 would be a perfect line. And it goes the way you might expect: wetter months come before higher prices."])

#part("images/p2_scatter.png", [3. The scatter chart],
  [Every dot is one month. Left to right: how much wetter or drier than usual the rain was, measured in standard deviations (0 is a normal month, +1 clearly wetter, −1 clearly drier). Up and down: how much the price changed compared with the normal change for that time of year, in percent. The orange line is the straight line that fits the dots best; it slopes upwards, so wetter months tend to come before price rises. Hovering a dot shows its month.],
  ["Every dot is a month. Further right means wetter than usual; higher up means the price jumped more than usual. See how the dots climb from bottom left to top right? Wet months tend to be followed by price rises. Now watch what happens if I use the rain from the same month... the pattern disappears."])

#part("images/p2_bars.png", [4. All seven vegetables], w: 80%,
  [The same link for every vegetable at the chosen delay, sorted from strongest to weakest. The selected vegetable is pink. At one month: cabbage +0.60, carrot +0.44, brinjal +0.40, then tomato, snake gourd, pumpkin, and beans at only +0.08.],
  ["Across all seven, cabbage, carrot and brinjal show the clearest link. Beans shows almost nothing. Keep these three in mind, because they come back on the next page."])

#part("images/p2_bottom.png", [5. The warning and the source bar],
  [The coral line says the pattern is only a clue. The small print explains why: seven vegetables times four delays is 28 links, and some will look strong just by chance. Source: Central Bank of Sri Lanka Dambulla wholesale prices and ERA5-Land national rainfall.],
  ["But be careful. With 28 links to look at, a few can look strong by luck. So this is a clue, not proof. On the next page we put it to a proper test."])

== Where the numbers come from

For each vegetable, month by month:
+ *Price change:* the change in the logarithm of the monthly average price, which is close to the percentage change.
+ *Remove the normal seasonal change:* some months always see prices rise or fall. We subtract the average change for that calendar month, so what remains is how *unusual* the change was.
+ *Rain:* the island-wide rain for the month, measured as how many standard deviations above or below the average for that calendar month it was. (A standard deviation is the typical spread; +1 means clearly wetter than usual, +2 very much wetter.)
+ *Correlation:* how closely the price changes line up with the rain from the chosen number of months earlier. It runs from −1 (perfectly opposite) through 0 (no straight-line link) to +1 (perfectly together).

The words come from fixed cut-offs: *Strong* if the correlation is 0.55 or more (ignoring sign), *Moderate* from 0.35, *Weak* from 0.15, otherwise *Barely any*.

#table(
  columns: (1.2fr, 1fr, 1fr, 1fr, 1fr),
  align: (left, center, center, center, center),
  table.header([Vegetable], [Same month], [1 month earlier], [2 months earlier], [3 months earlier]),
  [Cabbage], [+0.10], [*+0.60*], [+0.16], [−0.06],
  [Carrot], [−0.06], [*+0.44*], [+0.20], [0.00],
  [Brinjal], [+0.03], [*+0.40*], [−0.29], [+0.18],
  [Tomato], [+0.19], [+0.26], [+0.01], [−0.26],
  [Snake gourd], [+0.16], [+0.20], [−0.15], [−0.14],
  [Pumpkin], [+0.02], [+0.14], [+0.04], [−0.07],
  [Beans], [+0.21], [+0.08], [+0.03], [−0.09],
)

These are exactly the values from our earlier data audit, and an automated test checks the page reproduces all 28 to within 0.01. There are 122 months, not 123, because a change needs two months.

== What this page supports

It shows that, *at a one-month delay*, wetter months tend to come before price rises for cabbage, carrot and brinjal, and hardly at all for beans. In the audit, 10 of the 28 correlations were statistically significant when about 1.4 would be expected by chance alone. It is a description of the past, not a forecasting result. Page 3 is the real test, and the same three vegetables come out on top there too.

== How to demonstrate it

+ Start on *Cabbage* with *1 month earlier*. The first card says *Strong*, and the dots climb from bottom left to top right.
+ Slide to *Same month*: the link drops to "Barely any". Slide to *2 months earlier*: weaker again. Ask: "So when does rain show up in the price?" About a month later.
+ Point to the bar chart: at one month, cabbage, carrot and brinjal lead, and beans is near zero.
+ Click *Beans* to show what "barely any link" looks like: a shapeless cloud.
+ End on the coral line.

== What to say

#say["Every dot here is one month. Left to right is how much wetter or drier than usual that month was across the island. Up and down is how much the cabbage price changed compared with a normal month for that time of year.

When I use the rain from one month earlier, the dots line up: a wet month tends to come before a price rise. The card says the link is strong, about 0.6, on a scale where 1 is a perfect line.

Now watch when I use the rain from the same month... the pattern disappears. So rain seems to show up in the price about a month later. And across the seven vegetables, cabbage, carrot and brinjal show the clearest links. Beans shows almost nothing.

But be careful. With seven vegetables and four delays we are looking at 28 links, and a few can look strong just by chance. So this is a clue, not proof. On the next page we put it to a proper test."]

== Questions you may be asked

#qa[What does r = 0.60 mean?][It is a correlation: a number from −1 to +1 for how closely two things move together in a straight line. 0.60 is a fairly strong positive link: wetter months tend to be followed by bigger price rises. It does not mean rain explains 60% of the price; squaring it gives about 36% of the variation in these adjusted price changes lining up with rain.]

#qa[Why does the link appear after one month and not in the same month?][One plausible explanation is that heavy rain damages crops and disrupts harvesting and transport, and the shortage reaches the wholesale market a few weeks later. That is a reasonable hypothesis, but our study does not test the mechanism.]

#qa[Why is brinjal negative at two months (−0.29)?][It could be a rebound: after a price spike, prices tend to fall back as supply recovers, so a wet month two months ago lines up with a fall now. It could also be chance; with 28 correlations, a few moderate ones are expected by luck. We do not build any claim on it.]

#qa[Why remove the seasonal change?][Prices rise in some months every year whatever the weather, for example around festivals or harvest gaps. Without removing that, we would be correlating two seasonal patterns rather than unusual rain with unusual prices.]

#qa[How do you know the pattern is not just luck?][On this page, we do not fully know; that is the point of the coral line. In our audit we used permutation tests: we shuffled the data thousands of times to see how often a correlation this strong appears by accident. Ten of 28 were significant at the 5% level against about 1.4 expected by chance. But the real check is page 3, where rain has to improve forecasts on months the model has not seen.]

#qa[Is the rain measure here the same as in the forecasting test?][No, and that is deliberate. Here, "usual" rain is the average over all years, which is fine for describing the past. The forecasting test on page 3 uses only *earlier* years to define "usual", so that no future information is used.]

#qa[Does a "Strong" link mean you can forecast prices?][Not by itself. A strong past correlation can still add nothing once you already know past prices. That is exactly what page 3 tests, and the answer there is more modest.]

#dont[That rain *causes* price rises. That a "Strong" link means prices can be forecast. That the brinjal two-month value means anything specific.]

= Page 3: Does rain help? Try it

*Act:* The test. *Time:* three to four minutes. This is the main page. Let visitors drive it if they want.

== Purpose

To answer the research question with evidence the viewer can explore. For each vegetable, it compares two forecasts of next month's price made every month for five years, one from past prices only and one that also knew the rain, and shows which missed by less and whether the difference is trustworthy.

== The page, part by part

#shot("images/p3_full.png", [Page 3 with the main settings: cabbage, rain over the whole island, Dambulla market.])

#part("images/p3_controls.png", [1. The settings],
  [The vegetable buttons; *Where rain is measured* (whole island, around Dambulla, or the hill country around Nuwara Eliya); and *Market* (Dambulla or Pettah in Colombo). Whole island and Dambulla are the main analysis. The other choices are checks that the result is not a fluke of one choice.],
  ["The main analysis uses rain across the whole island and prices at Dambulla. You can change both to check whether the result still holds."])

#part("images/p3_cards.png", [2. The four cards],
  [Blue: *typical miss, prices only*: on average the forecast from past prices alone missed the real cabbage price by Rs 52 a kilo. Green: *typical miss, adding rain*: Rs 42 a kilo, and the chip says the overall error was 20% smaller. Green: the *verdict*, "Clear help", which "survives strict checks". Purple: the *price landed inside our range* 8 times in 10 with rain (7 in 10 with prices only); a perfect 80% range would score 8. The second and third cards change colour with the verdict: green for clear help, light blue for a hint, grey for no clear effect, coral for no help.],
  ["Every month we made two forecasts of next month's price. Using only past prices, we missed cabbage by about 52 rupees a kilo in a typical month. Adding the rain that had already fallen brought that down to about 42: about a fifth smaller overall error. And that gain survives strict statistical checks, so we call it clear help."])

#part("images/p3_chart.png", [3. The forecast chart],
  [Navy line with dots: the real price each month from September 2021 to October 2026. Dotted grey line: what the prices-only forecast said the month before. Green line: what the forecast that also knew the rain said. Light blue band: the likely range around the rain forecast. Where green is closer to navy than grey is, rain helped that month.],
  ["Navy is what actually happened. Grey is the forecast from past prices only; green also knew the rain. Look at early 2024: the price shot up, and the forecast that knew about the very wet end of 2023 got much closer. It is not perfect: in December 2023 it overshot. But over all 62 months it missed by less."])

#part("images/p3_bars.png", [4. All seven vegetables],
  [For every vegetable, how much smaller the forecast error became when rain was added, with the verdict written beside each bar, sorted from most to least help. Green: clear help (cabbage +20%, brinjal +12%, carrot +8%). Light blue: a hint (tomato +5%). Grey: no clear effect (snake gourd and pumpkin, +2%). Coral: no help (beans, below zero). The small print: 62 real forecasts, September 2021 to October 2026, using only rain already observed.],
  ["Here are all seven side by side. Rain clearly helps cabbage, brinjal and carrot. Tomato looks a little better but not enough to trust. Snake gourd and pumpkin: no clear effect. And for beans, adding rain actually made the forecast slightly worse. So the answer depends on the vegetable, and that is the finding."])

#part("images/p3_source.png", [5. The small print and the source bar],
  ["Rain is only ever the rain already observed, never future rain" is the key fairness point. Source: Central Bank of Sri Lanka Dambulla and Pettah wholesale prices; ERA5-Land rainfall; backtest results from the study.],
  ["Every forecast only used the rain that had already fallen. Nothing from the future was used."])

== How the forecasts were made

#key[*Standing in the past.* Imagine it is the end of August 2021. We know every monthly price up to August and every month's rain up to August. We fit the models on that history and forecast September's price. Then we move to the end of September, refit with one more month, and forecast October. We repeat until October 2026. That gives 62 genuine forecasts per vegetable, each made without seeing the future.]

*The prices-only forecast* predicts next month's price from this month's price, last month's price, and the price in the same month last year (which captures the seasonal pattern). At each step it picks the best combination of these using only the past data.

*The rain forecast* is exactly the same, plus two rain numbers: how much wetter or drier than usual this month was, and the same averaged over the last three months. "Usual" means the average for that calendar month in *earlier* years only. Because everything else is identical, any improvement comes from the rain.

*The two error measures on the cards:*
- *Typical miss* (mean absolute error) is the average size of the miss in rupees per kilo. For cabbage: Rs 52 without rain, Rs 42 with.
- *Overall error* (root mean square error of the log price) weights big misses more heavily and treats misses as proportions of the price. The "% smaller overall error" is based on this. For cabbage it is 19.7%, shown as 20%. The two measures need not agree exactly, because they measure different things.

*The verdict* comes from statistical tests run in the study, not from the dashboard:
- *Clear help:* the error fell, and the improvement passed the Clark–West test (a test designed for comparing a model with a version of itself that has extra information) *after* a correction for testing seven vegetables at once (the Holm correction), *and* passed a bootstrap check that reshuffles blocks of months 4,000 times.
- *A hint, not proven:* the improvement passes before the correction for seven tests but not after.
- *No clear effect:* a small improvement that passes neither.
- *No help:* the error did not fall at all.

*The range* is the forecast plus the spread of the model's own past errors (from the 10th to the 90th percentile), so it should contain the real price about 8 times in 10.

== Values with the main settings (Whole island, Dambulla)

#table(
  columns: (1.15fr, 0.9fr, 0.9fr, 0.8fr, 1.3fr, 1fr),
  align: (left, center, center, center, left, center),
  table.header([Vegetable], [Miss, prices only], [Miss, with rain], [Error change], [Verdict], [Inside range (with / without rain)]),
  [Cabbage], [Rs 52], [Rs 42], [20% smaller], [Clear help], [8 / 7],
  [Brinjal], [Rs 62], [Rs 53], [12% smaller], [Clear help], [8 / 7],
  [Carrot], [Rs 85], [Rs 81], [8% smaller], [Clear help], [7 / 7],
  [Tomato], [Rs 95], [Rs 90], [5% smaller], [A hint, not proven], [7 / 7],
  [Snake gourd], [Rs 42], [Rs 41], [2% smaller], [No clear effect], [7 / 8],
  [Pumpkin], [Rs 28], [Rs 27], [2% smaller], [No clear effect], [8 / 8],
  [Beans], [Rs 79], [Rs 79], [2% larger], [No help], [8 / 7],
)

(The "inside range" values are rounded to whole months on screen; for example cabbage is 7.7 and 6.9 out of 10.)

== What changes with the other settings

These are *checks*, not separate findings. Error change in percent, with the verdict:

#table(
  columns: (1.5fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
  align: (left, center, center, center, center, center, center, center),
  table.header([Rain area, market], [Cab.], [Brin.], [Carr.], [Tom.], [Snake], [Pump.], [Beans]),
  [Island, Dambulla (main)], [19.7 C], [12.4 C], [8.2 C], [4.8 H], [1.8 N], [1.8 N], [−1.5 X],
  [Island, Pettah], [22.7 C], [9.7 C], [8.8 C], [7.2 H], [2.0 N], [2.2 N], [−2.9 X],
  [Dambulla, Dambulla], [18.3 C], [13.1 C], [8.2 C], [5.5 H], [2.8 H], [2.0 N], [−1.1 X],
  [Dambulla, Pettah], [21.7 C], [10.7 C], [8.8 C], [7.7 C], [3.5 H], [2.4 H], [−1.5 X],
  [Nuwara Eliya, Dambulla], [21.5 C], [11.8 C], [8.0 H], [5.4 H], [2.7 H], [1.1 N], [−2.1 X],
  [Nuwara Eliya, Pettah], [24.1 C], [9.6 C], [9.0 C], [7.6 H], [0.9 N], [2.4 N], [−2.9 X],
)

C = Clear help, H = A hint, not proven, N = No clear effect, X = No help.

*How to read it.* Cabbage and brinjal are "Clear help" in every version. Carrot is clear help in five of six. Beans is negative in every version. Tomato reaches "Clear help" in one version (Dambulla rain, Pettah market); because it is one check among many, we do not count it as a finding.

== What this page supports

It is the main evidence for the research question. For cabbage, brinjal and carrot, rain that has already fallen improves one-month-ahead forecasts beyond what past prices alone give, and the improvement survives strict tests and the regional and market checks. For snake gourd, pumpkin and beans it does not. Tomato is uncertain. The range card shows the honest limit: even the better forecast misses often.

== How to demonstrate it

+ Start on *Cabbage, Whole island, Dambulla*. Read the four cards from left to right.
+ Point at the chart: navy is what happened, dotted grey is the prices-only forecast, green also knew the rain. Point to early 2024, where the green line catches the spike better.
+ Point at the bar chart: green bars at the top, beans dipping below zero at the bottom.
+ Click *Beans*: the verdict turns coral, "No help". Let that land.
+ Click *Brinjal* and *Carrot* (clear help), then *Tomato* (a hint).
+ Switch *Where rain is measured* to *Hill country* and the *Market* to *Pettah*. The bar chart reorders slightly but the story holds.
+ Finish on the range card: even the better forecast lands inside its range only about 7 or 8 times in 10.

== What to say

#say["Every month from August 2021, we stood at the end of the month and made two forecasts of next month's price. One used only past prices. The other used the same past prices plus the rain that had already fallen. Then we checked which one missed by less. That gives 62 real forecasts for each vegetable.

For cabbage, the prices-only forecast missed by about 52 rupees a kilo in a typical month. Adding rain brought that down to about 42, about a fifth smaller overall error. And that gain survives strict statistical checks, so we call it clear help.

You can see it in the chart: here in early 2024 the price spiked, and the forecast that knew about the very wet end of 2023 got much closer.

The bar chart shows all seven side by side. Cabbage, brinjal and carrot are clear gains. Tomato looks a bit better but not enough to trust. Snake gourd and pumpkin, no clear effect. And beans: rain made it slightly worse.

If I change where the rain is measured, or switch to the Pettah market in Colombo, the picture stays much the same, so the result is not a fluke of one choice.

And the last card is the honest part: even the better forecast is often off. The real price fell inside our 80 percent range about seven or eight times in ten. So rain helps for some vegetables, but it does not make prices predictable."]

== Questions you may be asked

#qa[Is this a real test or are you fitting the past?][It is a real out-of-sample test. Each forecast used only data available at that moment, and the model was refitted from scratch every month. Rain from the month being forecast was never used. One honest caveat: an early pilot version of the study had already looked at the same period, so we call the results exploratory rather than a fully fresh confirmation.]

#qa[Why does the error drop 20% while the typical miss drops from 52 to 42 rupees (about 18%)?][They are different measures. The typical miss is the average rupee error. The 20% is based on the root mean square error of the log price, which counts big misses more heavily and measures misses as proportions. We use the second for the verdict because large misses matter most, and the first on the card because rupees are easy to understand.]

#qa[What exactly does "Clear help" mean?][The forecast with rain had a lower error, and three things held. First, the Clark–West test, which is designed for comparing a model with a bigger version of itself, found the improvement significant. Second, that stayed true after the Holm correction for having tested seven vegetables. Third, a block bootstrap, which rebuilds the 62 months from random blocks 4,000 times, agreed. All three had to pass.]

#qa[Why not use the usual Diebold–Mariano test?][Because our two models are nested: the rain model is the prices-only model plus two terms. In that case Diebold–Mariano is biased against the bigger model, since estimating the extra terms adds noise even when rain genuinely helps. Clark–West corrects for that. We still report Diebold–Mariano as a supplement, and it agrees for cabbage, brinjal and carrot.]

#qa[Why is tomato only "a hint"?][Tomato's improvement (4.8%) is significant if you look at tomato alone (p = 0.027), but we tested seven vegetables. After correcting for that, its p-value is 0.109, above the 0.05 line. Its gain also disappears in the second half of the test period.]

#qa[Why is tomato "Clear help" with Dambulla rain and Pettah?][That is one of several checks we ran, not the main analysis. If you run enough versions, one will pass by chance. The main tomato result is not significant, so we do not claim a tomato finding.]

#qa[Why did rain make beans worse?][Rain added no useful information for beans, and estimating two extra terms adds a little noise, so the forecast got slightly worse (1.5%). It suggests bean prices are driven by other things, or by rain somewhere we did not measure.]

#qa[Why is island-wide rain the main measure and not rain where the crops grow?][Dambulla receives vegetables from many regions, and we did not have exact growing-area boundaries. So we fixed the island average as the main measure in advance and used hand-drawn boxes around Dambulla and Nuwara Eliya as checks. The checks gave similar results; rain around Nuwara Eliya worked slightly better for cabbage, which grows in the hill country.]

#qa[Why does Nuwara Eliya rain make carrot only a hint with Dambulla prices?][Carrot's gain is about the same (8.0% against 8.2%), but the statistical evidence is a little weaker in that version, so it falls just short of the strict bar. Carrot was always the most borderline of the three clear results.]

#qa[Is Pettah an independent confirmation?][Not really. Pettah shares the same weather and much of the same supply chain, so it is a consistency check: the same frozen model, nothing tuned on Pettah, and the same pattern. A truly independent check would be new months published after the study.]

#qa[What is the range, and why should it contain the price 8 times in 10?][It is an 80% range: the forecast plus the spread of the model's own past errors, from the 10th to the 90th percentile. If it were perfectly calibrated it would contain the real price 8 times in 10. Ours do so about 7 to 8 times in 10, so they are a little too narrow, mainly because the error history was short at the start and 2022 had large errors.]

#qa[Why does the rain forecast sometimes overshoot, as in December 2023?][It is not perfect. For December 2023 it forecast about Rs 527 when the price was Rs 323. Over all 62 months, though, its misses are smaller on average for cabbage, which is what the 20% measures.]

#qa[Why not use machine learning?][Our question is whether rain adds information beyond past prices. A simple model with and without rain answers that directly and fairly, and its results can be explained. With only about 110 training months per vegetable, a complex machine learning model would easily fit noise. A fancier model would also make it harder to see where an improvement comes from.]

#qa[Why not include the exchange rate?][We tried it in the pilot. Adding the exchange rate made the forecasts worse for all seven vegetables (by between 1.8% and 16.7%), so it was left out. Most of these vegetables are grown locally. The exchange rate appears only as context on page 4.]

#qa[Could you forecast two or three months ahead?][Not with this design. Forecasting further ahead would need the rain of future months, which means using rainfall *forecasts*. That is a separate study.]

#qa[Why use the logarithm of the price?][Vegetable prices move in proportions: a rise from 100 to 200 rupees is the same kind of event as from 200 to 400. The logarithm turns proportional changes into equal steps, so expensive months do not dominate the model, and an error of 0.1 is roughly a 10% miss.]

#qa[With only 62 forecasts, can you trust this?][It is a modest sample, and neighbouring months are related, which we allowed for with Newey–West standard errors and the block bootstrap. That is exactly why we require several tests to agree before saying "clear help", and why we call the result exploratory.]

#dont[That rain *causes* price changes (better forecasts show information, not cause). That this is a working price-prediction tool. That the regional or Pettah views are new findings. That tomato is helped by rain.]

= Page 4: Rain is only one piece

*Act:* The bigger picture. *Time:* about one and a half minutes.

== Purpose

To step back. Vegetable prices are part of a wider food system. This page shows three other pressures on food in Sri Lanka, the rice harvest, rice imports and the exchange rate, each on its own. None of them feeds the forecasting test.

== The page, part by part

#shot("images/p4_full.png", [Page 4: three other pressures on food, shown separately.])

#part("images/p4_cards.png", [1. The three cards],
  [Green: *wetter growing seasons, better paddy harvests*: correlation +0.68 between Yala-season rain and the share of sown rice land that was harvested, over 16 seasons, "a link, not proof". Orange: *rice bought from abroad, peak year*: 30% of rice supply was imported in 2017, against 4% in 2024. Purple: *rupee price of one US dollar*: about Rs 333 now, up 75% since January 2021.],
  ["Three other forces matter for food. Wetter rice seasons go with better harvests. In bad years Sri Lanka imports up to about a third of its rice. And the rupee has lost a lot of value since 2021."])

#part("images/p4_harvest.png", [2. Weather and the rice harvest], w: 62%,
  [Each dot is one Yala season (March to August), 2010 to 2025. Left to right: season rain compared with the usual, in millimetres. Up and down: the share of sown land that was harvested, compared with the usual. Both have their long-run trend removed. The green line slopes upwards. The lonely dot at the bottom left is a very dry season with heavy crop loss. The note says this is a short series and only an association.],
  ["In seasons that were wetter than usual, a bigger share of the planted rice fields was actually harvested. In a drought, farmers plant but some fields fail. But this is 16 seasons, so it is a link, not proof."])

#part("images/p4_imports.png", [3. Rice imports], w: 62%,
  [The share of rice supply that was imported each year, 2010 to 2024. The coral bar is the peak, 2017 (about 30%). The other tall bars are 2014 (about 20%) and 2022 (about 26%). The note says the conversion from paddy to milled rice (0.67) is our assumption.],
  ["Most years Sri Lanka grows almost all its rice. But after poor harvests, in 2014 and 2017, and in the 2022 crisis, imports jumped to a fifth or more of supply."])

#part("images/p4_fx.png", [4. The exchange rate], w: 62%,
  [Rupees per US dollar, monthly, from 2010. A slow rise until 2021, then a sudden jump in 2022 (shaded, "2022 crisis") to over 350, and about 333 now. The note says we do not estimate how much of this passed through into food prices.],
  ["In 2022, during the economic crisis, the rupee fell sharply: a dollar went from about 200 rupees to over 350. That makes everything imported more expensive. We show it as context; we do not claim how much it raised vegetable prices."])

#part("images/p4_source.png", [5. The source bar],
  [ERA5-Land; Department of Census and Statistics paddy statistics; FAOSTAT; Central Bank of Sri Lanka exchange rates. "Context only; none feeds the forecasts" means none of these three is used in the forecasting test on page 3.],
  ["These three are shown side by side on purpose. They are separate pressures, measured in different ways, so I am not combining them into one score."])

== Where the numbers come from

*Rice harvest.* The Department of Census and Statistics publishes rice (paddy) statistics for each season. Yala is the season from about March to August. For each Yala season from 2010 to 2025 we took the share of sown land that was harvested (a good drought indicator, because in a dry season some planted fields fail) and the total ERA5-Land rain for March to August. Both have their long-run trend removed, so that two series that simply rise over time do not look linked. Sixteen seasons give a correlation of +0.68.

*Rice imports.* The imported share is imports divided by (domestic rice plus imports). Domestic rice is paddy production times 0.67, because milled rice is about two thirds of the weight of paddy; this factor is our assumption. Imports come from FAOSTAT (the Food and Agriculture Organization's database), which agrees almost exactly with UN Comtrade. Peaks: 2017 (29.5%), 2022 (25.6%) and 2014 (20.1%).

*Exchange rate.* The Central Bank of Sri Lanka's daily indicative rupee to US dollar rate, averaged by month. The latest month shows about Rs 333; January 2021 was about Rs 190, hence +75%. The highest monthly average was about Rs 363 in November 2022.

== What this page supports

That rain and food prices are connected in more than one way, and that vegetables are not the only story. It shows each pressure separately on purpose: they are measured differently, on different timescales, with small samples, so combining them into one score would be misleading.

== How to demonstrate it

+ Read the three cards across the top, one sentence each.
+ Hover a dot in the left chart, the coral bar in the middle chart and the 2022 jump in the right chart.
+ Say clearly that these three are shown side by side on purpose and not added together.

== What to say

#say["Vegetable prices are only part of the food story. Three other forces matter.

First, weather and rice. In growing seasons that were wetter than usual, a bigger share of the planted rice fields was actually harvested. Over 16 seasons the correlation is about plus 0.68. That is a link, not proof, because 16 seasons is a short series.

Second, imports. In bad years Sri Lanka buys a lot of rice from abroad: up to about 30 percent of supply in 2017, after a poor harvest. In normal years it is only a few percent.

Third, the rupee. A US dollar cost about 190 rupees at the start of 2021 and about 333 now, after the 2022 economic crisis. That makes everything imported more expensive.

These are three separate pressures. I am deliberately not combining them into one score."]

== Questions you may be asked

#qa[Why rice, when the study is about vegetables?][Rice is the staple food, and it is where the original idea came from: weather affects the harvest, a poor harvest means more imports, and the rupee affects what imports cost. We found the data too thin to test that chain properly (14 to 16 yearly points), so it became context rather than the main study.]

#qa[What does "trend removed" mean, and why?][Both rain and harvests can drift over time for unrelated reasons, such as new rice varieties or irrigation. Removing a straight-line trend from each means we compare whether a season was wetter *than expected* with whether the harvest was better *than expected*.]

#qa[Why the share harvested and not the yield or production?][The share of sown land that is harvested is the most direct sign of crop failure in a dry season. Rain against yield was weak in our data (−0.16), and rain against production weaker than against the harvested share. We tested several and report the clearest, which is why we call it suggestive only.]

#qa[Why did imports peak in 2014, 2017 and 2022?][2014 and 2017 were years of low domestic rice production, after poor seasons. 2022 was the economic crisis. Without 2017 and 2022, the yearly link between low production and high imports weakens from −0.79 to −0.46, so two events drive much of the pattern.]

#qa[Where does the 0.67 come from?][It is the approximate weight of milled rice obtained from a given weight of paddy (rice in its husk). It is a standard approximation, but in our project it is an assumption, not a measured figure, and the chart says so.]

#qa[Is this a self-sufficiency rate?][No. It is an apparent import share. We do not have data on stocks, waste, seed or animal feed, which a true self-sufficiency calculation needs.]

#qa[Does the exchange rate drive vegetable prices?][We cannot say how much. Rice and some imported foods moved with the rupee in the same month and the next, but 2022 also had very high general inflation, and without a consumer price index we cannot separate the two. For our seven vegetables, adding the exchange rate made forecasts worse, which suggests it does not add information for these mostly local crops.]

#qa[What happened in 2022?][Sri Lanka had a severe economic crisis. The rupee, which had been held near 200 per dollar, was allowed to float in March 2022 and fell sharply, reaching about 363 per dollar (monthly average) by late 2022. Food prices rose steeply at the same time.]

#dont[That rain explains rice imports. That the exchange rate explains vegetable prices. Any combined "vulnerability index".]

= Page 5: What did we learn?

*Act:* The bigger picture. *Time:* about one minute, then questions.

== Purpose

A clear, memorable ending. The visitor first guesses which vegetable rain helps most, then reveals three findings. Committing to a guess makes people pay attention to the answer.

== The page, part by part

#grid(columns: (1fr, 1fr), gutter: 10pt,
  shot("images/p5_before.png", [Before the reveal.]),
  shot("images/p5_after.png", [After the reveal, with cabbage guessed.]))

#part("images/p5_question.png", [1. The guess and the button], w: 70%,
  ["Ready for the answer? One click, three findings." Then the question "First, your guess: which vegetable does rain help most?" with the seven vegetables as buttons (choosing one is optional), and the dark *Wanna see the conclusion?* button. The *Next* button at the bottom is greyed out because this is the last page.],
  ["Before I show you: which vegetable do you think rain helps most? Pick one."])

#part("images/p5_guess.png", [2. The guess result],
  [After the reveal, a strip answers the guess. Cabbage gives "Spot on: rain helped cabbage most, 20% smaller errors." Brinjal or carrot gives "Close": rain helps it, but cabbage gained most. Any other vegetable gives "A fair guess, but rain gave it no gain we can trust." With no guess, there is no strip. A short burst of confetti plays once, only when the button is clicked.],
  ["Let's see... spot on! Rain helped cabbage the most." Or, for a wrong guess: "A fair guess, but rain gave it no gain we can trust. Cabbage gained most."])

#part("images/p5_cards.png", [3. The three findings],
  [Green, *8–20% smaller errors*, "Rain helps some vegetables": for cabbage, brinjal and carrot, knowing last month's rain made next month's forecast clearly better. Pink, *about 25% typical miss* (shown as "\~25%"), "…but not all, and not precisely": tomato, snake gourd, pumpkin and beans showed no gain we can trust, and even the best forecasts miss by about a quarter of the price. Blue, *Next: test on new months*, "What it means": a research finding about where rain carries information, not a price app; next, check it on months not yet published and use rain from the farms themselves. The *Hide again* link underneath resets the page for the next visitor.],
  ["Three things. One: rain helps some vegetables, 8 to 20 percent better forecasts for cabbage, brinjal and carrot. Two: not all, and not precisely; even the best forecasts miss by about a quarter. Three: this is a research finding, not a price app. Next we would test it on new months and use rain from where the vegetables grow."])

== Where the numbers come from

All are read from the stored results for the main analysis (Dambulla, island-wide rain). "8–20%" is the range of error reductions for the three vegetables labelled clear help (8.2% carrot to 19.7% cabbage). "About 25%" is the median, across the seven vegetables, of the typical miss as a share of the price, with rain (24.8%). The "best" vegetable is the clear-help vegetable with the largest gain, which is cabbage.

== What this page supports

It states the conclusion of the whole study in three parts: rain helps some vegetables; not all, and not precisely; and it is a research finding with a clear next step, not a product.

== How to demonstrate it

+ Pause on the question. Ask the visitor: "Which vegetable do you think rain helps most?" Let them click their guess.
+ Click *Wanna see the conclusion?* Read the guess result aloud.
+ Read the large number on each card, then its heading.
+ Leave the page up during questions. Click *Hide again* before the next visitor.

== What to say

#say["Before I show you, which vegetable do you think rain helps most? ... Let's see if you were right.

Three things.

One: rain helps some vegetables. For cabbage, brinjal and carrot, knowing last month's rain made next month's forecast 8 to 20 percent better, and that survives strict checks.

Two: not all, and not precisely. The other four gained nothing we can trust, and even the best forecasts still miss by about a quarter of the price.

Three: this is a research finding about where rain carries information. It is not a price app. The next step is to test it on months that have not been published yet, and to use rain measured where the vegetables actually grow."]

== Questions you may be asked

#qa[Why do you say it is not a price app?][Because even the best forecast misses by about a quarter of the price in a typical month, and its ranges are a little too narrow. The finding is that rain carries *some* information for *some* vegetables, which is useful to know, but not accurate enough to set prices or make trading decisions on.]

#qa[What would make the result stronger?][Three things. A fresh test on months published after the study, since our test period was partly seen in a pilot. Rainfall from the actual growing areas instead of the island average. And a consumer price index, so prices can be adjusted for inflation.]

#qa[Who could use this?][Researchers and planners interested in which crops are most sensitive to weather, for example for early warning of price spikes in cabbage, brinjal and carrot after unusually wet months. It points to where rain information is worth collecting and using.]

#qa[Why the guess and the confetti?][It is a public gallery. Asking for a guess makes people think before they see the answer, and the confetti gives the visit a clear ending. The text itself stays as cautious as the evidence, and a wrong guess is answered honestly.]

#dont["Rain predicts vegetable prices." Say instead: "For three of seven vegetables, past rain improves one-month-ahead forecasts." No causal claims.]

= General questions about the whole project

#qa[What is your research question?][Does adding rainfall information improve short-term forecasts of selected vegetable prices in Sri Lanka, and does the improvement differ between vegetables?]

#qa[Why did you choose this topic?][We started with a broader idea, how weather affects rice production, imports and food prices. After checking every dataset, the vegetable price question had by far the most data (about 120 months for seven vegetables), enough for a proper forecasting test, while the rice chain had only 14 to 16 yearly points.]

#qa[What data did you use?][Daily wholesale prices from the Central Bank of Sri Lanka (via Macro Lab), ERA5-Land rainfall from the Copernicus Climate Data Store, rice statistics from the Department of Census and Statistics, rice trade from FAOSTAT (checked against UN Comtrade), and exchange rates from the Central Bank of Sri Lanka. Each page names its sources in the source bar.]

#qa[Which data did you reject, and why?][CHIRPS satellite rainfall (only one day was available), HARTI weekly price bulletins (long gaps, duplicates, and a different price definition), and the World Bank food price file (mostly modelled estimates rather than observed prices).]

#qa[What was the hardest problem?][Discovering that the original rainfall processing was wrong by a factor of 12 to 21, because ERA5-Land stores rain as a running total through each day. We rebuilt every rainfall series with the correct method.]

#qa[What are the main limitations?][The test period was partly seen in a pilot, so results are exploratory. Rain is averaged over the island or large boxes, not measured on farms. 62 forecasts per vegetable is a modest sample. Prices are not adjusted for inflation. Only rain is modelled, not transport, policy or the 2022 crisis. And only one month ahead.]

#qa[Did you use artificial intelligence?][An AI coding assistant helped write and debug the dashboard code and check wording. All data comes from the official sources listed. The research question, the choice of models and tests, and the interpretation are our own, and every number on the dashboard is read from the analysis results and checked by automated tests.]

#qa[How do you know the numbers on the dashboard are right?][Nothing on the dashboard is typed in by hand: every number is read from the stored analysis outputs when the page loads. 28 automated tests check, for example, that the cabbage card shows 19.7% and "Clear help", that page 2 reproduces the audited correlation table, and that the rain map reproduces our rainfall series. An earlier audit checked all 55 numbers in a previous version against the analysis outputs.]

#qa[What tools did you use?][Python, with pandas and NumPy for the analysis and xarray for the weather files; Streamlit and Plotly for the dashboard.]

= A full run-through in five minutes

#table(
  columns: (0.7fr, 1fr, 2.5fr),
  table.header([Time], [Page], [What to do and say]),
  [0:00], [1], [Cabbage cards: 16 to 452 rupees, 28 times, 6 in 10 months. Click beans and tomato. Show the rain map. Ask the question.],
  [1:30], [2], [Cabbage, one month earlier: "Strong". Slide to same month: it disappears. Bar chart: cabbage, carrot, brinjal. "A clue, not proof."],
  [3:00], [3], [Cabbage: 52 to 42 rupees, clear help. Chart: early 2024. Bar chart of all seven. Click beans: no help. Mention the checks. Range card: 7 or 8 in 10.],
  [4:15], [4], [Three cards in one sentence each. Not combined.],
  [4:45], [5], [Ask for a guess. Reveal. Three findings. Hide again for the next visitor.],
)

#key[*If you forget everything else:* rain helps forecast cabbage, brinjal and carrot prices one month ahead, by 8 to 20 percent; it does not help the other four; even the best forecasts miss by about a quarter; and better forecasts do not prove that rain causes price changes.]
