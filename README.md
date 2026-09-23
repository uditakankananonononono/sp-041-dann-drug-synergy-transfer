# SP-041 / DOC-1-044 - Domain-Adversarial Cross-Study Drug-Synergy Transfer

## Summary (from `DOC-1-044/README.md`)


Executed experiment 41: domain-adversarial prediction of cancer-drug synergy across open DrugComb screens.
Verdict: INVALID / NOT EVALUABLE, zero success credit (41/200). See LEDGER-ENTRY.md.

- protocol/ - immutable lock chain (original lock, governing A-1+A-2 lock, both .sha256 sidecars)
- code/ - preprocess_zip.py (the locked A-2 auditor tool), preprocess_zip_attempt1.py (preserved superseded attempt), figures/generate_figures.py
- paper/ - DOC-1-044-paper.pdf (19 pages) and LaTeX source
- manifest/ - per-file SHA-256 manifests for the data pack and the original 29-file artifact bundle
- tool/ - auditor install/run guide

Heavy artifacts (full per-block audit CSV, raw data pack, figures PNG) live in the Drive folder (see LEDGER-ENTRY.md). Raw DrugComb v1.4 is fetched from Zenodo record 18449193 and verified against raw-manifest.json digests (in the data pack).

## Contents

- `DOC-1-044/` - migrated unchanged from `science-program/DOC-1-044` (15 files)
- `EXP-041-DOC-1-044-domain-adversarial-synergy/` - migrated unchanged from `science-program/projects/EXP-041-DOC-1-044-domain-adversarial-synergy` (3 files)

## Provenance

Split out of the `science-program` repository (source commit `028a7141ed5f951a7b6e6517d4e72768d414a560`) on 2026-09-23. Every file is byte-identical to the source; `MIGRATION_MANIFEST.tsv` lists sha256, original path and new path for each of the 18 files.

Part of Udita Phookan's computational science program: every experiment locks its question, validation design, success gate and failure policy before outcome analysis, and negative results are preserved. Program-wide ledgers and standards live in the `science-program-ledger` repository.
