"""
Contract Text Processor
Handles chunking and filtering of contract text for efficient analysis.
"""

from typing import List


class ContractProcessor:
    """
    Processes contract text into analyzable chunks.
    Optimized for legal document structure.
    """
    
    # Comprehensive list of risk-related keywords for filtering
    RISK_KEYWORDS = [
        # Liability terms
        "liability", "indemnify", "indemnification", "hold harmless", "damages",
        "consequential", "negligence", "fault", "responsible", "waive", "waiver",
        
        # Termination terms
        "termination", "terminate", "cancel", "cancellation", "exit", "expire",
        "expiration", "renewal", "renew", "automatic renewal", "notice period",
        
        # Financial terms
        "payment", "fee", "charge", "refund", "penalty", "interest", "late payment",
        "non-refundable", "prepaid", "advance", "price increase",
        
        # IP terms  
        "intellectual property", "copyright", "patent", "trademark", "license",
        "work for hire", "ownership", "assign", "assignment", "proprietary",
        
        # Confidentiality terms
        "confidential", "confidentiality", "non-disclosure", "nda", "secret",
        "proprietary information", "trade secret",
        
        # Restrictive terms
        "non-compete", "non-solicitation", "exclusive", "exclusivity", "restrict",
        "prohibition", "covenant",
        
        # Dispute terms
        "arbitration", "mediation", "dispute", "litigation", "jurisdiction",
        "governing law", "venue", "jury", "court", "attorney fees",
        
        # Compliance terms
        "compliance", "regulation", "regulatory", "audit", "inspection", "warranty",
        "representation", "breach", "default", "cure period",
        
        # Data terms
        "data", "privacy", "personal information", "gdpr", "ccpa", "security",
        "breach notification", "data protection",
    ]
    
    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 200):
        """
        Initialize the processor.
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks to preserve context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for analysis.
        
        Tries to split at paragraph boundaries when possible.
        
        Args:
            text: Full contract text
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Try to split at paragraph boundaries
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If adding this paragraph exceeds chunk size, save current and start new
            if len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If no paragraphs found, fall back to simple chunking
        if not chunks:
            chunks = self._simple_chunk(text)
        
        return chunks

    def _simple_chunk(self, text: str) -> List[str]:
        """Simple character-based chunking with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence ending punctuation
                for punct in ['. ', '.\n', '? ', '?\n', '! ', '!\n']:
                    last_punct = text[start:end].rfind(punct)
                    if last_punct > self.chunk_size // 2:
                        end = start + last_punct + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            
        return chunks

    def filter_relevant_chunks(self, chunks: List[str], 
                                keywords: List[str] = None,
                                min_matches: int = 1) -> List[str]:
        """
        Filter chunks to only those containing risk-related keywords.
        
        Args:
            chunks: List of text chunks
            keywords: Custom keywords (uses default RISK_KEYWORDS if None)
            min_matches: Minimum keyword matches required
            
        Returns:
            List of relevant chunks sorted by relevance
        """
        keywords = keywords or self.RISK_KEYWORDS
        
        scored_chunks = []
        for chunk in chunks:
            chunk_lower = chunk.lower()
            matches = sum(1 for kw in keywords if kw.lower() in chunk_lower)
            if matches >= min_matches:
                scored_chunks.append((matches, chunk))
        
        # Sort by number of matches (most relevant first)
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        return [chunk for _, chunk in scored_chunks]

    def extract_sections(self, text: str) -> dict:
        """
        Extract named sections from the contract.
        
        Args:
            text: Full contract text
            
        Returns:
            Dictionary with section names as keys and content as values
        """
        import re
        
        # Common section patterns
        section_patterns = [
            r'(?:^|\n)(\d+\.?\s+[A-Z][A-Z\s]+)(?:\n|\.)',  # "1. TERM AND TERMINATION"
            r'(?:^|\n)(ARTICLE\s+\d+[:\.]?\s*[A-Z\s]+)',    # "ARTICLE 1: DEFINITIONS"
            r'(?:^|\n)(SECTION\s+\d+[:\.]?\s*[A-Z\s]+)',    # "SECTION 1: PAYMENT"
            r'(?:^|\n)([A-Z][A-Z\s]{3,}:)',                  # "PAYMENT TERMS:"
        ]
        
        sections = {}
        for pattern in section_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                section_name = match.strip().rstrip(':.')
                # Find content after this section until next section
                start_idx = text.find(match)
                if start_idx >= 0:
                    # Simple extraction - content after section header
                    content_start = start_idx + len(match)
                    content_end = content_start + 2000  # Limit content length
                    sections[section_name] = text[content_start:content_end].strip()[:500]
        
        return sections


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_pages_estimate(text: str, words_per_page: int = 500) -> int:
    """Estimate number of pages based on word count."""
    return max(1, count_words(text) // words_per_page)