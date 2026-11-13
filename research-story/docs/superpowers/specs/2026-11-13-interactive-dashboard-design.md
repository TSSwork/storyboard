# Interactive dashboard redesign (short design)

**Intent.** The storyboard explains method; the audience (general public, internship evaluators) needs to *see* the finding by playing with it. Theory is spoken when evaluators ask, not shown.

**Goals.** Eye-catching but elegant KPI cards that react to widgets; plain-language labels; pages 4–8 merged into one dashboard; conclusion revealed by a "Wanna see the conclusion?" button with soft confetti; smooth page transitions.

**Non-goals / anti-goals.** No new models, commodities, horizons or claims; v2 outputs and raw data untouched. Must not oversell: null and negative results (beans worse, pumpkin/snake gourd no gain, tomato unclear, ~24% error even at best) show as plainly as wins. Not loud: no gradients-for-show, no shouting colours.

**Approaches.** (1) Streamlit + hand-drawn HTML/SVG cards + bundled confetti script — chosen: keeps the copy-and-`uv run` portability. (2) React/Vite rewrite — breaks portability. (3) Stock `st.metric` + `st.balloons` — looks cheap.

**Design (4 pages).**
1. Prices go wild — vegetable picker; KPIs: highest vs lowest monthly price, biggest one-month jump, share of months moving >20%; price + rain chart.
2. Does rain help? Try it — vegetable, rain region (whole island / Dambulla / Nuwara Eliya), rain window (where available), market; KPIs: typical miss without vs with rain (Rs/kg), change in error, how sure we are (strong / weak / none from the evidence label), price inside predicted range (x of 10); actual vs both forecasts chart; 7-vegetable verdict strip.
3. Wider picture — current page 9 plus KPI cards.
4. Conclusion reveal — button → confetti → takeaway cards staggered in.

Palette extends navy/soft blue/coral with calm companions (sage green for "helped", slate grey for "no change"); line icons as inline SVG; fade/slide transitions; reduced-motion respected. Speaking guides rewritten for 4 pages, carrying the technical depth.

**Left to the builder.** Exact copy, icon shapes, chart styling, which spec combinations exist in the data (show only those).
