# WMU Unofficial Guide Web Dataset

This dataset was created from publicly accessible r/WMU webpages for a class RAG project called **The Unofficial Guide**.

## Domain
Unofficial student advice about Western Michigan University student life, with emphasis on CS/program concerns, dining, housing, parking, and career preparation.

## Important note
These files are **source-derived notes**, not official university guidance and not complete copies of the original webpages. They summarize and lightly paraphrase public Reddit content so the RAG system can be built without republishing entire threads. Each file includes the original source URL at the top.

## How to use
Copy the `.txt` files from `documents/` into the `documents/` folder of your forked GitHub repo. If your ingestion code reads `data/raw/`, copy these same files there instead.

## Suggested evaluation questions
1. What do students say about WMU CS program quality for transfer students?
2. How should a student find old CS syllabi for transfer credit?
3. What do students say about WMU dining options and hours?
4. Is the meal plan worth it for freshmen living in the dorms?
5. Which dorms are mentioned as not requiring a meal plan?
6. What are common complaints about WMU parking?
7. Does parking enforcement completely stop after the semester?
8. What housing red flags were reported in the CCATK apartment discussion?
9. What career support is mentioned for engineering or CS-adjacent students?
10. Are Reddit answers about parking tickets reliable enough to follow without official confirmation?

## Recommended README language
This project uses a curated dataset of public r/WMU source-derived notes. Each document contains a source URL, collection date, and summarized student-generated content. The dataset was cleaned to remove Reddit navigation text, menus, ads, and unrelated recommendation links, while preserving the substantive student advice or concern from each source.
