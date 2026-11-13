# Research story: materials

Everything that goes with the dashboard but is not needed to run it. The app itself is in the sibling folder **`../research-story/`** (see its README for how to run it).

```
research-story-materials/
├── story_pages/     speaking guides, one per page (5 files)
├── docs/            story map, claim audit and register, data sources, method references,
│                    and the design note and build plan (docs/superpowers/)
├── tests/           automated checks for the app
├── scripts/         tools that rebuild or check data (some need the full research project)
├── archive/         the earlier 10-slide version: PNG slides, guides, slide code
├── app2.py          a friend's general-purpose dashboard, kept for reference (ideas borrowed: scatter page, guess before reveal)
├── SUMMARY.docx     your summary document
└── Summary_ Sri Lanka Climate Intelligence Dashboard.pdf
```

## Speaking guides
Each file in `story_pages/` covers what to do on the page, what to say, the key points, what each card means, "If an evaluator asks" (the method), and what not to claim. Start with `03_does_rain_help.md`, which has the central result.

## Running the tests
The tests check the app in `../research-story/`, so run them with the app's environment:

```
cd ../research-story
uv run --with pytest pytest ../research-story-materials/tests
```

The tests check that the cards show the stored results (for example, cabbage: 19.7% smaller error, "Clear help"; beans: "No help"), that the rain map reproduces the national and Dambulla-area rain series, that the pattern page reproduces the audited lag table, and that every page runs.

## Scripts
Run these from inside `../research-story/`. All three need the full research project (`raw/`, `research_audit/`) one level up.

```
uv run python ../research-story-materials/scripts/audit_claims.py   # re-run the claim audit
uv run python ../research-story-materials/scripts/sync_data.py      # refresh research-story/data/ from the project
```

`build_rain_grid.py` needs `xarray`, so run it from the parent project instead:

```
cd ..        # the work/ folder
uv run python research-story-materials/scripts/build_rain_grid.py
```
