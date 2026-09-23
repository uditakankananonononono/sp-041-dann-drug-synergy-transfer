# DOC-1-044 Phase 0 preregistration lock

**Title:** Domain-adversarial prediction of cancer-drug synergy across open screens  
**Status:** Phase 0 only; no outcome-bearing file has been downloaded, queried, previewed, or analyzed.  
**Locked design version:** 1.0, 2026-09-23 (Asia/Calcutta)

## 1. Open sources and availability evidence

1. **DrugComb raw data v1.4 (primary data source):** https://zenodo.org/records/18449193  
   The public Zenodo landing page identifies an open dataset, version v1.4, published 2026-02-01. It lists a 2.0 GB `drugcomb_data_v1.4.csv` plus drug and cell-line identifier workbooks, with posted MD5 digests. The page states that the CSV contains raw percent-inhibition measurements for combination and monotherapy screens. The files were not opened or downloaded during Phase 0.
2. **DrugComb documentation:** https://drugcomb.org/help/  
   Public documentation defines the available response concepts, including ZIP, Bliss, Loewe, HSA, S, and CSS.
3. **DrugComb data descriptor/update paper:** https://pmc.ncbi.nlm.nih.gov/articles/PMC8218202/  
   Open-access description of the repository and its curated combination studies; distributed under CC BY 4.0.
4. **NCI-ALMANAC source page:** https://wiki.nci.nih.gov/display/NCIDTPdata/NCI-ALMANAC and https://dtp.cancer.gov/ncialmanac/initializePage.do  
   Official NCI pages establish that ALMANAC is a public combination-screen resource. DrugComb is frozen as the operational source so that one harmonized schema and one synergy definition are used.
5. **Prior cross-study feasibility study:** https://www.nature.com/articles/s42003-023-04783-5  
   The open paper explicitly names ALMANAC, O'Neil, FORCINA, and Mathews as the four largest DrugComb studies, performs 1-vs-1 and 3-vs-1 inter-study validation, and identifies dose-setting variation as a major transfer problem. Code: https://github.com/GuanLab/DrugComb-cross-study-prediction.

Availability was checked only from landing pages, documentation, and publications. No values from the outcome table were accessed.

## 2. Feasibility evidence

The raw archive is public, versioned, and supplies the combination measurements and identifier maps needed to form study-specific domains. The published cross-study study demonstrates that the four named studies can be harmonized and evaluated across studies. DrugComb supplies a common set of synergy metrics, while the archive's identifier files support canonical drug and cell-line mapping. A domain-adversarial neural network (DANN) is computationally modest at this scale: two drug fingerprints plus cell-line identity features, a small multilayer encoder, a regression head, and a gradient-reversal domain head. The experiment needs no wet lab and no private data.

This feasibility finding does not imply that DANN will help. Cross-study shift can be biological, measurement-driven, or both; removal of domain information may erase predictive signal.

## 3. Frozen cohort and split

### 3.1 Unit and outcome

The prediction unit is an unordered `(canonical_drug_A, canonical_drug_B, canonical_cell_line)` triplet within one source study. The outcome is the **mean ZIP synergy score** across all valid dose matrices/replicates for that triplet within that study. Drug order is canonicalized lexicographically after identifier mapping. No alternative synergy definition will replace ZIP after inspection.

### 3.2 Frozen studies

- **Labeled source domains:** O'Neil, FORCINA, and Mathews.
- **Locked external target:** ALMANAC.
- Study membership will be determined only by the exact study/source field in DrugComb v1.4, after trimming whitespace and case-folding for matching. A mapping table from raw labels to these four names will be written before any outcome summary; ambiguous labels are excluded and logged, not manually reassigned based on results.

### 3.3 Inclusion/exclusion

Include a triplet only if:

1. both agents map unambiguously to one DrugComb canonical drug identifier;
2. the two canonical drugs are distinct;
3. the cell line maps unambiguously to one canonical DrugComb cell-line identifier;
4. a parseable canonical SMILES is available for both drugs and produces a valid RDKit Morgan fingerprint;
5. at least one finite ZIP value exists for the triplet; and
6. the triplet belongs to exactly one of the four frozen study labels for the record being aggregated.

For duplicate raw rows, aggregate only within the exact study-triplet using the arithmetic mean. Exclude missing/non-finite ZIP values, mixtures without a single canonical structure, and unresolved identifiers. No filtering by the magnitude or sign of ZIP is permitted. No outlier removal is permitted.

### 3.4 Features

- Each drug: radius-2, 2048-bit Morgan fingerprint from canonical SMILES, generated with RDKit; the pair representation is order invariant: elementwise sum and absolute difference of the two fingerprints.
- Cell line: one-hot canonical cell-line identifier over the vocabulary observed in source training plus the unlabeled target feature table; an `UNK` level is reserved.
- No dose, monotherapy response, omics, study name, or target ZIP-derived feature enters the synergy regressor. The domain head alone receives domain labels.

### 3.5 Exact split and leakage rules

**External test:** every qualifying ALMANAC triplet is test-only. Its ZIP outcome is sealed until all source-only fitting, hyperparameter choice, and checkpoint selection are complete. ALMANAC input features and domain membership may be used without ZIP labels by DANN during training; this makes the primary analysis explicitly transductive unsupervised domain adaptation.

**Source partition:** create a group key from the unordered canonical drug pair. Sort unique source pair keys by `SHA256("DOC-1-044|" + pair_key)`. Assign the first 80% (floor) to training and the remaining 20% to validation. Every triplet for a drug pair, across all three source studies and all cell lines, follows its pair. This prevents the same pair crossing source train/validation.

If a source study has fewer than 50 qualifying validation triplets after this deterministic split, use deterministic 5-fold grouped cross-validation instead, with fold = first 8 hex digits of the same hash modulo 5; fold 0 is validation for model selection, and the deviation is logged. This fallback is based only on cohort size, never outcomes.

After model/hyperparameter selection, refit on all qualifying source triplets for each locked seed and evaluate once on all qualifying ALMANAC triplets. No ALMANAC labels are used for early stopping, tuning, thresholding, normalization, or model choice. Outcome standardization uses source-training mean and SD only, then predictions are transformed back to native ZIP units.

### 3.6 Fixed seeds and software

Seeds: 1044, 2044, 3044. Python 3.11; PyTorch 2.4.x; RDKit 2024.03.x; scikit-learn 1.5.x. Exact resolved environment and file hashes will be recorded at execution. If these versions cannot be installed, only patch-level substitution is allowed and must be declared before opening outcomes.

## 4. Hypothesis

A gradient-reversal domain-adversarial encoder trained on labeled O'Neil, FORCINA, and Mathews examples plus unlabeled ALMANAC inputs will learn study-invariant representations and improve rank prediction of held-out ALMANAC ZIP synergy relative to an architecture-matched source-only empirical-risk-minimization model.

## 5. Locked models and quantitative success gates

### 5.1 Models

**ERM control:** invariant input encoder, two hidden layers (512, 128; ReLU; dropout 0.2), then a 64-unit regression head. AdamW, learning rate 1e-3, weight decay 1e-4, batch size 256, maximum 200 epochs, early stopping on source validation MSE with patience 20.

**DANN:** exactly the ERM model plus a domain classifier (128, 64, four-way softmax) attached through gradient reversal. Domain-loss weight follows `lambda(p)=2/(1+exp(-10p))-1`, where p is fractional training progress. Batches are balanced by source domain and include an equal-sized unlabeled ALMANAC feature batch. All other optimization and stopping rules match ERM. Checkpoint selection uses source validation regression MSE only.

No architecture or hyperparameter search is allowed. Each model is trained under the three fixed seeds; per-triplet predictions are averaged across seeds before primary evaluation.

### 5.2 Primary endpoint and gate

Primary endpoint: Spearman correlation between ensemble prediction and observed ZIP over all qualifying ALMANAC triplets.

The result is **useful-positive** only if all hold:

1. DANN ALMANAC Spearman rho >= 0.30;
2. DANN minus ERM Spearman rho >= 0.05; and
3. the lower bound of a paired 95% bootstrap confidence interval for the difference is > 0. Bootstrap resampling is clustered by unordered drug pair, 10,000 replicates, seed 44044, percentile interval.

### 5.3 Guardrails and secondary endpoints

- Native-scale ALMANAC MAE for DANN must be no worse than ERM by more than 5%: `MAE_DANN <= 1.05 * MAE_ERM`.
- Secondary, not gate-changing: Pearson r; MAE; RMSE; and AUROC/AP for `ZIP > 10`, reported only if both classes contain at least 50 triplets.
- Report performance by cell line and by whether both drugs, one drug, or neither drug appeared in labeled source training. These strata are descriptive and cannot rescue a failed primary gate.

## 6. Controls and nulls

1. **ERM architecture control** above, isolating domain adversarial training.
2. **Source-mean null:** constant source-training mean ZIP.
3. **Pair-frequency-safe linear baseline:** ridge regression on the same fixed features; alpha fixed at 1.0.
4. **Label permutation null:** within each source study, permute ZIP across triplets using seed 944044, train the ERM pipeline once, and evaluate on ALMANAC. Expected rho is near zero; this is a leakage check, not a gate.
5. **Domain-prediction diagnostic:** train a post-hoc multinomial logistic classifier on frozen encoder representations to distinguish four studies. DANN should reduce balanced domain accuracy relative to ERM. This is mechanistic evidence, not a success gate.
6. **Drug-order invariance check:** swapping A/B must change predictions by <1e-7 absolute; failure invalidates the run.
7. **Leakage audit:** assert no unordered drug pair overlaps source train and validation, and no ALMANAC outcome was loaded into the training/tuning process.

## 7. Uncertainty assessment

Primary uncertainty is the 10,000-replicate drug-pair-clustered paired bootstrap, which respects correlation among cell lines for the same pair. Report point estimates and 95% intervals for both models and their difference. Also report the three seed-specific metrics and their range. Do not treat triplets as independent for the main confidence interval. Missing structures and identifier ambiguity may induce selection bias; publish a CONSORT-like accounting by study of raw rows, mapped rows, eligible triplets, and every exclusion reason without outcome-stratified exclusions.

Key risks fixed in advance: target transductivity limits deployment claims; domain invariance can remove biology; ALMANAC may differ strongly in drug/cell-line coverage; ZIP aggregation can hide dose-landscape variation; and canonical identifier errors can dominate model effects. Conclusions are restricted to the four in-vitro screens and do not claim clinical synergy.

## 8. Failure policy

All completed runs are preserved. A gate failure is an informative negative, not grounds for outcome-dependent retuning, alternate endpoints, subgroup fishing, dataset substitution, or suppression. Bugs may be corrected only with a written amendment that identifies the bug, affected code/hash, and whether any outcomes had been viewed. The original result remains archived. Any new architecture, metric, cohort, split, feature set, or synergy definition is a separately numbered, newly locked experiment.

Useful-negative classification is allowed only if the locked pipeline is valid and establishes a reproducible boundary, such as DANN failing to beat ERM under strict external transfer. An invalid run (corrupt file, leakage, failed invariance assertion) is labeled invalid, not negative.

## 9. Compute budget

Hard cap for the locked experiment:

- data storage: 10 GB;
- preprocessing: 8 CPU-hours, 32 GB RAM maximum;
- training: at most 12 GPU-hours on one GPU with <=24 GB VRAM (3 ERM + 3 DANN seed runs, plus one permutation-null ERM); no distributed training;
- bootstrap/evaluation: 4 CPU-hours;
- total wall-clock target: <=24 hours after data acquisition.

If the cap is exceeded, stop and report. Do not reduce the cohort or tune the model after viewing outcomes to fit the budget.

## 10. Lock statement

This document freezes the data version/source, four studies, eligibility rules, target, features, group split, seeds, models, optimization, primary gate, guardrail, nulls, uncertainty method, failure policy, and compute cap before access to outcome-bearing values. Execution must first verify the archive's posted MD5 digests and record local SHA-256 hashes. Any unavoidable schema-only amendment must be made before computing or summarizing ZIP outcomes and stored beside this lock.

---

# EXP-41 (DOC-1-044) AMENDMENT A-1

**Prospective, issued under lock section 10 before any outcome data access.**

1. Package and implementation. ZIP computed with the synergy Python package, pinned to exactly synergy==1.0.0, via synergy.combination.ZIP (Yadav et al. 2015, doi 10.1016/j.csbj.2015.09.001), with use_jacobian=True (package default, deliberately pinned).
2. Monotherapy models. Single-drug dose-response fits use synergy.single.hill.Hill. Fit per block on that block's own monotherapy rows (row drug alone, column drug alone) within the sealed cohort. A block is excluded if it lacks monotherapy rows for either drug or has fewer than 4 usable dose points for a Hill fit (E0 fixed at 100; no imputation of missing monotherapy points). Excluded-block counts recorded in the audit trail; exclusions never change post-hoc.
3. Runtime environment, fully pinned. Python 3.11.15, torch 2.4.1, rdkit 2024.03.6, scikit-learn 1.5.2, pandas 3.0.6, synergy==1.0.0, numpy pinned to the version pandas 3.0.6 resolves to in your environment (record the exact resolved version in the audit trail).
4. Unit handling. Convert conc_r and conc_c to micromolar using the record's conc_r_unit / conc_c_unit fields before any fit. Exclude blocks whose unit field is missing or unparseable; record the exclusion count.
5. Missing-dose handling. Exclude any block containing a missing (NaN) inhibition value among its assayed combo dose points. No imputation, no interpolation. Excluded-block count recorded.
6. Block construction. A block is the set of rows sharing one block_id in drugcomb_data_v1.4.csv (MD5 f5f071de351ec38ffe29c328519a7be5, 2,008,117,325 bytes), carried as (conc_r, conc_c, inhibition) matrices. Fixed step order: (a) cohort selection per the sealed plan; (b) unit conversion; (c) block construction; (d) missing-dose exclusion; (e) Hill monotherapy fits; (f) ZIP computation. Per-block sample counts at each step are part of the audit trail.
7. Re-lock procedure. Append this amendment to the lock file, compute the new lock SHA-256, and seal BEFORE computing or viewing any ZIP value. Store the amended lock and new SHA-256 beside the original per section 10.

Section 5.2 success gates are unchanged in any respect.

---

# AMENDMENT A-2 - effect orientation, score scale, and study-label mapping

Supersedes any inconsistent effect-scale wording in A-1; all other A-1 provisions and all section 5.2 gates remain unchanged. For every finite raw percent-inhibition value I, define the ZIP/Hill response E=(100-I)/100. Pass E without clipping to both monotherapy Hill fits and synergy.combination.ZIP; the fixed untreated response is E0=1.0, not 100. Values outside [0,1] after this deterministic conversion are excluded at the whole-block level and logged, because ZIP v1.0.0 requires responses in [0,1]; no winsorization or clipping. Convert each returned ZIP delta to native DrugComb percentage-point units as ZIP_native=100*delta before matrix/triplet aggregation and before applying every locked gate or secondary threshold. Preserve raw inhibition and fractional E in the audit. For study matching, trim and casefold raw labels and use the frozen explicit map: ALMANAC->ALMANAC, ONEIL->O'Neil, Mathews->Mathews, FORCINA->FORCINA; no other alias is admitted. Append A-2 beside the original lock and A-1, record its SHA-256, and seal it before any ZIP value is computed or summarized. The prior stopped attempts remain blockers, not runs or negatives.
