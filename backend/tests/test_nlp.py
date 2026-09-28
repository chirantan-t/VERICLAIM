import sys
sys.path.append('d:/PROJECTS/VERICLAIM/backend')
from app.nlp.citation_extractor import CitationExtractor
from app.nlp.reference_parser import ReferenceParser
from app.nlp.claim_extractor import ClaimExtractor
from app.nlp.claim_linker import ClaimLinker
from app.schemas.document import Sentence

def test_citation_extractor():
    ce = CitationExtractor()
    text = "Model X improves classification accuracy by 23% [12]. Another point [3, 4] and [5-7]."
    citations = ce.extract_citations(text)
    print("Extracted citations:", citations)
    assert "[12]" in citations
    assert "[3, 4]" in citations
    assert "[5-7]" in citations

def test_reference_parser():
    rp = ReferenceParser()
    raw = "Smith J, Doe A. Deep learning for claims. Journal of NLP, 2020."
    parsed = rp.parse_reference(raw)
    print("Parsed reference:", parsed)
    assert parsed["year"] == 2020
    assert "Smith J" in parsed["authors"][0]
    assert parsed["title"] == "Deep learning for claims"

def test_claim_extraction_and_linking():
    ce = ClaimExtractor()
    cl = ClaimLinker()

    sentences = [
        Sentence(sentence_id="s1", text="This paper improves classification accuracy by 23% [12].", page_number=1, citation_markers=["[12]"]),
        Sentence(sentence_id="s2", text="We used a standard dataset.", page_number=1, citation_markers=[]),
        Sentence(sentence_id="s3", text="Our model outperforms the baseline.", page_number=1, citation_markers=["[2]"]) # 5 words only though
    ]

    claims = ce.extract_claims(sentences)
    assert len(claims) == 1
    assert claims[0].sentence_id == "s1"
    
    linked_claims = cl.link_claims(claims)
    assert len(linked_claims) == 1
    assert linked_claims[0].linked_citations == ["[12]"]
    print("Extracted and linked claims:", linked_claims)

if __name__ == "__main__":
    test_citation_extractor()
    test_reference_parser()
    test_claim_extraction_and_linking()
    print("All NLP tests passed.")
