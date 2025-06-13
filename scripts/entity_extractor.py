import spacy
import re

# Attempt to load a spaCy model (e.g., en_core_web_sm)
# User should download this: python -m spacy download en_core_web_sm
NLP_MODEL = None
try:
    NLP_MODEL = spacy.load('en_core_web_sm')
except OSError:
    print("spaCy model 'en_core_web_sm' not found. Please download it by running:")
    print("python -m spacy download en_core_web_sm")
    # Fallback or further action could be added here if needed

# Predefined list of skills (can be expanded and managed externally)
DEFAULT_SKILLS_LIST = [
    'python', 'java', 'c++', 'javascript', 'ruby', 'php', 'swift', 'kotlin', 'golang',
    'sql', 'mysql', 'postgresql', 'mongodb', 'nosql',
    'html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'django', 'flask',
    'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes',
    'machine learning', 'deep learning', 'artificial intelligence', 'ai', 'data analysis',
    'data science', 'statistics', 'nlp', 'natural language processing',
    'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'keras', 'pytorch',
    'project management', 'agile', 'scrum', 'product management',
    'communication', 'teamwork', 'problem solving', 'leadership'
]

def extract_name(doc):
    """Extracts person names from a spaCy Doc."""
    names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    # Often the first PERSON entity is the candidate's name, but this isn't guaranteed.
    # Consider more robust name extraction if needed.
    return names[0] if names else None

def extract_emails(text):
    """Extracts email addresses using regex."""
    return list(set(re.findall(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', text, re.I)))

def extract_phones(text):
    """Extracts phone numbers using a basic regex."""
    # This regex is basic and might need improvement for international numbers or various formats.
    return list(set(re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\s]??\d{4}|\d{10})', text)))

def extract_skills(text, skills_list=DEFAULT_SKILLS_LIST):
    """Extracts skills from text based on a predefined list using regex for whole word matching."""
    found_skills = set()
    # Using regex for case-insensitive, whole-word matching for each skill
    for skill in skills_list:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.add(skill.lower()) # Store skills in lowercase for consistency
    return sorted(list(found_skills))

def extract_education(doc):
    """Extracts education-related phrases (very basic)."""
    education_keywords = ['university', 'college', 'institute', 'b.sc', 'm.sc', 'ph.d', 'bachelor', 'master', 'degree', 'diploma']
    education_mentions = []
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in education_keywords):
            # This is a naive approach. More sophisticated parsing would look for organization entities near keywords.
            education_mentions.append(sent.text.strip())
    return list(set(education_mentions)) # Use set to avoid duplicate sentences

def extract_experience_years(text):
    """Extracts years of experience using regex (basic)."""
    # Matches 'X years experience', 'X+ years of experience', 'X years of work'
    matches = re.findall(r'(\d+\+?)\s+years?\s+(?:of\s+)?(?:experience|work|exp\.)', text, re.IGNORECASE)
    # Convert to integers, handling 'X+' by just taking X for now
    numeric_years = [int(re.sub(r'\+', '', m)) for m in matches]
    return sorted(list(set(numeric_years))) # Return unique, sorted years found

def extract_job_titles(doc):
    """Placeholder for extracting job titles. This often requires custom NER or rule-based systems."""
    # Example: Look for Noun Phrases that appear capitalized and near experience keywords
    # This is highly heuristic and would need significant refinement.
    potential_titles = []
    common_titles = ['engineer', 'developer', 'manager', 'analyst', 'scientist', 'consultant', 'specialist', 'architect']
    for chunk in doc.noun_chunks:
        # A very simple check: if the chunk contains a common title word and is mostly title-cased
        if any(title_word in chunk.text.lower() for title_word in common_titles) and chunk.text.istitle():
            # Further checks could be proximity to dates, company names (ORG entities), etc.
            potential_titles.append(chunk.text.strip())
    return list(set(potential_titles))

def extract_entities(text, skills_list=DEFAULT_SKILLS_LIST):
    """Main function to process text and return a dictionary of extracted entities."""
    if not NLP_MODEL:
        print("spaCy NLP model not loaded. Cannot extract entities.")
        return {}
    if not text or not isinstance(text, str):
        return {} # Return empty dict for empty or invalid input

    doc = NLP_MODEL(text)

    name = extract_name(doc)
    emails = extract_emails(text)
    phones = extract_phones(text)
    skills = extract_skills(text, skills_list)
    education_mentions = extract_education(doc)
    experience_years = extract_experience_years(text)
    job_titles = extract_job_titles(doc)

    # General NER entities for context
    ner_entities = {ent.label_: [] for ent in doc.ents}
    for ent in doc.ents:
        ner_entities[ent.label_].append(ent.text)
    for label in ner_entities:
        ner_entities[label] = list(set(ner_entities[label])) # Unique entities per label

    return {
        'name': name,
        'emails': emails,
        'phones': phones,
        'skills': skills,
        'education_mentions': education_mentions,
        'experience_years': experience_years,
        'job_titles': job_titles, # Basic extraction
        'ner_entities': ner_entities # General NER for context
    }

if __name__ == '__main__':
    if not NLP_MODEL:
        print("Skipping entity_extractor example: spaCy model not loaded.")
    else:
        sample_cv_text = """
        Dr. John Michael Doe, PhD.
        Contact: (123) 456-7890, john.doe@email.com.
        Summary: A Python Developer and Data Scientist with 5+ years of experience in data analysis and machine learning.
        Proficient in SQL, Pandas, and Scikit-learn. Also knows Java.
        Education: M.Sc. in Computer Science from Major University (2018). B.Sc. from State College.
        Experience: Senior Software Engineer at Tech Innovations Inc. (2020-Present).
        Previously, Software Developer at Another Corp. (3 years of work).
        Skills: Python, Java, SQL, Pandas, Scikit-learn, Docker, Communication, Machine Learning.
        """
        print("Extracting entities from sample CV text:")
        entities = extract_entities(sample_cv_text)
        import json
        print(json.dumps(entities, indent=2))

        sample_jd_text = """
        We are looking for a Software Engineer with Python and SQL skills.
        Must have a Bachelor's degree and 3 years experience in development.
        """
        print("\nExtracting entities from sample JD text:")
        jd_entities = extract_entities(sample_jd_text)
        print(json.dumps(jd_entities, indent=2))
