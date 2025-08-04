"""
Test negspaCy integration for advanced contradiction detection.
"""

import pytest
from annex4ac.review import analyze_documents


def test_negspacy_basic_contradiction_detection():
    """Test basic contradiction detection using negspaCy."""
    # Test case: document with both affirmed and negated statements
    docs_texts = [
        ("test.pdf", "No personal data are stored. Personal data are stored for 2 years.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should find contradiction about personal data (now can be warning or error)
    contradiction_issues = [
        issue for issue in issues 
        if "personal data" in issue["message"] and "Contradictory" in issue["message"]
    ]
    
    assert len(contradiction_issues) > 0, "Should find contradiction about personal data"


def test_negspacy_no_false_positive():
    """Test that negspaCy doesn't trigger false positives for simple negations."""
    # Test case: document with only negated statements (no contradiction)
    docs_texts = [
        ("test.pdf", "No personal data are stored. We store system logs only.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should NOT find contradiction since there's no affirmed statement
    contradiction_errors = [
        issue for issue in issues 
        if issue["type"] == "error" and "personal data" in issue["message"] and ("Contradictory" in issue["message"] or "Inconsistent" in issue["message"])
    ]
    
    assert len(contradiction_errors) == 0, "Should not find false positive contradiction"


def test_negspacy_cross_document_contradiction():
    """Test cross-document contradiction detection with negspaCy."""
    docs_texts = [
        ("doc1.pdf", "This is a high-risk AI system."),
        ("doc2.pdf", "This is not a high-risk AI system.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should find cross-document contradiction about high-risk
    contradiction_errors = [
        issue for issue in issues 
        if issue["type"] == "error" and "high-risk" in issue["message"] and "Inconsistent" in issue["message"]
    ]
    
    assert len(contradiction_errors) > 0, "Should find cross-document contradiction about high-risk"


def test_negspacy_multiple_terms():
    """Test contradiction detection for multiple key terms."""
    docs_texts = [
        ("doc1.pdf", "Personal data is stored and monitored. The system is compliant."),
        ("doc2.pdf", "No personal data is stored. The system is not monitored and not compliant.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should find contradictions for multiple terms
    contradiction_errors = [
        issue for issue in issues 
        if issue["type"] == "error" and ("Contradictory" in issue["message"] or "Inconsistent" in issue["message"])
    ]
    
    assert len(contradiction_errors) > 0, "Should find contradictions for multiple terms"


def test_negspacy_fallback_without_spacy():
    """Test that the system falls back to basic detection when spaCy is not available."""
    # Mock spaCy to be unavailable
    import annex4ac.review
    original_spacy_available = annex4ac.review.SPACY_AVAILABLE
    annex4ac.review.SPACY_AVAILABLE = False
    
    try:
        docs_texts = [
            ("test.pdf", "No personal data are stored. Personal data are stored for 2 years.")
        ]
        
        issues = analyze_documents(docs_texts)
        
        # Should still find contradictions using fallback method
        contradiction_errors = [
            issue for issue in issues 
            if issue["type"] == "error" and "personal data" in issue["message"]
        ]
        assert len(contradiction_errors) > 0, "Should find contradictions using fallback method"
    finally:
        # Restore original value
        annex4ac.review.SPACY_AVAILABLE = original_spacy_available


def test_negspacy_complex_negation_patterns():
    """Test complex negation patterns."""
    docs_texts = [
        ("doc1.pdf", "The system stores personal data without consent. Biometric identification is used."),
        ("doc2.pdf", "Personal data is never stored. No biometric identification is performed.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should find contradictions for complex negation patterns
    contradiction_errors = [
        issue for issue in issues 
        if issue["type"] == "error" and ("Contradictory" in issue["message"] or "Inconsistent" in issue["message"])
    ]
    
    assert len(contradiction_errors) > 0, "Should find contradictions for complex negation patterns"


def test_negspacy_no_contradiction_same_stance():
    """Test that no contradiction is found when both documents have the same stance."""
    docs_texts = [
        ("doc1.pdf", "Personal data is stored securely."),
        ("doc2.pdf", "Personal data is also stored with encryption.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should NOT find contradictions when both documents affirm the same thing
    contradiction_errors = [
        issue for issue in issues 
        if issue["type"] == "error" and "personal data" in issue["message"] and ("Contradictory" in issue["message"] or "Inconsistent" in issue["message"])
    ]
    
    assert len(contradiction_errors) == 0, "Should not find contradictions when both documents have the same stance" 