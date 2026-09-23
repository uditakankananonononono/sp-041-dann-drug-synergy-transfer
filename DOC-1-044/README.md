# DOC-1-044 (SP-041) - packaged result

Executed experiment 41: domain-adversarial prediction of cancer-drug synergy across open DrugComb screens.
Verdict: INVALID / NOT EVALUABLE, zero success credit (41/200). See LEDGER-ENTRY.md.

- protocol/ - immutable lock chain (original lock, governing A-1+A-2 lock, both .sha256 sidecars)
- code/ - preprocess_zip.py (the locked A-2 auditor tool), preprocess_zip_attempt1.py (preserved superseded attempt), figures/generate_figures.py
- paper/ - DOC-1-044-paper.pdf (19 pages) and LaTeX source
- manifest/ - per-file SHA-256 manifests for the data pack and the original 29-file artifact bundle
- tool/ - auditor install/run guide

Heavy artifacts (full per-block audit CSV, raw data pack, figures PNG) live in the Drive folder (see LEDGER-ENTRY.md). Raw DrugComb v1.4 is fetched from Zenodo record 18449193 and verified against raw-manifest.json digests (in the data pack).
