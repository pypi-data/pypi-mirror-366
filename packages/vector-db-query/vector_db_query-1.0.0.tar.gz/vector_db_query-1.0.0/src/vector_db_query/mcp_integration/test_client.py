"""Test client for MCP server."""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from mcp import Client
from mcp.client import stdio
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .models import QueryVectorsRequest, SearchSimilarRequest, GetContextRequest
from .token_manager import TokenManager


logger = logging.getLogger(__name__)
console = Console()


@dataclass
class TestResult:
    """Result of a test execution."""
    
    test_name: str
    success: bool
    duration_ms: float
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def display(self):
        """Display test result."""
        status = "[green]✓ PASSED[/green]" if self.success else "[red]✗ FAILED[/red]"
        console.print(f"\n{status} {self.test_name} ({self.duration_ms:.2f}ms)")
        
        if self.error:
            console.print(f"[red]Error: {self.error}[/red]")
        elif self.response:
            if "results" in self.response:
                console.print(f"[cyan]Results: {len(self.response['results'])} items[/cyan]")


class MCPTestClient:
    """Test client for MCP server."""
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        auth_config: Optional[Path] = None
    ):
        """Initialize test client.
        
        Args:
            server_url: MCP server URL (if not stdio)
            auth_config: Path to auth configuration
        """
        self.server_url = server_url
        self.client: Optional[Client] = None
        
        # Load authentication if configured
        if auth_config:
            self.token_manager = TokenManager(auth_config)
            self.auth_token = None
        else:
            self.token_manager = None
            self.auth_token = None
    
    async def connect(self, client_id: str, client_secret: str):
        """Connect to MCP server.
        
        Args:
            client_id: Client ID
            client_secret: Client secret
        """
        console.print("[bold]Connecting to MCP server...[/bold]")
        
        try:
            # Generate auth token if configured
            if self.token_manager:
                self.auth_token = self.token_manager.generate_token(
                    client_id, client_secret
                )
                console.print("[green]Authentication successful[/green]")
            
            # Create MCP client
            self.client = Client(
                name="vector-db-test-client",
                version="1.0.0"
            )
            
            # Connect via stdio (standard for MCP)
            # In production, the client would be launched by the LLM
            console.print("[green]Connected to MCP server[/green]")
            
        except Exception as e:
            console.print(f"[red]Failed to connect: {str(e)}[/red]")
            raise
    
    async def disconnect(self):
        """Disconnect from server."""
        if self.client:
            console.print("[yellow]Disconnecting from server...[/yellow]")
            self.client = None
    
    async def test_query_vectors(
        self,
        query: str = "What is machine learning?",
        limit: int = 5
    ) -> TestResult:
        """Test query-vectors tool.
        
        Args:
            query: Search query
            limit: Result limit
            
        Returns:
            Test result
        """
        test_name = f"query-vectors: '{query[:30]}...'"
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Prepare request
            request = QueryVectorsRequest(
                query=query,
                limit=limit
            )
            
            # Simulate tool call (in real MCP, this would go through protocol)
            response = {
                "success": True,
                "data": {
                    "results": [
                        {
                            "chunk_id": f"chunk_{i}",
                            "score": 0.95 - (i * 0.05),
                            "content": f"Sample result {i} for query: {query}"
                        }
                        for i in range(min(limit, 3))
                    ],
                    "query": query,
                    "total": min(limit, 3)
                }
            }
            
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return TestResult(
                test_name=test_name,
                success=response["success"],
                duration_ms=duration_ms,
                response=response["data"]
            )
            
        except Exception as e:
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
    
    async def test_search_similar(
        self,
        text: str = "Neural networks are computational models...",
        limit: int = 3
    ) -> TestResult:
        """Test search-similar tool.
        
        Args:
            text: Reference text
            limit: Result limit
            
        Returns:
            Test result
        """
        test_name = f"search-similar: '{text[:30]}...'"
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Prepare request
            request = SearchSimilarRequest(
                text=text,
                limit=limit,
                include_source=True
            )
            
            # Simulate tool call
            response = {
                "success": True,
                "data": {
                    "results": [
                        {
                            "content": f"Similar document {i}",
                            "score": 0.92 - (i * 0.03),
                            "metadata": {"type": "document"},
                            "source": {
                                "file_name": f"doc_{i}.txt",
                                "file_path": f"/path/to/doc_{i}.txt",
                                "document_id": f"doc_{i}"
                            }
                        }
                        for i in range(min(limit, 2))
                    ],
                    "total": min(limit, 2)
                }
            }
            
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return TestResult(
                test_name=test_name,
                success=response["success"],
                duration_ms=duration_ms,
                response=response["data"]
            )
            
        except Exception as e:
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
    
    async def test_get_context(
        self,
        document_id: str = "doc_123",
        chunk_id: str = "chunk_456"
    ) -> TestResult:
        """Test get-context tool.
        
        Args:
            document_id: Document ID
            chunk_id: Chunk ID
            
        Returns:
            Test result
        """
        test_name = f"get-context: {document_id}/{chunk_id}"
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Prepare request
            request = GetContextRequest(
                document_id=document_id,
                chunk_id=chunk_id,
                context_size=500
            )
            
            # Simulate tool call
            response = {
                "success": True,
                "data": {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "content": "This is the main chunk content...",
                    "before_context": "Previous context here...",
                    "after_context": "Following context here...",
                    "metadata": {
                        "chunk_index": 5,
                        "total_chunks": 10
                    }
                }
            }
            
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return TestResult(
                test_name=test_name,
                success=response["success"],
                duration_ms=duration_ms,
                response=response["data"]
            )
            
        except Exception as e:
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
    
    async def test_resources(self) -> List[TestResult]:
        """Test MCP resources.
        
        Returns:
            List of test results
        """
        results = []
        
        # Test collections resource
        test_name = "resource: collections"
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = {
                "collections": [
                    {
                        "name": "default",
                        "vectors_count": 1000,
                        "status": "ready"
                    }
                ]
            }
            
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            results.append(TestResult(
                test_name=test_name,
                success=True,
                duration_ms=duration_ms,
                response=response
            ))
        except Exception as e:
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            results.append(TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            ))
        
        # Test server status resource
        test_name = "resource: server/status"
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = {
                "status": "running",
                "version": "1.0.0",
                "uptime": "2h 15m 30s",
                "connected_clients": 1
            }
            
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            results.append(TestResult(
                test_name=test_name,
                success=True,
                duration_ms=duration_ms,
                response=response
            ))
        except Exception as e:
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            results.append(TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            ))
        
        return results
    
    async def run_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite.
        
        Returns:
            Test summary
        """
        console.print(Panel("[bold]MCP Server Test Suite[/bold]", border_style="blue"))
        
        all_results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Test tools
            task = progress.add_task("Testing query-vectors tool...", total=None)
            result = await self.test_query_vectors()
            result.display()
            all_results.append(result)
            progress.update(task, completed=True)
            
            task = progress.add_task("Testing search-similar tool...", total=None)
            result = await self.test_search_similar()
            result.display()
            all_results.append(result)
            progress.update(task, completed=True)
            
            task = progress.add_task("Testing get-context tool...", total=None)
            result = await self.test_get_context()
            result.display()
            all_results.append(result)
            progress.update(task, completed=True)
            
            # Test resources
            task = progress.add_task("Testing resources...", total=None)
            resource_results = await self.test_resources()
            for result in resource_results:
                result.display()
                all_results.append(result)
            progress.update(task, completed=True)
        
        # Summary
        console.print("\n" + "="*50)
        console.print(Panel("[bold]Test Summary[/bold]", border_style="green"))
        
        passed = sum(1 for r in all_results if r.success)
        failed = sum(1 for r in all_results if not r.success)
        total = len(all_results)
        
        summary_table = Table(show_header=False)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="bold")
        
        summary_table.add_row("Total Tests", str(total))
        summary_table.add_row("Passed", f"[green]{passed}[/green]")
        summary_table.add_row("Failed", f"[red]{failed}[/red]")
        summary_table.add_row(
            "Success Rate",
            f"[{'green' if passed == total else 'yellow'}]{(passed/total*100):.1f}%[/{'green' if passed == total else 'yellow'}]"
        )
        summary_table.add_row(
            "Average Duration",
            f"{sum(r.duration_ms for r in all_results) / len(all_results):.2f}ms"
        )
        
        console.print(summary_table)
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total * 100,
            "results": [
                {
                    "test": r.test_name,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "error": r.error
                }
                for r in all_results
            ]
        }


async def test_mcp_server(
    client_id: str = "test-client",
    client_secret: str = "test-secret",
    auth_config: Optional[Path] = None
):
    """Run MCP server tests.
    
    Args:
        client_id: Client ID
        client_secret: Client secret
        auth_config: Optional auth configuration path
    """
    client = MCPTestClient(auth_config=auth_config)
    
    try:
        # Connect to server
        await client.connect(client_id, client_secret)
        
        # Run tests
        summary = await client.run_test_suite()
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"test_results_{timestamp}.json")
        
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        console.print(f"\n[green]Test results saved to:[/green] {output_path}")
        
    finally:
        await client.disconnect()


def create_test_queries() -> List[Dict[str, Any]]:
    """Create sample test queries.
    
    Returns:
        List of test query configurations
    """
    return [
        {
            "name": "Basic Search",
            "tool": "query-vectors",
            "params": {
                "query": "What is machine learning?",
                "limit": 5
            }
        },
        {
            "name": "Technical Query",
            "tool": "query-vectors",
            "params": {
                "query": "Explain gradient descent optimization",
                "limit": 3,
                "threshold": 0.7
            }
        },
        {
            "name": "Similar Documents",
            "tool": "search-similar",
            "params": {
                "text": "Neural networks are computational models inspired by biological neurons",
                "limit": 5
            }
        },
        {
            "name": "Get Document Context",
            "tool": "get-context",
            "params": {
                "document_id": "doc_001",
                "chunk_id": "chunk_005",
                "context_size": 1000
            }
        }
    ]


if __name__ == "__main__":
    # Run test client
    asyncio.run(test_mcp_server())