# AI CV Filtering System

This project aims to filter and rank CVs based on a job description using AI techniques.

## Setup
1. Place CV files (PDF or TXT) and the job description (TXT) in the 'data/' folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Download spaCy model: `python -m spacy download en_core_web_sm` (or other models)

## Running the System
Run the main script: `python scripts/main.py name_of_jd_file.txt`
