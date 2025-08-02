"""
Test multipart handling functions and structured responses.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from annex4ac.review import (
    handle_multipart_review_request,
    handle_text_review_request,
    create_review_response,
    analyze_documents
)


def test_create_review_response():
    """Test creating structured review response."""
    issues = [
        {
            "type": "error",
            "section": "1",
            "file": "doc1.pdf",
            "message": "Missing content for Annex IV section 1 (system overview)."
        },
        {
            "type": "warning",
            "section": None,
            "file": "doc1.pdf",
            "message": "No mention of transparency or explainability."
        }
    ]
    
    processed_files = ["doc1.pdf", "doc2.pdf"]
    
    response = create_review_response(issues, processed_files)
    
    assert response["success"] is True
    assert response["processed_files"] == ["doc1.pdf", "doc2.pdf"]
    assert response["total_files"] == 2
    assert response["issues"] == issues
    assert response["summary"]["total_issues"] == 2
    assert response["summary"]["errors"] == 1
    assert response["summary"]["warnings"] == 1


def test_handle_text_review_request():
    """Test handling text review request."""
    text_content = "This AI system processes personal data indefinitely."
    
    response = handle_text_review_request(text_content, "test.txt")
    
    assert response["success"] is True
    assert response["processed_files"] == ["test.txt"]
    assert response["total_files"] == 1
    assert len(response["issues"]) > 0
    assert "summary" in response


def test_analyze_documents_structured_output():
    """Test that analyze_documents returns structured data."""
    docs_texts = [
        ("doc1.pdf", "This document only has system overview but is missing other required sections."),
        ("doc2.pdf", "This is a high-risk AI system but has no post-market monitoring plan.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Check that issues are structured dictionaries
    assert isinstance(issues, list)
    for issue in issues:
        assert isinstance(issue, dict)
        assert "type" in issue
        assert "section" in issue
        assert "file" in issue
        assert "message" in issue
        assert issue["type"] in ["error", "warning"]
        assert issue["section"] is None or issue["section"] in [str(i) for i in range(1, 10)]


def test_analyze_documents_error_types():
    """Test that missing sections are marked as errors."""
    docs_texts = [
        ("doc1.pdf", "This document only has system overview but is missing other required sections.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should find missing sections as errors
    error_issues = [issue for issue in issues if issue["type"] == "error"]
    assert len(error_issues) > 0
    
    # Check that missing sections have section numbers
    section_errors = [issue for issue in error_issues if issue["section"] is not None]
    assert len(section_errors) > 0


def test_analyze_documents_warning_types():
    """Test that compliance gaps are marked as warnings."""
    docs_texts = [
        ("doc1.pdf", "This AI system processes data but has no mention of transparency or explainability.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should find compliance gaps as warnings
    warning_issues = [issue for issue in issues if issue["type"] == "warning"]
    assert len(warning_issues) > 0


def test_analyze_documents_cross_document_contradictions():
    """Test that cross-document contradictions are marked as errors."""
    docs_texts = [
        ("doc1.pdf", "This is a high-risk AI system."),
        ("doc2.pdf", "This is a minimal-risk AI system.")
    ]
    
    issues = analyze_documents(docs_texts)
    
    # Should find cross-document contradictions as errors
    contradiction_errors = [
        issue for issue in issues 
        if issue["type"] == "error" and "Contradiction" in issue["message"]
    ]
    assert len(contradiction_errors) > 0
    
    # Cross-document issues should have empty file field
    for issue in contradiction_errors:
        assert issue["file"] == ""


def test_multipart_request_validation():
    """Test multipart request validation."""
    headers = {'Content-Type': 'application/json'}  # Wrong content type
    body = b"test"
    
    with pytest.raises(ValueError, match="Content-Type must be multipart/form-data"):
        handle_multipart_review_request(headers, body)


def test_multipart_request_processing():
    """Test multipart request processing with mock data."""
    headers = {'Content-Type': 'multipart/form-data; boundary=test'}
    
    # Create simple multipart body
    boundary = "test"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="files"; filename="test.pdf"\r\n'
    body += b'Content-Type: application/pdf\r\n\r\n'
    body += b"This is test content for AI system analysis."
    body += b'\r\n'
    body += f"--{boundary}--\r\n".encode()
    
    # Mock the PDF processing to avoid actual file operations
    with patch('annex4ac.review.extract_text_from_pdf') as mock_extract:
        mock_extract.return_value = "This AI system processes personal data indefinitely."
        
        response = handle_multipart_review_request(headers, body)
        
        assert response["success"] is True
        assert response["total_files"] == 1
        assert "test.pdf" in response["processed_files"]
        assert len(response["issues"]) > 0


def test_error_handling_in_multipart():
    """Test error handling when PDF processing fails."""
    headers = {'Content-Type': 'multipart/form-data; boundary=test'}
    
    # Create multipart body
    boundary = "test"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="files"; filename="test.pdf"\r\n'
    body += b'Content-Type: application/pdf\r\n\r\n'
    body += b"Test content"
    body += b'\r\n'
    body += f"--{boundary}--\r\n".encode()
    
    # Mock PDF processing to raise an exception
    with patch('annex4ac.review.extract_text_from_pdf') as mock_extract:
        mock_extract.side_effect = Exception("PDF processing failed")
        
        response = handle_multipart_review_request(headers, body)
        
        # Should still return a response, but with error information
        assert response["success"] is True
        assert response["total_files"] == 1
        # The error should be captured in the document text
        assert any("Error extracting text" in issue["message"] for issue in response["issues"]) 