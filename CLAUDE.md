# BoomerTowns — the Succession Index
Split from atlas-engine Sep 2026. City-level succession scores from public
state registries; business-level Roll-up Radar + Pro tools per SPEC.md.
House rules: no fabricated data; public registries + partnerships only
(never scrape LoopNet/BizBuySell); no owner names on public pages; claim/
correct/opt-out before any business-level page ships; revenue = labeled
modeled bands only. Commands: pipelines/mainstreet.py (city refresh),
pipelines/mainstreet_entities.py + classify.py (Pro data, gitignored),
site/build.py --base-url X.
