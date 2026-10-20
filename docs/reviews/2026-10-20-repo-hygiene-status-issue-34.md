# Status Report — Repo Hygiene (issue #34)

**Report ID**: C3
**Date**: 2026-10-20
**Repository**: `blix-scraper`
**Branch**: `chore/issue-34-repo-hygiene`
**Commit**: `a8bc7a2` — *docs: purge deleted orchestrator/storage references and fix examples*
**Scope**: Baseline verification (tests/lint/coverage), live-run regression matrix, consolidated defect register, prioritized backlog, roadmap corrections.
**Document class**: Review / status report (informational). **Not** a specification.

> **Source-of-truth policy**: `openspec/specs/cli/spec.md` remains the authoritative CLI
> specification. This report describes *conformance gaps against it*; it does not
> redefine CLI behavior. Where this report and the spec disagree, the spec wins.

---

## 1. Verdict

| Signal | State |
|---|---|
| Build health (clean tree) | ✅ Green — 688 passed / 2 skipped, 83% coverage |
| Lint & types | ✅ Green — ruff clean + formatted, mypy clean |
| Live smoke (3 scraper runs) | ✅ All exit 0, counts match baseline |
| Correctness of core logic | 🔴 **4 Critical defects** (retry dead, scroll unbounded, range semantics wrong, `full_shop` field filtering broken) |
| Documentation accuracy | 🔴 README/user-guide/api-reference/architecture document **removed** commands |
| Roadmap accuracy | 🔴 Stale by ~8 months; lists shipped work as pending |

**Assessment**: The repository is *mechanically* healthy but *behaviorally* weaker than the
green test suite implies. The three most consequential defects (C-02, C-03, C-04) are
invisible to the current test suite — coverage reports 83% while the retry decorator,
range predicate, and scroll loop are effectively unverified. Treat "83% / 688 green"
as an *activity* metric, not a *confidence* metric.

**Recommendation**: Do not close issue #34 on documentation hygiene alone. Fix C-02/C-03/C-04
(small, well-bounded changes) and purge the removed-command docs in the same PR series.

---

## 2. Baselines — verification method and numbers

### 2.1 Test suite

Two runs were performed, because the result is environment-dependent (see M-01).

| Tree state | Command | Result |
|---|---|---|
| Clean copy (no `.env`) — `/tmp/opencode/blix-clean` | `python -m pytest -q --cov=src --cov-report=term` | **688 passed, 2 skipped, 1 warning** in 66.54s |
| As-checked-out worktree (`.env` present) | same | **677 passed, 2 skipped, 11 failed** in 69.38s |

The 11 failures are **all** in `tests/test_config.py` (`TestEnvironmentVariables`,
`TestHierarchicalConfiguration`, `TestEnvironmentVariableOverrides`) and are caused by the
gitignored local `.env` file, not by the commit under review. The claimed A2 baseline
(*688 pass, clean*) is **reproduced only on a tree without `.env`**.

Root cause (verified by direct execution):

```
from /tmp (no .env)          -> Settings().scraping.retry.max_attempts == 5   # env var wins
from repo cwd (with .env)    -> Settings().scraping.retry.max_attempts == 3   # .env wins
```

`src/config.py:65-96` — `map_backwards_compatibility_fields` is a `mode="before"` validator
that runs on the *already merged* source values. The legacy flat key `MAX_RETRIES` supplied by
`dotenv` (`src/config.py:57-62`) is therefore mapped *after* the nested env var
`SCRAPING__RETRY__MAX_ATTEMPTS`, silently overriding it. The tests use
`@patch.dict("os.environ", {...}, clear=True)` (`tests/test_config.py:289`, `:300`, `:312`),
which clears `os.environ` but **not** `.env` — so the suite is non-hermetic.

> Practical consequence: a developer with a normal `.env` sees 11 red tests and will
> either chase a phantom regression or start ignoring the suite. Both are expensive.

### 2.2 Coverage

| Scope | Coverage |
|---|---|
| **Total** (`src/`) | **83%** (1643 stmts, 272 missed) |
| `src/webdriver/driver_factory.py` | **28%** ← weakest module, all browser construction untested |
| `src/webdriver/helpers.py` | 53% (`116-131` = `scroll_to_bottom`, uncovered) |
| `src/cli/__init__.py` | 73% |
| `src/domain/date_filter.py` | 100% — but see C-03: covered lines, wrong semantics |
| `src/scrapers/base.py` | 96% — but retry path never exercised (C-02) |

Note the juxtaposition: `date_filter.py` is at 100% coverage and still implements the
wrong range predicate, and `base.py` is at 96% while its retry predicate is unreachable
code. Line coverage is not asserting behavior here.

### 2.3 Lint and types

| Check | Command | Result |
|---|---|---|
| Lint | `ruff check src/ tests/` | ✅ `All checks passed!` |
| Format | `ruff format --check src/ tests/` | ✅ `49 files already formatted` |
| Types | `mypy src/` | ✅ `Success: no issues found in 26 source files` |

⚠️ Both ruff invocations emit a config deprecation warning:
`The top-level linter settings are deprecated ... 'select' -> 'lint.select'` (see L-03).

---

## 3. Live-run matrix

Three live browser runs (B2–B4) plus one config run (B1), all on commit `a8bc7a2`, headless.
"Baseline" is the value recorded in the C2 register.

| ID | Command | Exit | Observed (this pass) | Baseline | Match |
|---|---|---|---|---|---|
| B1 | `python -m src.cli config` | **0** | config table rendered (data dir, base URL, delays) | exit 0 | ✅ |
| B2 | `python -m src.cli scrape-shops --headless` | **0** | **Total: 261 shops** | 261 | ✅ |
| B3 | `python -m src.cli scrape-leaflets biedronka --headless` | **0** | **Total: 15 leaflets** | 15 | ✅ |
| B4 | `python -m src.cli search kawa --headless` | **0** | **2 of 22** offers (`filtered_out=20`, `final_count=2`) | 2 / 22 | ✅ |

**Runs B2–B4 reproduce the baseline deterministically.** Two incidental observations from
these runs became findings:

1. **B2 printed `bi1` twice** (identical slug, identical leaflet count 19). `261` is therefore
   a *row* count, not a *unique shop* count — see M-02.
2. **B4 logged `element_not_found` for `.offer-list` at 10s** (`src/webdriver/helpers.py:103-105`)
   yet the command still exited 0 and parsed 22 offers. The failure was swallowed by
   `src/scrapers/search_scraper.py:51-57`; parsing succeeded only because the offers live in a
   `window.offers` script tag. A stale selector is masked by a broad `except Exception` — see H-06.
3. Driver banner: `could not detect version_main ... assuming chrome 108 or higher`
   (chromedriver 146.0.7680.165 vs detected 146.0.7680.164). Benign today; fragile on upgrade.

---

## 4. Defect register

Severity: **C**ritical = wrong behavior in normal use / silent failure; **H**igh = user-visible
or maintenance-expensive; **M**edium = correctness/ergonomics risk; **L**ow = hygiene.
All items below were re-verified in this pass against source at `a8bc7a2`.

### 4.1 Critical

#### C-01 — `scrape-full-shop --fields/--exclude` is documented as nested but only accepts top-level keys

- **Evidence**: `src/cli/__init__.py:872-878` docstring promises
  `--fields name` "filters 'name' field in shop, leaflets, and offers".
  `src/cli/__init__.py:884-900` validates against `full_shop` fields, which
  `src/utils/data_export.py:413-415` defines as only `["shop","leaflets","offers","keywords"]`.
  `src/utils/data_export.py:464-508` (`filter_fields`) is **shallow** — it never recurses.
- **Reproduced**:
  ```
  $ python -m src.cli scrape-full-shop biedronka --fields name
  Error: Invalid fields for 'full_shop': 'name' - unknown field.
         Use --fields-list full_shop to see available fields.   (exit 2)
  ```
  `fields-list full_shop` returns 4 rows, all typed `string` (see M-04).
- **Impact**: The documented field-filtering workflow for the flagship command is unusable.
  Even if a top-level key passed validation, the shallow filter would drop `leaflets`/
  `offers` content wholesale rather than projecting nested fields.
- **Decision required**: either implement recursive projection (preferred, matches docs)
  or restrict the contract to top-level keys and correct the help text + tests.

#### C-02 — Retry policy never matches the exceptions actually raised (dead code)

- **Evidence**: `src/scrapers/base.py:41-51`. The predicate is
  `retry_if_exception_type((TimeoutError, ConnectionError))` — Python **builtins**.
  `src/webdriver/helpers.py:61-69` and `:103-105` raise
  `selenium.common.exceptions.TimeoutException`.
- **Verified**: `issubclass(selenium...TimeoutException, TimeoutError) == False`;
  MRO is `TimeoutException → WebDriverException → Exception`.
  Navigation failures surface as `WebDriverException` / `urllib3` `MaxRetryError`, also unmatched.
- **Impact**: `max_attempts=3`, `backoff_factor`, and `jitter` (`src/config.py:17-22`) are
  configuration theater. Any transient timeout fails the run immediately. `base.py` shows 96%
  coverage because no test asserts that a retry *occurs*.
- **Effort**: S.

#### C-03 — Date ranges implement *containment*, spec requires *overlap*; `valid_from` semantics inverted

- **Spec**: `openspec/specs/cli/spec.md:181-183` — `--within-range` → "only leaflets with
  validity **overlapping** that range"; `:205-207` — search equivalent.
- **Evidence**: `src/domain/date_filter.py:103-116` requires
  `entity.valid_from >= date_from` **and** `entity.valid_until <= date_to` — i.e. the entity
  must be fully *inside* the range.
- **Impact**: A leaflet valid 2026-10-01→2026-10-31 is **excluded** from
  `--within-range "2026-10-15 to 2026-10-16"`, although it is valid on both days. The common
  user intent (and the spec) is inclusion. Also, a "starts on or after" reading of
  `--valid-from` (`:107-110` of the same file) excludes leaflets that began earlier but are
  still valid — contradicting the CLI help "valid from this date onwards" only in the
  overlap sense users expect.
- **Note**: 100% line coverage; no test encodes the overlap contract.
- **Effort**: S.

#### C-04 — `scroll_to_bottom` is an unbounded `while True` loop

- **Evidence**: `src/webdriver/helpers.py:108-131` — `while True`, 1.0s sleep per iteration,
  break condition is *only* `new_height == last_height`.
- **Impact**: On pages with infinite scroll, lazy-loaded carousels, or a height that oscillates
  by even 1px (ads, animations, cookie banners), this never terminates. It is on the hot path
  for **offers and leaflets and shops** (`src/scrapers/offer_scraper.py:40-41`,
  `leaflet_scraper.py:38-39`, `shop_scraper.py:25-26` → `_should_scroll() == True`).
- **Additional**: no overall timeout, no max-iteration cap, and `time.sleep` ignores the
  configured `request_delay_*` policy (`src/config.py`), so scroll pacing is outside config control.
- **Effort**: S.

### 4.2 High

#### H-01 — Documentation still advertises two commands the spec removed

The spec **removes** `list-shops` and `list-leaflets`
(`openspec/specs/cli/spec.md:84-102`, `:145-159`). Documentation contradicts it in five places:

| File:line | Contradiction |
|---|---|
| `README.md:118`, `:240` | "List scraped shops" → `list-shops` |
| `README.md:130-133`, `:212-218` | `list-leaflets biedronka --active-only/--active-on/--valid-from/--within-range` |
| `docs/user-guide.md:316-331` | Full `list-shops` and `list-leaflets` sections incl. options table |
| `docs/api-reference.md:53-54` | `list-shops` / `list-leaflets` listed as commands |
| `docs/architecture.md:210-211` | Command table rows for both |

A user following the README gets `No such command`. This is the single highest-value
documentation fix in the repo.

#### H-02 — Command inventory drift: 7 real commands, docs describe a different set

Actual (`@app.command()` at `src/cli/__init__.py:391,483,618,735,844,1012,1029`):
`scrape-shops`, `search`, `scrape-leaflets`, `scrape-offers`, `scrape-full-shop`, `config`, `fields-list`.

- README's CLI section (`README.md:94-145`) omits `search` from the command list (it appears only
  in examples at `:221-243`).
- README documents 2 commands that do not exist (H-01).
- No single page lists all 7 with consistent ordering. `docs/api-reference.md:53-54` and
  `docs/architecture.md:210-211` carry partial, divergent lists.

#### H-03 — No console-script entry point, yet docs/help text use `blix-scraper ...`

- **Evidence**: `pyproject.toml` has `[project]` but **no `[project.scripts]`**.
  `uv run blix-scraper ...` cannot work; only `python -m src.cli`.
- **Contradiction**: `src/cli/__init__.py` docstrings advertise `blix-scraper scrape_full_shop`
  (`:873`, `:876`, `:418`, etc.). See also M-06 (underscore command names).

#### H-04 — Entry point and data directory are CWD-sensitive

- **Evidence (crash)**: `uv run python src/__main__.py` →
  `ImportError: attempted relative import with no known parent package`
  (`src/__main__.py:3`). The file is not runnable directly; only `-m src` works.
- **Evidence (silent)**: `src/config.py:38` — `data_dir: Path = Path("data")` is resolved against
  the **process CWD**, not the package/repo root. Running `python -m src.cli scrape-shops --save`
  from another directory writes `./data` wherever the user happened to be.
- **Impact**: Broken copy-paste from docs, and exports landing in unexpected locations.

#### H-05 — Timezone handling assigns UTC instead of converting; `valid_until` boundary is off by one

- **Evidence**: `src/scrapers/leaflet_scraper.py:110-113` —
  `date_parser.parse(str(date_start)).replace(tzinfo=timezone.utc)` (same at
  `search_scraper.py:221-225`, and in the CLI fallback `src/cli/__init__.py:70,76`).
  `.replace(tzinfo=...)` **relabels** a wall-clock value as UTC rather than converting it.
- **Two consequences**:
  1. A leaflet valid from local midnight is treated as valid from 00:00 **UTC** = 01:00/02:00
     local (CET/CEST), so `active_on` boundaries shift by the offset.
  2. `valid_until` is stored at 00:00. Status uses `now > valid_until`
     (`leaflet_scraper.py:125-129`), so a leaflet whose last valid day is 2026-10-21 flips to
     `archived` at **00:00 on 10-21**, losing its final day. This is a real off-by-one-day bug.
- **Note**: `DateParser` itself is correct (`src/utils/date_parser.py:78-89` sets
  `TIMEZONE: UTC`, `RETURN_AS_TIMEZONE_AWARE: True`, then `to_utc`); the defect is in the
  scraper/CLI paths that bypass it with `dateutil`.

#### H-06 — Wait timeouts are silently swallowed, masking stale selectors

- **Evidence**: `src/scrapers/search_scraper.py:51-57` (`except Exception:` → debug log),
  `src/scrapers/keyword_scraper.py:33-38` (`except Exception:`), plus broad
  `except Exception` blocks at `search_scraper.py:56,125,227,250,259,308`.
- **Observed live**: B4 logged `element_not_found ... value=.offer-list timeout=10` and continued.
  `.offer-list` appears to be a stale selector; the success of the run depended on a fallback
  (`window.offers`) that the wait never validated.
- **Impact**: Pages that genuinely fail to load are indistinguishable from pages where an
  optional section is absent. This is how silent data loss looks.
- **Good contrast**: `offer_scraper.py:38-39` correctly lets `TimeoutException` propagate.

### 4.3 Medium

| ID | Finding | Evidence |
|---|---|---|
| **M-01** | Test suite non-hermetic w.r.t. `.env`; flat aliases override nested env vars (11 failures locally). | `src/config.py:57-65`, `:65-96`; `tests/test_config.py:289,300,312` |
| **M-02** | Shops are not de-duplicated across "Popularne sklepy" and the full list → duplicate rows (`bi1` twice in B2). `261` is rows, not unique shops. | `src/scrapers/shop_scraper.py:37-62` (no slug dedup before `append`) |
| **M-03** | Stale search wait selector `.offer-list`; has no matching element on current site. | observed B4; `src/scrapers/search_scraper.py:55` |
| **M-04** | `fields-list full_shop` renders every field as `string` (arrays/objects mislabeled); error text says "Use `--fields-list full_shop`" but the real invocation is `fields-list full_shop` (command, not flag). | `src/utils/data_export.py:379-384,413-415`; `src/cli/__init__.py:891` |
| **M-05** | `--output` documented as "Custom output **directory**" but implemented as a **file path**. | `README.md:149`; help `src/cli/__init__.py:395-397` |
| **M-06** | CLI docstrings/help advertise `blix-scraper` + underscore verbs (`scrape_full_shop`, `scrape_shops`) that do not exist (command is `scrape-full-shop`, no console script). | `src/cli/__init__.py:418,873,876`; `pyproject.toml` (no scripts) |
| **M-07** | The CLI spec is internally contradictory: `Original Requirements` still specifies the removed `list-leaflets` command and its date options. | `openspec/specs/cli/spec.md:84-102` / `:145-159` vs `:163-255` |

### 4.4 Low

| ID | Finding | Evidence |
|---|---|---|
| **L-01** | `roadmap.md` stale: "Last updated: 2026-02-22"; still lists date filtering as pending though shipped. | `roadmap.md:7-9`, `:35` |
| **L-02** | `.serena/` untracked and not ignored → dirty worktree on every session. | `git status`; `.gitignore` (no `.serena/`) |
| **L-03** | Ruff config uses deprecated top-level keys (`select` → `lint.select`); warning on every run. | `pyproject.toml`; ruff output |
| **L-04** | Two spec trees coexist: legacy `specs/` (`002-improve-testing`, `01-examples-docs-update`) and `openspec/specs/`. Ambiguous source of truth for readers. | `ls specs/`, `ls openspec/specs/` |
| **L-05** | Leaflet table renders `N/A` in the last column for every row (unpopulated metric). | observed B3 output |

### 4.5 Cleared (N-series, spot-confirmed)

C2 cleared N-01..N-05. The two most load-bearing claims were re-verified clean at `a8bc7a2`:

- No `storage` / `JSONStorage` / `ScraperOrchestrator` references remain in `src/` (grep: 0 hits).
- No reads from `data/` in `src/` (grep: 0 hits) — consistent with spec `:118-126`.

---

## 5. Prioritized backlog — top 10

Ordered by (user-visible impact × confidence) ÷ effort. Effort: **S** ≤ 0.5 day, **M** ≈ 1 day, **L** > 2 days.

| # | ID | Fix | Why now | Effort | Verification |
|---|---|---|---|---|---|
| 1 | C-02 | Retry on `selenium.common.exceptions.TimeoutException`/`WebDriverException` (+ `urllib3` `MaxRetryError`), or introduce a project `RetryableError` and raise it from `helpers.py`. | Configuration currently lies; transient failures abort runs. One-line predicate change with large reliability payoff. | **S** | Unit test with a fake driver raising `TimeoutException`, assert 3 calls. |
| 2 | C-04 | Cap `scroll_to_bottom`: `max_scrolls`, `deadline`, and tolerate ±N px height noise. | Infinite hang risk on every scroll-enabled scraper. | **S** | Fake driver with ever-growing height must terminate; assert call cap. |
| 3 | C-03 | Change range predicate to overlap: `entity.valid_from <= date_to and entity.valid_until >= date_from`. Keep `active_on` as-is. | Spec-mandated behavior; currently returns wrong (empty) result sets. | **S** | Parametrized tests: contained / overlapping / disjoint / adjacent. |
| 4 | C-01 | Implement recursive `filter_fields` for nested `full_shop` (project `name` into shop, each leaflet, each offer), or narrow the documented contract to 4 top-level keys and delete the false example. | Flagship command's documented workflow is unusable (exit 2). | **M** | CLI test: `--fields name --save` produces nested projection with no loss of structure. |
| 5 | H-06 | Separate "optional section absent" from "required content timed out": delete `.offer-list` wait or replace with the real container; replace bare `except Exception` with `except TimeoutException` + `warning` log. | Prevents silent data loss and stale-selector rot; B4 already shows the smell. | **M** | Test asserts warning emitted and `TimeoutException` surfaced for required waits. |
| 6 | H-05 | Convert instead of relabel: parse with `dateutil` + `tzinfos`/`astimezone(UTC)`; store `valid_until` as end-of-day (`23:59:59.999999`) or compare dates not instants. | Fixes incorrect `active/archived` status at day boundaries (off-by-one day). | **M** | Boundary tests around 00:00 UTC and DST transitions. |
| 7 | H-01 + H-02 | Purge `list-shops`/`list-leaflets` from `README.md`, `docs/user-guide.md`, `docs/api-reference.md`, `docs/architecture.md`; publish one canonical 7-command table. | Users copy commands that fail; spec already says removed. | **M** | Docs-only; grep for `list-shops\|list-leaflets` returns 0 outside `openspec/` history. |
| 8 | M-01 | Make tests hermetic: `Settings(_env_file=None)` in config tests (or a `conftest` fixture), and fix alias precedence so nested env vars beat flat dotenv keys. | Restores trust in the suite; explains today's 11 local failures. | **M** | `pytest tests/test_config.py` green with `.env` present **and** absent. |
| 9 | H-03 + M-06 + H-04 | Add `[project.scripts] blix-scraper = "src.cli:main"`; correct docstrings to hyphenated commands; anchor `data_dir` to repo root (or document CWD explicitly); stop advertising `python src/__main__.py`. | Removes the largest class of copy-paste failures. | **S** | `uv run blix-scraper --help` lists 7 commands. |
| 10 | M-02 | De-duplicate shops by slug (merge `is_popular`), so counts are meaningful and `scrape-full-shop` lookups are unambiguous. | Reported totals (261) are wrong as "number of shops"; affects any downstream analytics. | **S** | `scrape-shops` output has 0 duplicate slugs; test with a fixture containing a popular duplicate. |

**Deferred / next cycle**: M-03 (fold into #5), M-04, M-05, M-07 (spec amendment), L-01..L-05.

### Suggested sequencing

1. **PR A (reliability, S+S+S)**: C-02, C-04, C-03 + their tests. Small diff, highest risk reduction.
2. **PR B (contract)**: C-01 (+ M-04) — decide nested vs top-level, then align help, validation, tests.
3. **PR C (docs purge)**: H-01, H-02, M-05, M-06, L-01 + roadmap corrections (§6).
4. **PR D (hygiene)**: M-01, H-03, H-04, L-02, L-03, L-04.
5. **PR E (data quality)**: H-05, H-06, M-02, M-03.

---

## 6. Roadmap corrections

`roadmap.md` is stale (`:35` claims 2026-02-22) and misrepresents shipped work as pending.
The following is a ready-to-apply correction set. **Not applied by this report** (see §8, Risk R-4).

### 6.1 Items marked pending that are already implemented

| `roadmap.md` line | Current text | Reality | Action |
|---|---|---|---|
| `:8` | `- [ ] Add filtering for valid data` | Date filtering shipped: `src/domain/date_filter.py`, `--active-on/--valid-from/--valid-until/--within-range` on `search` and `scrape-leaflets`; spec `openspec/specs/cli/spec.md:58-79`. | Mark `[x]`, link spec. **Caveat**: correctness blocked by C-03 — mark `[x]` only after C-03 lands, else `[~]`. |
| `:9` | `- [ ] Pass the date I want the info for` | Same as above. | Mark `[x]` (post C-03). |
| `:19` | `- [ ] Export to more formats (Excel, JSON Lines)` | JSON export with field filtering, dated dirs, metadata envelope shipped (`src/utils/data_export.py`). Excel/JSONL **not** shipped. | Reword to `[x] JSON export (field filtering, dated dirs)` + `[ ] Excel / JSON Lines`. |

### 6.2 Items that should be added (missing from roadmap entirely)

```markdown
### Correctness (from issue #34 review, docs/reviews/2026-10-20-repo-hygiene-status-issue-34.md)
- [ ] C-02 Retry policy never matches Selenium exceptions
- [ ] C-04 Unbounded scroll loop has no cap or deadline
- [ ] C-03 Date range filtering is containment, spec requires overlap
- [ ] C-01 scrape-full-shop --fields cannot filter nested data
- [ ] H-05 valid_until treated as 00:00 → leaflet loses its last valid day

### Documentation
- [ ] Remove list-shops/list-leaflets from README, user-guide, api-reference, architecture
- [ ] Publish single canonical 7-command table
- [ ] Add [project.scripts] console entry point
- [ ] Archive or reconcile legacy specs/ tree vs openspec/specs/
```

### 6.3 Front-matter fix

Replace `*Last updated: 2026-02-22*` with `*Last updated: 2026-10-20*` and add a one-line
provenance note pointing at this review.

### 6.4 Spec correction (owner: spec maintainer — not unilaterally edited here)

`openspec/specs/cli/spec.md` needs a status promotion (`Status: Draft` at `:5`) and a
disposition for `Original Requirements` (`:163-255`), which still specifies the removed
`list-leaflets` command. Recommended: retitle that section
`## Historical Requirements (superseded by MODIFIED/REMOVED above)` and add an explicit
note that it is retained for traceability only. This preserves the spec as source of truth
while eliminating the internal contradiction (M-07).

---

## 7. Documentation ↔ implementation sync matrix

| Document | Verified accurate? | Notes |
|---|---|---|
| `openspec/specs/cli/spec.md` | ⚠️ Mostly | Authoritative; internally contradictory (M-07); `search`/`scrape-full-shop`/`config`/`fields-list` not covered |
| `README.md` | ❌ | 2 removed commands (`:118,130-133,212-218,240`); `search` missing from command list; `--output` wording (M-05) |
| `docs/user-guide.md` | ❌ | `list-shops`/`list-leaflets` sections (`:316-331`) |
| `docs/api-reference.md` | ❌ | Command list (`:53-54`) |
| `docs/architecture.md` | ❌ | Command table (`:210-211`) |
| `docs/developer-guide.md` | ⬜ Not audited | Outside this pass's scope; no contradiction found by grep |
| `docs/domain-model.md` | ⬜ Not audited | Entities at `src/domain/entities.py` exist as described by name; field-level audit pending |
| `docs/implementation-patterns.md` | ⬜ Not audited | — |
| `docs/ci-cd-implementation.md` | ⬜ Not audited | CI lint job added at `7db44a4`; document may predate it |
| `docs/phase5-testing-best-practices-report.md` | ⬜ Not audited | Historical report |
| `roadmap.md` | ❌ | Stale (§6) |
| `docs/_index.md` | ⚠️ | `updated: 2026-01-16`; links resolve, but points at a removed-command-bearing user guide |
| `AGENTS.md` | ⚠️ | Documents `uv run python -m src` only — correct, but silent on `src.cli`, `.env`, and the fact that `python src/__main__.py` crashes |

---

## 8. Risks and assumptions

| ID | Risk / assumption | Impact | Mitigation |
|---|---|---|---|
| R-1 | The C2 register file was not present in the repo, so **M-01..M-07 and L-01..L-05 IDs are reconstructed** from an independent audit. Wording and numbering may not match C2 exactly. | Traceability mismatch if C2 IDs are cited elsewhere. | C and H items (the decision-driving set) were re-verified line-by-line; treat M/L IDs as provisional. |
| R-2 | Live counts (261 / 15 / 22→2) are point-in-time snapshots of a third-party site. | Counts cannot be used as test assertions. | Assert on *shape* (exit 0, non-empty, schema-valid), not magnitude. |
| R-3 | The 11 local test failures were attributed to `.env` by isolating `Settings()` in/out of the repo CWD and by running the full suite in a `.env`-free copy. I did **not** run the suite with `.env` renamed in place (to avoid mutating a developer's local config). | Attribution is strong but not exhaustive — another env source could contribute. | Confirm with `Settings(_env_file=None)` regression test (fix #8). |
| R-4 | `roadmap.md` and `openspec/specs/cli/spec.md` were **deliberately not edited**; corrections are proposed in §6. | Parallel agents may be editing these files; silent rewrites would create conflicts, and the spec must stay authoritative. | Apply §6 in a dedicated docs PR after review. |
| R-5 | Coverage figures are from `--cov=src` on a clean tree; the in-worktree run reports the same 83% because the failures are config tests. | Coverage is not evidence of behavioral correctness (see C-02/C-03). | Prefer mutation/branch tests for the three critical fixes. |
| R-6 | M-02 (duplicate `bi1`) was observed in live B2 output; the duplicate-row count was not re-derived programmatically after the run artifact was rotated. | `261` may overstate unique shops by an unknown amount. | Re-run `scrape-shops` and `sort | uniq -d` on slugs. |
| R-7 | H-05's off-by-one depends on `valid_until` being stored date-only at 00:00. Confirmed for `leaflet_scraper`; `search_scraper` derives validity from page data and may differ. | Partial scope. | Audit `search_scraper.py:205-230` when fixing. |
| R-8 | Non-CLI documentation (`developer-guide.md`, `domain-model.md`, `implementation-patterns.md`, `ci-cd-implementation.md`, `phase5-testing-best-practices-report.md`) was **not audited** in this pass; only CLI-facing docs were checked against the spec. | Additional drift may exist outside the CLI surface. | Run a follow-up docs sweep; do not read the ⬜ rows in §7 as "verified accurate". |

---

## Appendix A — Reproduction commands

```bash
# Baselines (clean tree, no .env)
python -m pytest -q --cov=src --cov-report=term
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run mypy src/

# Defect reproductions
uv run python -m src.cli scrape-full-shop biedronka --fields name        # C-01 → exit 2
uv run python -c "from selenium.common.exceptions import TimeoutException as T; print(issubclass(T, TimeoutError))"  # C-02 → False
uv run python src/__main__.py --help                                     # H-04 → ImportError
uv run python -m src.cli search kawa --headless                          # H-06 → element_not_found, exit 0

# Live matrix
uv run python -m src.cli config
uv run python -m src.cli scrape-shops --headless
uv run python -m src.cli scrape-leaflets biedronka --headless
uv run python -m src.cli search kawa --headless

# Docs drift
grep -rn "list-shops\|list-leaflets" README.md docs/
```

## Appendix B — Report provenance

- Branch/commit read from `git rev-parse --abbrev-ref HEAD` / `git log -1`: `chore/issue-34-repo-hygiene` @ `a8bc7a2`.
- All `file:line` references verified against the working tree at that commit.
- Live runs executed headless on 2026-10-20; chromedriver 146.0.7680.165.
- Clean-tree baseline executed in `/tmp/opencode/blix-clean` (rsync of the repo excluding `.git`, `.venv`, `.env`, `data/`, `logs/`).
