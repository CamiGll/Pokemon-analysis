import unittest
import os
import sys
import fitz  # PyMuPDF for creating test PDF

# Add project root (parent of 'scripts' and 'tests') to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from scripts.cv_loader import get_cv_files, read_txt_file, extract_text_from_pdf, load_all_cvs

class TestCVLoader(unittest.TestCase):
    TEST_DATA_DIR = os.path.join(project_root, 'tests', 'test_data_cv_loader')
    sample_txt_file = os.path.join(TEST_DATA_DIR, 'sample_cv.txt')
    sample_pdf_file = os.path.join(TEST_DATA_DIR, 'sample_cv.pdf')
    another_txt_file = os.path.join(TEST_DATA_DIR, 'another_cv.txt')
    unsupported_file = os.path.join(TEST_DATA_DIR, 'unsupported.docx')

    @classmethod
    def setUpClass(cls):
        # Create a directory for test data if it doesn't exist
        if not os.path.exists(cls.TEST_DATA_DIR):
            os.makedirs(cls.TEST_DATA_DIR)

        # Create dummy TXT file
        with open(cls.sample_txt_file, 'w', encoding='utf-8') as f:
            f.write('This is a sample text CV.')
        with open(cls.another_txt_file, 'w', encoding='utf-8') as f:
            f.write('Another text CV here.')

        # Create dummy PDF file using PyMuPDF
        try:
            doc = fitz.open()  # New empty PDF
            page = doc.new_page()
            page.insert_text((50, 72), 'This is a sample PDF CV content.')
            doc.save(cls.sample_pdf_file)
            doc.close()
        except Exception as e:
            print(f'Error creating sample PDF for testing: {e}')
            # Handle cases where sample_pdf_file might not be created

        # Create dummy unsupported file
        with open(cls.unsupported_file, 'w', encoding='utf-8') as f:
            f.write('This is a docx file and should be ignored by get_cv_files if specific.')

    @classmethod
    def tearDownClass(cls):
        # Clean up created files and directory
        for f in [cls.sample_txt_file, cls.sample_pdf_file, cls.another_txt_file, cls.unsupported_file]:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(cls.TEST_DATA_DIR):
            os.rmdir(cls.TEST_DATA_DIR)

    def test_get_cv_files(self):
        cv_files = get_cv_files(self.TEST_DATA_DIR)
        self.assertIn(self.sample_txt_file, cv_files)
        if os.path.exists(self.sample_pdf_file): # Only assert if PDF creation succeeded
             self.assertIn(self.sample_pdf_file, cv_files)
        self.assertIn(self.another_txt_file, cv_files)
        self.assertNotIn(self.unsupported_file, cv_files) # .docx should be ignored
        self.assertEqual(len(cv_files), 3 if os.path.exists(self.sample_pdf_file) else 2)

    def test_read_txt_file(self):
        content = read_txt_file(self.sample_txt_file)
        self.assertEqual(content, 'This is a sample text CV.')
        self.assertIsNone(read_txt_file('non_existent.txt'))

    def test_extract_text_from_pdf(self):
        if not os.path.exists(self.sample_pdf_file):
            self.skipTest(f"Sample PDF file {self.sample_pdf_file} not created, skipping test.")
        content = extract_text_from_pdf(self.sample_pdf_file)
        self.assertEqual(content, 'This is a sample PDF CV content.')
        self.assertIsNone(extract_text_from_pdf('non_existent.pdf'))

    def test_load_all_cvs(self):
        loaded_cvs = load_all_cvs(self.TEST_DATA_DIR)
        expected_num_loaded = 3 if os.path.exists(self.sample_pdf_file) else 2
        self.assertEqual(len(loaded_cvs), expected_num_loaded)
        filenames = [item[0] for item in loaded_cvs]
        self.assertIn(os.path.basename(self.sample_txt_file), filenames)
        if os.path.exists(self.sample_pdf_file):
            self.assertIn(os.path.basename(self.sample_pdf_file), filenames)

        # Check content of one loaded TXT file
        for fname, content in loaded_cvs:
            if fname == os.path.basename(self.sample_txt_file):
                self.assertEqual(content, 'This is a sample text CV.')
                break

if __name__ == '__main__':
    unittest.main()
