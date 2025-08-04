"""Natural Language Processing extraction for entity recognition and sentiment analysis."""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import spacy
from textblob import TextBlob

from ..utils.logger import get_logger

logger = get_logger(__name__)


class EntityType(Enum):
    """Types of entities we extract."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    MONEY = "money"
    PRODUCT = "product"


class SentimentPolarity(Enum):
    """Sentiment polarity categories."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class Entity:
    """Represents an extracted entity."""
    text: str
    type: EntityType
    start: int
    end: int
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    polarity: SentimentPolarity
    score: float  # -1.0 to 1.0
    subjectivity: float  # 0.0 to 1.0
    sentence_sentiments: List[Dict[str, float]] = None


class NLPExtractor:
    """Extracts entities and analyzes sentiment from text."""
    
    def __init__(self):
        """Initialize NLP extractor with spaCy model."""
        self._nlp = None
        self._load_model()
        
        # Regex patterns for additional entity types
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+?1[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    
    def _load_model(self):
        """Load spaCy model, with fallback to basic model."""
        try:
            # Try to load the preferred model
            import en_core_web_sm
            self._nlp = en_core_web_sm.load()
            logger.info("Loaded spaCy model: en_core_web_sm")
        except ImportError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
            # Create a minimal pipeline for basic functionality
            try:
                self._nlp = spacy.blank("en")
                logger.info("Using blank spaCy model")
            except Exception as e:
                logger.error(f"Failed to create spaCy model: {e}")
                self._nlp = None
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Extract using spaCy if available
        if self._nlp:
            try:
                doc = self._nlp(text)
                
                # Map spaCy entity types to our types
                entity_mapping = {
                    'PERSON': EntityType.PERSON,
                    'ORG': EntityType.ORGANIZATION,
                    'GPE': EntityType.LOCATION,
                    'LOC': EntityType.LOCATION,
                    'DATE': EntityType.DATE,
                    'MONEY': EntityType.MONEY,
                    'PRODUCT': EntityType.PRODUCT
                }
                
                for ent in doc.ents:
                    if ent.label_ in entity_mapping:
                        entities.append(Entity(
                            text=ent.text,
                            type=entity_mapping[ent.label_],
                            start=ent.start_char,
                            end=ent.end_char,
                            confidence=0.8  # SpaCy doesn't provide confidence scores
                        ))
            except Exception as e:
                logger.error(f"SpaCy entity extraction failed: {e}")
        
        # Extract emails using regex
        for match in self.email_pattern.finditer(text):
            entities.append(Entity(
                text=match.group(),
                type=EntityType.EMAIL,
                start=match.start(),
                end=match.end(),
                confidence=1.0
            ))
        
        # Extract phone numbers using regex
        for match in self.phone_pattern.finditer(text):
            entities.append(Entity(
                text=match.group(),
                type=EntityType.PHONE,
                start=match.start(),
                end=match.end(),
                confidence=0.9
            ))
        
        # Extract URLs using regex
        for match in self.url_pattern.finditer(text):
            entities.append(Entity(
                text=match.group(),
                type=EntityType.URL,
                start=match.start(),
                end=match.end(),
                confidence=1.0
            ))
        
        # Remove duplicates
        seen = set()
        unique_entities = []
        for entity in entities:
            key = (entity.text, entity.type, entity.start)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def analyze_sentiment(self, text: str, analyze_sentences: bool = False) -> SentimentResult:
        """Analyze sentiment of text.
        
        Args:
            text: Input text
            analyze_sentences: Whether to analyze individual sentences
            
        Returns:
            Sentiment analysis result
        """
        try:
            blob = TextBlob(text)
            
            # Overall sentiment
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify polarity
            if polarity < -0.6:
                sentiment = SentimentPolarity.VERY_NEGATIVE
            elif polarity < -0.2:
                sentiment = SentimentPolarity.NEGATIVE
            elif polarity < 0.2:
                sentiment = SentimentPolarity.NEUTRAL
            elif polarity < 0.6:
                sentiment = SentimentPolarity.POSITIVE
            else:
                sentiment = SentimentPolarity.VERY_POSITIVE
            
            # Analyze individual sentences if requested
            sentence_sentiments = None
            if analyze_sentences and blob.sentences:
                sentence_sentiments = []
                for sentence in blob.sentences:
                    sent_polarity = sentence.sentiment.polarity
                    sent_subjectivity = sentence.sentiment.subjectivity
                    sentence_sentiments.append({
                        'text': str(sentence),
                        'polarity': sent_polarity,
                        'subjectivity': sent_subjectivity
                    })
            
            return SentimentResult(
                polarity=sentiment,
                score=polarity,
                subjectivity=subjectivity,
                sentence_sentiments=sentence_sentiments
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            # Return neutral sentiment on error
            return SentimentResult(
                polarity=SentimentPolarity.NEUTRAL,
                score=0.0,
                subjectivity=0.0
            )
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text.
        
        Args:
            text: Input text
            max_phrases: Maximum number of phrases to extract
            
        Returns:
            List of key phrases
        """
        if not self._nlp:
            return []
        
        try:
            doc = self._nlp(text)
            
            # Extract noun phrases
            noun_phrases = []
            for chunk in doc.noun_chunks:
                # Filter out very short or very long phrases
                if 2 <= len(chunk.text.split()) <= 5:
                    noun_phrases.append(chunk.text.lower())
            
            # Count frequency
            phrase_freq = {}
            for phrase in noun_phrases:
                phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1
            
            # Sort by frequency and return top phrases
            sorted_phrases = sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)
            return [phrase for phrase, _ in sorted_phrases[:max_phrases]]
            
        except Exception as e:
            logger.error(f"Key phrase extraction failed: {e}")
            return []
    
    def extract_summary_metadata(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing extracted metadata
        """
        # Extract entities
        entities = self.extract_entities(text)
        
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity.type.value
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity.text)
        
        # Remove duplicates in each type
        for entity_type in entities_by_type:
            entities_by_type[entity_type] = list(set(entities_by_type[entity_type]))
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(text)
        
        # Extract key phrases
        key_phrases = self.extract_key_phrases(text)
        
        # Compile metadata
        metadata = {
            'nlp_extraction': {
                'entities': entities_by_type,
                'sentiment': {
                    'polarity': sentiment.polarity.value,
                    'score': sentiment.score,
                    'subjectivity': sentiment.subjectivity
                },
                'key_phrases': key_phrases,
                'statistics': {
                    'total_entities': len(entities),
                    'entity_types': len(entities_by_type),
                    'word_count': len(text.split()),
                    'char_count': len(text)
                }
            }
        }
        
        return metadata


class EmailNLPExtractor(NLPExtractor):
    """Specialized NLP extractor for emails."""
    
    def extract_email_metadata(self, subject: str, body: str, sender: str = None) -> Dict[str, Any]:
        """Extract metadata specific to emails.
        
        Args:
            subject: Email subject
            body: Email body
            sender: Email sender (optional)
            
        Returns:
            Email-specific metadata
        """
        # Combine subject and body for entity extraction
        full_text = f"{subject}\n\n{body}"
        
        # Get base metadata
        metadata = self.extract_summary_metadata(full_text)
        
        # Analyze subject sentiment separately
        subject_sentiment = self.analyze_sentiment(subject)
        metadata['nlp_extraction']['subject_sentiment'] = {
            'polarity': subject_sentiment.polarity.value,
            'score': subject_sentiment.score
        }
        
        # Detect urgency indicators
        urgency_keywords = ['urgent', 'asap', 'immediately', 'critical', 'important', 'priority']
        urgency_score = sum(1 for keyword in urgency_keywords if keyword in full_text.lower())
        metadata['nlp_extraction']['urgency_score'] = min(urgency_score / len(urgency_keywords), 1.0)
        
        # Detect action items
        action_patterns = [
            r'\bplease\s+\w+',
            r'\bcould\s+you\s+\w+',
            r'\bwould\s+you\s+\w+',
            r'\bneed\s+to\s+\w+',
            r'\bmust\s+\w+',
            r'\bshould\s+\w+'
        ]
        action_items = []
        for pattern in action_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            action_items.extend(matches)
        
        metadata['nlp_extraction']['action_items'] = action_items[:5]  # Limit to 5
        metadata['nlp_extraction']['has_action_items'] = len(action_items) > 0
        
        return metadata


class TranscriptNLPExtractor(NLPExtractor):
    """Specialized NLP extractor for meeting transcripts."""
    
    def extract_transcript_metadata(self, transcript: str, speakers: List[str] = None) -> Dict[str, Any]:
        """Extract metadata specific to transcripts.
        
        Args:
            transcript: Meeting transcript text
            speakers: List of speaker names (optional)
            
        Returns:
            Transcript-specific metadata
        """
        # Get base metadata
        metadata = self.extract_summary_metadata(transcript)
        
        # Detect questions
        questions = re.findall(r'[^.!?]*\?', transcript)
        metadata['nlp_extraction']['questions'] = questions[:10]  # Limit to 10
        metadata['nlp_extraction']['question_count'] = len(questions)
        
        # Detect decisions/conclusions
        decision_keywords = ['decided', 'agreed', 'concluded', 'resolved', 'determined']
        decisions = []
        sentences = transcript.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in decision_keywords):
                decisions.append(sentence.strip())
        
        metadata['nlp_extraction']['decisions'] = decisions[:5]  # Limit to 5
        
        # Analyze speaker contributions if available
        if speakers:
            speaker_stats = {}
            for speaker in speakers:
                # Count mentions
                mentions = len(re.findall(rf'\b{re.escape(speaker)}\b', transcript, re.IGNORECASE))
                speaker_stats[speaker] = mentions
            
            metadata['nlp_extraction']['speaker_mentions'] = speaker_stats
        
        # Detect topics discussed
        topic_indicators = ['about', 'regarding', 'concerning', 'discuss', 'talk about']
        topics = []
        for indicator in topic_indicators:
            pattern = rf'{indicator}\s+([^,.?!]+)'
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            topics.extend(matches)
        
        # Clean and deduplicate topics
        topics = list(set([topic.strip().lower() for topic in topics]))
        metadata['nlp_extraction']['topics'] = topics[:10]  # Limit to 10
        
        return metadata


# Factory function to get appropriate extractor
def get_nlp_extractor(content_type: str = "general") -> NLPExtractor:
    """Get appropriate NLP extractor for content type.
    
    Args:
        content_type: Type of content ('email', 'transcript', or 'general')
        
    Returns:
        Appropriate NLP extractor instance
    """
    if content_type == "email":
        return EmailNLPExtractor()
    elif content_type == "transcript":
        return TranscriptNLPExtractor()
    else:
        return NLPExtractor()