#!/usr/bin/env python3
"""
Юнит-тесты для проверки transparency анализа
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from annex4ac.review import analyze_text

def test_lack_of_transparency():
    """Тест: 'lack of transparency' не должен возвращать ошибку"""
    
    # Текст с "lack of transparency" - это нормальное утверждение
    text = """
    This AI system lacks transparency in its decision-making process.
    The system does not provide clear explanations for its outputs.
    """
    
    issues = analyze_text(text, "test_doc.pdf")
    
    # Проверяем, что нет ошибок связанных с "lack of transparency"
    transparency_errors = [
        issue for issue in issues 
        if "lack of transparency" in issue["message"].lower() or
           "transparency" in issue["message"].lower() and issue["type"] == "error"
    ]
    
    assert len(transparency_errors) == 0, f"Found unexpected transparency errors: {transparency_errors}"

def test_negated_transparency_is_warning():
    """Тест: отрицание transparency должно быть warning, не error"""
    
    text = """
    This system does not provide transparency.
    No transparency measures are implemented.
    """
    
    issues = analyze_text(text, "test_doc.pdf")
    
    # Проверяем, что отрицания transparency - это warnings, не errors
    transparency_issues = [
        issue for issue in issues 
        if "transparency" in issue["message"].lower()
    ]
    
    for issue in transparency_issues:
        assert issue["type"] == "warning", f"Transparency negation should be warning, got {issue['type']}: {issue['message']}"

def test_positive_transparency_is_ok():
    """Тест: положительные упоминания transparency не должны вызывать ошибки"""
    
    text = """
    This AI system provides full transparency.
    Transparency measures include detailed explanations.
    """
    
    issues = analyze_text(text, "test_doc.pdf")
    
    # Проверяем, что нет ошибок связанных с transparency
    transparency_errors = [
        issue for issue in issues 
        if "transparency" in issue["message"].lower() and issue["type"] == "error"
    ]
    
    assert len(transparency_errors) == 0, f"Found unexpected transparency errors: {transparency_errors}"

if __name__ == "__main__":
    pytest.main([__file__]) 