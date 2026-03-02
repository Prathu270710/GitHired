import PyPDF2
import docx
import os

def parse_resume(file_path):
    """Extract text from PDF or DOCX resume"""
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return parse_pdf(file_path)
    elif file_extension == '.docx':
        return parse_docx(file_path)
    else:
        return None, "Unsupported file format. Please upload PDF or DOCX."

def parse_pdf(file_path):
    """Extract text from PDF"""
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        
        if not text.strip():
            return None, "Could not extract text from PDF. Try a different file."
        
        return text.strip(), None
    
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"

def parse_docx(file_path):
    """Extract text from DOCX"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        if not text.strip():
            return None, "Could not extract text from DOCX. Try a different file."
        
        return text.strip(), None
    
    except Exception as e:
        return None, f"Error reading DOCX: {str(e)}"