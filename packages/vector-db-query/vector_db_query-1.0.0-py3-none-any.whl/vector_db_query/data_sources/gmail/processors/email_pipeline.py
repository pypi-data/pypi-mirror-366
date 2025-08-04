"""Email processing pipeline that combines all processors."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from .base import EmailProcessor
from .content_extractor import ContentExtractor
from .meeting_extractor import MeetingExtractor
from .attachment_processor import AttachmentProcessor
from ....utils.logger import get_logger

logger = get_logger(__name__)


class EmailProcessingPipeline:
    """Main email processing pipeline."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize email processing pipeline.
        
        Config options:
            processors: List of processor names to use
            parallel_processing: Run processors in parallel (default: False)
            continue_on_error: Continue if a processor fails (default: True)
        """
        self.config = config or {}
        self.processors: List[EmailProcessor] = []
        
        # Initialize default processors
        self._init_processors()
    
    def _init_processors(self):
        """Initialize configured processors."""
        # Default processor configuration
        default_processors = {
            'content': ContentExtractor,
            'meeting': MeetingExtractor,
            'attachment': AttachmentProcessor
        }
        
        # Get configured processors or use all by default
        configured_processors = self.config.get('processors', list(default_processors.keys()))
        
        # Create processor instances
        for proc_name in configured_processors:
            if proc_name in default_processors:
                # Get processor-specific config
                proc_config = self.config.get(f'{proc_name}_config', {})
                processor = default_processors[proc_name](proc_config)
                self.processors.append(processor)
                logger.info(f"Initialized processor: {proc_name}")
            else:
                logger.warning(f"Unknown processor: {proc_name}")
    
    def add_processor(self, processor: EmailProcessor):
        """Add a custom processor to the pipeline.
        
        Args:
            processor: EmailProcessor instance
        """
        self.processors.append(processor)
        logger.info(f"Added processor: {processor.name}")
    
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email through the pipeline.
        
        Args:
            email_data: Raw email data
            
        Returns:
            Processed email data
        """
        start_time = datetime.utcnow()
        
        # Add processing metadata
        email_data['processing'] = {
            'started_at': start_time.isoformat(),
            'pipeline_version': '1.0.0',
            'processors_used': []
        }
        
        # Run processors
        if self.config.get('parallel_processing', False):
            email_data = await self._process_parallel(email_data)
        else:
            email_data = await self._process_sequential(email_data)
        
        # Complete processing metadata
        end_time = datetime.utcnow()
        email_data['processing']['completed_at'] = end_time.isoformat()
        email_data['processing']['duration_ms'] = int((end_time - start_time).total_seconds() * 1000)
        
        # Generate summary
        email_data['summary'] = self._generate_summary(email_data)
        
        return email_data
    
    async def _process_sequential(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email sequentially through each processor.
        
        Args:
            email_data: Email data
            
        Returns:
            Processed email data
        """
        for processor in self.processors:
            try:
                logger.debug(f"Running processor: {processor.name}")
                email_data = await processor.run(email_data)
                email_data['processing']['processors_used'].append(processor.name)
                
            except Exception as e:
                logger.error(f"Processor {processor.name} failed: {e}")
                
                if not self.config.get('continue_on_error', True):
                    raise
                
                # Record error but continue
                if 'processing_errors' not in email_data:
                    email_data['processing_errors'] = []
                
                email_data['processing_errors'].append({
                    'processor': processor.name,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return email_data
    
    async def _process_parallel(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email in parallel through processors.
        
        Args:
            email_data: Email data
            
        Returns:
            Processed email data
        """
        # Create tasks for each processor
        tasks = []
        for processor in self.processors:
            task = asyncio.create_task(self._run_processor_safe(processor, email_data.copy()))
            tasks.append((processor.name, task))
        
        # Wait for all tasks
        results = {}
        for proc_name, task in tasks:
            try:
                result = await task
                results[proc_name] = result
                email_data['processing']['processors_used'].append(proc_name)
            except Exception as e:
                logger.error(f"Processor {proc_name} failed: {e}")
                if not self.config.get('continue_on_error', True):
                    raise
        
        # Merge results
        email_data = self._merge_results(email_data, results)
        
        return email_data
    
    async def _run_processor_safe(self, processor: EmailProcessor, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run processor with error handling.
        
        Args:
            processor: Processor to run
            email_data: Email data
            
        Returns:
            Processed data
        """
        try:
            return await processor.run(email_data)
        except Exception as e:
            logger.error(f"Processor {processor.name} failed: {e}")
            raise
    
    def _merge_results(self, base_data: Dict[str, Any], results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results from parallel processing.
        
        Args:
            base_data: Base email data
            results: Results from each processor
            
        Returns:
            Merged data
        """
        # Start with base data
        merged = base_data.copy()
        
        # Merge each processor's results
        for proc_name, result in results.items():
            # Skip if same as input (no changes)
            if result == base_data:
                continue
            
            # Merge top-level keys
            for key, value in result.items():
                if key not in merged:
                    merged[key] = value
                elif isinstance(value, dict) and isinstance(merged[key], dict):
                    # Merge dictionaries
                    merged[key].update(value)
                elif isinstance(value, list) and isinstance(merged[key], list):
                    # Extend lists
                    merged[key].extend(value)
                else:
                    # Override with processor result
                    merged[key] = value
        
        return merged
    
    def _generate_summary(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate email summary from processed data.
        
        Args:
            email_data: Processed email data
            
        Returns:
            Summary dictionary
        """
        summary = {
            'from': email_data.get('headers', {}).get('from', ''),
            'subject': email_data.get('headers', {}).get('subject', ''),
            'date': email_data.get('date', ''),
            'has_attachments': len(email_data.get('attachments', [])) > 0,
            'attachment_count': len(email_data.get('attachments', [])),
            'processed': True
        }
        
        # Add content summary
        content_data = email_data.get('content', {})
        if content_data:
            summary['content_length'] = content_data.get('content_length', 0)
            summary['has_urls'] = len(content_data.get('extracted_entities', {}).get('urls', [])) > 0
            summary['key_phrases'] = len(content_data.get('key_phrases', [])) > 0
        
        # Add meeting summary
        meeting_data = email_data.get('meeting_info', {})
        if meeting_data:
            summary['has_meeting'] = meeting_data.get('has_meeting', False)
            summary['meeting_count'] = len(meeting_data.get('meetings', []))
            
            # Get meeting platforms
            if summary['meeting_count'] > 0:
                platforms = list(set(m.get('platform') for m in meeting_data['meetings']))
                summary['meeting_platforms'] = platforms
        
        # Add attachment summary
        if email_data.get('processed_attachments'):
            att_summary = email_data.get('attachment_summary', {})
            summary['attachment_categories'] = list(att_summary.get('by_category', {}).keys())
            summary['high_importance_attachments'] = att_summary.get('by_importance', {}).get('high', 0)
        
        # Processing status
        summary['processing_successful'] = len(email_data.get('processing_errors', [])) == 0
        summary['processors_run'] = len(email_data.get('processing', {}).get('processors_used', []))
        
        return summary
    
    async def process_batch(self, emails: List[Dict[str, Any]], max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Process multiple emails with concurrency control.
        
        Args:
            emails: List of email data
            max_concurrent: Maximum concurrent processing
            
        Returns:
            List of processed emails
        """
        logger.info(f"Processing batch of {len(emails)} emails")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(email):
            async with semaphore:
                return await self.process_email(email)
        
        # Process all emails
        tasks = [process_with_semaphore(email) for email in emails]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results
        processed_emails = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process email {i}: {result}")
                # Return original with error
                email = emails[i].copy()
                email['processing_error'] = str(result)
                processed_emails.append(email)
            else:
                processed_emails.append(result)
        
        logger.info(f"Processed {len(processed_emails)} emails")
        return processed_emails