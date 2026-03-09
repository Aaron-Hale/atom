# Reranker Evaluation Report

## Experiment
- Generated: 2026-03-09 02:13 UTC
- Purpose: compare vector-only retrieval against base and LoRA reranker modes
- Eval set: `eval/evalset_v1.jsonl`
- Eval items: 1903
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Vector encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker mode: `lora`
- Reranker backbone: `cross-encoder/ms-marco-MiniLM-L6-v2`
- LoRA adapter path: `models/reranker_lora_v3`
- Rerank candidate pool: top 50 vector candidates
- Reranker query mode: `clause_only`
- Score blend vector weight: 0.25
- Boilerplate penalty: 0.35
- Boilerplate filter enabled: `True`
- Boilerplate max-start: 1800
- Min candidates after filter fallback: 5
- Top-K: [3, 10]
- Reranker query policy: deterministic clause label only (`<clause_type> clause`)
- Example reranker query: assignment clause

## Vector Candidate Coverage (Oracle Overlap)

| K | Candidate Hit@K | Oracle Recall@K |
| --- | --- | --- |
| 20 | 0.2738 | 0.2197 |
| 50 | 0.3731 | 0.3137 |
| 100 | 0.4561 | 0.3902 |

## Overall Metrics

| K | Vec Hit@K | Base Hit@K | LoRA Hit@K | dBase | dLoRA | Vec Rec@K | Base Rec@K | LoRA Rec@K | dBase | dLoRA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 0.1125 | 0.1329 | 0.1287 | +0.0205 | +0.0163 | 0.0831 | 0.1058 | 0.1010 | +0.0227 | +0.0179 |
| 10 | 0.2060 | 0.2291 | 0.2275 | +0.0231 | +0.0215 | 0.1606 | 0.1833 | 0.1830 | +0.0227 | +0.0223 |

## Per-Clause Metrics

| Clause | N | Hit@3 Vec | Hit@3 Base | Hit@3 LoRA | dBase | dLoRA | Rec@3 Vec | Rec@3 Base | Rec@3 LoRA | dBase | dLoRA | Hit@10 Vec | Hit@10 Base | Hit@10 LoRA | dBase | dLoRA | Rec@10 Vec | Rec@10 Base | Rec@10 LoRA | dBase | dLoRA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assignment | 383 | 0.1123 | 0.1305 | 0.1279 | +0.0183 | +0.0157 | 0.0803 | 0.0902 | 0.0874 | +0.0099 | +0.0071 | 0.2141 | 0.2715 | 0.2611 | +0.0574 | +0.0470 | 0.1589 | 0.2003 | 0.1961 | +0.0414 | +0.0372 |
| change_of_control | 121 | 0.0909 | 0.1157 | 0.1157 | +0.0248 | +0.0248 | 0.0700 | 0.0918 | 0.0918 | +0.0218 | +0.0218 | 0.1818 | 0.1818 | 0.1818 | +0.0000 | +0.0000 | 0.1411 | 0.1559 | 0.1493 | +0.0148 | +0.0082 |
| confidentiality | 1 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| exclusivity | 180 | 0.0389 | 0.0556 | 0.0611 | +0.0167 | +0.0222 | 0.0193 | 0.0343 | 0.0371 | +0.0150 | +0.0178 | 0.0722 | 0.0667 | 0.0667 | -0.0056 | -0.0056 | 0.0511 | 0.0415 | 0.0415 | -0.0097 | -0.0097 |
| governing_law | 437 | 0.0503 | 0.1556 | 0.1510 | +0.1053 | +0.1007 | 0.0475 | 0.1545 | 0.1476 | +0.1070 | +0.1001 | 0.1030 | 0.2174 | 0.2174 | +0.1144 | +0.1144 | 0.1001 | 0.2157 | 0.2157 | +0.1156 | +0.1156 |
| limitation_of_liability | 275 | 0.2473 | 0.1527 | 0.1345 | -0.0945 | -0.1127 | 0.1728 | 0.1141 | 0.0950 | -0.0587 | -0.0778 | 0.4000 | 0.2945 | 0.3018 | -0.1055 | -0.0982 | 0.3107 | 0.2213 | 0.2295 | -0.0894 | -0.0812 |
| most_favored_nation | 28 | 0.0000 | 0.0357 | 0.0357 | +0.0357 | +0.0357 | 0.0000 | 0.0357 | 0.0357 | +0.0357 | +0.0357 | 0.0357 | 0.0714 | 0.0357 | +0.0357 | +0.0000 | 0.0357 | 0.0714 | 0.0357 | +0.0357 | +0.0000 |
| non_compete | 119 | 0.1092 | 0.1933 | 0.1849 | +0.0840 | +0.0756 | 0.0815 | 0.1362 | 0.1334 | +0.0548 | +0.0520 | 0.2101 | 0.3109 | 0.3193 | +0.1008 | +0.1092 | 0.1521 | 0.2334 | 0.2418 | +0.0813 | +0.0897 |
| termination | 284 | 0.1338 | 0.1197 | 0.1162 | -0.0141 | -0.0176 | 0.1078 | 0.0904 | 0.0880 | -0.0174 | -0.0198 | 0.2641 | 0.2324 | 0.2289 | -0.0317 | -0.0352 | 0.2025 | 0.1748 | 0.1702 | -0.0277 | -0.0323 |
| warranty | 75 | 0.1600 | 0.1467 | 0.1600 | -0.0133 | +0.0000 | 0.0928 | 0.1044 | 0.1128 | +0.0117 | +0.0200 | 0.2533 | 0.2267 | 0.2267 | -0.0267 | -0.0267 | 0.1689 | 0.1506 | 0.1606 | -0.0183 | -0.0083 |

## Comparison Examples

### Base: Cases Where Reranking Helped
#### Base Helped 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Vector top chunks:
  - rank 1, score 0.6624, doc `cuad_integritymediainc_20010329_10_k405_ex_10_47f47c769030`, chunk `cuad_integritymediainc_20010329_10_k405_ex_10_47f47c769030::chunk_00042`, offsets [27300, 28200], preview: "             other party its reasonable attorneys' fees in connection                   therewith in addition to the cos"
  - rank 2, score 0.6583, doc `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`, chunk `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::chunk_00039`, offsets [25350, 26250], preview: "CA 94306  To 2TheMart:            Dominic J. Magliarditi                         President                         18301"
  - rank 3, score 0.6508, doc `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa`, chunk `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa::chunk_00033`, offsets [21450, 22350], preview: "are then in conflict with the      corporate interests of the other Party; and  (d)  Upon termination or expiration of t"
- Base-reranked top chunks:
  - rank 1, score 0.8012, doc `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`, chunk `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::chunk_00033`, offsets [21450, 22350], preview: "use, or (d) is independently developed by recipient without reference to the Confidential Information.  The restriction "
  - rank 2, score 0.5139, doc `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250`, chunk `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250::chunk_00165`, offsets [107250, 108150], preview: "attorneys' fees and costs.  14.13 Further Assurances. Each Party shall promptly execute and deliver all such documents, "
  - rank 3, score 0.4771, doc `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce`, chunk `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce::chunk_00035`, offsets [22750, 23650], preview: "ssign this Agreement or any of its rights or delegate any of its duties under this Agreement without the prior written c"

#### Base Helped 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::termination`
- Clause: `termination`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the termination clause.
- Expected spans: [{'start': 18086, 'end': 18358}]
- Vector top chunks:
  - rank 1, score 0.7679, doc `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce`, chunk `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce::chunk_00019`, offsets [12350, 13250], preview: "d or extended as provided below, shall end as of December 31, 2000.        4.2   TERMINATION. Either party may terminate"
  - rank 2, score 0.7364, doc `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250`, chunk `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250::chunk_00098`, offsets [63700, 64600], preview: "rd party billing agents..  6. TERM AND TERMINATION  6.1 Term. The term of this Agreement shall continue for a period of "
  - rank 3, score 0.7333, doc `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e`, chunk `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e::chunk_00090`, offsets [58500, 59400], preview: "---------- ***Confidential Information has been omitted and has been filed separately with the Securities and Exchange C"
- Base-reranked top chunks:
  - rank 1, score 0.937, doc `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce`, chunk `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce::chunk_00019`, offsets [12350, 13250], preview: "d or extended as provided below, shall end as of December 31, 2000.        4.2   TERMINATION. Either party may terminate"
  - rank 2, score 0.9166, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00039`, offsets [25350, 26250], preview: "   10.2 Termination for Breach. In the event of a material breach of this Agreement by either party, the non-breaching p"
  - rank 3, score 0.7756, doc `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250`, chunk `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250::chunk_00098`, offsets [63700, 64600], preview: "rd party billing agents..  6. TERM AND TERMINATION  6.1 Term. The term of this Agreement shall continue for a period of "

#### Base Helped 3: `cuad_acceleratedtechnologiesholdingcorp_04_24_811731b9ed47::assignment`
- Clause: `assignment`
- Doc: `cuad_acceleratedtechnologiesholdingcorp_04_24_811731b9ed47`
- Question: In the agreement "JOINT VENTURE AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 9690, 'end': 9973}]
- Vector top chunks:
  - rank 1, score 0.6554, doc `cuad_valencetechnologyinc_02_14_2003_ex_10_jo_ce5d116b4ef1`, chunk `cuad_valencetechnologyinc_02_14_2003_ex_10_jo_ce5d116b4ef1::chunk_00034`, offsets [22100, 23000], preview: " Responsibilities of Party B  In addition to its other obligations under this Contract, Party B shall have the following"
  - rank 2, score 0.6523, doc `cuad_borrowmoneycom_inc_06_11_2020_ex_10_1_jo_7e6c66e6ae38`, chunk `cuad_borrowmoneycom_inc_06_11_2020_ex_10_1_jo_7e6c66e6ae38::chunk_00000`, offsets [0, 900], preview: "Exhibit 10.1  JOINT VENTURE AGREEMENT THIS JOINT VENTURE AGREEMENT (the "Agreement") made and entered into this 20th day"
  - rank 3, score 0.6415, doc `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0`, chunk `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0::chunk_00084`, offsets [54600, 55500], preview: "rent company (e.g. Igene or T&L, as the case may be) shall guarantee such subsidiary's or affiliate's performance hereun"
- Base-reranked top chunks:
  - rank 1, score 0.9528, doc `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0`, chunk `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0::chunk_00084`, offsets [54600, 55500], preview: "rent company (e.g. Igene or T&L, as the case may be) shall guarantee such subsidiary's or affiliate's performance hereun"
  - rank 2, score 0.8362, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00015`, offsets [9750, 10650], preview: "tion Notice) to an Alternate Producer on the same terms and conditions as those presented to Joint Venture Company. If J"
  - rank 3, score 0.8172, doc `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0`, chunk `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0::chunk_00082`, offsets [53300, 54200], preview: " security interest shall be created or levied on the Transferred Assets (except liens for taxes and materialsmen's liens"

### Base: Cases Where Reranking Failed
#### Base Regressed 1: `cuad_afsalabancorpinc_08_01_1996_ex_1_1_agenc_e8787a27fb7a::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_afsalabancorpinc_08_01_1996_ex_1_1_agenc_e8787a27fb7a`
- Question: In the agreement "AGENCY AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 112013, 'end': 112299}]
- Vector top chunks:
  - rank 1, score 0.6545, doc `cuad_athensbancsharescorp_11_02_2009_ex_1_2_a_589ba7323931`, chunk `cuad_athensbancsharescorp_11_02_2009_ex_1_2_a_589ba7323931::chunk_00206`, offsets [133900, 134800], preview: "party as a result  of the losses, claims, damages or liabilities (or actions, proceedings or claims in respect thereof) "
  - rank 2, score 0.6534, doc `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12`, chunk `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12::chunk_00026`, offsets [16900, 17800], preview: "ntial Information for any purpose outside the scope of this Agreement. Each party agrees to take all reasonable steps to"
  - rank 3, score 0.6499, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00049`, offsets [31850, 32750], preview: "ons they are otherwise obligated to perform.  8.6 No conditions, warranties or other terms apply to the Products, [ * ] "
- Base-reranked top chunks:
  - rank 1, score 0.907, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00049`, offsets [31850, 32750], preview: "ons they are otherwise obligated to perform.  8.6 No conditions, warranties or other terms apply to the Products, [ * ] "
  - rank 2, score 0.9038, doc `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12`, chunk `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12::chunk_00026`, offsets [16900, 17800], preview: "ntial Information for any purpose outside the scope of this Agreement. Each party agrees to take all reasonable steps to"
  - rank 3, score 0.8546, doc `cuad_fuelcellenergyinc_20191106_8_k_ex_10_1_1_0df2bad0551f`, chunk `cuad_fuelcellenergyinc_20191106_8_k_ex_10_1_1_0df2bad0551f::chunk_00079`, offsets [51350, 52250], preview: "ncluding, without limitation, business interruption, cost of capital, loss of anticipated revenues and profits, loss of "

#### Base Regressed 2: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0`
- Question: In the agreement "ODM - SUPPLY AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 10014, 'end': 10201}, {'start': 10206, 'end': 10413}]
- Vector top chunks:
  - rank 1, score 0.5955, doc `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236`, chunk `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236::chunk_00059`, offsets [38350, 39250], preview: "or specific provision of this Agreement.  15.6 Attorneys' Fees. The prevailing Party in any legal proceedings brought by"
  - rank 2, score 0.5848, doc `cuad_westpharmaceuticalservicesinc_20200116_8_0052329407ac`, chunk `cuad_westpharmaceuticalservicesinc_20200116_8_0052329407ac::chunk_00124`, offsets [80600, 81500], preview: "cts or operating results of it and/or its Affiliates; (b) that the Affected Party's creditworthiness may be reduced; and"
  - rank 3, score 0.579, doc `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926`, chunk `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926::chunk_00017`, offsets [11050, 11950], preview: " (regardless of form or structure) that would directly result in the Control of a Person or its business or assets chang"
- Base-reranked top chunks:
  - rank 1, score 0.9328, doc `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236`, chunk `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236::chunk_00059`, offsets [38350, 39250], preview: "or specific provision of this Agreement.  15.6 Attorneys' Fees. The prevailing Party in any legal proceedings brought by"
  - rank 2, score 0.8952, doc `cuad_westpharmaceuticalservicesinc_20200116_8_0052329407ac`, chunk `cuad_westpharmaceuticalservicesinc_20200116_8_0052329407ac::chunk_00124`, offsets [80600, 81500], preview: "cts or operating results of it and/or its Affiliates; (b) that the Affected Party's creditworthiness may be reduced; and"
  - rank 3, score 0.8294, doc `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926`, chunk `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926::chunk_00017`, offsets [11050, 11950], preview: " (regardless of form or structure) that would directly result in the Control of a Person or its business or assets chang"

#### Base Regressed 3: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443`
- Question: In the agreement "Distributor Agreement", find the exclusivity clause.
- Expected spans: [{'start': 2046, 'end': 2342}]
- Vector top chunks:
  - rank 1, score 0.6675, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00021`, offsets [13650, 14550], preview: " that it will not at any time represent the Company in any manner; that it will solicit orders for Products as an indepe"
  - rank 2, score 0.6543, doc `cuad_hyperionsoftwarecorp_09_28_1994_ex_10_47_ff3abeea554b`, chunk `cuad_hyperionsoftwarecorp_09_28_1994_ex_10_47_ff3abeea554b::chunk_00055`, offsets [35750, 36650], preview: "rty to act for the other party in any agency or other capacity, or to make commitments of any kind for the account of or"
  - rank 3, score 0.6435, doc `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f`, chunk `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f::chunk_00014`, offsets [9100, 10000], preview: "e paid by the customer (where Distributor will determine the customer price for the Products on a case by case basis) an"
- Base-reranked top chunks:
  - rank 1, score 0.8087, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00020`, offsets [13000, 13900], preview: "r distribute the Products to any third party. If, during the Term, Exhibit B and the Google Program  Guidelines conflict"
  - rank 2, score 0.5671, doc `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f`, chunk `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f::chunk_00009`, offsets [5850, 6750], preview: "mpensation shall be paid for the remaining monthly periods remaining in the Term, as if the termination of this Agreemen"
  - rank 3, score 0.4711, doc `cuad_fusemedicalinc_20190321_10_k_ex_10_43_11_2ac68dc12473`, chunk `cuad_fusemedicalinc_20190321_10_k_ex_10_43_11_2ac68dc12473::chunk_00035`, offsets [22750, 23650], preview: " for the Products in full within 30 days of their delivery. The Supplier shall be responsible for the costs of packaging"

### LoRA: Cases Where Reranking Helped
#### LoRA Helped 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Vector top chunks:
  - rank 1, score 0.6624, doc `cuad_integritymediainc_20010329_10_k405_ex_10_47f47c769030`, chunk `cuad_integritymediainc_20010329_10_k405_ex_10_47f47c769030::chunk_00042`, offsets [27300, 28200], preview: "             other party its reasonable attorneys' fees in connection                   therewith in addition to the cos"
  - rank 2, score 0.6583, doc `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`, chunk `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::chunk_00039`, offsets [25350, 26250], preview: "CA 94306  To 2TheMart:            Dominic J. Magliarditi                         President                         18301"
  - rank 3, score 0.6508, doc `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa`, chunk `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa::chunk_00033`, offsets [21450, 22350], preview: "are then in conflict with the      corporate interests of the other Party; and  (d)  Upon termination or expiration of t"
- LoRA-reranked top chunks:
  - rank 1, score 0.8012, doc `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`, chunk `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::chunk_00033`, offsets [21450, 22350], preview: "use, or (d) is independently developed by recipient without reference to the Confidential Information.  The restriction "
  - rank 2, score 0.4962, doc `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250`, chunk `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250::chunk_00165`, offsets [107250, 108150], preview: "attorneys' fees and costs.  14.13 Further Assurances. Each Party shall promptly execute and deliver all such documents, "
  - rank 3, score 0.4664, doc `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce`, chunk `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce::chunk_00035`, offsets [22750, 23650], preview: "ssign this Agreement or any of its rights or delegate any of its duties under this Agreement without the prior written c"

#### LoRA Helped 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::termination`
- Clause: `termination`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the termination clause.
- Expected spans: [{'start': 18086, 'end': 18358}]
- Vector top chunks:
  - rank 1, score 0.7679, doc `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce`, chunk `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce::chunk_00019`, offsets [12350, 13250], preview: "d or extended as provided below, shall end as of December 31, 2000.        4.2   TERMINATION. Either party may terminate"
  - rank 2, score 0.7364, doc `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250`, chunk `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250::chunk_00098`, offsets [63700, 64600], preview: "rd party billing agents..  6. TERM AND TERMINATION  6.1 Term. The term of this Agreement shall continue for a period of "
  - rank 3, score 0.7333, doc `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e`, chunk `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e::chunk_00090`, offsets [58500, 59400], preview: "---------- ***Confidential Information has been omitted and has been filed separately with the Securities and Exchange C"
- LoRA-reranked top chunks:
  - rank 1, score 0.9334, doc `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce`, chunk `cuad_embarkcominc_19991008_s_1a_ex_10_10_6487_689cf1ac16ce::chunk_00019`, offsets [12350, 13250], preview: "d or extended as provided below, shall end as of December 31, 2000.        4.2   TERMINATION. Either party may terminate"
  - rank 2, score 0.9166, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00039`, offsets [25350, 26250], preview: "   10.2 Termination for Breach. In the event of a material breach of this Agreement by either party, the non-breaching p"
  - rank 3, score 0.7875, doc `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250`, chunk `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250::chunk_00098`, offsets [63700, 64600], preview: "rd party billing agents..  6. TERM AND TERMINATION  6.1 Term. The term of this Agreement shall continue for a period of "

#### LoRA Helped 3: `cuad_acceleratedtechnologiesholdingcorp_04_24_811731b9ed47::assignment`
- Clause: `assignment`
- Doc: `cuad_acceleratedtechnologiesholdingcorp_04_24_811731b9ed47`
- Question: In the agreement "JOINT VENTURE AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 9690, 'end': 9973}]
- Vector top chunks:
  - rank 1, score 0.6554, doc `cuad_valencetechnologyinc_02_14_2003_ex_10_jo_ce5d116b4ef1`, chunk `cuad_valencetechnologyinc_02_14_2003_ex_10_jo_ce5d116b4ef1::chunk_00034`, offsets [22100, 23000], preview: " Responsibilities of Party B  In addition to its other obligations under this Contract, Party B shall have the following"
  - rank 2, score 0.6523, doc `cuad_borrowmoneycom_inc_06_11_2020_ex_10_1_jo_7e6c66e6ae38`, chunk `cuad_borrowmoneycom_inc_06_11_2020_ex_10_1_jo_7e6c66e6ae38::chunk_00000`, offsets [0, 900], preview: "Exhibit 10.1  JOINT VENTURE AGREEMENT THIS JOINT VENTURE AGREEMENT (the "Agreement") made and entered into this 20th day"
  - rank 3, score 0.6415, doc `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0`, chunk `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0::chunk_00084`, offsets [54600, 55500], preview: "rent company (e.g. Igene or T&L, as the case may be) shall guarantee such subsidiary's or affiliate's performance hereun"
- LoRA-reranked top chunks:
  - rank 1, score 0.9528, doc `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0`, chunk `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0::chunk_00084`, offsets [54600, 55500], preview: "rent company (e.g. Igene or T&L, as the case may be) shall guarantee such subsidiary's or affiliate's performance hereun"
  - rank 2, score 0.8288, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00015`, offsets [9750, 10650], preview: "tion Notice) to an Alternate Producer on the same terms and conditions as those presented to Joint Venture Company. If J"
  - rank 3, score 0.7792, doc `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0`, chunk `cuad_igenebiotechnologyinc_05_13_2003_ex_1_jo_67ba4093f0b0::chunk_00082`, offsets [53300, 54200], preview: " security interest shall be created or levied on the Transferred Assets (except liens for taxes and materialsmen's liens"

### LoRA: Cases Where Reranking Failed
#### LoRA Regressed 1: `cuad_afsalabancorpinc_08_01_1996_ex_1_1_agenc_e8787a27fb7a::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_afsalabancorpinc_08_01_1996_ex_1_1_agenc_e8787a27fb7a`
- Question: In the agreement "AGENCY AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 112013, 'end': 112299}]
- Vector top chunks:
  - rank 1, score 0.6545, doc `cuad_athensbancsharescorp_11_02_2009_ex_1_2_a_589ba7323931`, chunk `cuad_athensbancsharescorp_11_02_2009_ex_1_2_a_589ba7323931::chunk_00206`, offsets [133900, 134800], preview: "party as a result  of the losses, claims, damages or liabilities (or actions, proceedings or claims in respect thereof) "
  - rank 2, score 0.6534, doc `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12`, chunk `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12::chunk_00026`, offsets [16900, 17800], preview: "ntial Information for any purpose outside the scope of this Agreement. Each party agrees to take all reasonable steps to"
  - rank 3, score 0.6499, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00049`, offsets [31850, 32750], preview: "ons they are otherwise obligated to perform.  8.6 No conditions, warranties or other terms apply to the Products, [ * ] "
- LoRA-reranked top chunks:
  - rank 1, score 0.8734, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00049`, offsets [31850, 32750], preview: "ons they are otherwise obligated to perform.  8.6 No conditions, warranties or other terms apply to the Products, [ * ] "
  - rank 2, score 0.8487, doc `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12`, chunk `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12::chunk_00026`, offsets [16900, 17800], preview: "ntial Information for any purpose outside the scope of this Agreement. Each party agrees to take all reasonable steps to"
  - rank 3, score 0.8332, doc `cuad_fuelcellenergyinc_20191106_8_k_ex_10_1_1_0df2bad0551f`, chunk `cuad_fuelcellenergyinc_20191106_8_k_ex_10_1_1_0df2bad0551f::chunk_00079`, offsets [51350, 52250], preview: "ncluding, without limitation, business interruption, cost of capital, loss of anticipated revenues and profits, loss of "

#### LoRA Regressed 2: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0`
- Question: In the agreement "ODM - SUPPLY AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 10014, 'end': 10201}, {'start': 10206, 'end': 10413}]
- Vector top chunks:
  - rank 1, score 0.5955, doc `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236`, chunk `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236::chunk_00059`, offsets [38350, 39250], preview: "or specific provision of this Agreement.  15.6 Attorneys' Fees. The prevailing Party in any legal proceedings brought by"
  - rank 2, score 0.5848, doc `cuad_westpharmaceuticalservicesinc_20200116_8_0052329407ac`, chunk `cuad_westpharmaceuticalservicesinc_20200116_8_0052329407ac::chunk_00124`, offsets [80600, 81500], preview: "cts or operating results of it and/or its Affiliates; (b) that the Affected Party's creditworthiness may be reduced; and"
  - rank 3, score 0.579, doc `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926`, chunk `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926::chunk_00017`, offsets [11050, 11950], preview: " (regardless of form or structure) that would directly result in the Control of a Person or its business or assets chang"
- LoRA-reranked top chunks:
  - rank 1, score 0.9291, doc `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236`, chunk `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236::chunk_00059`, offsets [38350, 39250], preview: "or specific provision of this Agreement.  15.6 Attorneys' Fees. The prevailing Party in any legal proceedings brought by"
  - rank 2, score 0.8662, doc `cuad_westpharmaceuticalservicesinc_20200116_8_0052329407ac`, chunk `cuad_westpharmaceuticalservicesinc_20200116_8_0052329407ac::chunk_00124`, offsets [80600, 81500], preview: "cts or operating results of it and/or its Affiliates; (b) that the Affected Party's creditworthiness may be reduced; and"
  - rank 3, score 0.8259, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00032`, offsets [20800, 21700], preview: ". A party may suspend performance and/or terminate this Agreement with immediate effect, if:    (a) the other party ente"

#### LoRA Regressed 3: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443`
- Question: In the agreement "Distributor Agreement", find the exclusivity clause.
- Expected spans: [{'start': 2046, 'end': 2342}]
- Vector top chunks:
  - rank 1, score 0.6675, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00021`, offsets [13650, 14550], preview: " that it will not at any time represent the Company in any manner; that it will solicit orders for Products as an indepe"
  - rank 2, score 0.6543, doc `cuad_hyperionsoftwarecorp_09_28_1994_ex_10_47_ff3abeea554b`, chunk `cuad_hyperionsoftwarecorp_09_28_1994_ex_10_47_ff3abeea554b::chunk_00055`, offsets [35750, 36650], preview: "rty to act for the other party in any agency or other capacity, or to make commitments of any kind for the account of or"
  - rank 3, score 0.6435, doc `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f`, chunk `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f::chunk_00014`, offsets [9100, 10000], preview: "e paid by the customer (where Distributor will determine the customer price for the Products on a case by case basis) an"
- LoRA-reranked top chunks:
  - rank 1, score 0.8087, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00020`, offsets [13000, 13900], preview: "r distribute the Products to any third party. If, during the Term, Exhibit B and the Google Program  Guidelines conflict"
  - rank 2, score 0.5377, doc `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f`, chunk `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f::chunk_00009`, offsets [5850, 6750], preview: "mpensation shall be paid for the remaining monthly periods remaining in the Term, as if the termination of this Agreemen"
  - rank 3, score 0.5015, doc `cuad_fusemedicalinc_20190321_10_k_ex_10_43_11_2ac68dc12473`, chunk `cuad_fusemedicalinc_20190321_10_k_ex_10_43_11_2ac68dc12473::chunk_00035`, offsets [22750, 23650], preview: " for the Products in full within 30 days of their delivery. The Supplier shall be responsible for the costs of packaging"

## Failure Examples (By Method)

### Vector-Only Failures
#### Vector Failure 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::assignment`
- Clause: `assignment`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 12261, 'end': 12361}, {'start': 12412, 'end': 12439}]
- Top retrieved chunks:
  - rank 1, score 0.6169, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00046`, offsets [29900, 30800], preview: "ver Loop-branded Product to the Buyer. C. Pursuant to Section 2.4 of the Marketing Agreement, the Assignor desires to assign all rights and obligations under th"
  - rank 2, score 0.5958, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00045`, offsets [29250, 30150], preview: "ssignor and Assignee is a "Party;" together they are the "Parties"). RECITALS A. On August __, 2018, the Parties entered into a Marketing Agreement (the "Market"
  - rank 3, score 0.5783, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00026`, offsets [16900, 17800], preview: "Exchange Competitor.  4. ADVERTISING        4.1. Advertisements on the PaperExchange Site.              4.1.1. During the Term, VerticalNet shall have the exclu"

#### Vector Failure 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 0.695, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00066`, offsets [42900, 43800], preview: "ent or transfer of this Agreement to (a) a party's successor in connection with a Change in Control of such party, provided that such successor is not a competi"
  - rank 2, score 0.6332, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00067`, offsets [43550, 44450], preview: "his Agreement other than as permitted above will be null and void. This Agreement shall be binding upon and inure to the benefit of the parties and their respec"
  - rank 3, score 0.6236, doc `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0`, chunk `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0::chunk_00001`, offsets [650, 1550], preview: "rein, and intending to be legally bound hereby, the Parties agree as follows:  1. DEFINITIONS.       1.1 ADVERTISING shall mean any paid advertisements, links, "

#### Vector Failure 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Top retrieved chunks:
  - rank 1, score 0.6624, doc `cuad_integritymediainc_20010329_10_k405_ex_10_47f47c769030`, chunk `cuad_integritymediainc_20010329_10_k405_ex_10_47f47c769030::chunk_00042`, offsets [27300, 28200], preview: "             other party its reasonable attorneys' fees in connection                   therewith in addition to the costs thereof.        c.       If any part "
  - rank 2, score 0.6583, doc `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`, chunk `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::chunk_00039`, offsets [25350, 26250], preview: "CA 94306  To 2TheMart:            Dominic J. Magliarditi                         President                         18301 Von Karman Avenue,                     "
  - rank 3, score 0.6508, doc `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa`, chunk `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa::chunk_00033`, offsets [21450, 22350], preview: "are then in conflict with the      corporate interests of the other Party; and  (d)  Upon termination or expiration of this Agreement for any reason:       (i) "

#### Vector Failure 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 0.7397, doc `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3`, chunk `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3::chunk_00054`, offsets [35100, 36000], preview: "f infringement, the owner of said Derivative Work shall indemnify the other Party pursuant to this Section 9.                   9.4 LIMITATIONS ON LIABILITY. EX"
  - rank 2, score 0.7312, doc `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e`, chunk `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e::chunk_00083`, offsets [53950, 54850], preview: "PURSUANT TO SECTION 7.2  [Indemnity], OR TO THE EXTENT ARISING OUT OF ANY BREACH OF SECTION 11.4  [Nondisclosure], NEITHER PARTY WILL BE LIABLE (WHETHER IN CONT"
  - rank 3, score 0.7227, doc `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250`, chunk `cuad_tomonlineinc_20060501_20_f_ex_4_46_74970_177120bff250::chunk_00139`, offsets [90350, 91250], preview: "THE MAXIMUM EXTENT PERMISSIBLE UNDER APPLICABLE LAW, EXCEPT FOR THE WILFUL MISAPPROPRIATION OR INFRINGEMENT OF THE INTELLECTUAL PROPERTY OF A PARTY TO THIS AGRE"

#### Vector Failure 5: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 0.6531, doc `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc`, chunk `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc::chunk_00008`, offsets [5200, 6100], preview: "Goods           (hereinafter defined)) may be sold. The web pages at the Destination           shall be maintained in accordance with the requirements of this  "
  - rank 2, score 0.6315, doc `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa`, chunk `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa::chunk_00018`, offsets [11700, 12600], preview: "an entity which is a competitor to the other party. For the purposes of this Agreement, a "competitor" to MediaLinx shall be an Internet portal web site and/or "
  - rank 3, score 0.6225, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00026`, offsets [16900, 17800], preview: "Exchange Competitor.  4. ADVERTISING        4.1. Advertisements on the PaperExchange Site.              4.1.1. During the Term, VerticalNet shall have the exclu"

### Base-Reranker Failures
#### Base Failure 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::assignment`
- Clause: `assignment`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 12261, 'end': 12361}, {'start': 12412, 'end': 12439}]
- Top retrieved chunks:
  - rank 1, score 0.9295, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00046`, offsets [29900, 30800], preview: "ver Loop-branded Product to the Buyer. C. Pursuant to Section 2.4 of the Marketing Agreement, the Assignor desires to assign all rights and obligations under th"
  - rank 2, score 0.846, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00040`, offsets [26000, 26900], preview: " Assignment. This Agreement shall inure to the benefit of, and shall be binding upon, the Parties and their respective successors and assigns, but neither Party"
  - rank 3, score 0.794, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00045`, offsets [29250, 30150], preview: "ssignor and Assignee is a "Party;" together they are the "Parties"). RECITALS A. On August __, 2018, the Parties entered into a Marketing Agreement (the "Market"

#### Base Failure 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 0.835, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00066`, offsets [42900, 43800], preview: "ent or transfer of this Agreement to (a) a party's successor in connection with a Change in Control of such party, provided that such successor is not a competi"
  - rank 2, score 0.8064, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00067`, offsets [43550, 44450], preview: "his Agreement other than as permitted above will be null and void. This Agreement shall be binding upon and inure to the benefit of the parties and their respec"
  - rank 3, score 0.7911, doc `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236`, chunk `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236::chunk_00059`, offsets [38350, 39250], preview: "or specific provision of this Agreement.  15.6 Attorneys' Fees. The prevailing Party in any legal proceedings brought by or against the other Party to enforce a"

#### Base Failure 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 0.8361, doc `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3`, chunk `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3::chunk_00054`, offsets [35100, 36000], preview: "f infringement, the owner of said Derivative Work shall indemnify the other Party pursuant to this Section 9.                   9.4 LIMITATIONS ON LIABILITY. EX"
  - rank 2, score 0.8283, doc `cuad_sonos_inc_manufacturing_agreement_0_2a390ea9b1d0`, chunk `cuad_sonos_inc_manufacturing_agreement_0_2a390ea9b1d0::chunk_00113`, offsets [73450, 74350], preview: "censes, insurance, approvals and inspections in performance under this Agreement.  14.0 LIMITATION OF LIABILITY.  EXCEPT IN THE EVENT OF A VIOLATION OF SECTION "
  - rank 3, score 0.7936, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00051`, offsets [33150, 34050], preview: "portion of the fees paid         hereunder.  8.2     Limitations. Commerce One shall have no liability for any infringement         based on (i) the use of the "

#### Base Failure 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 0.8156, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00053`, offsets [34450, 35350], preview: "g the rights and obligations of the parties under Sections 4.3  [Non-Competition] and 5.8  [Non-Competition]) shall continue in full force and effect unless and"
  - rank 2, score 0.6807, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00048`, offsets [31200, 32100], preview: " Marks in accordance with the terms of this Agreement and with good trademark practices including, but not limited to, protecting the value of the goodwill resi"
  - rank 3, score 0.652, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00031`, offsets [20150, 21050], preview: "in its sole discretion, request that its Board of Directors and veteran industry sales force use reasonable efforts to provide pulp and paper industry specific "

#### Base Failure 5: `cuad_abilityinc_06_15_2020_ex_4_25_services_a_f9c7d740367d::assignment`
- Clause: `assignment`
- Doc: `cuad_abilityinc_06_15_2020_ex_4_25_services_a_f9c7d740367d`
- Question: In the agreement "SERVICES AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 5161, 'end': 5765}, {'start': 6181, 'end': 6479}, {'start': 6480, 'end': 6921}, {'start': 19304, 'end': 19488}]
- Top retrieved chunks:
  - rank 1, score 0.9477, doc `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc`, chunk `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc::chunk_00038`, offsets [24700, 25600], preview: "  (d) Assignment. This Agreement shall be binding upon the parties hereto and their respective successors and assigns; provided that this Agreement may not be a"
  - rank 2, score 0.8907, doc `cuad_conformisinc_20191101_10_q_ex_10_6_11861_9e1bda88a1df`, chunk `cuad_conformisinc_20191101_10_q_ex_10_6_11861_9e1bda88a1df::chunk_00080`, offsets [52000, 52900], preview: "ction with sale or transfer of all or substantially all   of the assigning Party's business or assets relating to the subject matter of this Agreement, whether "
  - rank 3, score 0.8739, doc `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca`, chunk `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca::chunk_00153`, offsets [99450, 100350], preview: "ment.  30       ASSIGNMENT OF RIGHTS AND OBLIGATIONS  30.1     No Party may assign,  sell, transfer or dispose of part or parts of its          rights or obliga"

### LoRA-Reranker Failures
#### LoRA Failure 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::assignment`
- Clause: `assignment`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 12261, 'end': 12361}, {'start': 12412, 'end': 12439}]
- Top retrieved chunks:
  - rank 1, score 0.8989, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00046`, offsets [29900, 30800], preview: "ver Loop-branded Product to the Buyer. C. Pursuant to Section 2.4 of the Marketing Agreement, the Assignor desires to assign all rights and obligations under th"
  - rank 2, score 0.846, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00040`, offsets [26000, 26900], preview: " Assignment. This Agreement shall inure to the benefit of, and shall be binding upon, the Parties and their respective successors and assigns, but neither Party"
  - rank 3, score 0.7569, doc `cuad_conformisinc_20191101_10_q_ex_10_6_11861_9e1bda88a1df`, chunk `cuad_conformisinc_20191101_10_q_ex_10_6_11861_9e1bda88a1df::chunk_00080`, offsets [52000, 52900], preview: "ction with sale or transfer of all or substantially all   of the assigning Party's business or assets relating to the subject matter of this Agreement, whether "

#### LoRA Failure 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 0.781, doc `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236`, chunk `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236::chunk_00059`, offsets [38350, 39250], preview: "or specific provision of this Agreement.  15.6 Attorneys' Fees. The prevailing Party in any legal proceedings brought by or against the other Party to enforce a"
  - rank 2, score 0.7698, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00066`, offsets [42900, 43800], preview: "ent or transfer of this Agreement to (a) a party's successor in connection with a Change in Control of such party, provided that such successor is not a competi"
  - rank 3, score 0.7669, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00067`, offsets [43550, 44450], preview: "his Agreement other than as permitted above will be null and void. This Agreement shall be binding upon and inure to the benefit of the parties and their respec"

#### LoRA Failure 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 0.8093, doc `cuad_sonos_inc_manufacturing_agreement_0_2a390ea9b1d0`, chunk `cuad_sonos_inc_manufacturing_agreement_0_2a390ea9b1d0::chunk_00113`, offsets [73450, 74350], preview: "censes, insurance, approvals and inspections in performance under this Agreement.  14.0 LIMITATION OF LIABILITY.  EXCEPT IN THE EVENT OF A VIOLATION OF SECTION "
  - rank 2, score 0.7911, doc `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3`, chunk `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3::chunk_00054`, offsets [35100, 36000], preview: "f infringement, the owner of said Derivative Work shall indemnify the other Party pursuant to this Section 9.                   9.4 LIMITATIONS ON LIABILITY. EX"
  - rank 3, score 0.7636, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00051`, offsets [33150, 34050], preview: "portion of the fees paid         hereunder.  8.2     Limitations. Commerce One shall have no liability for any infringement         based on (i) the use of the "

#### LoRA Failure 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 0.8156, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00053`, offsets [34450, 35350], preview: "g the rights and obligations of the parties under Sections 4.3  [Non-Competition] and 5.8  [Non-Competition]) shall continue in full force and effect unless and"
  - rank 2, score 0.5942, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00048`, offsets [31200, 32100], preview: " Marks in accordance with the terms of this Agreement and with good trademark practices including, but not limited to, protecting the value of the goodwill resi"
  - rank 3, score 0.5719, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00058`, offsets [37700, 38600], preview: "ion of VerticalNet's agreement to enter into an exclusivity and non-competition agreement herein, in conjunction with the other obligations under this Agreement"

#### LoRA Failure 5: `cuad_abilityinc_06_15_2020_ex_4_25_services_a_f9c7d740367d::assignment`
- Clause: `assignment`
- Doc: `cuad_abilityinc_06_15_2020_ex_4_25_services_a_f9c7d740367d`
- Question: In the agreement "SERVICES AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 5161, 'end': 5765}, {'start': 6181, 'end': 6479}, {'start': 6480, 'end': 6921}, {'start': 19304, 'end': 19488}]
- Top retrieved chunks:
  - rank 1, score 0.9206, doc `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc`, chunk `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc::chunk_00038`, offsets [24700, 25600], preview: "  (d) Assignment. This Agreement shall be binding upon the parties hereto and their respective successors and assigns; provided that this Agreement may not be a"
  - rank 2, score 0.8907, doc `cuad_conformisinc_20191101_10_q_ex_10_6_11861_9e1bda88a1df`, chunk `cuad_conformisinc_20191101_10_q_ex_10_6_11861_9e1bda88a1df::chunk_00080`, offsets [52000, 52900], preview: "ction with sale or transfer of all or substantially all   of the assigning Party's business or assets relating to the subject matter of this Agreement, whether "
  - rank 3, score 0.8323, doc `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca`, chunk `cuad_startecglobalcommunicationscorp_11_16_19_9f96e3eebaca::chunk_00153`, offsets [99450, 100350], preview: "ment.  30       ASSIGNMENT OF RIGHTS AND OBLIGATIONS  30.1     No Party may assign,  sell, transfer or dispose of part or parts of its          rights or obliga"
