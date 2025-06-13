import os
import argparse
import pandas as pd
from datetime import datetime

# Assuming other scripts are in the same directory (scripts/)
from .cv_loader import load_all_cvs
from .jd_processor import load_jd_text_from_file, process_job_description
from .entity_extractor import extract_entities, NLP_MODEL # Import NLP_MODEL to check if loaded
from .matcher import calculate_relevance_score

OUTPUT_DIR = 'output/'

def run_cv_filter(jd_filename):
    """Main function to run the CV filtering process."""
    if not NLP_MODEL:
        print("Error: spaCy NLP model ('en_core_web_sm') not loaded.")
        print("Please ensure it's downloaded: python -m spacy download en_core_web_sm")
        return

    print(f"--- Starting CV Filtering Process for JD: {jd_filename} ---")

    # 1. Load and Process Job Description
    print("1. Loading and processing Job Description...")
    jd_text = load_jd_text_from_file(jd_filename)
    if not jd_text:
        print(f"Failed to load Job Description: {jd_filename}. Exiting.")
        return
    jd_entities = process_job_description(jd_text)
    if not jd_entities:
        print("Failed to process Job Description. Extracted entities are empty. Exiting.")
        return
    print(f"JD Processed. Required Skills: {jd_entities.get('required_skills', 'None')}")
    # Add min_experience_years and education_keywords to jd_entities for matcher testing
    # This is a placeholder; these should ideally be extracted by jd_processor
    # For now, we'll add some defaults if not present for more complete matching.
    if 'min_experience_years' not in jd_entities and 'experience_years' in jd_entities and jd_entities['experience_years']:
        jd_entities['min_experience_years'] = max(jd_entities['experience_years']) # Take max found in JD as a proxy
    # Example: jd_entities['education_keywords'] = ['bachelor', 'master'] # if extracted
    print("-"*30)

    # 2. Load CVs
    print("2. Loading CVs from 'data/' directory...")
    loaded_cvs = load_all_cvs() # Loads from default 'data/' directory
    if not loaded_cvs:
        print("No CVs found or loaded from 'data/' directory. Exiting.")
        return
    print(f"Found {len(loaded_cvs)} CVs to process.")
    print("-"*30)

    # 3. Process Each CV and Score
    print("3. Processing and Scoring CVs...")
    results = []
    for cv_filename, cv_text in loaded_cvs:
        print(f"  Processing CV: {cv_filename}")
        if not cv_text:
            print(f"    Skipping {cv_filename} due to empty content.")
            results.append({
                'Candidate File': cv_filename,
                'Candidate Name': 'N/A - Content Error',
                'Score': 0,
                'Explanation': 'CV content could not be loaded or is empty.'
            })
            continue

        cv_entities = extract_entities(cv_text)
        if not cv_entities:
            print(f"    Skipping {cv_filename} as no entities could be extracted.")
            results.append({
                'Candidate File': cv_filename,
                'Candidate Name': 'N/A - Extraction Error',
                'Score': 0,
                'Explanation': 'Could not extract entities from CV.'
            })
            continue

        score, explanation = calculate_relevance_score(cv_entities, jd_entities)
        candidate_name = cv_entities.get('name', 'N/A')

        results.append({
            'Candidate File': cv_filename,
            'Candidate Name': candidate_name,
            'Score': score,
            'Explanation': explanation
        })
        print(f"    Score for {cv_filename} ({candidate_name}): {score:.2f}")
    print("-"*30)

    # 4. Rank Candidates
    print("4. Ranking Candidates...")
    ranked_results_df = pd.DataFrame(results)
    if not ranked_results_df.empty:
        ranked_results_df = ranked_results_df.sort_values(by='Score', ascending=False).reset_index(drop=True)
        ranked_results_df.index += 1 # Start rank from 1
    print("-"*30)

    # 5. Output Results
    print("5. Outputting Results...")
    if ranked_results_df.empty:
        print("No candidates processed or ranked.")
    else:
        print("\n--- Ranked Candidates ---")
        # Print to console (adjust columns for readability if too wide)
        pd.set_option('display.max_colwidth', 60) # Adjust explanation column width
        pd.set_option('display.width', 120) # Adjust overall width
        print(ranked_results_df[['Candidate File', 'Candidate Name', 'Score', 'Explanation']].to_string())

        # Save to CSV
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(OUTPUT_DIR, f"ranked_cvs_{jd_filename.replace('.txt', '')}_{timestamp}.csv")
        try:
            ranked_results_df.to_csv(output_filename, index_label='Rank')
            print(f"\nResults saved to: {output_filename}")
        except Exception as e:
            print(f"\nError saving results to CSV: {e}")

    print("--- CV Filtering Process Finished ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI CV Filtering System - Main Script')
    parser.add_argument('jd_filename', type=str, help='Filename of the Job Description .txt file located in the data/ directory.')

    args = parser.parse_args()

    # Check if NLP_MODEL is loaded before running (entity_extractor tries to load it)
    if NLP_MODEL is None:
        print("CRITICAL: spaCy model 'en_core_web_sm' could not be loaded by entity_extractor.")
        print("Please ensure it's downloaded by running: python -m spacy download en_core_web_sm")
        print("Exiting main script.")
    else:
        # For testing, create dummy JD if it doesn't exist, or ensure one is present
        # This is just to make the script runnable with a default if no args provided in some IDEs
        # Command line execution is preferred: python scripts/main.py your_jd_file.txt
        jd_path_for_run = os.path.join('data', args.jd_filename)
        if not os.path.exists(jd_path_for_run):
            print(f"Error: Job description file '{args.jd_filename}' not found in 'data/' directory.")
            print("Please make sure it exists. Example: python scripts/main.py my_job_description.txt")
            # Example: Create a dummy JD for testing if it doesn't exist
            # with open(jd_path_for_run, 'w') as f_temp_jd:
            #     f_temp_jd.write('Required skills: python, java. Experience: 3 years.')
            # print(f"Created a dummy JD: {args.jd_filename} for testing. Please replace it with a real one.")
        else:
            run_cv_filter(args.jd_filename)
