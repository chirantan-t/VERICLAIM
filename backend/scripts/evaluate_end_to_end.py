import os
import json
from app.services.analysis_service import AnalysisService
from app.services.document_service import DocumentService

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed"))

def run():
    doc_service = DocumentService()
    analysis_service = AnalysisService()
    
    pdfs = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    if not pdfs:
        print("No PDFs found for end to end test.")
        return
        
    pdf_path = os.path.join(DATA_DIR, pdfs[0])
    print(f"Running end-to-end evaluation on {pdf_path}")
    
    doc_id = "test-e2e-doc"
    try:
        res = analysis_service.analyze_document(pdf_path, doc_id, pdfs[0], os.path.getsize(pdf_path))
        print("Analysis completed successfully.")
        
        stats = doc_service.get_statistics(doc_id)
        print("--- End to End Results ---")
        print(f"Number of pages: {res.document.metadata.pages}")
        print(f"Number of references/citations: {len(res.document.references)}")
        print(f"Number of extracted claims: {len(res.document.claims)}")
        print(f"Number of verifiable claims: {len(res.results)}")
        
        if stats:
            print(f"Number of supported claims: {stats.claims_supported}")
            print(f"Number of partial claims: {stats.claims_partially_supported}")
            print(f"Number of contradictions: {stats.claims_contradicted}")
            print(f"Number of insufficient-evidence claims: {stats.claims_insufficient}")
        else:
            # Manually count
            supp = part = contra = insuff = 0
            for r in res.results:
                if r.verdict == "SUPPORTED": supp += 1
                elif r.verdict == "PARTIALLY SUPPORTED": part += 1
                elif r.verdict == "CONTRADICTED": contra += 1
                else: insuff += 1
            print(f"Number of supported claims: {supp}")
            print(f"Number of partial claims: {part}")
            print(f"Number of contradictions: {contra}")
            print(f"Number of insufficient-evidence claims: {insuff}")
            
    except Exception as e:
        print(f"Error during E2E test: {e}")

if __name__ == "__main__":
    run()
