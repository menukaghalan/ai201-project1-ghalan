# The Unofficial Guide - Project 1

## Project Description

This project follows the course description of The Unofficial Guide: colleges have official knowledge, such as catalogs and university websites, and student-generated knowledge, such as subreddit threads, advice posts, and warnings that students share with each other. This system makes the second kind searchable. A user asks a plain-language question and receives a grounded, cited answer drawn from the WMU documents collected for this project.

## Domain

This RAG system is an unofficial WMU student-life guide based on public student discussion notes. It answers questions about Western Michigan University student experiences, including computer science program concerns, transfer advice, meal plans, dining, housing, parking, career preparation, and student-to-student advice. The domain is useful because official WMU pages describe policies and programs, but they do not always capture informal student tradeoffs such as parking frustration, whether meal plans feel worth it, or how students find old syllabi.

## Document Sources

| # | Source file | Type | URL/location |
|---|-------------|------|--------------|
| 1 | 01_wmu_cs_program_transfer_questions.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/p01c8s/how_good_is_the_cs_program_at_wmu/ |
| 2 | 02_wmu_cs_program_quality_transfer_thread.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/1c8yd4d/is_the_computer_science_program_here_quality/ |
| 3 | 03_wmu_ms_cs_program_questions.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/159boox/hows_the_ms_cs_program_at_wmu/ |
| 4 | 04_wmu_cs_syllabus_retrieval_advice.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/1gojxp6/im_trying_to_track_down_copies_of_some_computer/ |
| 5 | 05_wmu_cs_career_outcomes_concerns.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/1anzosf/careers_after_college/ |
| 6 | 06_wmu_engineering_cs_success_stories.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/t974pr/engineering_program/ |
| 7 | 07_wmu_dining_food_situation.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/ej7olm/how_is_the_food_situation/ |
| 8 | 08_wmu_meal_plan_value.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/nxpnbd/is_it_worth_getting_the_meal_plan/ |
| 9 | 09_wmu_dorms_without_required_meal_plan.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/1l84l2v/which_dorms_dont_require_you_to_get_a_meal_plan/ |
| 10 | 10_wmu_exchange_student_food_housing_career_fair.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/1r4yfzv/exchange_to_wmu/ |
| 11 | 11_wmu_parking_situation_and_costs.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/1nbrs6a/parking_situation/ |
| 12 | 12_wmu_parking_enforcement_rules_discussion.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/18ldb7o/what_day_does_wmu_stop_parking_enforcement/ |
| 13 | 13_wmu_off_campus_apartment_warning_ccatk.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/utiaeu/ccatk/ |
| 14 | 14_wmu_parking_ticket_registration_discussion.txt | Reddit thread | https://www.reddit.com/r/WMU/comments/kqkjwc/if_your_car_isnt_registered_at_wmu_how_would_they/ |

## Pipeline

```text
documents/*.txt -> src/ingest.py -> data/processed/documents.json
  -> src/chunk.py -> data/chunks/chunks.json
  -> all-MiniLM-L6-v2 embeddings -> ChromaDB
  -> retrieval top-k = 5 -> Groq LLM -> answer with source attribution
```

Commands used to rebuild:

```powershell
python src/ingest.py
python src/chunk.py
.\.venv\Scripts\python.exe src/build_index.py
.\.venv\Scripts\python.exe src/query.py
```

## Chunking Strategy

The ingest script reads from `documents/`, strips obvious HTML tags, normalizes whitespace, and preserves paragraph breaks. The chunker is paragraph-aware: it tries to keep related paragraphs together up to `MAX_CHARS = 900`, uses `MIN_CHARS = 250` as a soft minimum before finalizing a chunk, and carries `OVERLAP_CHARS = 100` characters into the next chunk when a split happens.

These numbers fit the corpus because the WMU files are short-to-medium public student discussion notes. Paragraph-level meaning matters: one paragraph may describe a student concern, while the next gives the takeaway or caution. The final rebuilt corpus contains 29 chunks in `data/chunks/chunks.json`.

## Embedding Model

The system uses `sentence-transformers/all-MiniLM-L6-v2`. I chose it because it is fast, small enough to run locally, and strong enough for semantic search over a small class corpus. For a production version, I would compare larger embedding models or API-hosted embeddings for better domain-specific accuracy and multilingual support. The tradeoffs would include cost, latency, context length, privacy, local reliability, and whether a larger model retrieves more precise chunks for ambiguous student language.

## Grounded Generation

`src/query.py` retrieves top-k chunks from ChromaDB and formats each chunk with source file, chunk index, and text. The generation prompt tells the Groq Llama model:

```text
Use ONLY the context below. Do not use outside knowledge.
If the context does not contain enough information to answer the question, say exactly:
"I don't have enough information in the provided documents to answer that."
When you answer, cite the source file names you used.
```

Source attribution appears in two ways: the answer itself cites source file names, and the CLI/Gradio output also lists retrieved source files, chunk numbers, and distance scores.

## Sample Chunks

**Sample 1 - 01_wmu_cs_program_transfer_questions.txt, chunk 0:** Source Title: r/WMU - How good is the CS program at WMU? Source Type: Public Reddit student/prospective-student discussion. Content: A prospective transfer student asked whether the WMU Computer Science program is good and specifically wanted to know what the CS program and professors are like. This shows that prospective students often want informal answers about program quality, faculty experience, and whether the major is worth transferring into.

**Sample 2 - 02_wmu_cs_program_quality_transfer_thread.txt, chunk 1:** The same commenter noted that WMU has had broader staffing challenges, but still recommended the program overall because of the engineering and applied sciences facilities, local transfer convenience, and relatively reasonable price. Key takeaway: the unofficial sentiment is mixed but generally reassuring.

**Sample 3 - 07_wmu_dining_food_situation.txt, chunk 0:** Students described WMU dining as generally acceptable to good, with enough variety that students do not have to eat the same food repeatedly. One student preferred Valley Dining Center because of its options and quality. Another student liked Bistro because it was close to many dorms and had good options, but criticized its hours because it closed at 8 p.m. on weekdays and was closed on weekends.

**Sample 4 - 08_wmu_meal_plan_value.txt, chunk 1:** A student who switched from unlimited to a 14-meal plan said they often ran out of meals by the end of the week. The comments suggest that unlimited can be convenient, but students should compare the price difference and their eating habits.

**Sample 5 - 13_wmu_off_campus_apartment_warning_ccatk.txt, chunk 1:** Key takeaway: off-campus housing comments can contain serious quality-of-life warnings. Students should verify current conditions, tour units carefully, ask current residents, check lease terms, and not rely on a single comment alone.

## Retrieval Test Examples

**Query:** What do students say about parking at WMU?

Top returned chunks:

| Rank | Source | Chunk | Distance | Returned chunk content |
|---|--------|-------|----------|------------------------|
| 1 | 11_wmu_parking_situation_and_costs.txt | 0 | 0.557 | Parking complaint mentioning about $150 per semester, full lots, parking far away, and Parkview travel. |
| 2 | 11_wmu_parking_situation_and_costs.txt | 1 | 0.656 | Key questions about permit cost, full lots, employee-reserved spaces, and travel time. |
| 3 | 12_wmu_parking_enforcement_rules_discussion.txt | 2 | 0.6775 | Parking enforcement may change during break windows, but some violations can still be enforced. |
| 4 | 12_wmu_parking_enforcement_rules_discussion.txt | 0 | 0.7017 | Thread about when WMU parking enforcement stops. |
| 5 | 14_wmu_parking_ticket_registration_discussion.txt | 1 | 0.7033 | Discussion of tickets for unregistered cars and disputed enforcement details. |

These chunks are relevant because they directly discuss parking cost, full lots, Parkview travel, permit enforcement, and ticket issues.

**Query:** What do students say about WMU meal plans?

Top returned chunks:

| Rank | Source | Chunk | Distance | Returned chunk content |
|---|--------|-------|----------|------------------------|
| 1 | 08_wmu_meal_plan_value.txt | 0 | 0.5048 | Freshman meal-plan discussion and advice about whether a plan is worth it in dorms. |
| 2 | 07_wmu_dining_food_situation.txt | 0 | 0.5794 | Dining hall quality, Valley Dining Center, Bistro hours, and carryout options. |
| 3 | 09_wmu_dorms_without_required_meal_plan.txt | 1 | 0.5946 | Britton/Hadley no-meal-plan discussion and disagreement about whether skipping a plan is wise. |
| 4 | 09_wmu_dorms_without_required_meal_plan.txt | 0 | 0.7061 | Housing and dining thread asking which dorms do not require meal plans. |
| 5 | 08_wmu_meal_plan_value.txt | 1 | 0.7388 | Unlimited plan convenience and risk of running out on a 14-meal plan. |

These chunks are relevant because they cover meal plan value, dining hall use, unlimited versus 14-meal plans, and dorms where meal plans may not be required.

**Query:** What advice is given for finding old WMU CS syllabi?

Top returned chunks:

| Rank | Source | Chunk | Distance | Returned chunk content |
|---|--------|-------|----------|------------------------|
| 1 | 04_wmu_cs_syllabus_retrieval_advice.txt | 0 | 0.928 | Student advice thread about tracking down Computer Science course syllabi. |
| 2 | 04_wmu_cs_syllabus_retrieval_advice.txt | 1 | 1.0946 | Exact semester/year advice and contacting the department administrative office. |
| 3 | 01_wmu_cs_program_transfer_questions.txt | 0 | 1.1317 | Broad WMU CS transfer/program question chunk. |
| 4 | 03_wmu_ms_cs_program_questions.txt | 0 | 1.1611 | MS CS prospective-student question chunk. |
| 5 | 03_wmu_ms_cs_program_questions.txt | 1 | 1.2027 | MS CS career/outcomes question context. |

The first two chunks are the important results because they directly mention contacting the professor, department administrative office, and matching the semester/year for transfer review.

## Example System Responses

**Question:** What do students say about parking at WMU?

**Answer:** Students complain about the parking situation at WMU, specifically mentioning that they pay about $150 per semester for parking, but many lots are full, and they may have to park far from where they need to go. They also mention that reserved employee spaces appear empty, making it hard to travel from main campus to Parkview campus within a reasonable time. (11_wmu_parking_situation_and_costs.txt)

**Question:** What advice is given for finding old WMU CS syllabi?

**Answer:** For finding old WMU CS syllabi, the advice given is to try contacting the professor, but if that does not work, students should also contact the department administrative office because departments often need to keep copies for accreditation purposes. Additionally, it is recommended to ask for the exact semester/year syllabus if transfer credit is involved, as institutions often require the syllabus from the same academic year or semester in which the course was taken. (Source: 04_wmu_cs_syllabus_retrieval_advice.txt)

## Out-of-Scope Refusal

**Question:** Which professor is best for organic chemistry at WMU?

**Answer:** I don't have enough information in the provided documents to answer that.

This is the desired behavior. The retriever returned weakly related CS/professor chunks, but the generator refused because the provided documents do not contain organic chemistry professor advice.

## Evaluation Report

| # | Question | Expected correct answer | Actual system response | Retrieved chunks/source files | Accuracy |
|---|----------|-------------------------|------------------------|-------------------------------|----------|
| 1 | What do students say about parking at WMU? | Parking is described as expensive and frustrating, with full lots, Parkview travel issues, enforcement, and ticket concerns. | Answered that students pay about $150 per semester, lots are full, students may park far away, and Parkview travel is difficult. | 11 chunks 0-1, 12 chunks 0 and 2, 14 chunk 1 | Accurate |
| 2 | What do students say about WMU meal plans? | Advice is mixed: lower plans may be enough, unlimited is convenient, 14-meal can run out, and no-meal-plan living depends on dorm and habits. | Answered that lower plans are recommended by some, unlimited is useful for repeated dining/snacks, 14-meal can run out, and no-meal-plan advice is mixed. | 08 chunks 0-1, 07 chunk 0, 09 chunks 0-1 | Accurate |
| 3 | What do students say about the WMU computer science program? | Students raise concerns about quality, staffing, transfer fit, and outcomes; some commenters still recommend WMU because of facilities, cost, and success stories. | Answered that concerns include quality and staffing, but some outcomes are successful and WMU issues are similar to comparable universities. | 01 chunks 0-1, 02 chunks 0-1, 03 chunks 0-1 | Accurate |
| 4 | What advice is given for finding old WMU CS syllabi? | Contact the professor and department administrative office; request the exact semester/year syllabus for transfer credit. | Answered with professor contact, department admin office, accreditation copies, and exact semester/year requirement. | 04 chunks 0-1 plus weaker CS chunks | Accurate |
| 5 | What do students say about off-campus housing or apartment concerns? | One warning cites mold, flooding risk, garbage, pests, utilities, and safety/neighborhood concerns; verify current conditions. | Answered with run-down interiors, mold, flooding risk, garbage, rats, stray animals, high utilities, and safety/neighborhood concerns. | 13 chunks 0-1, 09 chunks 0-1, 12 chunk 1 | Accurate |

All five evaluation questions were tested against the rebuilt ChromaDB index on 2026-06-07.

### Detailed Evaluation Outputs

**1. What do students say about parking at WMU?**

- **Expected answer:** Students complain about cost, full lots, reserved spaces, Parkview travel time, and parking enforcement/ticket uncertainty.
- **Actual system response:** Students complain about the parking situation at WMU, specifically mentioning that they pay about $150 per semester for parking, but many lots are full, and they may have to park far from where they need to go. They also mention that reserved employee spaces appear empty, which adds to their frustration. Additionally, students express concern about the travel time between main campus and Parkview campus. (11_wmu_parking_situation_and_costs.txt)
- **Retrieved chunks/source files:** 11_wmu_parking_situation_and_costs.txt chunks 0-1; 12_wmu_parking_enforcement_rules_discussion.txt chunks 0 and 2; 14_wmu_parking_ticket_registration_discussion.txt chunk 1.
- **Accuracy judgment:** Accurate.

**2. What do students say about WMU meal plans?**

- **Expected answer:** Students give mixed advice: lower plans may be enough, unlimited is convenient for frequent dining/snacks, 14-meal plans may run out, and no-meal-plan living depends on housing and habits.
- **Actual system response:** Students say that the meal plan is worth getting if living in the dorms, but choosing the lowest option is recommended. Some students like the unlimited plan because it allows them to enter dining halls several times a day for snacks, drinks, or social time. However, others mention that the unlimited plan may not be cost-effective for everyone, and some students who switched to a 14-meal plan often ran out of meals by the end of the week. (08_wmu_meal_plan_value.txt, 09_wmu_dorms_without_required_meal_plan.txt, 08_wmu_meal_plan_value.txt)
- **Retrieved chunks/source files:** 08_wmu_meal_plan_value.txt chunks 0-1; 07_wmu_dining_food_situation.txt chunk 0; 09_wmu_dorms_without_required_meal_plan.txt chunks 0-1.
- **Accuracy judgment:** Accurate.

**3. What do students say about the WMU computer science program?**

- **Expected answer:** Prospective students worry about quality, staffing, transfer fit, and outcomes; some commenters still recommend WMU because of facilities, cost, convenience, and success stories.
- **Actual system response:** Based on the provided context, students have expressed concerns about the quality of the WMU computer science program, with some mentioning that the department may be short-staffed (02_wmu_cs_program_quality_transfer_thread.txt). However, one commenter noted that people they knew had successful outcomes with CS and CE degrees, framing WMU's issues as similar to those at comparable universities (02_wmu_cs_program_quality_transfer_thread.txt). Prospective students also want to know about program quality, faculty experience, and whether the major is worth transferring into (01_wmu_cs_program_transfer_questions.txt, 01_wmu_cs_program_transfer_questions.txt Chunk Index: 1). Source files used: 01_wmu_cs_program_transfer_questions.txt, 02_wmu_cs_program_quality_transfer_thread.txt.
- **Retrieved chunks/source files:** 01_wmu_cs_program_transfer_questions.txt chunks 0-1; 02_wmu_cs_program_quality_transfer_thread.txt chunk 0; 03_wmu_ms_cs_program_questions.txt chunks 0-1.
- **Accuracy judgment:** Accurate.

**4. What advice is given for finding old WMU CS syllabi?**

- **Expected answer:** Contact the professor and department administrative office; ask for the exact semester/year syllabus because transfer review may require that version.
- **Actual system response:** For finding old WMU CS syllabi, the advice given is to try contacting the professor, but if that doesn't work, students should also contact the department administrative office because departments often need to keep copies for accreditation purposes. Additionally, it's recommended to ask for the exact semester/year syllabus if transfer credit is involved, as institutions often require the syllabus from the same academic year or semester in which the course was taken. (Source: 04_wmu_cs_syllabus_retrieval_advice.txt)
- **Retrieved chunks/source files:** 04_wmu_cs_syllabus_retrieval_advice.txt chunks 0-1; 01_wmu_cs_program_transfer_questions.txt chunk 0; 03_wmu_ms_cs_program_questions.txt chunks 0-1.
- **Accuracy judgment:** Accurate.

**5. What do students say about off-campus housing or apartment concerns?**

- **Expected answer:** At least one off-campus apartment warning mentions run-down conditions, mold, flooding risk, garbage, pests, utilities, and safety/neighborhood concerns; students should verify current conditions.
- **Actual system response:** According to the provided context, students have expressed concerns about off-campus housing, specifically about an apartment complex. A commenter gave a strongly negative warning about the complex, citing issues such as run-down interiors, mold in vents, flooding risk, garbage, rats, stray animals, and high utility bills. The commenter also mentioned general safety or neighborhood concerns and stated that they would not live there even at half the price. Source: 13_wmu_off_campus_apartment_warning_ccatk.txt (Chunk Index: 0 and 1)
- **Retrieved chunks/source files:** 13_wmu_off_campus_apartment_warning_ccatk.txt chunks 0-1; 09_wmu_dorms_without_required_meal_plan.txt chunks 0-1; 12_wmu_parking_enforcement_rules_discussion.txt chunk 1.
- **Accuracy judgment:** Accurate.

## Failure Case Analysis

**Question that exposed a weakness:** What advice is given for finding old WMU CS syllabi?

**What the system returned:** The answer was accurate, but retrieval included three weakly related CS program chunks after the two correct syllabus chunks.

**Root cause:** This is a retrieval-stage issue. With `TOP_K = 5`, ChromaDB returns the five nearest chunks even when only two are strongly relevant. Because several documents mention CS, transfer, and program questions, they can appear after the truly relevant syllabus chunks.

**What I would change:** Add a distance threshold or reranking step before generation. That would keep the two high-value syllabus chunks and drop lower-confidence CS chunks that are only broadly related.

## Query Interface

The project has both a CLI and a Gradio app.

CLI: `src/query.py` prompts for a question, prints the grounded answer, then prints retrieved source files, chunk numbers, and distance scores.

Gradio: `app.py` has one input field, `Your question`, and three output fields: `Grounded answer`, `Retrieved source files`, and `Retrieved chunks for debugging/evaluation`.

Complete CLI sample:

```text
Ask a question or type 'quit': What do students say about parking at WMU?

ANSWER:
Students complain about the parking situation at WMU, specifically mentioning that they pay about $150 per semester for parking, but many lots are full, and they may have to park far from where they need to go. They also mention that reserved employee spaces appear empty, making it hard to travel from main campus to Parkview campus within a reasonable time. (11_wmu_parking_situation_and_costs.txt)

RETRIEVED SOURCES:
- 11_wmu_parking_situation_and_costs.txt | chunk 0 | distance 0.557
- 11_wmu_parking_situation_and_costs.txt | chunk 1 | distance 0.656
- 12_wmu_parking_enforcement_rules_discussion.txt | chunk 2 | distance 0.6775
- 12_wmu_parking_enforcement_rules_discussion.txt | chunk 0 | distance 0.7017
- 14_wmu_parking_ticket_registration_discussion.txt | chunk 1 | distance 0.7033
```

## Spec Reflection

Planning helped implementation by forcing the system to define the domain, sources, chunking approach, retrieval method, and evaluation questions before documenting results. That made it easier to check the final pipeline against concrete expectations instead of only checking whether the code ran.

The implementation diverged from the initial project direction because the domain shifted from synthetic CS/professor data to real WMU student-life documents. I updated ingestion to read from `documents/`, rebuilt processed files and ChromaDB, and rewrote the docs around the real WMU corpus.

## AI Usage

**Instance 1**

- *What I gave the AI:* I gave ChatGPT-style tooling the project requirements, expected pipeline stages, and the WMU document folder structure.
- *What it produced:* It helped shape the ingestion, chunking, ChromaDB indexing, retrieval, and grounded generation scripts.
- *What I reviewed, revised, or overrode:* I checked file paths, source metadata, chunk counts, and retrieval outputs. I revised ingestion to use `documents/` instead of the older active input path.

**Instance 2**

- *What I gave the AI:* I gave Codex the final-submission rubric and asked it to inspect for old synthetic-data leakage, rebuild the WMU pipeline, and update documentation using actual outputs.
- *What it produced:* It found the old domain copy in `app.py`, identified the ingest path issue, rebuilt the artifacts, ran evaluation questions, and drafted README/planning updates.
- *What I reviewed, revised, or overrode:* I verified the generated documentation against actual command output, the manifest URLs, the chunk count, and the source-attributed system responses.
