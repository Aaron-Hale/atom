# Clause-Conditioned Binary LoRA Report

## Result Summary
- LoRA is the best method overall and in clause-macro quality on this split.
- Overall PR-AUC: lexical `0.4702`, pretrained `0.4791`, LoRA `0.6956`.
- Overall F1: lexical `0.5804`, pretrained `0.5212`, LoRA `0.6346`.
- Macro PR-AUC over clause types: lexical `0.3808`, pretrained `0.3882`, LoRA `0.5294`.

## Task And Dataset Policy
- Input is clause-conditioned: pair (`clause_type prompt`, `chunk text`).
- Positive label (`1`) means chunk overlaps any gold span of that clause type in the same document.
- Negative label (`0`) means no overlap for that clause type.
- Negatives include deterministic mixes of nearby same-doc, same-doc non-overlap, cross-doc hard negatives, and clause-absent document negatives.
- Train/val split is deterministic by `doc_id` hash bucket.

## Setup
- Train file: `data/clause_binary_train.jsonl`
- Val file: `data/clause_binary_val.jsonl`
- Base model: `cross-encoder/ms-marco-MiniLM-L6-v2`
- LoRA adapter: `models/clause_binary_lora`
- Threshold tuning rows (train): 20000

## Overall Metrics (val)

| Method | PR-AUC | ROC-AUC | F1 | Precision | Recall | Threshold |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| lexical | 0.4702 | 0.7793 | 0.5804 | 0.4778 | 0.7392 | 0.2500 |
| pretrained | 0.4791 | 0.7463 | 0.5212 | 0.4665 | 0.5904 | 0.0001 |
| lora | 0.6956 | 0.8664 | 0.6346 | 0.6315 | 0.6377 | 0.3261 |

## Macro Averages Over Clause Types (positive class)

| Method | Macro PR-AUC | Macro ROC-AUC | Macro F1 | Macro Precision | Macro Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| lexical | 0.3808 | 0.6546 | 0.4440 | 0.3771 | 0.5678 |
| pretrained | 0.3882 | 0.6326 | 0.3817 | 0.3722 | 0.4339 |
| lora | 0.5294 | 0.7572 | 0.4794 | 0.5064 | 0.4849 |

## Per-Clause Positive-Class Metrics (LoRA)

| Clause | Positives | Precision | Recall | F1 | PR-AUC | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| assignment | 295 | 0.7101 | 0.7390 | 0.7243 | 0.8144 | 0.9006 |
| change_of_control | 74 | 0.5250 | 0.5676 | 0.5455 | 0.5464 | 0.8135 |
| confidentiality | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| exclusivity | 174 | 0.6531 | 0.1839 | 0.2870 | 0.5373 | 0.7771 |
| governing_law | 170 | 0.8571 | 0.8118 | 0.8338 | 0.9288 | 0.9663 |
| limitation_of_liability | 277 | 0.6667 | 0.6426 | 0.6544 | 0.6977 | 0.8429 |
| most_favored_nation | 5 | 0.0000 | 0.0000 | 0.0000 | 0.1902 | 0.8014 |
| non_compete | 98 | 0.6296 | 0.6939 | 0.6602 | 0.5752 | 0.8709 |
| termination | 270 | 0.5149 | 0.7704 | 0.6172 | 0.5463 | 0.8295 |
| warranty | 75 | 0.5077 | 0.4400 | 0.4714 | 0.4579 | 0.7693 |

## Representative LoRA Errors

### Error 1: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00033|assignment|1|positive_overlap`
- Clause: `assignment`
- True: `1` Pred: `0` Score: 0.0334
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c` Chunk: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00033`
- Preview: "ereunder.  32. CONFIDENTIALITY  Both parties understand that the contents of this Agreement, including, but not limited to, all amounts paid or to be paid and any additional consid"

### Error 2: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00032|change_of_control|0|clause_absent_doc`
- Clause: `change_of_control`
- True: `0` Pred: `1` Score: 0.9155
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c` Chunk: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00032`
- Preview: "idating the remaining provisions or parts hereof.  30. RELATIONSHIP  Both parties agree that this Agreement does not constitute and shall not be construed as a constituting of a pa"

### Error 3: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00033|confidentiality|0|clause_absent_doc`
- Clause: `confidentiality`
- True: `0` Pred: `1` Score: 0.3705
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c` Chunk: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00033`
- Preview: "ereunder.  32. CONFIDENTIALITY  Both parties understand that the contents of this Agreement, including, but not limited to, all amounts paid or to be paid and any additional consid"

### Error 4: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00004|exclusivity|1|positive_overlap`
- Clause: `exclusivity`
- True: `1` Pred: `0` Score: 0.1226
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c` Chunk: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00004`
- Preview: " ADAMS GOLF in writing, CONSULTANT shall not:   A.give the right to use or permit the use of CONSULTANT'S name, facsimile signature, nickname, voice or likeness to any other manufa"

### Error 5: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00006|exclusivity|1|positive_overlap`
- Clause: `exclusivity`
- True: `1` Pred: `0` Score: 0.1318
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c` Chunk: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00006`
- Preview: "**] logo on his ADAMS GOLF [*****] or the ADAMS GOLF  [*****]. If CONSULTANT'S relationship with [*****] terminates during this Agreement, CONSULTANT shall be permitted to replace "

### Error 6: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00017|termination|0|clause_absent_doc`
- Clause: `termination`
- True: `0` Pred: `1` Score: 0.3500
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c` Chunk: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00017`
- Preview: "ition to its other legal and equitable remedies, to immediately terminate this Agreement, by giving written notice to CONSULTANT. ADAMS GOLF must exercise its right of termination "

### Error 7: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00033|change_of_control|0|clause_absent_doc`
- Clause: `change_of_control`
- True: `0` Pred: `1` Score: 0.4957
- Doc: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf` Chunk: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00033`
- Preview: "hall not include information that (a) is or becomes a part of the public domain through no act or omission of the other party; or (b) is independently developed by the other party "

### Error 8: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00000|exclusivity|1|positive_overlap`
- Clause: `exclusivity`
- True: `1` Pred: `0` Score: 0.1048
- Doc: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf` Chunk: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00000`
- Preview: "Exhibit 10d-2                                 RESELLER AGREEMENT                                   BY AND BETWEEN                                  PIVX CORPORATION                 "

### Error 9: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00001|exclusivity|1|positive_overlap`
- Clause: `exclusivity`
- True: `1` Pred: `0` Score: 0.3122
- Doc: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf` Chunk: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00001`
- Preview: "vue, Washington, 98007 ("Detto").  NOW THEREFORE, for good and valuable consideration, the parties hereby agree as follows:  1. GRANT OF RIGHTS  1.1 LICENSE. Subject to the terms a"

### Error 10: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00027|limitation_of_liability|0|nearby_same_doc`
- Clause: `limitation_of_liability`
- True: `0` Pred: `1` Score: 0.3495
- Doc: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf` Chunk: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00027`
- Preview: "F ANY LIMITED REMEDY PROVIDED HEREIN.                                         4  4.4 INDEMNIFICATION. Detto shall indemnify and hold PivX harmless from and against any and all dama"

### Error 11: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00032|limitation_of_liability|1|positive_overlap`
- Clause: `limitation_of_liability`
- True: `1` Pred: `0` Score: 0.0478
- Doc: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf` Chunk: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00032`
- Preview: "n with the business or goodwill of Detto.  6. GENERAL PROVISIONS  6.1 CONFIDENTIALITY. By virtue of this Agreement, each party may have access to information that is confidential t"

### Error 12: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00029|termination|0|nearby_same_doc`
- Clause: `termination`
- True: `0` Pred: `1` Score: 0.4869
- Doc: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf` Chunk: `cuad_adianutrition_inc_04_01_2005_ex_10_d2_re_4bb84acf0edf::chunk_00029`
- Preview: "l breach of this Agreement by the other party that is not cured within thirty (30) days of the other party's receipt of written notice of such breach. If a material breach is cured"
