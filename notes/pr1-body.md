## Result

First slice of #511 (AI for Science): a deterministic **neuroscience domain tag** (BCI vocabulary merged in — one facet, the bci-only records were a handful per month) for radar evidence records, as a **routing facet that never changes any score**.

- New `src/benchmark_radar/science_domains.py`: one shared derivation function + reviewed rule constants. The rules live in the package rather than `config.yml` because installed offline clients ship without the repo config — same precedent as the scoring weights in `rubric.py`.
- `snapshots.dashboard_data` and `QueryService` (`_radar_candidates` + `recent`) call the **same function**, so `radar.json` and the local CLI/HTTP query surfaces agree, and every stored historical day lights up without rewriting any snapshot (snapshots stay byte-identical on disk; asserted by test). This closes the contract gap where a field-copy in the query surface would have returned `[]` for all history.
- `facets.science_domains` added for the upcoming view.
- `QUERY_SCHEMA_VERSION` 6 → 7 for the new `science_domains` field.

### Vocabulary

Original rules plus the #511 domain review (thanks @ktwu01 for routing the neuro slice here):

- interface spellings: `BCI`, `brain-computer interface`, `brain-machine interface` (hyphen/space/en-dash)
- the brain-to-X family: `Brain2Text` / `Brain2Voice` / `Brain2Qwerty` and any later `brain2X`, plus `brain-to-text`-style spellings
- prosthetics & hardware: `neuroprosthesis` (+ speech neuroprosthesis), `Utah array`
- modalities: `sEEG`, `fNIRS`, `calcium imaging`, `optogenetics`, and full technique names (`electroencephalography`, `electrocorticography`) behind the EEG/ECoG acronyms
- unambiguous brain-region stems: `hippocampal`, `prefrontal`, `intracranial`
- the original set: EEG/MEG/ECoG/fMRI, motor imagery, SSVEP/P300, spiking, connectome, `neural decoding`/`signal`/`activity`, cortical compounds

**Precision red lines, locked by 15 unit tests** (each is a false-positive class found in a live-corpus audit, traced to its rule, and closed with a regression test):

- bare `neural` / `neuron` never tag — architecture prose ("neural networks", "neuron counts") and Romance-language NN names ("red neuronal") stay out
- acronyms are word anchored — "megabyte" cannot fire `meg`, "recognition" cannot fire `ecog`
- bare `cortex` is absent — its only live-corpus hits were the Snowflake product and adrenal anatomy; `cortic` still reaches cortical/cortico- compounds
- vetoes: "blood-brain barrier" hypothesis records (PathMap), the "acts as the brain of" metaphor, "brainstorm"

### Measured on the live corpus (53 snapshots, 8,367 unique records)

- **103 unique records tagged, 38 recommended**; weekly flow 5–17/wk (Jul–Aug) rising to 27–28/wk (Sep)
- highlights among them: LibriBrain100 (Oxford, 100 h MEG, neural speech decoding), BrainBench (EEG × LLM), CORAL (brain-wide neuron reconstruction), a negative-control protocol for clinical EEG foundation-model benchmarks, intracranial aneurysm AI detection
- the domain-review vocabulary adds 6 records the old rules missed (all via `intracranial`) with zero noise; the remaining new terms are recall investment for records the current sources do not yet collect (see follow-ups)

### Follow-ups (next slices of #511, not in this PR)

1. **Discovery sources**: arXiv `q-bio.NC` / `eess.SP` categories and neuro search terms, gated by measured precision (seed recall over MOABB / NeuroBench / BCI Competition / TUH / Sleep-EDF / HCP, per-source precision floors, daily-volume ceiling).
2. **"AI for Science · Neuroscience & BCI (Preview)" view**: nav entry, domain filter, rolling 7/30/90-day window.

## Verification

Six-step CI sequence in a clean detached worktree, in order:

- `ruff check .` ✅
- `ruff format --check .` ✅ (161 files)
- `benchmark-radar normalize-external` ✅
- `benchmark-radar classify` ✅ (53 snapshots; tags present in the generated `radar.json`, snapshots untouched)
- `benchmark-radar build-data-release` ✅ (1,284 benchmarks, 53 snapshots)
- `pytest -q` — **1,371 passed**, 9 failed; all 9 fail identically on pristine `main` in the same worktree (og_image fonts and technical-report LaTeX assets absent on this Windows host), so they are environment-only and not introduced here

Refs #511. Reviewers: the tag derivation is pure text matching over stored `title`/`summary` — no external calls, deterministic, replayable over history.
