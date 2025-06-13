import os
# Assuming entity_extractor.py is in the same directory or accessible via PYTHONPATH
from .entity_extractor import extract_skills, extract_entities, DEFAULT_SKILLS_LIST, NLP_MODEL

DATA_DIR = 'data/'

def load_jd_text_from_file(jd_filename, data_directory=DATA_DIR):
    """Loads text content from a job description file in the data directory."""
    file_path = os.path.join(data_directory, jd_filename)
    if not os.path.exists(file_path):
        print(f"Error: Job Description file not found at {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading Job Description file {file_path}: {e}")
        return None

def process_job_description(jd_text, skills_list=DEFAULT_SKILLS_LIST):
    """
    Extracts key information (especially skills) from the job description text.
    Leverages general entity extraction and specifically skill extraction.
    """
    if not jd_text or not isinstance(jd_text, str):
        print("JD text is empty or invalid.")
        return {}

    # Use the generic entity extractor for a broad overview
    # This will give us NER entities, and also skills if we pass the text directly
    # However, extract_entities already calls extract_skills.
    # We might want a more focused approach for JDs, e.g. prioritizing certain sections.
    # For now, let's use extract_entities and then specifically ensure 'required_skills' is populated.

    jd_extracted_info = extract_entities(jd_text, skills_list)

    # Ensure 'required_skills' is explicitly available for matching clarity
    # extract_entities returns 'skills', we can rename or alias it for JD context
    if 'skills' in jd_extracted_info:
        jd_extracted_info['required_skills'] = jd_extracted_info.pop('skills')
    else:
        jd_extracted_info['required_skills'] = []

    # Future: Could add extraction for specific JD fields like:
    # - Minimum years of experience required
    # - Education level required
    # - Specific tools or technologies not in the general skills list

    return jd_extracted_info

if __name__ == '__main__':
    if not NLP_MODEL: # Check if spaCy model loaded in entity_extractor
        print("Skipping jd_processor example: spaCy model not loaded.")
    else:
        # Create a dummy JD file in 'data/' for testing
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        sample_jd_filename = 'sample_jd.txt'
        sample_jd_content = """
        Job Title: Senior Python Developer (Remote)

        We are seeking an experienced Senior Python Developer to join our dynamic team.
        The ideal candidate will have 5+ years of experience in Python development,
        a strong understanding of web frameworks like Django or Flask, and proficiency in SQL.
        Knowledge of machine learning and AWS is a big plus.
        Responsibilities include designing and implementing software solutions.
        Requires a Bachelor's degree in Computer Science or related field.
        Key skills: Python, Django, SQL, REST APIs. Preferred: machine learning, AWS.
        """
        with open(os.path.join(DATA_DIR, sample_jd_filename), 'w', encoding='utf-8') as f:
            f.write(sample_jd_content)
        print(f"Created dummy {sample_jd_filename} in {DATA_DIR}")

        # Test load_jd_text_from_file
        print(f"\nLoading JD text from {sample_jd_filename}:")
        jd_text = load_jd_text_from_file(sample_jd_filename)
        if jd_text:
            print(f"JD Text (first 100 chars): {jd_text[:100]}...")

            # Test process_job_description
            print("\nProcessing Job Description:")
            jd_info = process_job_description(jd_text)
            import json
            print(json.dumps(jd_info, indent=2))
            print(f"\nSpecifically required skills: {jd_info.get('required_skills')}")
        else:
            print("Could not load JD text for processing.")

        # Test with a non-existent file
        print("\nAttempting to load non-existent JD:")
        non_existent_jd_text = load_jd_text_from_file('non_existent_jd.txt')
        if not non_existent_jd_text:
            print("Correctly handled non-existent JD file.")

        # Clean up dummy file (optional)
        # if os.path.exists(os.path.join(DATA_DIR, sample_jd_filename)):
        #     os.remove(os.path.join(DATA_DIR, sample_jd_filename))
