# DOC-1-044 auditor tool

preprocess_zip.py - reference implementation of the locked A-1/A-2 preprocessing rules and the program's cohort auditor for raw DrugComb archives.

Install: python3.11 venv; pip install torch==2.4.1 rdkit==2024.03.6 scikit-learn==1.5.2 pandas==3.0.6 numpy==1.26.4 scipy==1.17.1 synergy==1.0.0
Run: python preprocess_zip.py --csv drugcomb_data_v1.4.csv --out outputs/
Verify the archive's posted MD5 digests first (Zenodo record 18449193; see raw-manifest.json in the data pack).
Output: block_audit.csv (per-block disposition), block_zip.csv, triplets.csv, preprocess-audit.json, verdict JSON.
Runtime: ~14 min for v1.4 on a small CPU worker, constant memory.
