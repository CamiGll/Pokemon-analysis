import os
# May need to import from entity_extractor if complex entity types are directly compared
# from .entity_extractor import DEFAULT_SKILLS_LIST # Or pass skills list if needed

# Define weights for different matching criteria (tunable)
WEIGHT_SKILLS = 0.7  # Primary factor
WEIGHT_EXPERIENCE_YEARS = 0.2 # If years are found and comparable
WEIGHT_EDUCATION_KEYWORDS = 0.1 # If relevant education keywords match

def compare_skills(cv_skills, jd_required_skills):
    """
    Compares CV skills with JD required skills and calculates a score.
    Returns a score (0-1) and a list of matched and missing skills.
    """
    if not jd_required_skills: # No skills explicitly required by JD
        return 1.0, [], [] # Perfect score, no skills to match/miss
    if not cv_skills: # CV has no skills listed
        return 0.0, [], list(jd_required_skills) # Zero score, all JD skills missing

    cv_skills_set = set(s.lower() for s in cv_skills)
    jd_skills_set = set(s.lower() for s in jd_required_skills)

    matched_skills = list(cv_skills_set.intersection(jd_skills_set))
    missing_skills = list(jd_skills_set.difference(cv_skills_set))

    score = len(matched_skills) / len(jd_skills_set) if jd_skills_set else 1.0
    return score, matched_skills, missing_skills

def compare_experience_years(cv_experience_years, jd_min_experience_years=None):
    """
    Compares CV extracted experience years with JD's minimum requirement (if any).
    cv_experience_years: list of numbers (e.g., [2, 5]) from entity_extractor.
    jd_min_experience_years: a single number (e.g., 3) if specified in JD.
    Returns a score (0 or 1 for now - could be more nuanced).
    """
    if jd_min_experience_years is None: # JD does not specify min years
        return 1.0 # No requirement, so considered met
    if not cv_experience_years: # CV has no extractable years
        return 0.0

    # Check if any of the extracted CV experience years meet or exceed the JD minimum
    # For CVs with multiple year entries (e.g. from different roles), max might be relevant
    if max(cv_experience_years) >= jd_min_experience_years:
        return 1.0
    else:
        return 0.0

def compare_education_keywords(cv_education_mentions, jd_education_keywords=None):
    """
    Basic check if CV education mentions contain any JD education keywords.
    cv_education_mentions: list of sentences/phrases from entity_extractor.
    jd_education_keywords: list of keywords like ['bachelor', 'master', 'phd'].
    Returns a score (0 or 1).
    """
    if not jd_education_keywords: # JD has no specific education keywords
        return 1.0 # No requirement, so considered met
    if not cv_education_mentions:
        return 0.0

    cv_edu_text_lower = ' '.join(cv_education_mentions).lower()
    for keyword in jd_education_keywords:
        if keyword.lower() in cv_edu_text_lower:
            return 1.0 # Found at least one keyword
    return 0.0

def calculate_relevance_score(cv_entities, jd_entities):
    """
    Calculates an overall relevance score for a CV against a Job Description.
    cv_entities: Dictionary of entities extracted from the CV.
    jd_entities: Dictionary of requirements extracted from the JD.
    Returns a total score (0-1) and a textual explanation.
    """
    total_score = 0.0
    explanations = []

    # 1. Skill Matching
    cv_skills = cv_entities.get('skills', [])
    jd_req_skills = jd_entities.get('required_skills', []) # From jd_processor
    skill_score, matched_skills, missing_skills = compare_skills(cv_skills, jd_req_skills)
    total_score += skill_score * WEIGHT_SKILLS
    if jd_req_skills:
        explanations.append(f"Skills: Matched {len(matched_skills)}/{len(jd_req_skills)} ({', '.join(matched_skills) if matched_skills else 'None'}). Missing: {', '.join(missing_skills) if missing_skills else 'None'}.")
    else:
        explanations.append("Skills: No specific skills listed in JD.")

    # 2. Experience Years Matching (Basic)
    cv_exp_years = cv_entities.get('experience_years', []) # List of ints
    jd_min_exp = jd_entities.get('min_experience_years') # Placeholder: JD processor needs to extract this
    # For now, let's assume jd_min_exp might be manually added or extracted to jd_entities later
    # Example: jd_entities['min_experience_years'] = 3
    experience_score = compare_experience_years(cv_exp_years, jd_min_exp)
    total_score += experience_score * WEIGHT_EXPERIENCE_YEARS
    if jd_min_exp:
        exp_met_status = 'Met' if experience_score > 0 else 'Not Met/Found'
        cv_max_exp = max(cv_exp_years) if cv_exp_years else 'N/A'
        explanations.append(f"Experience Years: JD requires {jd_min_exp} yrs. CV shows ~{cv_max_exp} yrs. Status: {exp_met_status}.")
    else:
        explanations.append("Experience Years: No specific minimum years in JD.")

    # 3. Education Keywords Matching (Basic)
    cv_edu_mentions = cv_entities.get('education_mentions', [])
    jd_edu_keywords = jd_entities.get('education_keywords') # Placeholder: JD processor needs to extract this
    # Example: jd_entities['education_keywords'] = ['bachelor', 'master']
    education_score = compare_education_keywords(cv_edu_mentions, jd_edu_keywords)
    total_score += education_score * WEIGHT_EDUCATION_KEYWORDS
    if jd_edu_keywords:
        edu_met_status = 'Potentially Met' if education_score > 0 else 'Not Met/Found'
        explanations.append(f"Education Keywords: JD mentions ({', '.join(jd_edu_keywords)}). Status: {edu_met_status}.")
    else:
        explanations.append("Education Keywords: No specific education keywords in JD.")

    # Ensure total score is capped at 1.0 (if weights sum > 1 or scores are not strictly 0-1)
    final_score = min(total_score, 1.0)
    return final_score, ' '.join(explanations)

if __name__ == '__main__':
    # Sample CV and JD entities for testing
    sample_cv_entities = {
        'name': 'John Doe',
        'emails': ['john.doe@email.com'],
        'phones': ['123-456-7890'],
        'skills': ['python', 'sql', 'machine learning', 'communication'],
        'education_mentions': ['M.Sc. in Computer Science from Major University.', 'Bachelor of Science in AI'],
        'experience_years': [5, 2], # e.g. 5 years total, 2 years in a specific role
        'job_titles': ['Software Engineer', 'Data Analyst']
    }

    sample_jd_entities_1 = {
        'required_skills': ['python', 'sql', 'data analysis', 'tensorflow'],
        'min_experience_years': 3, # Added for testing this logic
        'education_keywords': ['m.sc', 'master', 'bachelor'] # Added for testing
    }

    sample_jd_entities_2 = {
        'required_skills': ['java', 'spring', 'microservices'],
        'min_experience_years': 5
    }

    print("--- Test Case 1: Good Match ---")
    score1, explanation1 = calculate_relevance_score(sample_cv_entities, sample_jd_entities_1)
    print(f"Score: {score1:.2f}")
    print(f"Explanation: {explanation1}")

    print("--- Test Case 2: Poor Match (different tech stack) ---")
    score2, explanation2 = calculate_relevance_score(sample_cv_entities, sample_jd_entities_2)
    print(f"Score: {score2:.2f}")
    print(f"Explanation: {explanation2}")

    # Test case: CV with fewer skills than JD
    sample_cv_less_skills = sample_cv_entities.copy()
    sample_cv_less_skills['skills'] = ['python']
    sample_cv_less_skills['experience_years'] = [1]
    sample_cv_less_skills['education_mentions'] = ['High School Diploma']

    print("--- Test Case 3: Partial Match (CV with fewer skills/exp) ---")
    score3, explanation3 = calculate_relevance_score(sample_cv_less_skills, sample_jd_entities_1)
    print(f"Score: {score3:.2f}")
    print(f"Explanation: {explanation3}")

    # Test case: JD with no specific experience or education requirements
    sample_jd_entities_no_exp_edu = {
        'required_skills': ['python', 'sql']
    }
    print("--- Test Case 4: JD with only skill requirements ---")
    score4, explanation4 = calculate_relevance_score(sample_cv_entities, sample_jd_entities_no_exp_edu)
    print(f"Score: {score4:.2f}")
    print(f"Explanation: {explanation4}")
