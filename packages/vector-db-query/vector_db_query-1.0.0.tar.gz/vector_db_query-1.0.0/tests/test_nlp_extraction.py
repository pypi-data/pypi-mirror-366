"""Tests for NLP extraction functionality."""

import pytest
from datetime import datetime

from vector_db_query.data_sources.nlp_extraction import (
    NLPExtractor, Entity, EntityType, SentimentResult, KeyPhrase
)


class TestNLPExtractor:
    """Test NLP extraction functionality."""
    
    @pytest.fixture
    def extractor(self):
        """Create NLP extractor instance."""
        return NLPExtractor()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for testing."""
        return """
        Apple Inc. announced today that Tim Cook will meet with executives from Microsoft 
        and Google at their headquarters in Cupertino, California on January 15, 2024. 
        The meeting will focus on AI collaboration and regulatory compliance. 
        John Smith from the FTC will also attend the meeting.
        """
    
    @pytest.fixture
    def email_text(self):
        """Sample email text."""
        return """
        From: john.doe@techcorp.com
        To: jane.smith@techcorp.com
        Subject: Project Alpha Update
        
        Hi Jane,
        
        I wanted to update you on Project Alpha. We've completed the initial phase 
        and are now moving to beta testing. The team in San Francisco is doing 
        great work. Sarah Johnson will lead the testing phase starting Monday.
        
        Can we schedule a call for tomorrow at 2 PM EST to discuss the timeline?
        
        Best regards,
        John
        """
    
    @pytest.fixture
    def meeting_text(self):
        """Sample meeting transcript."""
        return """
        Meeting: Quarterly Business Review
        Date: January 10, 2024
        Attendees: Mike Wilson (CEO), Lisa Chen (CFO), Robert Brown (CTO)
        
        Mike: Let's start with the financial overview. Lisa, can you share the Q4 results?
        
        Lisa: Absolutely. We exceeded our targets by 15%. Revenue was $45M, up from $39M 
        last quarter. Our biggest growth came from the enterprise segment.
        
        Robert: On the technical side, we launched three new features and improved 
        system performance by 30%. Customer satisfaction scores are at an all-time high.
        
        Mike: Excellent work everyone. Let's aim for 20% growth next quarter. I'll 
        coordinate with the board of directors in New York next week.
        
        Action Items:
        - Lisa to prepare detailed Q1 projections by Friday
        - Robert to present roadmap at the all-hands meeting
        - Mike to update investors by end of month
        """
    
    def test_entity_extraction(self, extractor, sample_text):
        """Test named entity extraction."""
        entities = extractor.extract_entities(sample_text)
        
        # Check for organizations
        org_entities = [e for e in entities if e.type == EntityType.ORGANIZATION]
        org_names = [e.text for e in org_entities]
        assert "Apple Inc." in org_names or "Apple" in org_names
        assert "Microsoft" in org_names
        assert "Google" in org_names
        assert any("FTC" in name for name in org_names)
        
        # Check for people
        person_entities = [e for e in entities if e.type == EntityType.PERSON]
        person_names = [e.text for e in person_entities]
        assert "Tim Cook" in person_names
        assert "John Smith" in person_names
        
        # Check for locations
        location_entities = [e for e in entities if e.type == EntityType.LOCATION]
        location_names = [e.text for e in location_entities]
        assert any("Cupertino" in name for name in location_names)
        assert any("California" in name for name in location_names)
        
        # Check for dates
        date_entities = [e for e in entities if e.type == EntityType.DATE]
        assert len(date_entities) > 0
    
    def test_sentiment_analysis(self, extractor):
        """Test sentiment analysis."""
        # Positive text
        positive_text = "This is absolutely fantastic! I love the new features and the team did an amazing job."
        pos_result = extractor.analyze_sentiment(positive_text)
        assert pos_result.polarity > 0.5
        assert pos_result.label == "positive"
        
        # Negative text
        negative_text = "This is terrible. The service was awful and I'm very disappointed with the results."
        neg_result = extractor.analyze_sentiment(negative_text)
        assert neg_result.polarity < -0.3
        assert neg_result.label == "negative"
        
        # Neutral text
        neutral_text = "The meeting is scheduled for Tuesday at 3 PM in conference room B."
        neu_result = extractor.analyze_sentiment(neutral_text)
        assert -0.1 <= neu_result.polarity <= 0.1
        assert neu_result.label == "neutral"
    
    def test_sentiment_with_sentences(self, extractor):
        """Test sentiment analysis with sentence breakdown."""
        mixed_text = """
        The product launch was incredibly successful! 
        However, we faced some serious challenges with supply chain.
        Overall, I think we did a good job managing the situation.
        """
        
        result = extractor.analyze_sentiment(mixed_text, analyze_sentences=True)
        
        assert result.sentence_sentiments is not None
        assert len(result.sentence_sentiments) >= 3
        
        # First sentence should be positive
        assert result.sentence_sentiments[0]['polarity'] > 0
        
        # Second sentence should be negative
        assert any(s['polarity'] < 0 for s in result.sentence_sentiments)
    
    def test_key_phrase_extraction(self, extractor, sample_text):
        """Test key phrase extraction."""
        phrases = extractor.extract_key_phrases(sample_text)
        
        assert len(phrases) > 0
        
        # Check for expected key phrases
        phrase_texts = [p.text.lower() for p in phrases]
        expected_phrases = ['ai collaboration', 'regulatory compliance', 'meeting']
        
        # At least some expected phrases should be found
        found_phrases = [ep for ep in expected_phrases if any(ep in pt for pt in phrase_texts)]
        assert len(found_phrases) > 0
        
        # Check scores
        for phrase in phrases:
            assert 0 <= phrase.score <= 1
    
    def test_email_extraction(self, extractor, email_text):
        """Test email-specific extraction."""
        result = extractor.extract_from_email(email_text)
        
        # Check entities
        assert len(result['entities']) > 0
        person_names = [e.text for e in result['entities'] if e.type == EntityType.PERSON]
        assert any("Jane" in name for name in person_names)
        assert any("Sarah Johnson" in name for name in person_names)
        
        # Check locations
        location_names = [e.text for e in result['entities'] if e.type == EntityType.LOCATION]
        assert any("San Francisco" in name for name in location_names)
        
        # Check sentiment
        assert result['sentiment'].polarity > 0  # Should be positive
        
        # Check key phrases
        assert len(result['key_phrases']) > 0
        phrase_texts = [p.text.lower() for p in result['key_phrases']]
        assert any("project alpha" in pt for pt in phrase_texts)
        
        # Check metadata
        assert result['metadata']['has_action_request'] is True  # Asking to schedule a call
        assert result['metadata']['urgency_score'] > 0.5  # "tomorrow" indicates urgency
    
    def test_transcript_extraction(self, extractor, meeting_text):
        """Test meeting transcript extraction."""
        result = extractor.extract_from_transcript(meeting_text)
        
        # Check participants
        assert len(result['participants']) >= 3
        participant_names = [p['name'] for p in result['participants']]
        assert "Mike Wilson" in participant_names
        assert "Lisa Chen" in participant_names
        assert "Robert Brown" in participant_names
        
        # Check roles
        roles = {p['name']: p['role'] for p in result['participants']}
        assert roles.get("Mike Wilson") == "CEO"
        assert roles.get("Lisa Chen") == "CFO"
        
        # Check topics
        assert len(result['topics']) > 0
        topic_texts = [t.text.lower() for t in result['topics']]
        assert any("financial" in t or "revenue" in t for t in topic_texts)
        
        # Check action items
        assert len(result['action_items']) == 3
        assert any("Lisa" in item and "projections" in item for item in result['action_items'])
        
        # Check key metrics
        assert len(result['key_metrics']) > 0
        metrics_dict = {m['metric']: m['value'] for m in result['key_metrics']}
        assert "$45M" in metrics_dict.values() or "45M" in str(metrics_dict.values())
        assert any("15%" in str(v) for v in metrics_dict.values())
        
        # Check sentiment by speaker
        assert "Mike Wilson" in result['sentiment_by_speaker']
        assert result['sentiment_by_speaker']["Mike Wilson"]['polarity'] > 0  # Positive tone
    
    def test_entity_confidence(self, extractor):
        """Test entity extraction with confidence scores."""
        text = "Amazon CEO Andy Jassy announced new AWS services."
        entities = extractor.extract_entities(text)
        
        # All entities should have confidence scores
        for entity in entities:
            assert hasattr(entity, 'confidence')
            assert 0 <= entity.confidence <= 1
        
        # Well-known entities should have high confidence
        amazon_entity = next((e for e in entities if "Amazon" in e.text), None)
        if amazon_entity and amazon_entity.confidence:
            assert amazon_entity.confidence > 0.7
    
    def test_empty_text_handling(self, extractor):
        """Test handling of empty or minimal text."""
        # Empty text
        empty_entities = extractor.extract_entities("")
        assert empty_entities == []
        
        empty_sentiment = extractor.analyze_sentiment("")
        assert empty_sentiment.polarity == 0
        assert empty_sentiment.label == "neutral"
        
        # Very short text
        short_text = "OK"
        short_entities = extractor.extract_entities(short_text)
        assert isinstance(short_entities, list)
        
        short_sentiment = extractor.analyze_sentiment(short_text)
        assert isinstance(short_sentiment, SentimentResult)
    
    def test_special_characters_handling(self, extractor):
        """Test handling of special characters and formatting."""
        text_with_special = """
        @JohnDoe mentioned that the Q4 results ($45.5M) exceeded expectations!
        #Success #TeamWork
        
        Contact: john.doe@company.com or call +1-555-0123
        Website: https://www.example.com
        """
        
        entities = extractor.extract_entities(text_with_special)
        assert len(entities) > 0
        
        # Should handle email and monetary values
        all_text = ' '.join([e.text for e in entities])
        assert any(char in all_text for char in ['@', '$', '.'])
    
    def test_multilingual_basics(self, extractor):
        """Test basic multilingual support."""
        # Note: Full multilingual support depends on spaCy model
        spanish_text = "La empresa Apple anunció nuevos productos en Madrid."
        
        # Should not crash
        entities = extractor.extract_entities(spanish_text)
        sentiment = extractor.analyze_sentiment(spanish_text)
        
        assert isinstance(entities, list)
        assert isinstance(sentiment, SentimentResult)
    
    def test_long_text_handling(self, extractor):
        """Test handling of long texts."""
        # Create a long text by repeating content
        base_text = "This is a test sentence with some entities like Google and John Smith. "
        long_text = base_text * 100  # Make it long
        
        # Should handle long text without issues
        entities = extractor.extract_entities(long_text)
        assert len(entities) > 0
        
        # Should find repeated entities
        google_count = sum(1 for e in entities if "Google" in e.text)
        assert google_count > 1
    
    def test_extract_all(self, extractor, sample_text):
        """Test comprehensive extraction."""
        result = extractor.extract_all(sample_text)
        
        assert 'entities' in result
        assert 'sentiment' in result
        assert 'key_phrases' in result
        
        assert len(result['entities']) > 0
        assert isinstance(result['sentiment'], SentimentResult)
        assert len(result['key_phrases']) > 0


class TestModels:
    """Test NLP models."""
    
    def test_entity_model(self):
        """Test Entity model."""
        entity = Entity(
            text="Apple Inc.",
            type=EntityType.ORGANIZATION,
            start=0,
            end=10,
            confidence=0.95
        )
        
        assert entity.text == "Apple Inc."
        assert entity.type == EntityType.ORGANIZATION
        assert entity.start == 0
        assert entity.end == 10
        assert entity.confidence == 0.95
    
    def test_sentiment_result_model(self):
        """Test SentimentResult model."""
        result = SentimentResult(
            polarity=0.8,
            subjectivity=0.6,
            label="positive",
            confidence=0.9,
            sentence_sentiments=[
                {"sentence": "Great!", "polarity": 0.9, "label": "positive"}
            ]
        )
        
        assert result.polarity == 0.8
        assert result.subjectivity == 0.6
        assert result.label == "positive"
        assert result.confidence == 0.9
        assert len(result.sentence_sentiments) == 1
    
    def test_key_phrase_model(self):
        """Test KeyPhrase model."""
        phrase = KeyPhrase(
            text="artificial intelligence",
            score=0.85,
            count=3
        )
        
        assert phrase.text == "artificial intelligence"
        assert phrase.score == 0.85
        assert phrase.count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])