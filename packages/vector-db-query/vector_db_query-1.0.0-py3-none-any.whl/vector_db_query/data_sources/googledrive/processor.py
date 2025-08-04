"""Gemini transcript processing pipeline."""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from ...processors.base import BaseProcessor
from ...utils.logger import get_logger
from .detector import GeminiTranscriptDetector
from ..nlp_extraction import get_nlp_extractor, TranscriptNLPExtractor

logger = get_logger(__name__)


class GeminiTranscriptProcessor(BaseProcessor):
    """Processor for Gemini meeting transcripts with multi-tab structure."""
    
    def __init__(self):
        """Initialize Gemini transcript processor."""
        super().__init__()
        self.detector = GeminiTranscriptDetector()
        self.processed_count = 0
        self.error_count = 0
        
        # Initialize NLP extractor for transcripts
        self.nlp_extractor = get_nlp_extractor('transcript')
    
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process a Gemini transcript.
        
        Args:
            content: Raw transcript content
            metadata: File metadata
            
        Returns:
            Processed document with extracted data
        """
        try:
            # Validate transcript
            validation = self.detector.validate_transcript(content)
            
            if not validation['is_valid']:
                logger.warning(f"Invalid Gemini transcript: {metadata.get('file_name', 'Unknown')}")
                self.error_count += 1
                return {
                    'success': False,
                    'error': 'Not a valid Gemini transcript',
                    'confidence': validation['confidence']
                }
            
            # Extract structured content
            processed_content = self._process_transcript_content(
                content,
                validation['tabs'],
                validation['metadata']
            )
            
            # Perform NLP extraction
            nlp_metadata = await self._perform_nlp_extraction(
                processed_content['full_content'],
                processed_content.get('speakers', [])
            )
            
            # Merge metadata
            enhanced_metadata = {
                **metadata,
                **validation['metadata'],
                **nlp_metadata,
                'processed_at': datetime.utcnow().isoformat(),
                'processor': 'gemini_transcript',
                'confidence': validation['confidence'],
                'tab_count': len(validation['tabs'])
            }
            
            # Create processed document
            result = {
                'success': True,
                'content': processed_content['full_content'],
                'structured_content': processed_content,
                'metadata': enhanced_metadata,
                'warnings': validation.get('warnings', [])
            }
            
            self.processed_count += 1
            logger.info(f"Successfully processed Gemini transcript: {metadata.get('file_name', 'Unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process Gemini transcript: {e}")
            self.error_count += 1
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_transcript_content(self,
                                  content: str,
                                  tabs: List[Dict[str, Any]],
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process and structure transcript content.
        
        Args:
            content: Raw content
            tabs: Detected tabs
            metadata: Extracted metadata
            
        Returns:
            Structured content dictionary
        """
        # Build structured document
        structured = {
            'meeting_title': metadata.get('meeting_title', 'Untitled Meeting'),
            'meeting_date': metadata.get('meeting_date'),
            'participants': metadata.get('participants', []),
            'duration': metadata.get('duration'),
            'tabs': {},
            'full_content': content,
            'summary': None,
            'action_items': [],
            'key_topics': []
        }
        
        # Process each tab
        for tab in tabs:
            tab_name = tab['name']
            tab_content = tab['content']
            
            # Store tab content
            structured['tabs'][tab_name] = {
                'number': tab['tab_number'],
                'content': tab_content,
                'length': len(tab_content),
                'extracted_data': self._extract_tab_data(tab_name, tab_content)
            }
            
            # Extract global information from specific tabs
            if 'summary' in tab_name.lower():
                structured['summary'] = self._extract_summary(tab_content)
            
            elif 'action' in tab_name.lower() or 'todo' in tab_name.lower():
                structured['action_items'].extend(self._extract_action_items(tab_content))
            
            elif 'transcript' in tab_name.lower():
                structured['key_topics'].extend(self._extract_key_topics(tab_content))
        
        # If no summary found, generate from first tab
        if not structured['summary'] and tabs:
            first_content = tabs[0]['content'][:1000]
            structured['summary'] = self._generate_summary(first_content)
        
        return structured
    
    def _extract_tab_data(self, tab_name: str, content: str) -> Dict[str, Any]:
        """Extract specific data based on tab type.
        
        Args:
            tab_name: Name of the tab
            content: Tab content
            
        Returns:
            Extracted data dictionary
        """
        data = {
            'type': 'unknown',
            'items': []
        }
        
        # Determine tab type
        tab_lower = tab_name.lower()
        
        if 'transcript' in tab_lower:
            data['type'] = 'transcript'
            # Extract speaker turns
            speaker_pattern = r'^([A-Z][^:]+):\s*(.+)$'
            for line in content.split('\n'):
                match = re.match(speaker_pattern, line.strip())
                if match:
                    data['items'].append({
                        'speaker': match.group(1),
                        'text': match.group(2)
                    })
        
        elif 'summary' in tab_lower:
            data['type'] = 'summary'
            # Extract bullet points
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith(('•', '-', '*', '►')):
                    data['items'].append(line[1:].strip())
        
        elif 'action' in tab_lower or 'todo' in tab_lower:
            data['type'] = 'actions'
            # Extract action items
            for line in content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                    data['items'].append(self._parse_action_item(line))
        
        elif 'note' in tab_lower:
            data['type'] = 'notes'
            # Keep as paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            data['items'] = paragraphs
        
        return data
    
    def _extract_summary(self, content: str) -> str:
        """Extract meeting summary.
        
        Args:
            content: Summary tab content
            
        Returns:
            Cleaned summary text
        """
        # Remove common headers
        lines = content.split('\n')
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip headers and empty lines
            if not line or line.lower() in ['summary', 'meeting summary', 'overview']:
                continue
            summary_lines.append(line)
        
        return '\n'.join(summary_lines).strip()
    
    def _extract_action_items(self, content: str) -> List[Dict[str, Any]]:
        """Extract action items from content.
        
        Args:
            content: Content possibly containing action items
            
        Returns:
            List of action item dictionaries
        """
        action_items = []
        
        # Common action item patterns
        patterns = [
            r'(?:TODO|Action|Task):\s*(.+)',
            r'\d+\.\s*(.+)',
            r'[•\-\*]\s*(.+)',
            r'(?:^|\n)([A-Z][^:]+):\s*(.+)'  # Person: task
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Try each pattern
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    if len(match.groups()) == 2:
                        # Person: task format
                        action_items.append({
                            'assignee': match.group(1),
                            'task': match.group(2),
                            'raw': line
                        })
                    else:
                        # Regular task format
                        action_items.append({
                            'task': match.group(1),
                            'raw': line
                        })
                    break
        
        return action_items
    
    def _parse_action_item(self, line: str) -> Dict[str, Any]:
        """Parse a single action item line.
        
        Args:
            line: Action item text
            
        Returns:
            Parsed action item
        """
        # Try to extract assignee
        assignee_match = re.match(r'^(.+?):\s*(.+)$', line)
        if assignee_match and len(assignee_match.group(1).split()) <= 3:
            return {
                'assignee': assignee_match.group(1),
                'task': assignee_match.group(2),
                'raw': line
            }
        
        # Try to extract due date
        due_date = None
        date_patterns = [
            r'by (\d{1,2}/\d{1,2}(?:/\d{2,4})?)',
            r'due (\d{1,2}/\d{1,2}(?:/\d{2,4})?)',
            r'before (\w+ \d{1,2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                due_date = match.group(1)
                break
        
        return {
            'task': line.strip('•-* \t'),
            'due_date': due_date,
            'raw': line
        }
    
    def _extract_key_topics(self, content: str) -> List[str]:
        """Extract key topics from transcript.
        
        Args:
            content: Transcript content
            
        Returns:
            List of key topics
        """
        topics = []
        
        # Look for emphasized phrases
        # ALL CAPS phrases (3+ words)
        caps_matches = re.findall(r'\b[A-Z]{3,}(?:\s+[A-Z]{3,})*\b', content)
        topics.extend([m.title() for m in caps_matches if len(m) > 5])
        
        # Quoted phrases
        quote_matches = re.findall(r'"([^"]+)"', content)
        topics.extend([m for m in quote_matches if 5 < len(m) < 50])
        
        # Section headers (lines that are followed by substantive content)
        lines = content.split('\n')
        for i, line in enumerate(lines[:-1]):
            line = line.strip()
            if (line and len(line) < 80 and 
                not line.endswith(('.', '?', '!')) and
                i + 1 < len(lines) and lines[i + 1].strip()):
                topics.append(line)
        
        # Deduplicate while preserving order
        seen = set()
        unique_topics = []
        for topic in topics:
            topic_lower = topic.lower()
            if topic_lower not in seen:
                seen.add(topic_lower)
                unique_topics.append(topic)
        
        return unique_topics[:10]  # Limit to top 10
    
    def _generate_summary(self, content: str) -> str:
        """Generate a basic summary from content.
        
        Args:
            content: Content to summarize
            
        Returns:
            Generated summary
        """
        # Simple extractive summary - first paragraph or first 3 sentences
        sentences = re.split(r'[.!?]+', content)
        summary_sentences = []
        
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Skip very short sentences
                summary_sentences.append(sentence)
        
        if summary_sentences:
            return '. '.join(summary_sentences) + '.'
        else:
            return content[:200] + '...' if len(content) > 200 else content
    
    async def _perform_nlp_extraction(self, content: str, speakers: List[str]) -> Dict[str, Any]:
        """Perform NLP extraction on transcript.
        
        Args:
            content: Transcript content
            speakers: List of speaker names
            
        Returns:
            NLP extraction metadata
        """
        try:
            # Use specialized transcript extractor
            if isinstance(self.nlp_extractor, TranscriptNLPExtractor):
                nlp_metadata = self.nlp_extractor.extract_transcript_metadata(
                    transcript=content,
                    speakers=speakers
                )
            else:
                # Fallback to general extraction
                nlp_metadata = self.nlp_extractor.extract_summary_metadata(content)
            
            return nlp_metadata
            
        except Exception as e:
            logger.error(f"NLP extraction failed: {e}")
            return {
                'nlp_extraction': {
                    'error': str(e),
                    'entities': {},
                    'sentiment': {'polarity': 'neutral', 'score': 0.0}
                }
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'processor': 'gemini_transcript',
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'success_rate': (
                self.processed_count / (self.processed_count + self.error_count)
                if (self.processed_count + self.error_count) > 0
                else 0
            )
        }


class GeminiProcessingPipeline:
    """Complete processing pipeline for Gemini transcripts."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize processing pipeline.
        
        Args:
            output_dir: Directory for processed output
        """
        self.processor = GeminiTranscriptProcessor()
        self.output_dir = output_dir or Path("data/processed/gemini")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_transcript(self,
                               file_data: Dict[str, Any],
                               save_structured: bool = True) -> Dict[str, Any]:
        """Process a single Gemini transcript.
        
        Args:
            file_data: File data including content
            save_structured: Whether to save structured output
            
        Returns:
            Processing result
        """
        try:
            # Extract base metadata
            metadata = {
                'file_id': file_data['id'],
                'file_name': file_data['name'],
                'modified_time': file_data['modifiedTime'],
                'source': 'google_drive'
            }
            
            # Process content
            result = await self.processor.process(
                file_data['content'],
                metadata
            )
            
            if result['success'] and save_structured:
                # Save structured content
                await self._save_structured_output(
                    result['structured_content'],
                    result['metadata']
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _save_structured_output(self,
                                    structured: Dict[str, Any],
                                    metadata: Dict[str, Any]):
        """Save structured output to files.
        
        Args:
            structured: Structured content
            metadata: Document metadata
        """
        try:
            # Generate base filename
            file_id = metadata['file_id']
            timestamp = datetime.fromisoformat(
                metadata['modified_time'].replace('Z', '+00:00')
            ).strftime('%Y%m%d_%H%M')
            
            base_name = f"gemini_{timestamp}_{file_id[:8]}"
            
            # Save full structured markdown
            md_path = self.output_dir / f"{base_name}.md"
            md_content = self._generate_markdown(structured, metadata)
            md_path.write_text(md_content, encoding='utf-8')
            
            # Save summary if available
            if structured.get('summary'):
                summary_path = self.output_dir / f"{base_name}_summary.txt"
                summary_path.write_text(structured['summary'], encoding='utf-8')
            
            # Save action items if available
            if structured.get('action_items'):
                actions_path = self.output_dir / f"{base_name}_actions.md"
                actions_content = self._format_action_items(structured['action_items'])
                actions_path.write_text(actions_content, encoding='utf-8')
            
            logger.info(f"Saved structured output: {base_name}")
            
        except Exception as e:
            logger.error(f"Failed to save structured output: {e}")
    
    def _generate_markdown(self,
                         structured: Dict[str, Any],
                         metadata: Dict[str, Any]) -> str:
        """Generate markdown document from structured content.
        
        Args:
            structured: Structured content
            metadata: Document metadata
            
        Returns:
            Markdown formatted content
        """
        lines = []
        
        # Header
        lines.append(f"# {structured['meeting_title']}")
        lines.append("")
        
        # Metadata section
        lines.append("## Meeting Information")
        if structured.get('meeting_date'):
            lines.append(f"- **Date**: {structured['meeting_date']}")
        if structured.get('duration'):
            lines.append(f"- **Duration**: {structured['duration']}")
        if structured.get('participants'):
            lines.append(f"- **Participants**: {', '.join(structured['participants'])}")
        lines.append(f"- **Source**: Gemini Transcript")
        lines.append(f"- **Confidence**: {metadata.get('confidence', 0):.0%}")
        lines.append("")
        
        # Summary section
        if structured.get('summary'):
            lines.append("## Summary")
            lines.append(structured['summary'])
            lines.append("")
        
        # Key topics
        if structured.get('key_topics'):
            lines.append("## Key Topics")
            for topic in structured['key_topics']:
                lines.append(f"- {topic}")
            lines.append("")
        
        # Action items
        if structured.get('action_items'):
            lines.append("## Action Items")
            for item in structured['action_items']:
                if 'assignee' in item:
                    lines.append(f"- **{item['assignee']}**: {item['task']}")
                else:
                    lines.append(f"- {item['task']}")
                if item.get('due_date'):
                    lines.append(f"  - Due: {item['due_date']}")
            lines.append("")
        
        # Tab contents
        if structured.get('tabs'):
            lines.append("## Meeting Content")
            for tab_name, tab_data in structured['tabs'].items():
                lines.append(f"\n### {tab_name}")
                
                if tab_data['extracted_data']['type'] == 'transcript':
                    # Format as conversation
                    for item in tab_data['extracted_data']['items'][:10]:  # First 10 turns
                        lines.append(f"\n**{item['speaker']}**: {item['text']}")
                    if len(tab_data['extracted_data']['items']) > 10:
                        lines.append(f"\n*... and {len(tab_data['extracted_data']['items']) - 10} more exchanges*")
                
                elif tab_data['extracted_data']['type'] in ['summary', 'actions']:
                    # Format as list
                    for item in tab_data['extracted_data']['items']:
                        if isinstance(item, dict):
                            lines.append(f"- {item.get('task', item.get('raw', str(item)))}")
                        else:
                            lines.append(f"- {item}")
                
                else:
                    # Include first part of content
                    content_preview = tab_data['content'][:500]
                    if len(tab_data['content']) > 500:
                        content_preview += "..."
                    lines.append(content_preview)
        
        # Metadata footer
        lines.append("")
        lines.append("---")
        lines.append(f"*Processed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*")
        lines.append(f"*File ID: {metadata['file_id']}*")
        
        return '\n'.join(lines)
    
    def _format_action_items(self, action_items: List[Dict[str, Any]]) -> str:
        """Format action items as markdown.
        
        Args:
            action_items: List of action items
            
        Returns:
            Markdown formatted action items
        """
        lines = ["# Action Items", ""]
        
        # Group by assignee
        by_assignee = {}
        unassigned = []
        
        for item in action_items:
            if 'assignee' in item:
                assignee = item['assignee']
                if assignee not in by_assignee:
                    by_assignee[assignee] = []
                by_assignee[assignee].append(item)
            else:
                unassigned.append(item)
        
        # Format by assignee
        for assignee, items in sorted(by_assignee.items()):
            lines.append(f"## {assignee}")
            for item in items:
                lines.append(f"- [ ] {item['task']}")
                if item.get('due_date'):
                    lines.append(f"  - Due: {item['due_date']}")
            lines.append("")
        
        # Unassigned items
        if unassigned:
            lines.append("## Unassigned")
            for item in unassigned:
                lines.append(f"- [ ] {item['task']}")
                if item.get('due_date'):
                    lines.append(f"  - Due: {item['due_date']}")
        
        return '\n'.join(lines)