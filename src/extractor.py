import fitz  # PyMuPDF
import os

class ContractExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        
    def extract_text(self):
        """Extracts raw text from the PDF file."""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"Oops! File not found at {self.pdf_path}")
            
        text = ""
        try:
            # Open the document
            with fitz.open(self.pdf_path) as doc:
                for page_num, page in enumerate(doc):
                    # We use "blocks" to keep the text grouped logically
                    blocks = page.get_text("blocks")
                    for b in blocks:
                        text += b[4] + " "  # b[4] is the actual text content
                
            return self.clean_text(text)
        except Exception as e:
            return f"Error during extraction: {str(e)}"

    def clean_text(self, text):
        """Basic cleaning to remove extra whitespace and newlines."""
        # Replace multiple newlines/spaces with a single space
        cleaned = " ".join(text.split())
        return cleaned

# Quick Test logic
if __name__ == "__main__":
    # Put a sample PDF in your data/ folder to test!
    test_path = "data/sample_contract.pdf" 
    if os.path.exists(test_path):
        extractor = ContractExtractor(test_path)
        print("--- Extraction Preview ---")
        print(extractor.extract_text()[:500]) # Print first 500 chars