import base64
import tempfile
import os
from PyPDF2 import PdfReader, PdfWriter
from fitz import open as fitz_open  # PyMuPDF
import difflib
import re

def find_page_and_highlight(pdf_path, search_text, threshold=0.6):
    """
    Find the best matches for search_text in the PDF and return a highlighted PDF.
    
    Args:
        pdf_path: Path to the PDF file
        search_text: Text to search for
        threshold: Similarity threshold for fuzzy matching
    
    Returns:
        Path to a highlighted PDF file and a list of page numbers where matches were found
    """
    # Open the PDF
    pdf_document = fitz_open(pdf_path)
    matching_pages = []
    
    # Clean and normalize the search text
    search_text = re.sub(r'\s+', ' ', search_text).strip()
    
    # Search each page for text
    for page_num, page in enumerate(pdf_document):
        text = page.get_text()
        
        # Split text into paragraphs (more natural chunks)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Find best matching paragraphs using fuzzy matching
        for paragraph in paragraphs:
            # Clean and normalize paragraph text
            paragraph = re.sub(r'\s+', ' ', paragraph).strip()
            
            # Calculate similarity
            similarity = difflib.SequenceMatcher(None, search_text.lower(), paragraph.lower()).ratio()
            
            if similarity > threshold:
                # Found a match, highlight it
                matching_pages.append(page_num)
                
                # Search for the paragraph in the page
                text_instances = page.search_for(paragraph)
                
                # Add highlight with better visibility
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=(1, 1, 0))  # Yellow highlight
                    highlight.set_opacity(0.3)  # Semi-transparent
                    highlight.update()
                break
    
    # If we found matches, save the highlighted PDF
    if matching_pages:
        output_path = tempfile.mktemp(suffix='.pdf')
        pdf_document.save(output_path)
        pdf_document.close()
        return output_path, matching_pages
    
    pdf_document.close()
    return None, []

def get_pdf_download_link(pdf_path, filename="highlighted.pdf"):
    """Generate a download link for a PDF file"""
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" target="_blank" class="highlighted-pdf-link">View Highlighted PDF</a>'
    return href

def cleanup_temp_pdf(pdf_path):
    """Clean up temporary PDF file"""
    try:
        if pdf_path and os.path.exists(pdf_path):
            os.unlink(pdf_path)
    except Exception as e:
        print(f"Error cleaning up temp PDF: {e}") 