import os
import fitz  # PyMuPDF

DATA_DIR = 'data/'

def get_cv_files(data_directory=DATA_DIR):
    """Lists all .txt and .pdf files in the specified data directory."""
    cv_files = []
    if not os.path.exists(data_directory):
        print(f"Error: Data directory '{data_directory}' not found.")
        return cv_files
    for filename in os.listdir(data_directory):
        if filename.lower().endswith('.txt') or filename.lower().endswith('.pdf'):
            cv_files.append(os.path.join(data_directory, filename))
    return cv_files

def read_txt_file(file_path):
    """Reads content from a .txt file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        return None
    except Exception as e:
        print(f"Error reading TXT file {file_path}: {e}")
        return None

def extract_text_from_pdf(file_path):
    """Extracts text content from a .pdf file using PyMuPDF."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        return text
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        return None
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return None

def load_all_cvs(data_directory=DATA_DIR):
    """
    Loads all CVs (.txt and .pdf) from the data directory.
    Returns a list of tuples: (filename, text_content).
    """
    cv_file_paths = get_cv_files(data_directory)
    loaded_cvs = []
    for file_path in cv_file_paths:
        filename = os.path.basename(file_path)
        content = None
        if filename.lower().endswith('.txt'):
            content = read_txt_file(file_path)
        elif filename.lower().endswith('.pdf'):
            content = extract_text_from_pdf(file_path)

        if content is not None:
            loaded_cvs.append((filename, content))
        else:
            print(f"Could not load or parse: {filename}")
    return loaded_cvs

if __name__ == '__main__':
    # Example Usage: Create dummy files in 'data/' directory for testing
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Create a dummy TXT file
    with open(os.path.join(DATA_DIR, 'sample_cv1.txt'), 'w', encoding='utf-8') as f:
        f.write('This is a sample text CV from John Doe. Skills: Python, Java.')

    # Create a dummy PDF file (requires PyMuPDF to be installed and working)
    try:
        pdf_doc = fitz.open() # Create a new PDF
        page = pdf_doc.new_page()
        page.insert_text((50, 72), 'This is a sample PDF CV from Jane Smith. Experience: 5 years in Project Management.')
        pdf_doc.save(os.path.join(DATA_DIR, 'sample_cv2.pdf'))
        pdf_doc.close()
        print(f"Created dummy sample_cv2.pdf in {DATA_DIR}")
    except Exception as e:
        print(f"Could not create dummy PDF for testing: {e}. PDF tests might not run as expected.")

    # Test get_cv_files
    print("Listing CV files:")
    cv_files = get_cv_files()
    print(cv_files)

    # Test load_all_cvs
    print("\nLoading all CVs:")
    all_loaded_cvs = load_all_cvs()
    for filename, content_preview in all_loaded_cvs:
        print(f"  {filename}: {content_preview[:100]}...")

    # Clean up dummy files (optional, comment out if you want to inspect them)
    # if os.path.exists(os.path.join(DATA_DIR, 'sample_cv1.txt')):"
    #     os.remove(os.path.join(DATA_DIR, 'sample_cv1.txt'))"
    # if os.path.exists(os.path.join(DATA_DIR, 'sample_cv2.pdf')):"
    #     os.remove(os.path.join(DATA_DIR, 'sample_cv2.pdf'))"
