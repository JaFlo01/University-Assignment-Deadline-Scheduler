import fitz 
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    document = fitz.open(pdf_path)
    text = ""

    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()

    document.close()
    return text

def normalize_text(text):
    """Normalize text by removing extra spaces and line breaks."""
    # Replace multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text)

    text = text.strip()
    return text

def extract_deadlines(text):
    """Extract various assignment deadlines based on multiple patterns."""
    patterns = [
        # Different ways deadlines could be formatted
        r"(Homework|HW)\s*(\d+)\s*due\s*(\d{1,2}/\d{1,2})",
        r"Assignment\s*(\d+)\s*Due\s*on\s*(\w+\s*\d{1,2})",
        r"(Lab|Project|Quiz)\s*(\d+)\s*\((\w+\s*\d{1,2})\)",
        r"Assignment\s*(\d+)\s*due\s*(\w+\s*\d{1,2})",
        r"Homework\s*(\d+)\s*due\s*on\s*(\w+\s*\d{1,2})",
        r"Quiz\s*(\d+)\s*on\s*(\w+\s*\d{1,2})"
    ]

    deadlines = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 3:
                assignment = f"{match[0]} {match[1]} due on {match[2]}"
            elif len(match) == 2:
                assignment = f"Assignment {match[0]} due on {match[1]}"
            else:
                assignment = f"{match[0]} due on {match[-1]}"
            deadlines.append(assignment)

    # Remove duplicates and sort by assignment type and number if possible
    deadlines = sorted(set(deadlines), key=lambda x: (re.findall(r'\d+', x), x))
    
    return deadlines

def extract_exams(text):
    """Extract various exam dates based on multiple patterns."""
    patterns = [
        # Different ways deadlines could be formatted
        r"(Midterm|Final)\s*Exam\s*on\s*(\w+\.\s*\d{1,2})",
        r"Exam\s*(\d+)\s*on\s*(\w+\.\s*\d{1,2})",
        r"Exam\s*(I+|II+)\s*(on\s*)?(\w+\s*\d{1,2})"
    ]

    exams = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 3:
                exam = f"Exam {match[0]} on {match[2]}"
            elif len(match) == 2:
                exam = f"{match[0]} Exam on {match[1]}"
            exams.append(exam)

    # Remove duplicates and sort by exam type and number if possible
    exams = sorted(set(exams), key=lambda x: (re.findall(r'\d+', x), x))
    
    return exams

def process_pdf_schedule(pdf_path):
    """Process the PDF schedule for various formats."""
    pdf_text = extract_text_from_pdf(pdf_path)
    normalized_text = normalize_text(pdf_text)
    
    # Extract deadlines and exams
    deadlines = extract_deadlines(normalized_text)
    exams = extract_exams(normalized_text)

    return deadlines, exams
