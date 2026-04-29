import pytest
from nlp_model import keyword_boost, predict_intents

def test_keyword_boost_fees():
    intents = keyword_boost("What are the semester fees?")
    assert "fees" in intents

def test_keyword_boost_multiple():
    intents = keyword_boost("Tell me about the hostel and library")
    assert "hostel" in intents
    assert "library" in intents

def test_keyword_boost_general():
    intents = keyword_boost("hello bot")
    assert "general" in intents

def test_predict_intents_fallback():
    # If text is complete gibberish, it should fallback
    intents = predict_intents("asdjhfkasdhjfk")
    assert "fallback" in intents or len(intents) == 0

def test_predict_intents_keyword_explicit():
    # "scholarship" requires explicit keyword mention
    intents = predict_intents("Tell me about scholarship opportunities")
    assert "scholarship" in intents
