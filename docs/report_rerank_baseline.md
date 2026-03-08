# Rerank Baseline Report (Day 8)

## Experiment
- Generated: 2026-03-08 00:15 UTC
- Purpose: compare vector-only retrieval vs vector + base cross-encoder reranking
- Eval set: `eval/evalset_v1.jsonl`
- Eval items: 1903
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Vector encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker mode: `base`
- Base reranker: `cross-encoder/ms-marco-MiniLM-L6-v2`
- Rerank candidate pool: top 20 vector candidates
- Top-K: [3, 10]
- Query policy: deterministic contract-specific question format `In the agreement "<title cue>", find the <clause_type> clause.`
- Title cue policy: first meaningful contract header/title line from source text after skipping filing boilerplate lines
- Example question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.

## Overall Metrics

| K | Vector Hit@K | Base Hit@K | Delta | Vector Recall@K | Base Recall@K | Delta |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 0.0431 | 0.0641 | +0.0210 | 0.0313 | 0.0479 | +0.0165 |
| 10 | 0.0941 | 0.1109 | +0.0168 | 0.0701 | 0.0823 | +0.0122 |

## Per-Clause Metrics

| Clause | N | Hit@3 Vec | Hit@3 Base | dHit@3 | Rec@3 Vec | Rec@3 Base | dRec@3 | Hit@10 Vec | Hit@10 Base | dHit@10 | Rec@10 Vec | Rec@10 Base | dRec@10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assignment | 383 | 0.0209 | 0.0418 | +0.0209 | 0.0111 | 0.0259 | +0.0148 | 0.0444 | 0.0757 | +0.0313 | 0.0261 | 0.0439 | +0.0178 |
| change_of_control | 121 | 0.0248 | 0.0661 | +0.0413 | 0.0140 | 0.0554 | +0.0413 | 0.0744 | 0.1240 | +0.0496 | 0.0574 | 0.1022 | +0.0448 |
| confidentiality | 1 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 |
| exclusivity | 180 | 0.0389 | 0.0722 | +0.0333 | 0.0285 | 0.0460 | +0.0176 | 0.0722 | 0.0889 | +0.0167 | 0.0440 | 0.0568 | +0.0128 |
| governing_law | 437 | 0.0114 | 0.0320 | +0.0206 | 0.0114 | 0.0303 | +0.0189 | 0.0412 | 0.0549 | +0.0137 | 0.0412 | 0.0521 | +0.0109 |
| limitation_of_liability | 275 | 0.0655 | 0.0800 | +0.0145 | 0.0490 | 0.0605 | +0.0115 | 0.1455 | 0.1345 | -0.0109 | 0.1062 | 0.0964 | -0.0098 |
| most_favored_nation | 28 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 |
| non_compete | 119 | 0.0588 | 0.0588 | +0.0000 | 0.0493 | 0.0501 | +0.0008 | 0.1597 | 0.1933 | +0.0336 | 0.1249 | 0.1557 | +0.0308 |
| termination | 284 | 0.0951 | 0.1162 | +0.0211 | 0.0665 | 0.0815 | +0.0150 | 0.1655 | 0.1725 | +0.0070 | 0.1218 | 0.1301 | +0.0083 |
| warranty | 75 | 0.0933 | 0.1200 | +0.0267 | 0.0711 | 0.0960 | +0.0249 | 0.2133 | 0.2400 | +0.0267 | 0.1593 | 0.1674 | +0.0081 |

## Comparison Examples

### Cases Where Reranking Helped
#### Helped 1: `cuad_agapeatpcorp_20191202_10_ka_ex_10_1_1191_a920109383a0::assignment`
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

#### Helped 2: `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::governing_law`
- Clause: `governing_law`
- Doc: `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`
- Question: In the agreement "EXHIBIT C AIRSOPURE FRANCHISE AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 56975, 'end': 57149}]
- Vector top chunks:
  - rank 1, score 0.617, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00073`, offsets [73000, 73869], preview: "es incurred therein by such arty or parties (including without Initiation such as costs, expenses and fees on any appeal"
  - rank 2, score 0.6122, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00016`, offsets [16000, 17200], preview: "esolutions by Your Board of Directors authorizing execution of this Agreement, certified by the Secretary of the corpora"
  - rank 3, score 0.6068, doc `cuad_scansourceinc_20190822_10_k_ex_10_38_117_31966022f4b5`, chunk `cuad_scansourceinc_20190822_10_k_ex_10_38_117_31966022f4b5::chunk_00001`, offsets [1000, 2200], preview: "  1. Nonexclusive Value Added Distributor Agreement Terms and Conditions 2. EXHIBIT A: Territory 3. EXHIBIT B: Value Add"
- Base-reranked top chunks:
  - rank 1, score 3.0308, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00000`, offsets [0, 1200], preview: "[LOGO]                                      EXHIBIT C                                      AIRSOPURE                    "
  - rank 2, score 2.5898, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00016`, offsets [16000, 17200], preview: "esolutions by Your Board of Directors authorizing execution of this Agreement, certified by the Secretary of the corpora"
  - rank 3, score 2.4835, doc `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34`, chunk `cuad_airtechinternationalgroupinc_05_08_2000__2a643ab6ac34::chunk_00063`, offsets [63000, 64200], preview: "-----------------------  Title:       ------------------------------                                         18         "

#### Helped 3: `cuad_alliancebancorpincofpennsylvania_10_18_2_85c8f489bb2d::governing_law`
- Clause: `governing_law`
- Doc: `cuad_alliancebancorpincofpennsylvania_10_18_2_85c8f489bb2d`
- Question: In the agreement "AGENCY AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 128176, 'end': 128402}]
- Vector top chunks:
  - rank 1, score 0.5992, doc `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc`, chunk `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc::chunk_00005`, offsets [5000, 6200], preview: " by Client with its covenants hereunder, the execution and delivery of this Agreement, and the performance by Agent of i"
  - rank 2, score 0.5857, doc `cuad_antares_pharma_inc_manufacturing_agreeme_291e937415e6`, chunk `cuad_antares_pharma_inc_manufacturing_agreeme_291e937415e6::chunk_00092`, offsets [92000, 93200], preview: "hin [***] from receipt of such notice of dispute, a senior executive representative having full power and authority to s"
  - rank 3, score 0.5801, doc `cuad_buffalowildwingsinc_06_05_1998_ex_10_3_f_5d521b68c12d`, chunk `cuad_buffalowildwingsinc_06_05_1998_ex_10_3_f_5d521b68c12d::chunk_00002`, offsets [2000, 3200], preview: ". . . 26 XXI.   OPERATION IN THE EVENT OF ABSENCE, DISABILITY OR DEATH . . . . . . . 26 XXII.  INDEPENDENT CONTRACTOR AN"
- Base-reranked top chunks:
  - rank 1, score -0.4261, doc `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc`, chunk `cuad_blackstonegsolong_shortcreditincomefund__02bc1345b6cc::chunk_00005`, offsets [5000, 6200], preview: " by Client with its covenants hereunder, the execution and delivery of this Agreement, and the performance by Agent of i"
  - rank 2, score -1.0845, doc `cuad_americanphysicianscapitalinc_03_31_2003__2b007bce9814`, chunk `cuad_americanphysicianscapitalinc_03_31_2003__2b007bce9814::chunk_00014`, offsets [14000, 15200], preview: "ective date, all previous agreements, if any, between MICOA                   and the Agency. There are other agreements"
  - rank 3, score -1.5779, doc `cuad_emeraldhealthbioceuticalsinc_20200218_1__184329868240`, chunk `cuad_emeraldhealthbioceuticalsinc_20200218_1__184329868240::chunk_00012`, offsets [12000, 13200], preview: "ceability of Clauses: If any provision of this Agreement violates any law or is unenforceable for any other reason, it s"

### Cases Where Reranking Failed
#### Regressed 1: `cuad_airspannetworksinc_04_11_2000_ex_10_5_di_593bb74ff443::exclusivity`
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

#### Regressed 2: `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e::governing_law`
- Clause: `governing_law`
- Doc: `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e`
- Question: In the agreement "CO-BRANDING, MARKETING AND DISTRIBUTION AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 74858, 'end': 75019}]
- Vector top chunks:
  - rank 1, score 0.6053, doc `cuad_energouscorp_03_16_2017_ex_10_24_strateg_284bdebdfede`, chunk `cuad_energouscorp_03_16_2017_ex_10_24_strateg_284bdebdfede::chunk_00019`, offsets [19000, 20200], preview: "es, then, subject to the terms and conditions of this Agreement and during the Term, each party (in such capacity, "Lice"
  - rank 2, score 0.5857, doc `cuad_apollo_endosurgery_manufacturing_and_sup_f706626ebbbf`, chunk `cuad_apollo_endosurgery_manufacturing_and_sup_f706626ebbbf::chunk_00001`, offsets [1000, 2200], preview: "esearch and development, manufacture, distribution and marketing of certain medical devices.  B. ESTABLISHMENT is engage"
  - rank 3, score 0.581, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00000`, offsets [0, 1200], preview: "Exhibit 10.4                                CO-BRANDING AGREEMENT  This Co-Branding Agreement (this "Agreement") dated S"
- Base-reranked top chunks:
  - rank 1, score 3.2505, doc `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e`, chunk `cuad_audibleinc_20001113_10_q_ex_10_32_259958_08d9606c327e::chunk_00000`, offsets [0, 1200], preview: "EXHIBIT 10.32                 CO-BRANDING, MARKETING AND DISTRIBUTION AGREEMENT       This Agreement, dated as of Januar"
  - rank 2, score 1.7247, doc `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3`, chunk `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3::chunk_00012`, offsets [12000, 13200], preview: " marketing, promotion and sale of the Co-Branded Service. In connection with such license each party agrees not to use t"
  - rank 3, score 1.4933, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00000`, offsets [0, 1200], preview: "Exhibit 10.4                                CO-BRANDING AGREEMENT  This Co-Branding Agreement (this "Agreement") dated S"

#### Regressed 3: `cuad_blackboxstocksinc_08_05_2014_ex_10_1_dis_84d148a0f354::warranty`
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
#### Reranker Failure 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::assignment`
- Clause: `assignment`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 12261, 'end': 12361}, {'start': 12412, 'end': 12439}]
- Top retrieved chunks:
  - rank 1, score 2.0142, doc `cuad_garrettmotioninc_20181001_8_k_ex_2_4_113_23126d0016b5`, chunk `cuad_garrettmotioninc_20181001_8_k_ex_2_4_113_23126d0016b5::chunk_00011`, offsets [11000, 12200], preview: "y, the public.  "Trademark Assignment Agreement" has the meaning set forth in Section 2.01. 3  Source: GARRETT MOTION INC., 8-K, 10/1/2018      Table of Content"
  - rank 2, score 1.7337, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00029`, offsets [29000, 30200], preview: " with a principal place of business at 480 Fernand-Poitras, Terrebonne, Quebec, Canada (the "Assignor"), and Indorama Loop Technologies, LLC, a Delaware limited"
  - rank 3, score 1.6374, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00026`, offsets [26000, 27200], preview: " Assignment. This Agreement shall inure to the benefit of, and shall be binding upon, the Parties and their respective successors and assigns, but neither Party"

#### Reranker Failure 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 2.483, doc `cuad_phreesia_inc_05_28_2019_ex_10_18_strateg_e12e8d428b63`, chunk `cuad_phreesia_inc_05_28_2019_ex_10_18_strateg_e12e8d428b63::chunk_00003`, offsets [3000, 4200], preview: "m time to time, which are incorporated into this Agreement by reference. 1      "Change of Control" means any of the following: (a) any merger, reorganization, "
  - rank 2, score 2.2207, doc `cuad_phreesia_inc_05_28_2019_ex_10_18_strateg_e12e8d428b63`, chunk `cuad_phreesia_inc_05_28_2019_ex_10_18_strateg_e12e8d428b63::chunk_00105`, offsets [105000, 106200], preview: "this Agreement, [***]. 26. Change of Control.  26.1 Competing Providers. This Section 26 will only apply in the event of a Change of Control to a Competing Prov"
  - rank 3, score 1.3297, doc `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c`, chunk `cuad_whitesmoke_inc_11_08_2011_ex_10_26_promo_11becb35dc3c::chunk_00021`, offsets [21000, 22200], preview: "goes into administration,  receivership or administrative receivership, is declared bankrupt or insolvent or is dissolved or otherwise ceases to carry on  busin"

#### Reranker Failure 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Top retrieved chunks:
  - rank 1, score 3.0623, doc `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0`, chunk `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0::chunk_00000`, offsets [0, 1200], preview: "1                                                                    EXHIBIT 10.26  Confidential Treatment Requested                            CO-BRANDING AGRE"
  - rank 2, score 2.9798, doc `cuad_pcquotecominc_19990721_s_1a_ex_10_11_637_9b47d1bf2f2c`, chunk `cuad_pcquotecominc_19990721_s_1a_ex_10_11_637_9b47d1bf2f2c::chunk_00000`, offsets [0, 1200], preview: "[LOGO]  SECOND AMENDMENT TO CO-BRANDING AGREEMENT  THIS SECOND AMENDMENT TO CO-BRANDING AGREEMENT (this "Amendment") is made and entered into, effective for all"
  - rank 3, score 2.3546, doc `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6`, chunk `cuad_paperexchangecominc_20000322_s_1a_ex_10__fd061ce107b6::chunk_00000`, offsets [0, 1200], preview: "Exhibit 10.4                                CO-BRANDING AGREEMENT  This Co-Branding Agreement (this "Agreement") dated September 30, 1999 (the "Effective Date")"

#### Reranker Failure 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 1.9438, doc `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc`, chunk `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc::chunk_00025`, offsets [25000, 26200], preview: "ecrets or other proprietary rights           beyond that stated in this Section 9(b).    (c)  No Combination Claims. Notwithstanding Section 9(b), NAI will not "
  - rank 2, score 1.6259, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00013`, offsets [13000, 14200], preview: "being restricted by the Marketing and Sale Restriction. If at any subsequent time during the term of this Agreement Loop gives Joint Venture Party written notic"
  - rank 3, score 1.571, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00033`, offsets [33000, 34200], preview: "t practicable after         Commerce One has exhausted all diligent efforts, (iii) terminate this           Agreement and refund to Corio a pro-rated portion of"

#### Reranker Failure 5: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 3.2001, doc `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0`, chunk `cuad_neoformainc_19991202_s_1a_ex_10_26_52245_7a155e8713a0::chunk_00000`, offsets [0, 1200], preview: "1                                                                    EXHIBIT 10.26  Confidential Treatment Requested                            CO-BRANDING AGRE"
  - rank 2, score 2.9589, doc `cuad_vivint_solar_inc_non_competition_agreeme_f6704d689c07`, chunk `cuad_vivint_solar_inc_non_competition_agreeme_f6704d689c07::chunk_00001`, offsets [1000, 2200], preview: "ition Agreement.  WHEREAS, the Parties also desire to extend the term of the non-solicitation obligations under the Non-Competition Agreement.  AGREEMENT  NOW, "
  - rank 3, score 2.6816, doc `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa`, chunk `cuad_healthcentralcom_19991108_s_1a_ex_10_27__33c9fc258faa::chunk_00011`, offsets [11000, 12200], preview: "sers with substantial places of business in Canada) and HCI shall be entitled to sell advertising and sponsorships on all pages of the Co-Branded Site to US adv"
