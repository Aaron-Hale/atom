# Reranker Evaluation Report

## Experiment
- Generated: 2026-03-08 03:43 UTC
- Purpose: compare vector-only retrieval against base and LoRA reranker modes
- Eval set: `eval/evalset_v1.jsonl`
- Eval items: 1903
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Vector encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker mode: `lora`
- Reranker backbone: `cross-encoder/ms-marco-MiniLM-L6-v2`
- LoRA adapter path: `models/reranker_lora`
- Rerank candidate pool: top 20 vector candidates
- Top-K: [1, 3, 5, 10]
- Query policy: deterministic contract-specific question format `In the agreement "<title cue>", find the <clause_type> clause.`
- Title cue policy: first meaningful contract header/title line from source text after skipping filing boilerplate lines
- Example question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.

## Vector Candidate Coverage (Oracle Overlap)

| K | Candidate Hit@K | Oracle Recall@K |
| --- | --- | --- |
| 20 | 0.1345 | 0.1008 |
| 50 | 0.2107 | 0.1610 |
| 100 | 0.2733 | 0.2159 |

## Overall Metrics

| K | Vec Hit@K | Base Hit@K | LoRA Hit@K | dBase | dLoRA | Vec Rec@K | Base Rec@K | LoRA Rec@K | dBase | dLoRA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.0184 | 0.0326 | 0.0142 | +0.0142 | -0.0042 | 0.0126 | 0.0254 | 0.0102 | +0.0127 | -0.0025 |
| 3 | 0.0410 | 0.0662 | 0.0363 | +0.0252 | -0.0047 | 0.0301 | 0.0496 | 0.0265 | +0.0195 | -0.0036 |
| 5 | 0.0599 | 0.0857 | 0.0547 | +0.0257 | -0.0053 | 0.0430 | 0.0630 | 0.0404 | +0.0200 | -0.0026 |
| 10 | 0.0956 | 0.1130 | 0.0893 | +0.0173 | -0.0063 | 0.0714 | 0.0838 | 0.0675 | +0.0124 | -0.0039 |

## Per-Clause Metrics

| Clause | N | Hit@1 Vec | Hit@1 Base | Hit@1 LoRA | dBase | dLoRA | Rec@1 Vec | Rec@1 Base | Rec@1 LoRA | dBase | dLoRA | Hit@3 Vec | Hit@3 Base | Hit@3 LoRA | dBase | dLoRA | Rec@3 Vec | Rec@3 Base | Rec@3 LoRA | dBase | dLoRA | Hit@5 Vec | Hit@5 Base | Hit@5 LoRA | dBase | dLoRA | Rec@5 Vec | Rec@5 Base | Rec@5 LoRA | dBase | dLoRA | Hit@10 Vec | Hit@10 Base | Hit@10 LoRA | dBase | dLoRA | Rec@10 Vec | Rec@10 Base | Rec@10 LoRA | dBase | dLoRA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assignment | 383 | 0.0078 | 0.0235 | 0.0183 | +0.0157 | +0.0104 | 0.0065 | 0.0136 | 0.0113 | +0.0071 | +0.0048 | 0.0235 | 0.0548 | 0.0418 | +0.0313 | +0.0183 | 0.0115 | 0.0329 | 0.0275 | +0.0214 | +0.0160 | 0.0313 | 0.0731 | 0.0653 | +0.0418 | +0.0339 | 0.0163 | 0.0450 | 0.0402 | +0.0287 | +0.0239 | 0.0574 | 0.0914 | 0.0783 | +0.0339 | +0.0209 | 0.0331 | 0.0535 | 0.0496 | +0.0204 | +0.0165 |
| change_of_control | 121 | 0.0000 | 0.0413 | 0.0248 | +0.0413 | +0.0248 | 0.0000 | 0.0351 | 0.0207 | +0.0351 | +0.0207 | 0.0165 | 0.0661 | 0.0413 | +0.0496 | +0.0248 | 0.0124 | 0.0558 | 0.0303 | +0.0434 | +0.0179 | 0.0331 | 0.0909 | 0.0744 | +0.0579 | +0.0413 | 0.0227 | 0.0702 | 0.0510 | +0.0475 | +0.0282 | 0.0744 | 0.1240 | 0.1322 | +0.0496 | +0.0579 | 0.0579 | 0.0960 | 0.0960 | +0.0382 | +0.0382 |
| confidentiality | 1 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| exclusivity | 180 | 0.0222 | 0.0444 | 0.0000 | +0.0222 | -0.0222 | 0.0130 | 0.0324 | 0.0000 | +0.0194 | -0.0130 | 0.0333 | 0.0722 | 0.0167 | +0.0389 | -0.0167 | 0.0278 | 0.0507 | 0.0111 | +0.0229 | -0.0167 | 0.0444 | 0.0778 | 0.0278 | +0.0333 | -0.0167 | 0.0301 | 0.0570 | 0.0176 | +0.0270 | -0.0125 | 0.0778 | 0.0889 | 0.0444 | +0.0111 | -0.0333 | 0.0468 | 0.0614 | 0.0258 | +0.0146 | -0.0210 |
| governing_law | 437 | 0.0046 | 0.0160 | 0.0137 | +0.0114 | +0.0092 | 0.0046 | 0.0160 | 0.0120 | +0.0114 | +0.0074 | 0.0092 | 0.0320 | 0.0206 | +0.0229 | +0.0114 | 0.0092 | 0.0303 | 0.0189 | +0.0212 | +0.0097 | 0.0137 | 0.0366 | 0.0343 | +0.0229 | +0.0206 | 0.0137 | 0.0349 | 0.0326 | +0.0212 | +0.0189 | 0.0366 | 0.0503 | 0.0435 | +0.0137 | +0.0069 | 0.0366 | 0.0486 | 0.0418 | +0.0120 | +0.0051 |
| limitation_of_liability | 275 | 0.0400 | 0.0473 | 0.0218 | +0.0073 | -0.0182 | 0.0250 | 0.0346 | 0.0129 | +0.0096 | -0.0121 | 0.0655 | 0.0836 | 0.0582 | +0.0182 | -0.0073 | 0.0474 | 0.0614 | 0.0376 | +0.0139 | -0.0098 | 0.0982 | 0.1055 | 0.0655 | +0.0073 | -0.0327 | 0.0698 | 0.0765 | 0.0473 | +0.0067 | -0.0224 | 0.1455 | 0.1309 | 0.1236 | -0.0145 | -0.0218 | 0.1056 | 0.0945 | 0.0960 | -0.0112 | -0.0097 |
| most_favored_nation | 28 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0357 | 0.0000 | 0.0000 | -0.0357 | -0.0357 | 0.0357 | 0.0000 | 0.0000 | -0.0357 | -0.0357 | 0.0357 | 0.0357 | 0.0357 | +0.0000 | +0.0000 | 0.0357 | 0.0357 | 0.0357 | +0.0000 | +0.0000 |
| non_compete | 119 | 0.0168 | 0.0168 | 0.0084 | +0.0000 | -0.0084 | 0.0168 | 0.0140 | 0.0084 | -0.0028 | -0.0084 | 0.0504 | 0.0504 | 0.0420 | +0.0000 | -0.0084 | 0.0476 | 0.0476 | 0.0327 | -0.0000 | -0.0149 | 0.0756 | 0.1092 | 0.0672 | +0.0336 | -0.0084 | 0.0672 | 0.0885 | 0.0579 | +0.0213 | -0.0093 | 0.1345 | 0.1681 | 0.1261 | +0.0336 | -0.0084 | 0.1081 | 0.1398 | 0.1063 | +0.0317 | -0.0018 |
| termination | 284 | 0.0352 | 0.0528 | 0.0106 | +0.0176 | -0.0246 | 0.0230 | 0.0433 | 0.0088 | +0.0202 | -0.0142 | 0.0915 | 0.1127 | 0.0352 | +0.0211 | -0.0563 | 0.0630 | 0.0809 | 0.0305 | +0.0179 | -0.0325 | 0.1197 | 0.1373 | 0.0634 | +0.0176 | -0.0563 | 0.0872 | 0.0996 | 0.0519 | +0.0123 | -0.0353 | 0.1620 | 0.1761 | 0.1162 | +0.0141 | -0.0458 | 0.1261 | 0.1335 | 0.0946 | +0.0074 | -0.0315 |
| warranty | 75 | 0.0400 | 0.0400 | 0.0133 | +0.0000 | -0.0267 | 0.0244 | 0.0333 | 0.0027 | +0.0089 | -0.0218 | 0.0933 | 0.1200 | 0.0667 | +0.0267 | -0.0267 | 0.0778 | 0.0960 | 0.0409 | +0.0182 | -0.0369 | 0.1733 | 0.1733 | 0.0800 | +0.0000 | -0.0933 | 0.1131 | 0.1178 | 0.0442 | +0.0047 | -0.0689 | 0.2400 | 0.2667 | 0.1867 | +0.0267 | -0.0533 | 0.1744 | 0.1817 | 0.1082 | +0.0072 | -0.0662 |

## Comparison Examples

### Base: Cases Where Reranking Helped
#### Base Helped 1: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c`
- Question: In the agreement "ENDORSEMENT AGREEMENT", find the exclusivity clause.
- Expected spans: [{'start': 2245, 'end': 2477}, {'start': 2512, 'end': 2975}, {'start': 4447, 'end': 4542}]
- Vector top chunks:
  - rank 1, score 0.5744, doc `cuad_vitaminshoppecominc_09_13_1999_ex_10_26__728558ef455c`, chunk `cuad_vitaminshoppecominc_09_13_1999_ex_10_26__728558ef455c::chunk_00007`, offsets [7000, 8200], preview: "      during [*****] of the term of the Agreement.                e)       Excite is in the process of developing a "Spo"
  - rank 2, score 0.5637, doc `cuad_n2kinc_10_16_1997_ex_10_16_sponsorship_a_963c3ffff65f`, chunk `cuad_n2kinc_10_16_1997_ex_10_16_sponsorship_a_963c3ffff65f::chunk_00008`, offsets [8000, 9200], preview: " Excite Site and to formulate a meaningful response.                   Sponsor will have [****] after receipt of such wr"
  - rank 3, score 0.5597, doc `cuad_looksmartltd_07_20_2012_ex_99_d_i_sponso_50e9cf8bbd9c`, chunk `cuad_looksmartltd_07_20_2012_ex_99_d_i_sponso_50e9cf8bbd9c::chunk_00024`, offsets [24000, 25200], preview: ", the Company or its assets or businesses, (b) for its  decision with respect to making any investment contemplated here"
- Base-reranked top chunks:
  - rank 1, score 1.4764, doc `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c`, chunk `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00002`, offsets [2000, 3200], preview: "ll times 3.[*****] 4.[*****] (CONSULTANT may continue to place the [*****] logo on the [*****] consistent with historica"
  - rank 2, score -0.4152, doc `cuad_sporthaleyinc_09_29_1997_ex_10_2_10_endo_302538e39486`, chunk `cuad_sporthaleyinc_09_29_1997_ex_10_2_10_endo_302538e39486::chunk_00000`, offsets [0, 1200], preview: "ENDORSEMENT AGREEMENT      THIS ENDORSEMENT AGREEMENT is made and entered into effective this day of ___________________"
  - rank 3, score -0.4398, doc `cuad_holidayrvsuperstoresinc_04_15_2002_ex_10_6416397c454a`, chunk `cuad_holidayrvsuperstoresinc_04_15_2002_ex_10_6416397c454a::chunk_00009`, offsets [9000, 10200], preview: "pt to incorporate such editions and amendments in the final version disseminated by the Company.                 In the "

#### Base Helped 2: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::assignment`
- Clause: `assignment`
- Doc: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0`
- Question: In the agreement "ODM - SUPPLY AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 9752, 'end': 9870}, {'start': 14946, 'end': 15094}, {'start': 15095, 'end': 15243}, {'start': 17635, 'end': 17870}]
- Vector top chunks:
  - rank 1, score 0.5662, doc `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0`, chunk `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::chunk_00007`, offsets [7000, 8200], preview: "product and the associated shipping costs. 5.4 Payment terms Unless separate payment terms are agreed to outside of this"
  - rank 2, score 0.562, doc `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca`, chunk `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca::chunk_00031`, offsets [31000, 32200], preview: "                                    Page  11           this Agreement,  the manner in which the  Subcommittee's,  or any"
  - rank 3, score 0.5438, doc `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca`, chunk `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca::chunk_00108`, offsets [108000, 109200], preview: "A     PARTIES TO THE AGREEMENT  SCHEDULE B     VOTING INTERESTS, OWNERSHIP  INTERESTS IN SEGMENTS AND ALLOCATION        "
- Base-reranked top chunks:
  - rank 1, score 3.7302, doc `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0`, chunk `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::chunk_00014`, offsets [14000, 15200], preview: "ion of this agreement is held to be invalid by a court of competent jurisdiction, then the remaining provisions will nev"
  - rank 2, score 2.9844, doc `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0`, chunk `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::chunk_00000`, offsets [0, 1200], preview: "ODM - SUPPLY AGREEMENT BETWEEN: ORGANIC PREPARATIONS INC. 2nd Floor, Transpacific Haus Lini Highway, Port Vila. Vanuatu "
  - rank 3, score 2.8382, doc `cuad_vaxcyte_inc_05_22_2020_ex_10_19_supply_a_8b67ebb9c275`, chunk `cuad_vaxcyte_inc_05_22_2020_ex_10_19_supply_a_8b67ebb9c275::chunk_00094`, offsets [94000, 95200], preview: "be withheld unreasonably) except each Party may assign this Supply Agreement without the other Party's consent in the ca"

#### Base Helped 3: `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::governing_law`
- Clause: `governing_law`
- Doc: `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`
- Question: In the agreement "AIRSOPURE FRANCHISE AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 56975, 'end': 57149}]
- Vector top chunks:
  - rank 1, score 0.6778, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00035`, offsets [35000, 36200], preview: "y provisions of this Agreement or any other agreement between You and AIRSOPURE or its affiliates or suppliers;  3. You "
  - rank 2, score 0.6637, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00073`, offsets [73000, 73869], preview: "es incurred therein by such arty or parties (including without Initiation such as costs, expenses and fees on any appeal"
  - rank 3, score 0.6545, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00051`, offsets [51000, 52200], preview: "(or any shareholder if Your Franchise is a corporation) shall not, for a period of two years following termination of th"
- Base-reranked top chunks:
  - rank 1, score 3.6954, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00034`, offsets [34000, 35200], preview: "ent are personal to You, and that AIRSOPURE has entered into this Agreement and granted the Franchise rights and license"
  - rank 2, score 3.4384, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00051`, offsets [51000, 52200], preview: "(or any shareholder if Your Franchise is a corporation) shall not, for a period of two years following termination of th"
  - rank 3, score 3.3165, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00048`, offsets [48000, 49200], preview: "E subsequent to the termination or expiration of the Franchise herein granted in obtaining injunctive or other relief fo"

### Base: Cases Where Reranking Failed
#### Base Regressed 1: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443`
- Question: In the agreement "Distributor Agreement", find the exclusivity clause.
- Expected spans: [{'start': 2046, 'end': 2342}]
- Vector top chunks:
  - rank 1, score 0.6338, doc `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3`, chunk `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3::chunk_00011`, offsets [11000, 12200], preview: " the Distributor                                      Page -3-                    is that of vendor and vendee.  This  A"
  - rank 2, score 0.6243, doc `cuad_neonsystemsinc_03_01_1999_ex_10_5_distri_d45b462c8336`, chunk `cuad_neonsystemsinc_03_01_1999_ex_10_5_distri_d45b462c8336::chunk_00018`, offsets [18000, 19200], preview: "adjudged to be unenforceable or unlawful by any court, then such unenforceable or unlawful provision shall be excised he"
  - rank 3, score 0.6233, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00014`, offsets [14000, 15200], preview: "xpressly granted by this Agreement.  9.03.  Indemnity. The Distributor agrees to hold the Company free and harmless from"
- Base-reranked top chunks:
  - rank 1, score 3.4164, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00013`, offsets [13000, 14200], preview: "r distribute the Products to any third party. If, during the Term, Exhibit B and the Google Program  Guidelines conflict"
  - rank 2, score 2.1931, doc `cuad_neonsystemsinc_03_01_1999_ex_10_5_distri_d45b462c8336`, chunk `cuad_neonsystemsinc_03_01_1999_ex_10_5_distri_d45b462c8336::chunk_00018`, offsets [18000, 19200], preview: "adjudged to be unenforceable or unlawful by any court, then such unenforceable or unlawful provision shall be excised he"
  - rank 3, score 1.2536, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00049`, offsets [49000, 50200], preview: "ny rights it may have to receive any compensation or indemnity upon termination  or expiration of this Agreement, other "

#### Base Regressed 2: `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b`
- Question: In the agreement "Miltenyi Biotec-Bellicum Supply Agreement", find the limitation of liability clause.
- Expected spans: [{'start': 117859, 'end': 118179}, {'start': 143213, 'end': 143523}, {'start': 145050, 'end': 145319}, {'start': 145325, 'end': 145548}, {'start': 145551, 'end': 145866}, {'start': 145934, 'end': 146535}, {'start': 146541, 'end': 147125}, {'start': 146664, 'end': 147125}]
- Vector top chunks:
  - rank 1, score 0.6964, doc `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b`, chunk `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b::chunk_00140`, offsets [140000, 141200], preview: "ach supplied Miltenyi Product to comply with its obligations under this Agreement and under all Applicable Laws; and  (4"
  - rank 2, score 0.6877, doc `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b`, chunk `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b::chunk_00021`, offsets [21000, 22200], preview: "ion to the specific details set forth in the Module. Each Module exists independently of other Modules. Notwithstanding "
  - rank 3, score 0.6864, doc `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b`, chunk `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b::chunk_00148`, offsets [148000, 149200], preview: " any Third Party to the extent such Losses arise out of: (i) the material breach by Miltenyi of any representation, warr"
- Base-reranked top chunks:
  - rank 1, score 5.9816, doc `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b`, chunk `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b::chunk_00035`, offsets [35000, 36200], preview: " that are consistent with the corresponding limitations and obligations imposed on Bellicum  8      Miltenyi Biotec-Bell"
  - rank 2, score 5.3287, doc `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b`, chunk `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b::chunk_00030`, offsets [30000, 31200], preview: " and its Affiliates' and Subcontractors' activities and performance in connection with the manufacture of Miltenyi Produ"
  - rank 3, score 5.0616, doc `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b`, chunk `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b::chunk_00037`, offsets [37000, 38200], preview: "ndment.  (d) At the reasonable written request of Bellicum during the Term, Miltenyi shall enter into a direct supply ag"

#### Base Regressed 3: `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::warranty`
- Clause: `warranty`
- Doc: `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`
- Question: In the agreement "DISTRIBUTOR AGREEMENT", find the warranty clause.
- Expected spans: [{'start': 6573, 'end': 6916}]
- Vector top chunks:
  - rank 1, score 0.6761, doc `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f`, chunk `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f::chunk_00027`, offsets [27000, 28200], preview: "ce with Sections 8 and 10.3 to permit Distributor to offer a six-month warranty on the Products to customers and to enab"
  - rank 2, score 0.6659, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00006`, offsets [6000, 7200], preview: "ffiliates harmless from and against any and all claims, judgments, costs, awards, expenses (including reasonable attorne"
  - rank 3, score 0.6586, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00007`, offsets [7000, 8200], preview: "ed by negligence of Distributor, its agents, employees or customers, Distributor agrees to pay all charges associated wi"
- Base-reranked top chunks:
  - rank 1, score 4.4785, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00029`, offsets [29000, 30200], preview: "therwise [ * ]the Distributor App(s) or other products of Distributor to [ * ].  8. WARRANTIES  8.1 Each party warrants "
  - rank 2, score 3.8517, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00007`, offsets [7000, 8200], preview: "ed by negligence of Distributor, its agents, employees or customers, Distributor agrees to pay all charges associated wi"
  - rank 3, score 3.6652, doc `cuad_scansourceinc_20190822_10_k_ex_10_38_117_31966022f4b5`, chunk `cuad_scansourceinc_20190822_10_k_ex_10_38_117_31966022f4b5::chunk_00022`, offsets [22000, 23200], preview: "ibit C (End User License Agreement ("EULA")). For purposes of this Agreement, all references to "Customer" or "You" ther"

### LoRA: Cases Where Reranking Helped
#### LoRA Helped 1: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c`
- Question: In the agreement "ENDORSEMENT AGREEMENT", find the exclusivity clause.
- Expected spans: [{'start': 2245, 'end': 2477}, {'start': 2512, 'end': 2975}, {'start': 4447, 'end': 4542}]
- Vector top chunks:
  - rank 1, score 0.5744, doc `cuad_vitaminshoppecominc_09_13_1999_ex_10_26__728558ef455c`, chunk `cuad_vitaminshoppecominc_09_13_1999_ex_10_26__728558ef455c::chunk_00007`, offsets [7000, 8200], preview: "      during [*****] of the term of the Agreement.                e)       Excite is in the process of developing a "Spo"
  - rank 2, score 0.5637, doc `cuad_n2kinc_10_16_1997_ex_10_16_sponsorship_a_963c3ffff65f`, chunk `cuad_n2kinc_10_16_1997_ex_10_16_sponsorship_a_963c3ffff65f::chunk_00008`, offsets [8000, 9200], preview: " Excite Site and to formulate a meaningful response.                   Sponsor will have [****] after receipt of such wr"
  - rank 3, score 0.5597, doc `cuad_looksmartltd_07_20_2012_ex_99_d_i_sponso_50e9cf8bbd9c`, chunk `cuad_looksmartltd_07_20_2012_ex_99_d_i_sponso_50e9cf8bbd9c::chunk_00024`, offsets [24000, 25200], preview: ", the Company or its assets or businesses, (b) for its  decision with respect to making any investment contemplated here"
- LoRA-reranked top chunks:
  - rank 1, score 0.3161, doc `cuad_sonuscorp_03_12_1997_ex_10_11_sponsorshi_3c6463a27524`, chunk `cuad_sonuscorp_03_12_1997_ex_10_11_sponsorshi_3c6463a27524::chunk_00024`, offsets [24000, 25200], preview: "set forth below, be of no further  force or effect on the exercise by the Sponsor of its right to terminate  this Agreem"
  - rank 2, score -0.384, doc `cuad_holidayrvsuperstoresinc_04_15_2002_ex_10_6416397c454a`, chunk `cuad_holidayrvsuperstoresinc_04_15_2002_ex_10_6416397c454a::chunk_00009`, offsets [9000, 10200], preview: "pt to incorporate such editions and amendments in the final version disseminated by the Company.                 In the "
  - rank 3, score -0.5, doc `cuad_looksmartltd_07_20_2012_ex_99_d_i_sponso_50e9cf8bbd9c`, chunk `cuad_looksmartltd_07_20_2012_ex_99_d_i_sponso_50e9cf8bbd9c::chunk_00018`, offsets [18000, 19200], preview: "t of or relating to any material breach or inaccuracy of the  representations, warranties or covenants of such Sponsor c"

#### LoRA Helped 2: `cuad_adurobiotech_inc_06_02_2020_ex_10_7_cons_5182855f40b2::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_adurobiotech_inc_06_02_2020_ex_10_7_cons_5182855f40b2`
- Question: In the agreement "CONSULTING AGREEMENT", find the exclusivity clause.
- Expected spans: [{'start': 8854, 'end': 9244}]
- Vector top chunks:
  - rank 1, score 0.608, doc `cuad_globaltechnologiesltd_06_08_2020_ex_10_1_a17021f3e841`, chunk `cuad_globaltechnologiesltd_06_08_2020_ex_10_1_a17021f3e841::chunk_00009`, offsets [9000, 10200], preview: " and agrees with the Company that, in performing Consulting Services under this Agreement, Consultant will: (a) Comply w"
  - rank 2, score 0.5925, doc `cuad_globaltechnologiesltd_06_08_2020_ex_10_1_a17021f3e841`, chunk `cuad_globaltechnologiesltd_06_08_2020_ex_10_1_a17021f3e841::chunk_00001`, offsets [1000, 2200], preview: ". CONDITIONS. This Agreement will not take effect, and Consultant will have no obligation to provide any service whatsoe"
  - rank 3, score 0.592, doc `cuad_medalistdiversifiedreit_inc_05_18_2020_e_6426b993cdb7`, chunk `cuad_medalistdiversifiedreit_inc_05_18_2020_e_6426b993cdb7::chunk_00015`, offsets [15000, 16200], preview: "e or appoint, a majority of the Board, or the CEO or COO or CFO of the Company. 9. General Provisions. 9.1 Entire Agreem"
- LoRA-reranked top chunks:
  - rank 1, score 1.0251, doc `cuad_drivendeliveries_inc_05_22_2020_ex_10_4__0f87b862acbc`, chunk `cuad_drivendeliveries_inc_05_22_2020_ex_10_4__0f87b862acbc::chunk_00025`, offsets [25000, 26200], preview: "ussions, or representations between the Parties. Consultant represents and warrants that it is not relying on any statem"
  - rank 2, score 0.6966, doc `cuad_adurobiotech_inc_06_02_2020_ex_10_7_cons_5e245063fb3c`, chunk `cuad_adurobiotech_inc_06_02_2020_ex_10_7_cons_5e245063fb3c::chunk_00008`, offsets [8000, 9200], preview: "ding Services to, Aduro or its affiliates. In the event of a breach of this Paragraph 7 by Consultant, Aduro shall be en"
  - rank 3, score 0.6966, doc `cuad_adurobiotech_inc_06_02_2020_ex_10_7_cons_5182855f40b2`, chunk `cuad_adurobiotech_inc_06_02_2020_ex_10_7_cons_5182855f40b2::chunk_00008`, offsets [8000, 9200], preview: "ding Services to, Aduro or its affiliates. In the event of a breach of this Paragraph 7 by Consultant, Aduro shall be en"

#### LoRA Helped 3: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::assignment`
- Clause: `assignment`
- Doc: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0`
- Question: In the agreement "ODM - SUPPLY AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 9752, 'end': 9870}, {'start': 14946, 'end': 15094}, {'start': 15095, 'end': 15243}, {'start': 17635, 'end': 17870}]
- Vector top chunks:
  - rank 1, score 0.5662, doc `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0`, chunk `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::chunk_00007`, offsets [7000, 8200], preview: "product and the associated shipping costs. 5.4 Payment terms Unless separate payment terms are agreed to outside of this"
  - rank 2, score 0.562, doc `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca`, chunk `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca::chunk_00031`, offsets [31000, 32200], preview: "                                    Page  11           this Agreement,  the manner in which the  Subcommittee's,  or any"
  - rank 3, score 0.5438, doc `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca`, chunk `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca::chunk_00108`, offsets [108000, 109200], preview: "A     PARTIES TO THE AGREEMENT  SCHEDULE B     VOTING INTERESTS, OWNERSHIP  INTERESTS IN SEGMENTS AND ALLOCATION        "
- LoRA-reranked top chunks:
  - rank 1, score 1.6461, doc `cuad_teleglobeinternationalholdingsltd_03_29__c12a0545ec90`, chunk `cuad_teleglobeinternationalholdingsltd_03_29__c12a0545ec90::chunk_00033`, offsets [33000, 34200], preview: "ies, after the RFS Date, hereto in the holding of the meetings of the PG and the I&ASC; and   (f) those costs reasonably"
  - rank 2, score 0.2538, doc `cuad_vertexenergyinc_08_14_2014_ex_10_24_oper_f654a2a63676`, chunk `cuad_vertexenergyinc_08_14_2014_ex_10_24_oper_f654a2a63676::chunk_00055`, offsets [55000, 56200], preview: "e been inserted for convenience of reference only and shall not define or limit any of the terms and provisions hereof. "
  - rank 3, score 0.1225, doc `cuad_teleglobeinternationalholdingsltd_03_29__c12a0545ec90`, chunk `cuad_teleglobeinternationalholdingsltd_03_29__c12a0545ec90::chunk_00023`, offsets [23000, 24200], preview: "blished pursuant to this Paragraph 3 shall be amended by the Management Committee as and when as it is necessary.   13  "

### LoRA: Cases Where Reranking Failed
#### LoRA Regressed 1: `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::termination`
- Clause: `termination`
- Doc: `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`
- Question: In the agreement "ACCURAY INCORPORATED MULTIPLE LINAC AND MULTI-MODALITY DISTRIBUTOR AGREEMENT", find the termination clause.
- Expected spans: [{'start': 38022, 'end': 38322}, {'start': 48024, 'end': 48268}, {'start': 48758, 'end': 48941}]
- Vector top chunks:
  - rank 1, score 0.658, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00071`, offsets [71000, 72200], preview: "ings, representations and warranties, written and oral. If  any part of the terms and conditions stated herein are held "
  - rank 2, score 0.6423, doc `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3`, chunk `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3::chunk_00031`, offsets [31000, 32200], preview: "  DURATION AND TERMINATION           4.1      Duration.   Unless  earlier   terminated   otherwise  provided            "
  - rank 3, score 0.6306, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00001`, offsets [1000, 2200], preview: "urgery System, which is FDA cleared in the United States to provide treatment planning and image-guided stereotactic rad"
- LoRA-reranked top chunks:
  - rank 1, score -0.1228, doc `cuad_array_biopharma_inc_license_development__d3382a9f64de`, chunk `cuad_array_biopharma_inc_license_development__d3382a9f64de::chunk_00205`, offsets [205000, 206200], preview: "Approval from MHLW.  ARTICLE XIV   EFFECT OF TERMINATION  65        [ * ] = Certain confidential information contained i"
  - rank 2, score -0.2065, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00064`, offsets [64000, 65200], preview: "stributor agrees that it will help develop and work to preserve the goodwill of Accuray, and will not unreasonably harm "
  - rank 3, score -0.2327, doc `cuad_upjohninc_20200121_10_12g_ex_2_6_1194869_b3c0474f7b87`, chunk `cuad_upjohninc_20200121_10_12g_ex_2_6_1194869_b3c0474f7b87::chunk_00153`, offsets [153000, 154200], preview: "ion (b) shall not apply with respect to API as Product. 7.8 Effect of Termination or Expiration. (a) The termination or "

#### LoRA Regressed 2: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443`
- Question: In the agreement "Distributor Agreement", find the exclusivity clause.
- Expected spans: [{'start': 2046, 'end': 2342}]
- Vector top chunks:
  - rank 1, score 0.6338, doc `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3`, chunk `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3::chunk_00011`, offsets [11000, 12200], preview: " the Distributor                                      Page -3-                    is that of vendor and vendee.  This  A"
  - rank 2, score 0.6243, doc `cuad_neonsystemsinc_03_01_1999_ex_10_5_distri_d45b462c8336`, chunk `cuad_neonsystemsinc_03_01_1999_ex_10_5_distri_d45b462c8336::chunk_00018`, offsets [18000, 19200], preview: "adjudged to be unenforceable or unlawful by any court, then such unenforceable or unlawful provision shall be excised he"
  - rank 3, score 0.6233, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00014`, offsets [14000, 15200], preview: "xpressly granted by this Agreement.  9.03.  Indemnity. The Distributor agrees to hold the Company free and harmless from"
- LoRA-reranked top chunks:
  - rank 1, score -0.2872, doc `cuad_europeanmicroholdingsinc_03_06_1998_ex_1_d1f272bfcd9e`, chunk `cuad_europeanmicroholdingsinc_03_06_1998_ex_1_d1f272bfcd9e::chunk_00050`, offsets [50000, 51200], preview: "nication under this Agreement given by      either party to the other will be in writing and delivered either (a) in    "
  - rank 2, score -0.9083, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00012`, offsets [12000, 13200], preview: "ns contemplated hereby shall be reviewed in advance by, and shall be subject to the written approval (such approval not "
  - rank 3, score -1.7081, doc `cuad_invendacorp_20000828_s_1a_ex_10_2_258820_6bcb45dbf9cf`, chunk `cuad_invendacorp_20000828_s_1a_ex_10_2_258820_6bcb45dbf9cf::chunk_00028`, offsets [28000, 29200], preview: "nt that the Agreement is terminated pursuant to Section             16.a.v due to e-centives' acquisition by an Excite@H"

#### LoRA Regressed 3: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443::non_compete`
- Clause: `non_compete`
- Doc: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443`
- Question: In the agreement "Distributor Agreement", find the non compete clause.
- Expected spans: [{'start': 4148, 'end': 4686}, {'start': 4687, 'end': 4974}, {'start': 4975, 'end': 5179}, {'start': 12860, 'end': 13245}, {'start': 37858, 'end': 38234}]
- Vector top chunks:
  - rank 1, score 0.6784, doc `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3`, chunk `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3::chunk_00011`, offsets [11000, 12200], preview: " the Distributor                                      Page -3-                    is that of vendor and vendee.  This  A"
  - rank 2, score 0.6447, doc `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3`, chunk `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3::chunk_00045`, offsets [45000, 46200], preview: "s thereafter,  nor will Distributor solicit                            any  customer  or  potential  customer  of Compan"
  - rank 3, score 0.6359, doc `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443`, chunk `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443::chunk_00002`, offsets [2000, 3200], preview: "ws:  1.   APPOINTMENT.      -----------  1.1  Subject to the provisions of this Agreement, Airspan hereby appoints Distr"
- LoRA-reranked top chunks:
  - rank 1, score 0.8592, doc `cuad_fusemedicalinc_20190321_10_k_ex_10_43_11_2ac68dc12473`, chunk `cuad_fusemedicalinc_20190321_10_k_ex_10_43_11_2ac68dc12473::chunk_00012`, offsets [12000, 13200], preview: "junction with any trade marks owned or licensed by the Distributor.  9.3 All representations of the Trade Marks that the"
  - rank 2, score -0.9305, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00040`, offsets [40000, 41200], preview: "mic burden  relating to the Taxes. Subject to the foregoing and to compliance with applicable laws, Accuray and Distribu"
  - rank 3, score -0.9687, doc `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b`, chunk `cuad_bellicumpharmaceuticals_inc_05_07_2019_e_fa7d3a81805b::chunk_00021`, offsets [21000, 22200], preview: "ion to the specific details set forth in the Module. Each Module exists independently of other Modules. Notwithstanding "

## Failure Examples (By Method)

### Vector-Only Failures
#### Vector Failure 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::assignment`
- Clause: `assignment`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 12261, 'end': 12361}, {'start': 12412, 'end': 12439}]
- Top retrieved chunks:
  - rank 1, score 0.5722, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00029`, offsets [29000, 30200], preview: " with a principal place of business at 480 Fernand-Poitras, Terrebonne, Quebec, Canada (the "Assignor"), and Indorama Loop Technologies, LLC, a Delaware limited"
  - rank 2, score 0.529, doc `cuad_aspirityholdingsllc_05_07_2012_ex_10_6_o_ca7322524cd1`, chunk `cuad_aspirityholdingsllc_05_07_2012_ex_10_6_o_ca7322524cd1::chunk_00020`, offsets [20000, 21200], preview: "ll be subject to the prior  approval of the Company. The Contractor shall also oversee designing and printing all marketing materials (subject to the prior  app"
  - rank 3, score 0.5151, doc `cuad_lejuholdingsltd_03_12_2014_ex_10_34_inte_1156b972e5ba`, chunk `cuad_lejuholdingsltd_03_12_2014_ex_10_34_inte_1156b972e5ba::chunk_00021`, offsets [21000, 22200], preview: "s of which are as follows:   (i) Party B will provide real estate, home furnishing and life related data required by Party A, and Party A will use its technolog"

#### Vector Failure 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 0.5721, doc `cuad_kitovpharmaltd_20190326_20_f_ex_4_15_115_14a8af380b5b`, chunk `cuad_kitovpharmaltd_20190326_20_f_ex_4_15_115_14a8af380b5b::chunk_00003`, offsets [3000, 4200], preview: " are specified in European Commission Directive 2003/94/EC and the FDA's current Good Manufacturing Practices, particularly 21 CFR § 210 et seq., and 21 CFR §§ "
  - rank 2, score 0.5528, doc `cuad_changepointcorp_03_08_2000_ex_10_6_licen_f13c18aff07c`, chunk `cuad_changepointcorp_03_08_2000_ex_10_6_licen_f13c18aff07c::chunk_00040`, offsets [40000, 41200], preview: "or its Customers, subject to the mutual written          agreement on the scope of such services, pricing and other terms and          conditions.  5.7      SAL"
  - rank 3, score 0.5505, doc `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926`, chunk `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926::chunk_00011`, offsets [11000, 12200], preview: "ion or series of related contracts or transactions (regardless of form or structure) that would directly result in the Control of a Person or its business or as"

#### Vector Failure 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Top retrieved chunks:
  - rank 1, score 0.6061, doc `cuad_energouscorp_03_16_2017_ex_10_24_strateg_284bdebdfede`, chunk `cuad_energouscorp_03_16_2017_ex_10_24_strateg_284bdebdfede::chunk_00019`, offsets [19000, 20200], preview: "es, then, subject to the terms and conditions of this Agreement and during the Term, each party (in such capacity, "Licensor") hereby grants to the other party "
  - rank 2, score 0.5913, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00025`, offsets [25000, 26200], preview: ".7     Sales and Marketing Efforts. The parties shall engage in joint marketing         and sales activities as set forth in EXHIBIT D attached hereto and made "
  - rank 3, score 0.5778, doc `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3`, chunk `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3::chunk_00012`, offsets [12000, 13200], preview: " marketing, promotion and sale of the Co-Branded Service. In connection with such license each party agrees not to use the other party's Marks in any manner tha"

#### Vector Failure 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 0.6748, doc `cuad_vericelcorp_08_06_2019_ex_10_10_supply_a_785f5856b5f8`, chunk `cuad_vericelcorp_08_06_2019_ex_10_10_supply_a_785f5856b5f8::chunk_00075`, offsets [75000, 76200], preview: "sent of the other party, and the Indemnified Party shall use reasonable efforts to mitigate liabilities arising from such Third Party Claim.  7.5 Disclaimer. EX"
  - rank 2, score 0.6685, doc `cuad_scansourceinc_20190822_10_k_ex_10_38_117_31966022f4b5`, chunk `cuad_scansourceinc_20190822_10_k_ex_10_38_117_31966022f4b5::chunk_00048`, offsets [48000, 49200], preview: "EXHIBIT C (SOFTWARE LICENSE AGREEMENT), OR AMOUNTS DUE FOR PRODUCTS AND SERVICES PURCHASED WITH RESPECT TO THE PAYMENT OF WHICH NO BONA FIDE DISPUTE EXISTS, ALL"
  - rank 3, score 0.6588, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00033`, offsets [33000, 34200], preview: "t practicable after         Commerce One has exhausted all diligent efforts, (iii) terminate this           Agreement and refund to Corio a pro-rated portion of"

#### Vector Failure 5: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 0.5808, doc `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc`, chunk `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc::chunk_00005`, offsets [5000, 6200], preview: "rties may mutually agree upon in writing from time to time) a hot           link to Internet locations specified by the Co-Host (the           "Destination") fr"
  - rank 2, score 0.564, doc `cuad_vivint_solar_inc_non_competition_agreeme_f6704d689c07`, chunk `cuad_vivint_solar_inc_non_competition_agreeme_f6704d689c07::chunk_00001`, offsets [1000, 2200], preview: "ition Agreement.  WHEREAS, the Parties also desire to extend the term of the non-solicitation obligations under the Non-Competition Agreement.  AGREEMENT  NOW, "
  - rank 3, score 0.5594, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00025`, offsets [25000, 26200], preview: ".7     Sales and Marketing Efforts. The parties shall engage in joint marketing         and sales activities as set forth in EXHIBIT D attached hereto and made "

### Base-Reranker Failures
#### Base Failure 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::assignment`
- Clause: `assignment`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 12261, 'end': 12361}, {'start': 12412, 'end': 12439}]
- Top retrieved chunks:
  - rank 1, score 2.0142, doc `cuad_garrettmotioninc_20181001_8_k_ex_2_4_113_23126d0016b5`, chunk `cuad_garrettmotioninc_20181001_8_k_ex_2_4_113_23126d0016b5::chunk_00011`, offsets [11000, 12200], preview: "y, the public.  "Trademark Assignment Agreement" has the meaning set forth in Section 2.01. 3  Source: GARRETT MOTION INC., 8-K, 10/1/2018      Table of Content"
  - rank 2, score 1.7337, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00029`, offsets [29000, 30200], preview: " with a principal place of business at 480 Fernand-Poitras, Terrebonne, Quebec, Canada (the "Assignor"), and Indorama Loop Technologies, LLC, a Delaware limited"
  - rank 3, score 1.6374, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00026`, offsets [26000, 27200], preview: " Assignment. This Agreement shall inure to the benefit of, and shall be binding upon, the Parties and their respective successors and assigns, but neither Party"

#### Base Failure 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 2.483, doc `cuad_phreesia_inc_05_28_2019_ex_10_18_strateg_e12e8d428b63`, chunk `cuad_phreesia_inc_05_28_2019_ex_10_18_strateg_e12e8d428b63::chunk_00003`, offsets [3000, 4200], preview: "m time to time, which are incorporated into this Agreement by reference. 1      "Change of Control" means any of the following: (a) any merger, reorganization, "
  - rank 2, score 2.2207, doc `cuad_phreesia_inc_05_28_2019_ex_10_18_strateg_e12e8d428b63`, chunk `cuad_phreesia_inc_05_28_2019_ex_10_18_strateg_e12e8d428b63::chunk_00105`, offsets [105000, 106200], preview: "this Agreement, [***]. 26. Change of Control.  26.1 Competing Providers. This Section 26 will only apply in the event of a Change of Control to a Competing Prov"
  - rank 3, score 1.3297, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00021`, offsets [21000, 22200], preview: "goes into administration,  receivership or administrative receivership, is declared bankrupt or insolvent or is dissolved or otherwise ceases to carry on  busin"

#### Base Failure 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Top retrieved chunks:
  - rank 1, score 3.0623, doc `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0`, chunk `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0::chunk_00000`, offsets [0, 1200], preview: "1                                                                    EXHIBIT 10.26  Confidential Treatment Requested                            CO-BRANDING AGRE"
  - rank 2, score 2.9798, doc `cuad_pcquotecominc_19990721_s_1a_ex_10_11_637_9b47d1bf2f2c`, chunk `cuad_pcquotecominc_19990721_s_1a_ex_10_11_637_9b47d1bf2f2c::chunk_00000`, offsets [0, 1200], preview: "[LOGO]  SECOND AMENDMENT TO CO-BRANDING AGREEMENT  THIS SECOND AMENDMENT TO CO-BRANDING AGREEMENT (this "Amendment") is made and entered into, effective for all"
  - rank 3, score 2.3546, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00000`, offsets [0, 1200], preview: "Exhibit 10.4                                CO-BRANDING AGREEMENT  This Co-Branding Agreement (this "Agreement") dated September 30, 1999 (the "Effective Date")"

#### Base Failure 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 1.9438, doc `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc`, chunk `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc::chunk_00025`, offsets [25000, 26200], preview: "ecrets or other proprietary rights           beyond that stated in this Section 9(b).    (c)  No Combination Claims. Notwithstanding Section 9(b), NAI will not "
  - rank 2, score 1.6259, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00013`, offsets [13000, 14200], preview: "being restricted by the Marketing and Sale Restriction. If at any subsequent time during the term of this Agreement Loop gives Joint Venture Party written notic"
  - rank 3, score 1.571, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00033`, offsets [33000, 34200], preview: "t practicable after         Commerce One has exhausted all diligent efforts, (iii) terminate this           Agreement and refund to Corio a pro-rated portion of"

#### Base Failure 5: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 3.2001, doc `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0`, chunk `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0::chunk_00000`, offsets [0, 1200], preview: "1                                                                    EXHIBIT 10.26  Confidential Treatment Requested                            CO-BRANDING AGRE"
  - rank 2, score 2.9589, doc `cuad_vivint_solar_inc_non_competition_agreeme_f6704d689c07`, chunk `cuad_vivint_solar_inc_non_competition_agreeme_f6704d689c07::chunk_00001`, offsets [1000, 2200], preview: "ition Agreement.  WHEREAS, the Parties also desire to extend the term of the non-solicitation obligations under the Non-Competition Agreement.  AGREEMENT  NOW, "
  - rank 3, score 2.6816, doc `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa`, chunk `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa::chunk_00011`, offsets [11000, 12200], preview: "sers with substantial places of business in Canada) and HCI shall be entitled to sell advertising and sponsorships on all pages of the Co-Branded Site to US adv"

### LoRA-Reranker Failures
#### LoRA Failure 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::assignment`
- Clause: `assignment`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 12261, 'end': 12361}, {'start': 12412, 'end': 12439}]
- Top retrieved chunks:
  - rank 1, score -0.446, doc `cuad_energouscorp_03_16_2017_ex_10_24_strateg_284bdebdfede`, chunk `cuad_energouscorp_03_16_2017_ex_10_24_strateg_284bdebdfede::chunk_00019`, offsets [19000, 20200], preview: "es, then, subject to the terms and conditions of this Agreement and during the Term, each party (in such capacity, "Licensor") hereby grants to the other party "
  - rank 2, score -0.4975, doc `cuad_immunomedicsinc_08_07_2019_ex_10_1_promo_15c247b0c8c8`, chunk `cuad_immunomedicsinc_08_07_2019_ex_10_1_promo_15c247b0c8c8::chunk_00046`, offsets [46000, 47200], preview: "ution of the Brand Plan, potential changes to the Brand Plan and the promotion and Detailing of the Product to the Targets in the Territory.  4.2.2 Membership. "
  - rank 3, score -0.5815, doc `cuad_lejuholdingsltd_03_12_2014_ex_10_34_inte_1156b972e5ba`, chunk `cuad_lejuholdingsltd_03_12_2014_ex_10_34_inte_1156b972e5ba::chunk_00021`, offsets [21000, 22200], preview: "s of which are as follows:   (i) Party B will provide real estate, home furnishing and life related data required by Party A, and Party A will use its technolog"

#### LoRA Failure 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 1.3194, doc `cuad_gpaqacquisitionholdingsinc_20200123_s_4a_a3ae5a6630d5`, chunk `cuad_gpaqacquisitionholdingsinc_20200123_s_4a_a3ae5a6630d5::chunk_00026`, offsets [26000, 27200], preview: "y or against the other Party, or a receiver or custodian is appointed or applied for by the other Party, or an assignment for the benefit of creditors or a tran"
  - rank 2, score 1.1332, doc `cuad_buffalowildwingsinc_06_05_1998_ex_10_3_f_5d521b68c12d`, chunk `cuad_buffalowildwingsinc_06_05_1998_ex_10_3_f_5d521b68c12d::chunk_00033`, offsets [33000, 34200], preview: "emedy with which to compensate us for any breach of the terms of Paragraph V, VI and VII of this Agreement.  All of your employees having access to our confiden"
  - rank 3, score 0.4525, doc `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236`, chunk `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236::chunk_00038`, offsets [38000, 39200], preview: "nge any of Manufacturer's patents or other intellectual property rights.  15.5 No Third Party Beneficiaries. The Parties agree that this Agreement is for the be"

#### LoRA Failure 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Top retrieved chunks:
  - rank 1, score -1.0042, doc `cuad_exactsciencescorp_20180822_8_k_ex_10_1_1_6399d42c1afd`, chunk `cuad_exactsciencescorp_20180822_8_k_ex_10_1_1_6399d42c1afd::chunk_00115`, offsets [115000, 116200], preview: "il the Product in the Co-Promote Field in the Territory during the Term of this Agreement and in compliance with this Agreement. 39  Source: EXACT SCIENCES CORP"
  - rank 2, score -1.4926, doc `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e`, chunk `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e::chunk_00075`, offsets [75000, 76200], preview: "oice of Laws rules.       11.12    Venue.  Company hereby irrevocably consents to non-exclusive personal jurisdiction and venue in the state and federal courts "
  - rank 3, score -2.745, doc `cuad_aspirityholdingsllc_05_07_2012_ex_10_6_o_ca7322524cd1`, chunk `cuad_aspirityholdingsllc_05_07_2012_ex_10_6_o_ca7322524cd1::chunk_00020`, offsets [20000, 21200], preview: "ll be subject to the prior  approval of the Company. The Contractor shall also oversee designing and printing all marketing materials (subject to the prior  app"

#### LoRA Failure 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 1.9415, doc `cuad_legacyeducationallianceinc_20200330_10_k_5e895acf3bd6`, chunk `cuad_legacyeducationallianceinc_20200330_10_k_5e895acf3bd6::chunk_00031`, offsets [31000, 32200], preview: "ing, radio advertising, direct mail, outbound calls, email marketing, affiliate marketing, online advertising, infomercials and other marketing methods, by or t"
  - rank 2, score 0.9256, doc `cuad_euromediaholdingscorp_20070215_10sb12g_e_9e877bd56484`, chunk `cuad_euromediaholdingscorp_20070215_10sb12g_e_9e877bd56484::chunk_00015`, offsets [15000, 16200], preview: "limitation, any libelous, slanderous or obscene material, violations of copyright, trade- mark rights or other intellectual property rights, personality right, "
  - rank 3, score 0.7677, doc `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc`, chunk `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc::chunk_00025`, offsets [25000, 26200], preview: "ecrets or other proprietary rights           beyond that stated in this Section 9(b).    (c)  No Combination Claims. Notwithstanding Section 9(b), NAI will not "

#### LoRA Failure 5: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 0.8055, doc `cuad_netgrocerinc_07_31_1998_ex_10_15_sponsor_a75738cb82de`, chunk `cuad_netgrocerinc_07_31_1998_ex_10_15_sponsor_a75738cb82de::chunk_00018`, offsets [18000, 19200], preview: "upermarkets, as listed in Exhibit A. The parties may                   amend Exhibit A from time to time and Excite will not                   unreasonably with"
  - rank 2, score 0.5153, doc `cuad_revolutionmedicinesinc_20200117_s_1_ex_1_fc6159983c1f`, chunk `cuad_revolutionmedicinesinc_20200117_s_1_ex_1_fc6159983c1f::chunk_00136`, offsets [136000, 137200], preview: " writing at least [***] prior to the anticipated launch of such Product in the Co-Promotion Territory. If (i) RevMed does not provide the above election notice "
  - rank 3, score 0.3849, doc `cuad_aimmunetherapeuticsinc_20200205_8_k_ex_1_cc54107a4dee`, chunk `cuad_aimmunetherapeuticsinc_20200205_8_k_ex_1_cc54107a4dee::chunk_00060`, offsets [60000, 61200], preview: "ne by [***].  ARTICLE 5 COMMERCIALIZATION  5.1 Commercialization. During the Term, as between the Parties, Aimmune shall be solely responsible for Commercializi"
