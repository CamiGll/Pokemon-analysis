import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from scripts.entity_extractor import extract_entities, extract_emails, extract_phones, extract_skills, extract_experience_years, NLP_MODEL, DEFAULT_SKILLS_LIST

class TestEntityExtractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not NLP_MODEL:
            raise unittest.SkipTest("spaCy model not loaded, skipping entity_extractor tests.")

    sample_text_1 = """
    John Doe, an experienced Python Developer. Reachable at john.doe@example.com or (123)456-7890.
    Skills: Python, Java, SQL. Experience: 5 years of work in software development, 3+ years with Python.
    Education: M.Sc. in Data Science from Big University.
    """

    sample_text_2 = "Jane Smith. jane@test.co.uk. No phone. Skills: project management, agile."

    def test_extract_emails(self):
        self.assertEqual(extract_emails(self.sample_text_1), ['john.doe@example.com'])
        self.assertEqual(extract_emails(self.sample_text_2), ['jane@test.co.uk'])

    def test_extract_phones(self):
        # Regex might pick up various formats, ensure the primary one is there
        phones1 = extract_phones(self.sample_text_1)
        self.assertIn('(123)456-7890', phones1) # Exact match based on current regex
        self.assertEqual(extract_phones(self.sample_text_2), [])

    def test_extract_skills(self):
        skills1 = extract_skills(self.sample_text_1, DEFAULT_SKILLS_LIST)
        self.assertIn('python', skills1)
        self.assertIn('java', skills1)
        self.assertIn('sql', skills1)

        skills2 = extract_skills(self.sample_text_2, DEFAULT_SKILLS_LIST)
        self.assertIn('project management', skills2)
        self.assertIn('agile', skills2)

    def test_extract_experience_years(self):
        years = extract_experience_years(self.sample_text_1)
        self.assertIn(5, years)
        self.assertIn(3, years) # From '3+ years'
        self.assertEqual(len(years), 2) # Should find two distinct numbers

    def test_extract_entities_comprehensive(self):
        entities = extract_entities(self.sample_text_1)
        self.assertEqual(entities.get('name'), 'John Doe')
        self.assertIn('john.doe@example.com', entities.get('emails', []))
        self.assertIn('(123)456-7890', entities.get('phones', []))
        self.assertTrue(all(s in entities.get('skills', []) for s in ['python', 'java', 'sql']))
        self.assertIn(5, entities.get('experience_years', []))
        self.assertIn(3, entities.get('experience_years', []))
        self.assertTrue(any('M.Sc.' in edu for edu in entities.get('education_mentions', [])))
        # Check for job titles (basic)
        self.assertTrue(any('Python Developer' in title for title in entities.get('job_titles',[])))

    def test_extract_entities_empty_input(self):
        self.assertEqual(extract_entities(None), {})
        self.assertEqual(extract_entities(''), {})

if __name__ == '__main__':
    unittest.main()
