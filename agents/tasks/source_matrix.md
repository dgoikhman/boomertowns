# Task: national data-source coverage matrix (comprehensive, batched)

Build the definitive matrix of succession-relevant public data sources.
Work in batches of 10 states per run so PRs stay reviewable. Read
data/research/source_matrix.csv first (if present) and continue from the
first state (alphabetical) not yet covered; also add national sources
(FMCSA carrier census, SBA 7a/504 FOIA files) on the first run only.

For each state, research via WebSearch and record one row per source:
state, source_type (sos_registry | contractor_board | professional_board |
ucc | national), agency, bulk_available (yes/no/api), format, cost,
update_frequency, fields_of_interest (issue/filing dates? status? NAICS or
classification?), url, confidence (high/med/low), notes.

Rules: every row needs a source URL you actually found; mark confidence
honestly; if a state sells only through resellers or requires FOIA, say so
with the mechanism; never guess prices — write "unlisted" instead.
Write/append data/research/source_matrix.csv, then open a PR on branch
research/sources-<batch> whose body ranks this batch's states by
value-for-effort (bulk quality × business count) in one line each.
