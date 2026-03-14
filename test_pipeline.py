"""
Contract Risk Intelligence - Test Pipeline
Production-ready testing for small business contracts.
"""

from src.extractor import ContractExtractor
from src.processor import ContractProcessor
from src.analyzer import RiskAnalyzer, print_risk_report
import os


def run_full_analysis(pdf_path: str):
    """
    Run complete contract risk analysis pipeline.
    
    Args:
        pdf_path: Path to the contract PDF file
    """
    print("\n🚀 CONTRACT RISK INTELLIGENCE SYSTEM")
    print("=" * 50)
    print("Designed for Small Business Contract Review\n")

    # Step 1: Extract text from PDF
    print("📄 STEP 1: Extracting text from contract...")
    ext = ContractExtractor(pdf_path)
    raw_text = ext.extract_text()
    print(f"   ✅ Extracted {len(raw_text):,} characters from {os.path.basename(pdf_path)}")
    
    # Preview
    print(f"\n   📝 Preview (first 300 chars):")
    print(f"   {raw_text[:300]}...")

    # Step 2: Process into chunks
    print("\n📋 STEP 2: Processing contract...")
    proc = ContractProcessor(chunk_size=1500, chunk_overlap=200)
    chunks = proc.create_chunks(raw_text)
    relevant_chunks = proc.filter_relevant_chunks(chunks)
    print(f"   ✅ Created {len(chunks)} text segments")
    print(f"   ✅ Found {len(relevant_chunks)} high-priority segments with risk keywords")

    # Step 3: Run AI-powered analysis
    print("\n🤖 STEP 3: Running AI Risk Analysis...")
    analyzer = RiskAnalyzer(model_name="google/flan-t5-small", use_ai=True)
    
    # Analyze the full contract
    report = analyzer.analyze_contract(raw_text)
    
    # Print the beautiful report
    print_risk_report(report)
    
    # Return the report for further use (e.g., in Streamlit app)
    return report


def run_demo_analysis():
    """
    Run a demo analysis with sample contract text.
    Useful for testing without a PDF file.
    """
    print("\n🚀 DEMO MODE - Testing with Sample Contract Text")
    print("=" * 50)
    
    # Sample contract text with various risk patterns
    sample_text = """
    SERVICE AGREEMENT
    
    This Agreement is entered into between ABC Corp ("Provider") and Client ("Customer").
    
    1. TERM AND TERMINATION
    This agreement shall automatically renew for successive one-year periods unless 
    either party provides 30 days written notice. Provider may terminate this agreement 
    immediately without cause upon written notice. Upon termination, all fees paid are 
    non-refundable and Customer shall pay any remaining amounts due.
    
    2. LIABILITY AND INDEMNIFICATION
    Customer agrees to indemnify, defend, and hold harmless Provider from all claims, 
    damages, and expenses arising from Customer's use of the Services. Provider's 
    liability shall be unlimited for any damages arising from this agreement. Customer 
    assumes sole risk for all outcomes resulting from use of the Services.
    
    3. INTELLECTUAL PROPERTY
    All work product created under this Agreement shall be considered work made for hire 
    and Customer hereby assigns all intellectual property rights to Provider. Provider 
    grants Customer a non-exclusive, perpetual, irrevocable license to use the deliverables.
    
    4. PAYMENT TERMS
    Customer shall pay all invoices within 15 days. Late payments shall accrue interest 
    at 2% per month. Provider reserves the right to increase prices annually without notice.
    All fees are non-refundable under any circumstances.
    
    5. CONFIDENTIALITY
    Both parties agree to maintain confidentiality of proprietary information indefinitely.
    Either party may share confidential information with third parties without consent for 
    business purposes.
    
    6. NON-COMPETE
    Customer agrees not to engage with any competing business for a period of 3 years 
    following termination. Customer shall not solicit any employees of Provider.
    
    7. DISPUTE RESOLUTION
    Any disputes shall be resolved through binding arbitration. Both parties waive their 
    right to a jury trial. The prevailing party shall be entitled to recover attorney fees.
    Governing law shall be the State of Delaware.
    
    8. DATA PRIVACY
    Provider may collect and process personal data from Customer's end users. Provider may
    share data with third party affiliates for marketing purposes. Data will be retained
    indefinitely unless Customer requests deletion.
    """
    
    print("📄 Analyzing sample contract...")
    
    # Run analysis
    analyzer = RiskAnalyzer(model_name="google/flan-t5-small", use_ai=True)
    report = analyzer.analyze_contract(sample_text)
    
    # Print report
    print_risk_report(report)
    
    return report


if __name__ == "__main__":
    # Check if sample PDF exists
    pdf_path = "data/sample_contract.pdf"
    
    if os.path.exists(pdf_path):
        print("📁 Found sample_contract.pdf - Running full analysis...")
        run_full_analysis(pdf_path)
    else:
        print("📁 No PDF found - Running demo with sample text...")
        print("   (Place a PDF in data/sample_contract.pdf for real analysis)\n")
        run_demo_analysis()
