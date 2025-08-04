"""Base email processor interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from ....utils.logger import get_logger

logger = get_logger(__name__)


class EmailProcessor(ABC):
    """Abstract base class for email processors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize processor with optional configuration.
        
        Args:
            config: Processor-specific configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def process(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email data and return enriched/transformed data.
        
        Args:
            email_data: Raw email data
            
        Returns:
            Processed email data
        """
        pass
    
    async def pre_process(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-processing hook, can be overridden.
        
        Args:
            email_data: Email data before processing
            
        Returns:
            Modified email data
        """
        return email_data
    
    async def post_process(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-processing hook, can be overridden.
        
        Args:
            email_data: Email data after processing
            
        Returns:
            Modified email data
        """
        return email_data
    
    async def run(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete processing pipeline.
        
        Args:
            email_data: Raw email data
            
        Returns:
            Fully processed email data
        """
        try:
            # Pre-process
            data = await self.pre_process(email_data)
            
            # Main processing
            data = await self.process(data)
            
            # Post-process
            data = await self.post_process(data)
            
            # Add processing metadata
            if 'processing_metadata' not in data:
                data['processing_metadata'] = {}
            
            data['processing_metadata'][self.name] = {
                'processed_at': datetime.utcnow().isoformat(),
                'processor_version': '1.0.0'
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            # Add error to metadata
            if 'processing_errors' not in email_data:
                email_data['processing_errors'] = []
            
            email_data['processing_errors'].append({
                'processor': self.name,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return email_data