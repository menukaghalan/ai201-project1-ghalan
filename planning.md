# Project 1 Planning: The Unofficial Guide

## Domain

This project is an unofficial WMU student-life guide built from public student discussion notes. The guide focuses on Western Michigan University student concerns that are difficult to answer from official pages alone: computer science program concerns, transfer questions, meal plans, dining, housing, parking, career preparation, and practical student advice.

This knowledge is valuable because official university pages usually explain policies, programs, and services, but they do not capture how students describe day-to-day tradeoffs. Reddit-style student discussions can reveal concerns about parking frustration, whether meal plans feel worth the cost, how students think about CS outcomes, and what informal steps students take when official information is hard to locate.

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | 01_wmu_cs_program_transfer_questions.txt | Transfer student asks about WMU CS quality and professors. | https://www.reddit.com/r/WMU/comments/p01c8s/how_good_is_the_cs_program_at_wmu/ |
| 2 | 02_wmu_cs_program_quality_transfer_thread.txt | Student discussion of CS quality, staffing concerns, facilities, transfer convenience, and outcomes. | https://www.reddit.com/r/WMU/comments/1c8yd4d/is_the_computer_science_program_here_quality/ |
| 3 | 03_wmu_ms_cs_program_questions.txt | Prospective international MS CS student asks about academics, culture, careers, alumni network, and ROI. | https://www.reddit.com/r/WMU/comments/159boox/hows_the_ms_cs_program_at_wmu/ |
| 4 | 04_wmu_cs_syllabus_retrieval_advice.txt | Students advise how to find old WMU CS syllabi for transfer review. | https://www.reddit.com/r/WMU/comments/1gojxp6/im_trying_to_track_down_copies_of_some_computer/ |
| 5 | 05_wmu_cs_career_outcomes_concerns.txt | Prospective CS transfer asks about WMU reputation and job outcomes. | https://www.reddit.com/r/WMU/comments/1anzosf/careers_after_college/ |
| 6 | 06_wmu_engineering_cs_success_stories.txt | Alumni/student comment discusses CS career success and project clubs. | https://www.reddit.com/r/WMU/comments/t974pr/engineering_program/ |
| 7 | 07_wmu_dining_food_situation.txt | Students discuss dining hall quality, Valley, Bistro hours, and carryout options. | https://www.reddit.com/r/WMU/comments/ej7olm/how_is_the_food_situation/ |
| 8 | 08_wmu_meal_plan_value.txt | Students compare lower, 14-meal, and unlimited meal plans. | https://www.reddit.com/r/WMU/comments/nxpnbd/is_it_worth_getting_the_meal_plan/ |
| 9 | 09_wmu_dorms_without_required_meal_plan.txt | Comments identify dorms without required meal plans and debate no-meal-plan living. | https://www.reddit.com/r/WMU/comments/1l84l2v/which_dorms_dont_require_you_to_get_a_meal_plan/ |
| 10 | 10_wmu_exchange_student_food_housing_career_fair.txt | Exchange-student discussion of dining, residence halls, meal plans, and engineering career fairs. | https://www.reddit.com/r/WMU/comments/1r4yfzv/exchange_to_wmu/ |
| 11 | 11_wmu_parking_situation_and_costs.txt | Student complaint about parking cost, full lots, and Parkview travel. | https://www.reddit.com/r/WMU/comments/1nbrs6a/parking_situation/ |
| 12 | 12_wmu_parking_enforcement_rules_discussion.txt | Discussion of permit enforcement windows and always-enforced violations. | https://www.reddit.com/r/WMU/comments/18ldb7o/what_day_does_wmu_stop_parking_enforcement/ |
| 13 | 13_wmu_off_campus_apartment_warning_ccatk.txt | Negative off-campus apartment warning about mold, flooding, utilities, and pests. | https://www.reddit.com/r/WMU/comments/utiaeu/ccatk/ |
| 14 | 14_wmu_parking_ticket_registration_discussion.txt | Conflicting anecdotal discussion about unregistered cars and parking tickets. | https://www.reddit.com/r/WMU/comments/kqkjwc/if_your_car_isnt_registered_at_wmu_how_would_they/ |

## Chunking Strategy

**Chunk size:** The implemented chunker is paragraph-aware. It keeps chunks up to `MAX_CHARS = 900`, with a soft `MIN_CHARS = 250` before starting a new chunk.

**Overlap:** `OVERLAP_CHARS = 100`. When a chunk boundary is needed, the next chunk carries about 100 characters of prior context.

**Reasoning:** The WMU documents are short-to-medium public student discussion notes where paragraph-level meaning matters. A fixed tiny split could separate the student's complaint from the key takeaway, while very large chunks would mix unrelated topics such as dining, housing, and career fairs. The 900-character maximum usually preserves one topic block, and the 100-character overlap reduces the risk of losing context at paragraph boundaries.

## Retrieval Approach

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`.

**Vector store:** ChromaDB persistent store in `chroma_db/`.

**Top-k:** `TOP_K = 5` in `src/query.py`.

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is inexpensive to run locally and fast enough for a small class corpus. In production, I would compare it against larger embedding models for better domain-specific accuracy, especially for ambiguous student language. I would also weigh API-hosted models against local embeddings: API models may improve accuracy and multilingual support, but add cost, network latency, privacy concerns, and dependency on an external service. Context length also matters because long Reddit threads may need either better chunking or reranking before sending context to the LLM.

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about parking at WMU? | Students complain about cost, full lots, reserved spaces, Parkview travel time, and parking enforcement/ticket uncertainty. |
| 2 | What do students say about WMU meal plans? | Students give mixed advice: lower plans may be enough, unlimited is convenient for frequent dining/snacks, 14-meal plans may run out, and no-meal-plan living depends on housing and habits. |
| 3 | What do students say about the WMU computer science program? | The sentiment is mixed but generally practical: prospective students worry about quality, staffing, transfer fit, and outcomes; some commenters still recommend WMU because of facilities, cost, convenience, and success stories. |
| 4 | What advice is given for finding old WMU CS syllabi? | Contact the professor and department administrative office; ask for the exact semester/year syllabus because transfer review may require that version. |
| 5 | What do students say about off-campus housing or apartment concerns? | At least one off-campus apartment warning mentions run-down conditions, mold, flooding risk, garbage, pests, utilities, and safety/neighborhood concerns; students should verify current conditions. |

## Anticipated Challenges

1. Broad Reddit threads often mix multiple subtopics. A single exchange-student thread can mention dining, housing, meal plans, and career fairs, so retrieval may return a generally relevant chunk that does not fully answer a narrow question.

2. Student discussion language is subjective and anecdotal. The system must avoid presenting one user's complaint as official WMU policy or as a complete picture of campus life.

3. Chunk boundaries can split useful context. This is especially risky when a paragraph begins with the end of a prior idea, so the chunker uses a small overlap to preserve local continuity.

4. Out-of-scope questions may retrieve weakly related chunks. For example, a question about a non-CS professor could retrieve CS program chunks because both mention professors, so the generation prompt must enforce refusal when the context is insufficient.

## Architecture

```text
documents/*.txt
  -> src/ingest.py
  -> data/processed/documents.json
  -> src/chunk.py
  -> data/chunks/chunks.json
  -> sentence-transformers/all-MiniLM-L6-v2 embeddings
  -> ChromaDB persistent vector store
  -> retrieval top-k = 5
  -> Groq LLM grounded generation
  -> answer with source attribution
```

## AI Tool Plan

**Milestone 3 - Ingestion and chunking:** I used ChatGPT/Codex-style assistance to structure the ingestion and chunking scripts. The input was the project requirement, the desired WMU document folder, and the paragraph-aware chunking idea. I reviewed the generated code by checking that it reads `documents/*.txt`, writes `data/processed/documents.json`, and creates chunks with source file metadata.

**Milestone 4 - Embedding and retrieval:** I used AI assistance to set up ChromaDB retrieval with `all-MiniLM-L6-v2`. The input was the chunk schema and requirement to retrieve top-k chunks with source attribution. I verified the output by rebuilding ChromaDB and checking retrieved chunks for WMU parking, meal plan, dining, housing, CS, and syllabus questions.

**Milestone 5 - Generation and interface:** I used AI assistance to draft and refine the grounded generation prompt and Gradio interface. I reviewed the prompt to make sure it says to use only retrieved context, refuse when context is insufficient, and cite source file names. I also checked the interface text so it describes the WMU guide rather than the old synthetic professor dataset.
