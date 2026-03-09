# Reranker Evaluation Report

## Experiment
- Generated: 2026-03-08 02:51 UTC
- Purpose: compare vector-only retrieval against base and LoRA reranker modes
- Eval set: `eval/evalset_v1.jsonl`
- Eval items: 1903
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Vector encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker mode: `none`
- Top-K: [1, 3, 5, 10]
- Query policy: deterministic contract-specific question format `In the agreement "<title cue>", find the <clause_type> clause.`
- Title cue policy: first meaningful contract header/title line from source text after skipping filing boilerplate lines
- Example question: In the agreement "CO-BRANDING AND ADVERTISING AGREEMENT", find the assignment clause.

## Retrieval Representation Change

- Retrieval chunking parameters changed from `1200/200` to `900/250` (size/overlap).
- Embedding text is now enriched (index-time only) with deterministic metadata:
  - `Document Title: <title cue from source contract>`
  - `Section Heading: <simple heading cue in chunk, when available>`
  - `Chunk Text: <raw offset-preserving chunk text>`
- Raw chunk text and offsets are unchanged in retrieval metadata and outputs.
- Rebuild commands:
  - `PYTHONPATH=. .venv/bin/python scripts/chunk_contracts.py`
  - `TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. .venv/bin/python scripts/build_index.py --batch-size 16`
- Eval command:
  - `PYTHONPATH=. .venv/bin/python eval/run_retrieval_eval.py --reranker none --report docs/report_retrieval_baseline.md`

## Vector Candidate Coverage (Oracle Overlap)

| K | Candidate Hit@K | Oracle Recall@K |
| --- | --- | --- |
| 20 | 0.2738 | 0.2197 |
| 50 | 0.3731 | 0.3137 |
| 100 | 0.4561 | 0.3902 |

## Coverage Delta vs Prior Baseline

| K | Prior Candidate Hit@K | New Candidate Hit@K | Delta | Prior Oracle Recall@K | New Oracle Recall@K | Delta |
| --- | --- | --- | --- | --- | --- | --- |
| 20 | 0.1345 | 0.2738 | +0.1393 | 0.1008 | 0.2197 | +0.1189 |
| 50 | 0.2107 | 0.3731 | +0.1624 | 0.1610 | 0.3137 | +0.1527 |
| 100 | 0.2733 | 0.4561 | +0.1828 | 0.2159 | 0.3902 | +0.1743 |

## Overall Metrics

| Metric | @1 | @3 | @5 | @10 |
| --- | --- | --- | --- | --- |
| Hit@K | 0.0547 | 0.1125 | 0.1508 | 0.2060 |
| Recall@K | 0.0381 | 0.0831 | 0.1122 | 0.1606 |

## Per-Clause Metrics

| Clause | N | Hit@1 | Recall@1 | Hit@3 | Recall@3 | Hit@5 | Recall@5 | Hit@10 | Recall@10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assignment | 383 | 0.0574 | 0.0389 | 0.1123 | 0.0803 | 0.1514 | 0.1066 | 0.2141 | 0.1589 |
| change_of_control | 121 | 0.0413 | 0.0249 | 0.0909 | 0.0700 | 0.1322 | 0.1053 | 0.1818 | 0.1411 |
| confidentiality | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| exclusivity | 180 | 0.0167 | 0.0111 | 0.0389 | 0.0193 | 0.0500 | 0.0285 | 0.0722 | 0.0511 |
| governing_law | 437 | 0.0229 | 0.0217 | 0.0503 | 0.0475 | 0.0686 | 0.0669 | 0.1030 | 0.1001 |
| limitation_of_liability | 275 | 0.1345 | 0.0854 | 0.2473 | 0.1728 | 0.3164 | 0.2221 | 0.4000 | 0.3107 |
| most_favored_nation | 28 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0357 | 0.0357 |
| non_compete | 119 | 0.0252 | 0.0093 | 0.1092 | 0.0815 | 0.1597 | 0.1170 | 0.2101 | 0.1521 |
| termination | 284 | 0.0634 | 0.0475 | 0.1338 | 0.1078 | 0.1831 | 0.1421 | 0.2641 | 0.2025 |
| warranty | 75 | 0.0800 | 0.0667 | 0.1600 | 0.0928 | 0.2133 | 0.1372 | 0.2533 | 0.1689 |

## Comparison Examples

Reranker disabled; no vector-vs-reranker comparison examples.
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
