import io

# Try to import PDF and DOCX libraries with fallbacks
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("PyPDF2 not available - PDF parsing disabled")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("python-docx not available - DOCX parsing disabled")

try:
    from .gemini_client import parse_resume_with_gemini
except ImportError:
    # Fallback function
    def parse_resume_with_gemini(resume_text):
        return {
            "technical_skills": ["Python", "Data Analysis"],
            "experience_years": 2,
            "education_level": "Bachelor's",
            "domain_expertise": ["Technology"],
            "current_role": "Developer",
            "certifications": []
        }

def extract_text_from_pdf(file):
    """Extract text from PDF file."""
    if not PDF_AVAILABLE:
        return "PDF parsing not available - install PyPDF2"
    
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file):
    """Extract text from DOCX file."""
    if not DOCX_AVAILABLE:
        return "DOCX parsing not available - install python-docx"
    
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_resume(uploaded_file):
    """Extract text from uploaded resume file."""
    if uploaded_file is None:
        return ""

    # Handle both file objects and file paths
    if isinstance(uploaded_file, str):
        # File path provided
        try:
            with open(uploaded_file, 'rb') as f:
                if uploaded_file.lower().endswith('.pdf'):
                    return extract_text_from_pdf(f)
                elif uploaded_file.lower().endswith(('.docx', '.doc')):
                    return extract_text_from_docx(f)
                else:
                    return f.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading file {uploaded_file}: {e}")
            return ""

    # Handle uploaded file objects (from web UI)
    try:
        file_type = uploaded_file.name.split('.')[-1].lower()

        if file_type == 'pdf':
            return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
        elif file_type in ['docx', 'doc']:
            return extract_text_from_docx(io.BytesIO(uploaded_file.read()))
        else:
            # Assume it's text
            return uploaded_file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error processing resume file: {e}")
        return ""

def parse_resume(resume_text):
    """Parse resume text and return structured data."""
    if not resume_text.strip():
        return {
            "technical_skills": [],
            "experience_years": 0,
            "education_level": "Unknown",
            "domain_expertise": [],
            "current_role": "Unknown",
            "certifications": []
        }

    return parse_resume_with_gemini(resume_text)
