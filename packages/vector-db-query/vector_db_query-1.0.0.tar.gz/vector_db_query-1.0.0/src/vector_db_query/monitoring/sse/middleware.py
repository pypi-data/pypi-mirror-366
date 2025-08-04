"""
SSE middleware for web framework integration.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

try:
    from fastapi import Request, Response
    from fastapi.responses import StreamingResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from .models import SSEConnection, EventFilter, SSEEventType
from .manager import SSEManager

logger = logging.getLogger(__name__)


class SSEMiddleware:
    """
    Middleware for integrating SSE with web frameworks.
    
    Provides easy integration with FastAPI, Streamlit, and other frameworks.
    """
    
    def __init__(self, sse_manager: SSEManager):
        """
        Initialize SSE middleware.
        
        Args:
            sse_manager: SSE manager instance
        """
        self.sse_manager = sse_manager
        
        logger.info("SSEMiddleware initialized")
    
    # FastAPI Integration
    if FASTAPI_AVAILABLE:
        
        def create_fastapi_endpoint(
            self,
            path: str = "/events",
            event_filter: Optional[EventFilter] = None
        ) -> Callable:
            """
            Create a FastAPI SSE endpoint.
            
            Args:
                path: Endpoint path
                event_filter: Default event filter
                
            Returns:
                FastAPI endpoint function
            """
            
            async def sse_endpoint(request: Request):
                """FastAPI SSE endpoint."""
                # Extract client information
                client_ip = request.client.host if request.client else "unknown"
                user_agent = request.headers.get("user-agent", "unknown")
                
                # Create connection
                connection_id = await self.sse_manager.create_connection(
                    client_ip=client_ip,
                    user_agent=user_agent,
                    client_info={
                        'headers': dict(request.headers),
                        'query_params': dict(request.query_params)
                    }
                )
                
                logger.info(f"FastAPI SSE connection established: {connection_id}")
                
                # Create streaming response
                return StreamingResponse(
                    self.sse_manager.get_event_stream(connection_id, event_filter),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no",  # Disable nginx buffering
                    }
                )
            
            return sse_endpoint
        
        def add_to_fastapi_app(
            self,
            app,
            path: str = "/events",
            event_filter: Optional[EventFilter] = None
        ):
            """
            Add SSE endpoint to a FastAPI application.
            
            Args:
                app: FastAPI application
                path: Endpoint path
                event_filter: Default event filter
            """
            endpoint = self.create_fastapi_endpoint(path, event_filter)
            app.get(path)(endpoint)
            
            logger.info(f"Added FastAPI SSE endpoint at {path}")
    
    # Streamlit Integration
    if STREAMLIT_AVAILABLE:
        
        def create_streamlit_component(
            self,
            component_name: str = "sse_events",
            height: int = 400,
            event_filter: Optional[EventFilter] = None
        ):
            """
            Create a Streamlit component for SSE events.
            
            Args:
                component_name: Component name
                height: Component height
                event_filter: Event filter
                
            Returns:
                Streamlit component
            """
            
            # Create HTML for SSE connection
            html_content = f"""
            <div id="{component_name}" style="height: {height}px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;">
                <div id="events-container"></div>
            </div>
            
            <script>
            (function() {{
                const container = document.getElementById('events-container');
                const eventSource = new EventSource('/events');
                
                eventSource.onmessage = function(event) {{
                    const eventData = JSON.parse(event.data);
                    const eventDiv = document.createElement('div');
                    eventDiv.className = 'sse-event';
                    eventDiv.innerHTML = `
                        <div style="margin-bottom: 10px; padding: 5px; background: #f0f0f0; border-radius: 3px;">
                            <strong>${{eventData.event_type || 'event'}}</strong> - ${{eventData.timestamp}}
                            <div style="margin-top: 5px; font-size: 0.9em;">
                                ${{JSON.stringify(eventData, null, 2)}}
                            </div>
                        </div>
                    `;
                    
                    container.appendChild(eventDiv);
                    container.scrollTop = container.scrollHeight;
                    
                    // Keep only last 100 events
                    while (container.children.length > 100) {{
                        container.removeChild(container.firstChild);
                    }}
                }};
                
                eventSource.onerror = function(event) {{
                    const errorDiv = document.createElement('div');
                    errorDiv.style.color = 'red';
                    errorDiv.textContent = 'Connection error. Attempting to reconnect...';
                    container.appendChild(errorDiv);
                }};
            }})();
            </script>
            """
            
            return st.components.v1.html(html_content, height=height + 50)
        
        def display_sse_events(
            self,
            title: str = "Real-time Events",
            max_events: int = 20,
            event_filter: Optional[EventFilter] = None
        ):
            """
            Display SSE events in Streamlit.
            
            Args:
                title: Display title
                max_events: Maximum events to show
                event_filter: Event filter
            """
            st.subheader(title)
            
            # Create placeholder for events
            events_placeholder = st.empty()
            
            # Get recent events
            try:
                recent_events = asyncio.run(
                    self.sse_manager.get_recent_events(max_events)
                )
                
                if recent_events:
                    events_text = ""
                    for event in reversed(recent_events[-max_events:]):
                        timestamp = event.get('timestamp', 'Unknown')
                        event_type = event.get('event_type', 'unknown')
                        data = event.get('data', {})
                        
                        events_text += f"**{event_type}** - {timestamp}\n"
                        events_text += f"```json\n{data}\n```\n\n"
                    
                    events_placeholder.markdown(events_text)
                else:
                    events_placeholder.write("No recent events")
            
            except Exception as e:
                st.error(f"Error loading events: {str(e)}")
    
    # Generic Integration Helpers
    
    async def create_webhook_handler(
        self,
        webhook_url: str,
        event_types: Optional[list] = None
    ) -> str:
        """
        Create a webhook handler that forwards SSE events to an external URL.
        
        Args:
            webhook_url: Target webhook URL
            event_types: Event types to forward
            
        Returns:
            Handler ID
        """
        import aiohttp
        import json
        
        handler_id = f"webhook_{datetime.now().timestamp()}"
        
        async def webhook_sender(event):
            """Send event to webhook."""
            if event_types and event.event_type not in event_types:
                return
            
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        'event_type': event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
                        'data': event.data,
                        'timestamp': event.timestamp.isoformat(),
                        'event_id': event.event_id
                    }
                    
                    async with session.post(webhook_url, json=payload) as response:
                        if response.status >= 400:
                            logger.warning(f"Webhook {webhook_url} returned {response.status}")
            
            except Exception as e:
                logger.error(f"Error sending webhook to {webhook_url}: {str(e)}")
        
        # Add event listener
        self.sse_manager.add_event_listener(webhook_sender)
        
        logger.info(f"Created webhook handler {handler_id} for {webhook_url}")
        return handler_id
    
    def create_event_logger(
        self,
        log_file: str,
        event_types: Optional[list] = None,
        log_format: str = "json"
    ):
        """
        Create an event logger that writes SSE events to a file.
        
        Args:
            log_file: Log file path
            event_types: Event types to log
            log_format: Log format (json, text)
        """
        import json
        from pathlib import Path
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        def event_logger(event):
            """Log event to file."""
            if event_types and event.event_type not in event_types:
                return
            
            try:
                with log_path.open('a') as f:
                    if log_format == "json":
                        log_entry = {
                            'timestamp': event.timestamp.isoformat(),
                            'event_type': event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
                            'data': event.data,
                            'event_id': event.event_id
                        }
                        f.write(json.dumps(log_entry) + "\n")
                    
                    else:  # text format
                        f.write(f"[{event.timestamp}] {event.event_type}: {event.data}\n")
            
            except Exception as e:
                logger.error(f"Error logging event to {log_file}: {str(e)}")
        
        # Add event listener
        self.sse_manager.add_event_listener(event_logger)
        
        logger.info(f"Created event logger for {log_file}")
    
    def create_console_logger(
        self,
        event_types: Optional[list] = None,
        verbose: bool = False
    ):
        """
        Create a console logger for SSE events.
        
        Args:
            event_types: Event types to log
            verbose: Whether to log full event data
        """
        
        def console_logger(event):
            """Log event to console."""
            if event_types and event.event_type not in event_types:
                return
            
            event_type = event.event_type.value if hasattr(event.event_type, 'value') else event.event_type
            
            if verbose:
                logger.info(f"SSE Event [{event_type}]: {event.data}")
            else:
                data_summary = str(event.data)[:100] + "..." if len(str(event.data)) > 100 else str(event.data)
                logger.info(f"SSE Event [{event_type}]: {data_summary}")
        
        # Add event listener
        self.sse_manager.add_event_listener(console_logger)
        
        logger.info("Created console event logger")
    
    async def test_connection(self, duration: int = 10) -> Dict[str, Any]:
        """
        Test SSE connection by creating a temporary connection and sending test events.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            Test results
        """
        test_results = {
            'start_time': datetime.now().isoformat(),
            'duration_seconds': duration,
            'events_sent': 0,
            'events_received': 0,
            'errors': [],
            'success': False
        }
        
        try:
            # Create test connection
            connection_id = await self.sse_manager.create_connection(
                client_ip="127.0.0.1",
                user_agent="SSE Test Client",
                client_info={'test': True}
            )
            
            # Send test events
            for i in range(duration):
                test_event = {
                    'test_number': i + 1,
                    'message': f'Test event {i + 1}',
                    'timestamp': datetime.now().isoformat()
                }
                
                await self.sse_manager.send_to_connection(
                    connection_id,
                    test_event,
                    SSEEventType.CUSTOM
                )
                
                test_results['events_sent'] += 1
                await asyncio.sleep(1)
            
            # Disconnect
            await self.sse_manager.disconnect_connection(connection_id)
            
            test_results['success'] = True
            test_results['end_time'] = datetime.now().isoformat()
        
        except Exception as e:
            test_results['errors'].append(str(e))
            logger.error(f"SSE test failed: {str(e)}")
        
        return test_results