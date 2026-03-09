# Reranker Evaluation Report

## Experiment
- Generated: 2026-03-08 05:36 UTC
- Purpose: compare vector-only retrieval against base and LoRA reranker modes
- Eval set: `eval/evalset_v1.jsonl`
- Eval items: 1903
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Vector encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker mode: `base`
- Reranker backbone: `cross-encoder/ms-marco-MiniLM-L6-v2`
- LoRA adapter path: `models/reranker_lora`
- Rerank candidate pool: top 20 vector candidates
- Top-K: [3, 10]
- Query policy: deterministic contract-specific question format `In the agreement "<title cue>", find the <clause_type> clause.`
- Title cue policy: first meaningful contract header/title line from source text after skipping filing boilerplate lines
- Example question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.

## Vector Candidate Coverage (Oracle Overlap)

| K | Candidate Hit@K | Oracle Recall@K |
| --- | --- | --- |
| 20 | 0.2738 | 0.2197 |
| 50 | 0.3731 | 0.3137 |
| 100 | 0.4561 | 0.3902 |

## Overall Metrics

| K | Vector Hit@K | Base Hit@K | Delta | Vector Recall@K | Base Recall@K | Delta |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 0.1125 | 0.1009 | -0.0116 | 0.0831 | 0.0755 | -0.0077 |
| 10 | 0.2060 | 0.2007 | -0.0053 | 0.1606 | 0.1558 | -0.0048 |

## Per-Clause Metrics

| Clause | N | Hit@3 Vec | Hit@3 Base | dHit@3 | Rec@3 Vec | Rec@3 Base | dRec@3 | Hit@10 Vec | Hit@10 Base | dHit@10 | Rec@10 Vec | Rec@10 Base | dRec@10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assignment | 383 | 0.1123 | 0.0992 | -0.0131 | 0.0803 | 0.0647 | -0.0156 | 0.2141 | 0.2298 | +0.0157 | 0.1589 | 0.1626 | +0.0037 |
| change_of_control | 121 | 0.0909 | 0.1157 | +0.0248 | 0.0700 | 0.0883 | +0.0183 | 0.1818 | 0.2066 | +0.0248 | 0.1411 | 0.1734 | +0.0324 |
| confidentiality | 1 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 |
| exclusivity | 180 | 0.0389 | 0.0611 | +0.0222 | 0.0193 | 0.0462 | +0.0269 | 0.0722 | 0.0833 | +0.0111 | 0.0511 | 0.0613 | +0.0102 |
| governing_law | 437 | 0.0503 | 0.0709 | +0.0206 | 0.0475 | 0.0686 | +0.0212 | 0.1030 | 0.1236 | +0.0206 | 0.1001 | 0.1201 | +0.0200 |
| limitation_of_liability | 275 | 0.2473 | 0.1309 | -0.1164 | 0.1728 | 0.0898 | -0.0830 | 0.4000 | 0.3164 | -0.0836 | 0.3107 | 0.2368 | -0.0740 |
| most_favored_nation | 28 | 0.0000 | 0.0357 | +0.0357 | 0.0000 | 0.0357 | +0.0357 | 0.0357 | 0.0714 | +0.0357 | 0.0357 | 0.0714 | +0.0357 |
| non_compete | 119 | 0.1092 | 0.1261 | +0.0168 | 0.0815 | 0.0964 | +0.0149 | 0.2101 | 0.2185 | +0.0084 | 0.1521 | 0.1724 | +0.0202 |
| termination | 284 | 0.1338 | 0.1197 | -0.0141 | 0.1078 | 0.0900 | -0.0178 | 0.2641 | 0.2430 | -0.0211 | 0.2025 | 0.1811 | -0.0215 |
| warranty | 75 | 0.1600 | 0.1600 | +0.0000 | 0.0928 | 0.0951 | +0.0023 | 0.2533 | 0.2133 | -0.0400 | 0.1689 | 0.1423 | -0.0266 |

## Comparison Examples

### Base: Cases Where Reranking Helped
#### Base Helped 1: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::non_compete`
- Clause: `non_compete`
- Doc: `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c`
- Question: In the agreement "ENDORSEMENT AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5347, 'end': 5519}]
- Vector top chunks:
  - rank 1, score 0.6386, doc `cuad_womensgolfunlimitedinc_03_29_2000_ex_10__ec3d72dec9df`, chunk `cuad_womensgolfunlimitedinc_03_29_2000_ex_10__ec3d72dec9df::chunk_00010`, offsets [6500, 7400], preview: " the creation, manufacture, marketing, sale and promotion of the Products. As a condition precedent to, and a continuing"
  - rank 2, score 0.5982, doc `cuad_holidayrvsuperstoresinc_04_15_2002_ex_10_6416397c454a`, chunk `cuad_holidayrvsuperstoresinc_04_15_2002_ex_10_6416397c454a::chunk_00016`, offsets [10400, 11300], preview: "ia and shall be governed by and construed in accordance with the laws thereof without regard to principles of conflicts "
  - rank 3, score 0.5976, doc `cuad_virtualscopics_inc_11_12_2010_ex_10_1_st_f2ddb542f1fb`, chunk `cuad_virtualscopics_inc_11_12_2010_ex_10_1_st_f2ddb542f1fb::chunk_00063`, offsets [40950, 41850], preview: "or the purpose of obtaining employment whether in response to a general advertisement of employment or where such contac"
- Base-reranked top chunks:
  - rank 1, score 1.164, doc `cuad_ashworthinc_01_29_1999_ex_10_d_promotion_2bd4907bfee8`, chunk `cuad_ashworthinc_01_29_1999_ex_10_d_promotion_2bd4907bfee8::chunk_00027`, offsets [17550, 18450], preview: "ad been omitted from this Agreement.  Termination under the provisions of this section shall be without prejudice to any"
  - rank 2, score -0.0897, doc `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c`, chunk `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00007`, offsets [4550, 5450], preview: "expressly understood by the parties that CONSULTANT may play [* ****] clubs in the bag other than ADAMS GOLF clubs inclu"
  - rank 3, score -0.9401, doc `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c`, chunk `cuad_adamsgolfinc_03_21_2005_ex_10_17_endorse_ab2812efde0c::chunk_00000`, offsets [0, 900], preview: "REDACTED COPY  CONFIDENTIAL TREATMENT REQUESTED  CONFIDENTIAL PORTIONS OF THIS  DOCUMENT HAVE BEEN REDACTED  AND HAVE BE"

#### Base Helped 2: `cuad_adurobiotech_inc_06_02_2020_ex_10_7_cons_5182855f40b2::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_adurobiotech_inc_06_02_2020_ex_10_7_cons_5182855f40b2`
- Question: In the agreement "CONSULTING AGREEMENT", find the exclusivity clause.
- Expected spans: [{'start': 8854, 'end': 9244}]
- Vector top chunks:
  - rank 1, score 0.6682, doc `cuad_pandiontherapeuticsholdcollc_05_22_2020__f5cc2928ef9a`, chunk `cuad_pandiontherapeuticsholdcollc_05_22_2020__f5cc2928ef9a::chunk_00002`, offsets [1300, 2200], preview: "o this Agreement, and he shall not assist any other person or organization that engages in any such activity.  2. Term. "
  - rank 2, score 0.6646, doc `cuad_kiromicbiopharma_inc_05_11_2020_ex_10_23_9b72cb20a233`, chunk `cuad_kiromicbiopharma_inc_05_11_2020_ex_10_23_9b72cb20a233::chunk_00017`, offsets [11050, 11950], preview: "ed to be devoted to any other third party. The Consultant shall not use the funding, resources and facilities of any oth"
  - rank 3, score 0.6216, doc `cuad_sphere3dcorp_06_24_2020_ex_10_12_consult_2a2d58fce612`, chunk `cuad_sphere3dcorp_06_24_2020_ex_10_12_consult_2a2d58fce612::chunk_00016`, offsets [10400, 11300], preview: "e market price of the Company's securities in violation of law or regulation, nor pay or otherwise induce others to take"
- Base-reranked top chunks:
  - rank 1, score 3.2863, doc `cuad_pandiontherapeuticsholdcollc_05_22_2020__f5cc2928ef9a`, chunk `cuad_pandiontherapeuticsholdcollc_05_22_2020__f5cc2928ef9a::chunk_00000`, offsets [0, 900], preview: "Exhibit 10.17  IMMUNOTOLERANCE, INC.  CONSULTING AGREEMENT  This Consulting Agreement (the "Agreement"), made this 27t h"
  - rank 2, score 1.0501, doc `cuad_pandiontherapeuticsholdcollc_05_22_2020__f5cc2928ef9a`, chunk `cuad_pandiontherapeuticsholdcollc_05_22_2020__f5cc2928ef9a::chunk_00002`, offsets [1300, 2200], preview: "o this Agreement, and he shall not assist any other person or organization that engages in any such activity.  2. Term. "
  - rank 3, score 0.5631, doc `cuad_kiromicbiopharma_inc_05_11_2020_ex_10_23_9b72cb20a233`, chunk `cuad_kiromicbiopharma_inc_05_11_2020_ex_10_23_9b72cb20a233::chunk_00015`, offsets [9750, 10650], preview: "lict with any of the provisions of this Agreement, or that would preclude Consultant from complying with the provisions "

#### Base Helped 3: `cuad_afsalabancorpinc_08_01_1996_ex_1_1_agenc_e8787a27fb7a::governing_law`
- Clause: `governing_law`
- Doc: `cuad_afsalabancorpinc_08_01_1996_ex_1_1_agenc_e8787a27fb7a`
- Question: In the agreement "AGENCY AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 119866, 'end': 119957}]
- Vector top chunks:
  - rank 1, score 0.6824, doc `cuad_alliancebancorpincofpennsylvania_10_18_2_85c8f489bb2d`, chunk `cuad_alliancebancorpincofpennsylvania_10_18_2_85c8f489bb2d::chunk_00195`, offsets [126750, 127650], preview: "is Agreement is intended or shall be construed to give any person, firm or corporation, other than the Agent, the Compan"
  - rank 2, score 0.6437, doc `cuad_alamogordofinancialcorp_12_16_1999_ex_1__87abb558d8b7`, chunk `cuad_alamogordofinancialcorp_12_16_1999_ex_1__87abb558d8b7::chunk_00079`, offsets [51350, 52250], preview: "able in accordance with its terms.                 (iii)   Each  of  the  Agent  and  its   employees,   agents  and    "
  - rank 3, score 0.6372, doc `cuad_afsalabancorpinc_08_01_1996_ex_1_1_agenc_e8787a27fb7a`, chunk `cuad_afsalabancorpinc_08_01_1996_ex_1_1_agenc_e8787a27fb7a::chunk_00101`, offsets [65650, 66550], preview: "action on the part of the Company and the Association and, upon payment  therefor in accordance  with the terms of the P"
- Base-reranked top chunks:
  - rank 1, score -1.2885, doc `cuad_americanphysicianscapitalinc_03_31_2003__2b007bce9814`, chunk `cuad_americanphysicianscapitalinc_03_31_2003__2b007bce9814::chunk_00024`, offsets [15600, 16500], preview: "  this Agreement without the written permission of MICOA or its                   successors or assigns.           9.   "
  - rank 2, score -1.6509, doc `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc`, chunk `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc::chunk_00008`, offsets [5200, 6100], preview: "ith, violate, or result in a breach of, the terms, conditions or provisions of, or constitute a default under, the organ"
  - rank 3, score -2.5888, doc `cuad_americanphysicianscapitalinc_03_31_2003__2b007bce9814`, chunk `cuad_americanphysicianscapitalinc_03_31_2003__2b007bce9814::chunk_00023`, offsets [14950, 15850], preview: "e                   signatures may be executed in counterparts which shall                        together be regarded a"

### Base: Cases Where Reranking Failed
#### Base Regressed 1: `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::assignment`
- Clause: `assignment`
- Doc: `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`
- Question: In the agreement "ACCURAY INCORPORATED MULTIPLE LINAC AND MULTI-MODALITY DISTRIBUTOR AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 64511, 'end': 65043}, {'start': 65062, 'end': 65531}]
- Vector top chunks:
  - rank 1, score 0.7201, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00002`, offsets [1300, 2200], preview: "s, Accuray relies on qualified distributors to market and distribute its products and services.     Accuray and Siemens "
  - rank 2, score 0.6772, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00059`, offsets [38350, 39250], preview: "MENT     5.1. Orders. Distributor shall make an offer to a Customer based on the Quote provided by Accuray pursuant to t"
  - rank 3, score 0.6686, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00011`, offsets [7150, 8050], preview: "h proposed sale of a Product or  Service under this Agreement is subject to the approval rights of Accuray set forth in "
- Base-reranked top chunks:
  - rank 1, score 6.6096, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00002`, offsets [1300, 2200], preview: "s, Accuray relies on qualified distributors to market and distribute its products and services.     Accuray and Siemens "
  - rank 2, score 6.2492, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00011`, offsets [7150, 8050], preview: "h proposed sale of a Product or  Service under this Agreement is subject to the approval rights of Accuray set forth in "
  - rank 3, score 5.0566, doc `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821`, chunk `cuad_accurayinc_09_01_2010_ex_10_31_distribut_467b424e0821::chunk_00019`, offsets [12350, 13250], preview: "thereof, it (i)  possesses the knowledge, experience, skills, and ability required to properly fulfill its obligations u"

#### Base Regressed 2: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443::exclusivity`
- Clause: `exclusivity`
- Doc: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443`
- Question: In the agreement "Distributor Agreement", find the exclusivity clause.
- Expected spans: [{'start': 2046, 'end': 2342}]
- Vector top chunks:
  - rank 1, score 0.6675, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00021`, offsets [13650, 14550], preview: " that it will not at any time represent the Company in any manner; that it will solicit orders for Products as an indepe"
  - rank 2, score 0.6543, doc `cuad_hyperionsoftwarecorp_09_28_1994_ex_10_47_ff3abeea554b`, chunk `cuad_hyperionsoftwarecorp_09_28_1994_ex_10_47_ff3abeea554b::chunk_00055`, offsets [35750, 36650], preview: "rty to act for the other party in any agency or other capacity, or to make commitments of any kind for the account of or"
  - rank 3, score 0.6435, doc `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f`, chunk `cuad_entertainmentgamingasiainc_02_15_2005_ex_100309b1e06f::chunk_00014`, offsets [9100, 10000], preview: "e paid by the customer (where Distributor will determine the customer price for the Products on a case by case basis) an"
- Base-reranked top chunks:
  - rank 1, score 1.0207, doc `cuad_fusemedicalinc_20190321_10_k_ex_10_43_11_2ac68dc12473`, chunk `cuad_fusemedicalinc_20190321_10_k_ex_10_43_11_2ac68dc12473::chunk_00035`, offsets [22750, 23650], preview: " for the Products in full within 30 days of their delivery. The Supplier shall be responsible for the costs of packaging"
  - rank 2, score 0.859, doc `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354`, chunk `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::chunk_00022`, offsets [14300, 15200], preview: "is Agreement in accordance with its terms; or (c) arising from acts of third parties in relation to Products sold to the"
  - rank 3, score 0.3865, doc `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3`, chunk `cuad_limeenergyco_09_09_1999_ex_10_distributo_8400573272b3::chunk_00008`, offsets [5200, 6100], preview: "    representing each state.                        1.3      Term.  The term of this  Agreement  shall be ten (10)      "

#### Base Regressed 3: `cuad_alamogordofinancialcorp_12_16_1999_ex_1__87abb558d8b7::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_alamogordofinancialcorp_12_16_1999_ex_1__87abb558d8b7`
- Question: In the agreement "AGENCY AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 132638, 'end': 132909}]
- Vector top chunks:
  - rank 1, score 0.6545, doc `cuad_athensbancsharescorp_11_02_2009_ex_1_2_a_589ba7323931`, chunk `cuad_athensbancsharescorp_11_02_2009_ex_1_2_a_589ba7323931::chunk_00206`, offsets [133900, 134800], preview: "party as a result  of the losses, claims, damages or liabilities (or actions, proceedings or claims in respect thereof) "
  - rank 2, score 0.6534, doc `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12`, chunk `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12::chunk_00026`, offsets [16900, 17800], preview: "ntial Information for any purpose outside the scope of this Agreement. Each party agrees to take all reasonable steps to"
  - rank 3, score 0.6499, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00049`, offsets [31850, 32750], preview: "ons they are otherwise obligated to perform.  8.6 No conditions, warranties or other terms apply to the Products, [ * ] "
- Base-reranked top chunks:
  - rank 1, score 4.6042, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00049`, offsets [31850, 32750], preview: "ons they are otherwise obligated to perform.  8.6 No conditions, warranties or other terms apply to the Products, [ * ] "
  - rank 2, score 4.1629, doc `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12`, chunk `cuad_sparklingspringwaterholdingsltd_07_03_20_04dd8fbf3d12::chunk_00026`, offsets [16900, 17800], preview: "ntial Information for any purpose outside the scope of this Agreement. Each party agrees to take all reasonable steps to"
  - rank 3, score 3.6523, doc `cuad_sonos_inc_manufacturing_agreement_0_2a390ea9b1d0`, chunk `cuad_sonos_inc_manufacturing_agreement_0_2a390ea9b1d0::chunk_00113`, offsets [73450, 74350], preview: "censes, insurance, approvals and inspections in performance under this Agreement.  14.0 LIMITATION OF LIABILITY.  EXCEPT"

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
  - rank 1, score 4.1479, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00046`, offsets [29900, 30800], preview: "ver Loop-branded Product to the Buyer. C. Pursuant to Section 2.4 of the Marketing Agreement, the Assignor desires to assign all rights and obligations under th"
  - rank 2, score 3.664, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00045`, offsets [29250, 30150], preview: "ssignor and Assignee is a "Party;" together they are the "Parties"). RECITALS A. On August __, 2018, the Parties entered into a Marketing Agreement (the "Market"
  - rank 3, score 1.7616, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00040`, offsets [26000, 26900], preview: " Assignment. This Agreement shall inure to the benefit of, and shall be binding upon, the Parties and their respective successors and assigns, but neither Party"

#### Base Failure 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 2.6874, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00067`, offsets [43550, 44450], preview: "his Agreement other than as permitted above will be null and void. This Agreement shall be binding upon and inure to the benefit of the parties and their respec"
  - rank 2, score 1.3388, doc `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743`, chunk `cuad_edietscominc_20001030_10qsb_ex_10_4_2606_c8a39a863743::chunk_00066`, offsets [42900, 43800], preview: "ent or transfer of this Agreement to (a) a party's successor in connection with a Change in Control of such party, provided that such successor is not a competi"
  - rank 3, score 1.0677, doc `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3`, chunk `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3::chunk_00071`, offsets [46150, 47050], preview: " provided that no such assignment shall relieve a party of any of its obligations under this Agreement. In the event there is a change of Control of an Affiliat"

#### Base Failure 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Top retrieved chunks:
  - rank 1, score 3.3111, doc `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0`, chunk `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0::chunk_00000`, offsets [0, 900], preview: "1                                                                    EXHIBIT 10.26  Confidential Treatment Requested                            CO-BRANDING AGRE"
  - rank 2, score 0.6415, doc `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa`, chunk `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa::chunk_00018`, offsets [11700, 12600], preview: "an entity which is a competitor to the other party. For the purposes of this Agreement, a "competitor" to MediaLinx shall be an Internet portal web site and/or "
  - rank 3, score 0.5923, doc `cuad_changepointcorp_03_08_2000_ex_10_6_licen_f13c18aff07c`, chunk `cuad_changepointcorp_03_08_2000_ex_10_6_licen_f13c18aff07c::chunk_00063`, offsets [40950, 41850], preview: "O DISPLAY. During the term of this Agreement, each party          authorizes the other party to display and use the other's trademarks,          trade names and"

#### Base Failure 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 4.0493, doc `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236`, chunk `cuad_zounds_hearing_inc_manufacturing_design__66b3fd6cd236::chunk_00035`, offsets [22750, 23650], preview: " by the other Party. The terms of such joint marketing agreement will be mutually agreed to by the Parties in a separate document. 10. Limitation of Liability. "
  - rank 2, score 3.3699, doc `cuad_impressecorp_20000322_s_1a_ex_10_11_5199_d57d8dbb7fc7`, chunk `cuad_impressecorp_20000322_s_1a_ex_10_11_5199_d57d8dbb7fc7::chunk_00050`, offsets [32500, 33400], preview: "N THIS AGREEMENT, IMPRESSE HEREBY DISCLAIMS ALL WARRANTIES, EXPRESS, IMPLIED OR STATUTORY, WITH RESPECT TO THE IMPRESSE AREA OF THE CO-BRANDED SITE AND THE IMPR"
  - rank 3, score 3.1925, doc `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc`, chunk `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc::chunk_00039`, offsets [25350, 26250], preview: "ing not supplied by NAI, or to the extent they arise           solely based upon the alteration or modification of the Products by           the Co-Host or the "

#### Base Failure 5: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 3.6716, doc `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa`, chunk `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa::chunk_00017`, offsets [11050, 11950], preview: ") and HCI shall be entitled to sell advertising and sponsorships on all pages of the Co-Branded Site to US advertisers (for the purposes of this Agreement, US a"
  - rank 2, score 2.7539, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00053`, offsets [34450, 35350], preview: "g the rights and obligations of the parties under Sections 4.3  [Non-Competition] and 5.8  [Non-Competition]) shall continue in full force and effect unless and"
  - rank 3, score 2.4569, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00052`, offsets [33800, 34700], preview: "ly agree, subject to Section 13.6  [Amendment or Modification], to amend Sections 7.1.1  [Co-Branded Career Center] and/or 7.1.2  [Co-Branded Equipment Listings"
