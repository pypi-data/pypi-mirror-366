"""Fireflies transcript processing pipeline."""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from ...utils.logger import get_logger
from ..models import ProcessedDocument
from ..nlp_extraction import get_nlp_extractor, TranscriptNLPExtractor

logger = get_logger(__name__)


class FirefliesTranscriptProcessor:
    """Process Fireflies meeting transcripts for knowledge base storage."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize processor.
        
        Args:
            output_dir: Directory to save processed transcripts
        """
        self.output_dir = output_dir or Path("knowledge_base/meetings/fireflies")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize NLP extractor for transcripts
        self.nlp_extractor = get_nlp_extractor('transcript')
    
    def process_transcript(self, transcript: 'FirefliesTranscript') -> ProcessedDocument:
        """Process a Fireflies transcript into knowledge base format.
        
        Args:
            transcript: FirefliesTranscript object
            
        Returns:
            ProcessedDocument ready for embedding
        """
        try:
            # Extract metadata
            metadata = self._extract_metadata(transcript)
            
            # Format transcript with speaker diarization
            formatted_content = self._format_transcript(transcript)
            
            # Extract structured information
            structured_data = self._extract_structured_data(transcript)
            
            # Perform NLP extraction
            nlp_metadata = self._perform_nlp_extraction(transcript, formatted_content)
            
            # Create filename
            filename = self._generate_filename(transcript)
            file_path = self.output_dir / filename
            
            # Save to disk
            self._save_transcript(file_path, formatted_content, metadata)
            
            # Create processed document
            doc = ProcessedDocument(
                source_id=f"fireflies_{transcript.id}",
                source_type="fireflies",
                title=transcript.title,
                content=formatted_content,
                metadata={
                    **metadata,
                    **structured_data,
                    **nlp_metadata
                },
                file_path=str(file_path),
                processed_at=datetime.utcnow(),
                embedding_status="pending"
            )
            
            logger.info(f"Processed Fireflies transcript: {transcript.title}")
            return doc
            
        except Exception as e:
            logger.error(f"Failed to process transcript {transcript.id}: {e}")
            raise
    
    def _extract_metadata(self, transcript: 'FirefliesTranscript') -> Dict[str, Any]:
        """Extract metadata from transcript.
        
        Args:
            transcript: FirefliesTranscript object
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "meeting_id": transcript.id,
            "meeting_date": transcript.date.isoformat(),
            "duration_seconds": transcript.duration,
            "duration_minutes": transcript.duration // 60,
            "participants": transcript.participants,
            "participant_count": len(transcript.participants),
            "platform": transcript.platform or "Unknown",
            "host_email": transcript.host_email,
            "has_audio": bool(transcript.audio_url),
            "has_video": bool(transcript.video_url),
            "meeting_url": transcript.meeting_url
        }
        
        # Add meeting type detection
        title_lower = transcript.title.lower()
        if any(term in title_lower for term in ["standup", "stand-up", "daily"]):
            metadata["meeting_type"] = "standup"
        elif any(term in title_lower for term in ["1:1", "one-on-one", "1-on-1"]):
            metadata["meeting_type"] = "one_on_one"
        elif any(term in title_lower for term in ["review", "retro", "retrospective"]):
            metadata["meeting_type"] = "review"
        elif any(term in title_lower for term in ["planning", "sprint"]):
            metadata["meeting_type"] = "planning"
        elif any(term in title_lower for term in ["interview", "screening"]):
            metadata["meeting_type"] = "interview"
        else:
            metadata["meeting_type"] = "general"
        
        return metadata
    
    def _format_transcript(self, transcript: 'FirefliesTranscript') -> str:
        """Format transcript with speaker diarization preserved.
        
        Args:
            transcript: FirefliesTranscript object
            
        Returns:
            Formatted transcript text
        """
        lines = []
        
        # Add header
        lines.append(f"# {transcript.title}")
        lines.append(f"Date: {transcript.date.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append(f"Duration: {transcript.duration // 60} minutes")
        lines.append(f"Participants: {', '.join(transcript.participants)}")
        
        if transcript.platform:
            lines.append(f"Platform: {transcript.platform}")
        
        lines.append("\n---\n")
        
        # Add summary if available
        if transcript.summary:
            lines.append("## Summary")
            lines.append(transcript.summary)
            lines.append("")
        
        # Add action items if available
        if transcript.action_items:
            lines.append("## Action Items")
            for item in transcript.action_items:
                lines.append(f"- {item}")
            lines.append("")
        
        # Add transcript
        lines.append("## Transcript")
        lines.append(transcript.transcript_text)
        
        return "\n".join(lines)
    
    def _extract_structured_data(self, transcript: 'FirefliesTranscript') -> Dict[str, Any]:
        """Extract structured data from transcript.
        
        Args:
            transcript: FirefliesTranscript object
            
        Returns:
            Dictionary of extracted data
        """
        structured = {}
        
        # Extract decisions
        decisions = self._extract_decisions(transcript.transcript_text)
        if decisions:
            structured["decisions"] = decisions
        
        # Extract questions
        questions = self._extract_questions(transcript.transcript_text)
        if questions:
            structured["questions"] = questions
            structured["question_count"] = len(questions)
        
        # Extract mentions
        mentions = self._extract_mentions(transcript.transcript_text)
        if mentions:
            structured["mentions"] = list(mentions)
        
        # Extract links/URLs
        urls = self._extract_urls(transcript.transcript_text)
        if urls:
            structured["referenced_urls"] = urls
        
        # Speaker statistics
        speaker_stats = self._calculate_speaker_stats(transcript.transcript_text)
        if speaker_stats:
            structured["speaker_stats"] = speaker_stats
        
        return structured
    
    def _extract_decisions(self, text: str) -> List[str]:
        """Extract decisions from transcript.
        
        Args:
            text: Transcript text
            
        Returns:
            List of decisions
        """
        decisions = []
        
        # Common decision patterns
        decision_patterns = [
            r"(?:we|I|they?)\s+(?:will|'ll|are going to|decided to|agreed to)\s+(.+?)(?:\.|$)",
            r"(?:decision|agreed|decided):\s*(.+?)(?:\.|$)",
            r"(?:let's|let us)\s+(.+?)(?:\.|$)"
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            decisions.extend([m.strip() for m in matches if len(m.strip()) > 10])
        
        # Deduplicate
        return list(dict.fromkeys(decisions))[:10]  # Limit to top 10
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from transcript.
        
        Args:
            text: Transcript text
            
        Returns:
            List of questions
        """
        # Simple question extraction
        questions = re.findall(r"([^.!?]*\?)", text)
        
        # Filter out very short questions
        questions = [q.strip() for q in questions if len(q.strip()) > 10]
        
        # Remove speaker names if present
        cleaned_questions = []
        for q in questions:
            if ":" in q:
                q = q.split(":", 1)[1].strip()
            cleaned_questions.append(q)
        
        return cleaned_questions
    
    def _extract_mentions(self, text: str) -> set:
        """Extract @mentions and names from transcript.
        
        Args:
            text: Transcript text
            
        Returns:
            Set of mentioned names
        """
        mentions = set()
        
        # Extract @mentions
        at_mentions = re.findall(r"@(\w+)", text)
        mentions.update(at_mentions)
        
        # Extract names after common patterns
        name_patterns = [
            r"(?:thanks|thank you)\s+(\w+)",
            r"(\w+)\s+(?:said|mentioned|suggested|asked)",
            r"(?:hey|hi)\s+(\w+)"
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            mentions.update([m for m in matches if len(m) > 2])
        
        return mentions
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from transcript.
        
        Args:
            text: Transcript text
            
        Returns:
            List of URLs
        """
        # URL pattern
        url_pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"
        urls = re.findall(url_pattern, text)
        
        # Deduplicate
        return list(dict.fromkeys(urls))
    
    def _calculate_speaker_stats(self, text: str) -> Dict[str, Any]:
        """Calculate speaker statistics.
        
        Args:
            text: Transcript text with speaker labels
            
        Returns:
            Speaker statistics
        """
        stats = {}
        
        # Extract speaker turns
        speaker_pattern = r"^([^:]+):"
        speakers = re.findall(speaker_pattern, text, re.MULTILINE)
        
        if speakers:
            # Count turns per speaker
            from collections import Counter
            speaker_counts = Counter(speakers)
            
            stats["speaker_turns"] = dict(speaker_counts)
            stats["most_active_speaker"] = speaker_counts.most_common(1)[0][0]
            stats["total_turns"] = len(speakers)
        
        return stats
    
    def _generate_filename(self, transcript: 'FirefliesTranscript') -> str:
        """Generate filename for transcript.
        
        Args:
            transcript: FirefliesTranscript object
            
        Returns:
            Filename string
        """
        # Clean title for filename
        clean_title = re.sub(r"[^\w\s-]", "", transcript.title)
        clean_title = re.sub(r"[-\s]+", "-", clean_title)
        clean_title = clean_title[:50]  # Limit length
        
        # Format date
        date_str = transcript.date.strftime("%Y%m%d_%H%M")
        
        # Include platform if available
        platform = transcript.platform.lower() if transcript.platform else "meeting"
        
        return f"{date_str}_{platform}_{clean_title}_{transcript.id[:8]}.md"
    
    def _perform_nlp_extraction(self, transcript: 'FirefliesTranscript', formatted_content: str) -> Dict[str, Any]:
        """Perform NLP extraction on transcript.
        
        Args:
            transcript: FirefliesTranscript object
            formatted_content: Formatted transcript text
            
        Returns:
            NLP extraction metadata
        """
        try:
            # Use specialized transcript extractor
            if isinstance(self.nlp_extractor, TranscriptNLPExtractor):
                nlp_metadata = self.nlp_extractor.extract_transcript_metadata(
                    transcript=formatted_content,
                    speakers=transcript.participants
                )
            else:
                # Fallback to general extraction
                nlp_metadata = self.nlp_extractor.extract_summary_metadata(formatted_content)
            
            return nlp_metadata
            
        except Exception as e:
            logger.error(f"NLP extraction failed for transcript {transcript.id}: {e}")
            return {
                'nlp_extraction': {
                    'error': str(e),
                    'entities': {},
                    'sentiment': {'polarity': 'neutral', 'score': 0.0}
                }
            }
    
    def _save_transcript(self, file_path: Path, content: str, metadata: Dict[str, Any]) -> None:
        """Save transcript to file.
        
        Args:
            file_path: Path to save file
            content: Transcript content
            metadata: Metadata to include
        """
        # Add metadata header
        full_content = f"<!--\nMetadata:\n"
        for key, value in metadata.items():
            full_content += f"  {key}: {value}\n"
        full_content += "-->\n\n"
        full_content += content
        
        # Save to file
        file_path.write_text(full_content, encoding="utf-8")
        logger.debug(f"Saved transcript to: {file_path}")
    
    def process_batch(self, transcripts: List['FirefliesTranscript']) -> List[ProcessedDocument]:
        """Process multiple transcripts.
        
        Args:
            transcripts: List of FirefliesTranscript objects
            
        Returns:
            List of ProcessedDocument objects
        """
        processed = []
        
        for transcript in transcripts:
            try:
                doc = self.process_transcript(transcript)
                processed.append(doc)
            except Exception as e:
                logger.error(f"Failed to process transcript {transcript.id}: {e}")
                continue
        
        logger.info(f"Processed {len(processed)}/{len(transcripts)} transcripts")
        return processed