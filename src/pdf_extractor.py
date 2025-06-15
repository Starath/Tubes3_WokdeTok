import PyPDF2

def extract_text_pypdf2(pdf_path: str) -> str:
    """
    Extract text from PDF using PyPDF2
    args:
        pdf_path (str): Path to the PDF file
    returns:
        str: Extracted text from the PDF file, or None if an error occurs
    """
    text = ""
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    
    return text.strip()

if __name__ == '__main__':
    pdf_text = extract_text_pypdf2("test/ACCOUNTANT/10554236.pdf")
    print(pdf_text)