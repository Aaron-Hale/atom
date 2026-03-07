# Retrieval Baseline Report (Day 7, Vector-Only)

## Experiment
- Generated: 2026-03-07 23:39 UTC
- Purpose: baseline vector retrieval quality on deterministic eval set
- Eval set: `eval/evalset_v1.jsonl`
- Eval items: 1903
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Top-K: [1, 3, 5, 10]
- Query policy: deterministic contract-specific question format `In the agreement "<title cue>", find the <clause_type> clause.`
- Title cue policy: first meaningful contract header/title line from source text after skipping filing boilerplate lines
- Example question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.

## Overall Metrics

| Metric | @1 | @3 | @5 | @10 |
| --- | --- | --- | --- | --- |
| Hit@K | 0.0179 | 0.0431 | 0.0604 | 0.0941 |
| Recall@K | 0.0129 | 0.0313 | 0.0438 | 0.0701 |

## Per-Clause Metrics

| Clause | N | Hit@1 | Recall@1 | Hit@3 | Recall@3 | Hit@5 | Recall@5 | Hit@10 | Recall@10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assignment | 383 | 0.0078 | 0.0065 | 0.0209 | 0.0111 | 0.0261 | 0.0153 | 0.0444 | 0.0261 |
| change_of_control | 121 | 0.0000 | 0.0000 | 0.0248 | 0.0140 | 0.0413 | 0.0244 | 0.0744 | 0.0574 |
| confidentiality | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| exclusivity | 180 | 0.0222 | 0.0130 | 0.0389 | 0.0285 | 0.0444 | 0.0301 | 0.0722 | 0.0440 |
| governing_law | 437 | 0.0046 | 0.0046 | 0.0114 | 0.0114 | 0.0183 | 0.0183 | 0.0412 | 0.0412 |
| limitation_of_liability | 275 | 0.0291 | 0.0195 | 0.0655 | 0.0490 | 0.0945 | 0.0703 | 0.1455 | 0.1062 |
| most_favored_nation | 28 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| non_compete | 119 | 0.0252 | 0.0252 | 0.0588 | 0.0493 | 0.0924 | 0.0807 | 0.1597 | 0.1249 |
| termination | 284 | 0.0387 | 0.0265 | 0.0951 | 0.0665 | 0.1232 | 0.0846 | 0.1655 | 0.1218 |
| warranty | 75 | 0.0400 | 0.0244 | 0.0933 | 0.0711 | 0.1600 | 0.1087 | 0.2133 | 0.1593 |

## Failure Examples

### Example 1: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::assignment`
- Clause: `assignment`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.
- Expected spans: [{'start': 12261, 'end': 12361}, {'start': 12412, 'end': 12439}]
- Top retrieved chunks:
  - rank 1, score 0.5722, doc `cuad_loop_industries_inc_marketing_agreement__62371804542a`, chunk `cuad_loop_industries_inc_marketing_agreement__62371804542a::chunk_00029`, offsets [29000, 30200], preview: " with a principal place of business at 480 Fernand-Poitras, Terrebonne, Quebec, Canada (the "Assignor"), and Indorama Loop Technologies, LLC, a Delaware limited"
  - rank 2, score 0.529, doc `cuad_aspirityholdingsllc_05_07_2012_ex_10_6_o_ca7322524cd1`, chunk `cuad_aspirityholdingsllc_05_07_2012_ex_10_6_o_ca7322524cd1::chunk_00020`, offsets [20000, 21200], preview: "ll be subject to the prior  approval of the Company. The Contractor shall also oversee designing and printing all marketing materials (subject to the prior  app"
  - rank 3, score 0.5151, doc `cuad_lejuholdingsltd_03_12_2014_ex_10_34_inte_1156b972e5ba`, chunk `cuad_lejuholdingsltd_03_12_2014_ex_10_34_inte_1156b972e5ba::chunk_00021`, offsets [21000, 22200], preview: "s of which are as follows:   (i) Party B will provide real estate, home furnishing and life related data required by Party A, and Party A will use its technolog"

### Example 2: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::change_of_control`
- Clause: `change_of_control`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the change of control clause.
- Expected spans: [{'start': 16231, 'end': 16771}]
- Top retrieved chunks:
  - rank 1, score 0.5721, doc `cuad_kitovpharmaltd_20190326_20_f_ex_4_15_115_14a8af380b5b`, chunk `cuad_kitovpharmaltd_20190326_20_f_ex_4_15_115_14a8af380b5b::chunk_00003`, offsets [3000, 4200], preview: " are specified in European Commission Directive 2003/94/EC and the FDA's current Good Manufacturing Practices, particularly 21 CFR § 210 et seq., and 21 CFR §§ "
  - rank 2, score 0.5528, doc `cuad_changepointcorp_03_08_2000_ex_10_6_licen_f13c18aff07c`, chunk `cuad_changepointcorp_03_08_2000_ex_10_6_licen_f13c18aff07c::chunk_00040`, offsets [40000, 41200], preview: "or its Customers, subject to the mutual written          agreement on the scope of such services, pricing and other terms and          conditions.  5.7      SAL"
  - rank 3, score 0.5505, doc `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926`, chunk `cuad_atninternationalinc_20191108_10_q_ex_10__12b0ad9cb926::chunk_00011`, offsets [11000, 12200], preview: "ion or series of related contracts or transactions (regardless of form or structure) that would directly result in the Control of a Person or its business or as"

### Example 3: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::governing_law`
- Clause: `governing_law`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the governing law clause.
- Expected spans: [{'start': 21948, 'end': 22102}]
- Top retrieved chunks:
  - rank 1, score 0.6061, doc `cuad_energouscorp_03_16_2017_ex_10_24_strateg_284bdebdfede`, chunk `cuad_energouscorp_03_16_2017_ex_10_24_strateg_284bdebdfede::chunk_00019`, offsets [19000, 20200], preview: "es, then, subject to the terms and conditions of this Agreement and during the Term, each party (in such capacity, "Licensor") hereby grants to the other party "
  - rank 2, score 0.5913, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00025`, offsets [25000, 26200], preview: ".7     Sales and Marketing Efforts. The parties shall engage in joint marketing         and sales activities as set forth in EXHIBIT D attached hereto and made "
  - rank 3, score 0.5778, doc `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3`, chunk `cuad_randworldwideinc_20010402_8_ka_ex_10_2_2_7b2c5ddbf1b3::chunk_00012`, offsets [12000, 13200], preview: " marketing, promotion and sale of the Co-Branded Service. In connection with such license each party agrees not to use the other party's Marks in any manner tha"

### Example 4: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::limitation_of_liability`
- Clause: `limitation_of_liability`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the limitation of liability clause.
- Expected spans: [{'start': 20190, 'end': 20490}]
- Top retrieved chunks:
  - rank 1, score 0.6748, doc `cuad_vericelcorp_08_06_2019_ex_10_10_supply_a_785f5856b5f8`, chunk `cuad_vericelcorp_08_06_2019_ex_10_10_supply_a_785f5856b5f8::chunk_00075`, offsets [75000, 76200], preview: "sent of the other party, and the Indemnified Party shall use reasonable efforts to mitigate liabilities arising from such Third Party Claim.  7.5 Disclaimer. EX"
  - rank 2, score 0.6685, doc `cuad_scansourceinc_20190822_10_k_ex_10_38_117_31966022f4b5`, chunk `cuad_scansourceinc_20190822_10_k_ex_10_38_117_31966022f4b5::chunk_00048`, offsets [48000, 49200], preview: "EXHIBIT C (SOFTWARE LICENSE AGREEMENT), OR AMOUNTS DUE FOR PRODUCTS AND SERVICES PURCHASED WITH RESPECT TO THE PAYMENT OF WHICH NO BONA FIDE DISPUTE EXISTS, ALL"
  - rank 3, score 0.6588, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00033`, offsets [33000, 34200], preview: "t practicable after         Commerce One has exhausted all diligent efforts, (iii) terminate this           Agreement and refund to Corio a pro-rated portion of"

### Example 5: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77::non_compete`
- Clause: `non_compete`
- Doc: `cuad_2themartcominc_19990826_10_12g_ex_10_10__3712ddb0de77`
- Question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the non compete clause.
- Expected spans: [{'start': 5782, 'end': 5884}]
- Top retrieved chunks:
  - rank 1, score 0.5808, doc `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc`, chunk `cuad_beyondcomcorp_08_03_2000_ex_10_2_co_host_c20dc3c673bc::chunk_00005`, offsets [5000, 6200], preview: "rties may mutually agree upon in writing from time to time) a hot           link to Internet locations specified by the Co-Host (the           "Destination") fr"
  - rank 2, score 0.564, doc `cuad_vivint_solar_inc_non_competition_agreeme_f6704d689c07`, chunk `cuad_vivint_solar_inc_non_competition_agreeme_f6704d689c07::chunk_00001`, offsets [1000, 2200], preview: "ition Agreement.  WHEREAS, the Parties also desire to extend the term of the non-solicitation obligations under the Non-Competition Agreement.  AGREEMENT  NOW, "
  - rank 3, score 0.5594, doc `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed`, chunk `cuad_corioinc_07_20_2000_ex_10_5_license_and__9452e80180ed::chunk_00025`, offsets [25000, 26200], preview: ".7     Sales and Marketing Efforts. The parties shall engage in joint marketing         and sales activities as set forth in EXHIBIT D attached hereto and made "
