"""
Main VRIN client for interacting with the VRIN Memory Orchestration API.
"""

import os
import json
import time
from typing import Dict, List, Optional, Union, Any
import requests

from .exceptions import (
    VRINError, VRINAuthenticationError, VRINRateLimitError, 
    VRINTimeoutError, VRINValidationError, VRINServerError
)


class VRIN:
    """
    VRIN Memory Orchestration client.
    
    This class provides a simple interface for storing and retrieving knowledge
    using natural language queries, with automatic fact extraction and reasoning.
    
    Example:
        >>> from vrin import VRIN
        >>> vrin = VRIN(api_key="your_api_key")
        >>> vrin.insert("Python is a programming language created by Guido van Rossum")
        >>> facts = vrin.query("What is Python?")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://8gj3mzt6cg.execute-api.us-west-1.amazonaws.com/prod",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the VRIN client.
        
        Args:
            api_key: Your VRIN API key. If not provided, will look for VRIN_API_KEY environment variable.
            base_url: Base URL for the VRIN API. Defaults to production endpoint.
            timeout: Request timeout in seconds. Defaults to 30.
            max_retries: Maximum number of retries for failed requests. Defaults to 3.
        """
        self.api_key = api_key or os.getenv("VRIN_API_KEY")
        if not self.api_key:
            raise VRINAuthenticationError("API key is required. Set VRIN_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"VRIN-Python/{self._get_version()}",
            "Content-Type": "application/json"
        })
    
    def _get_version(self) -> str:
        """Get the package version."""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "0.1.0"
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the VRIN API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request data for POST requests
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            API response as dictionary
            
        Raises:
            VRINError: For various API errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Add headers from kwargs
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        # Special handling for health check (no auth required)
        if endpoint == "/health":
            headers.pop("Authorization", None)
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Handle different response status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise VRINAuthenticationError("Invalid API key", response.status_code)
                elif response.status_code == 429:
                    raise VRINRateLimitError("Rate limit exceeded", response.status_code, response.text)
                elif response.status_code == 408:
                    raise VRINTimeoutError("Request timed out", response.status_code, response.text)
                elif response.status_code >= 500:
                    raise VRINServerError(f"Server error: {response.status_code}", response.status_code, response.text)
                else:
                    # Try to parse error response
                    try:
                        error_data = response.json()
                        error_message = error_data.get("error", f"HTTP {response.status_code}")
                    except:
                        error_message = f"HTTP {response.status_code}: {response.text}"
                    
                    raise VRINError(error_message, response.status_code, response.text)
                    
            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    raise VRINTimeoutError("Request timed out after all retries")
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise VRINError(f"Request failed: {str(e)}")
                time.sleep(2 ** attempt)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the VRIN API.
        
        Returns:
            Health status information including database connectivity.
            
        Example:
            >>> status = vrin.health_check()
            >>> print(status)
            {'status': 'healthy', 'database_status': {'dynamodb': 'connected', 'neptune': 'connected'}}
        """
        return self._make_request("GET", "/health")
    
    def insert(self, text: str) -> Dict[str, Any]:
        """
        Insert knowledge into the system.
        
        The system will automatically extract facts from the provided text,
        handle temporal context, resolve conflicts, and store the information
        in a structured format.
        
        Args:
            text: Natural language text containing knowledge to be stored.
            
        Returns:
            Insertion result with details about extracted and stored facts.
            
        Example:
            >>> result = vrin.insert("Python was created by Guido van Rossum in 1991")
            >>> print(result)
            {'success': True, 'message': 'Inserted 2 knowledge triples', 'extracted_count': 2, 'inserted_count': 2}
        """
        if not text or not text.strip():
            raise VRINValidationError("Text cannot be empty")
        
        data = {"text": text.strip()}
        return self._make_request("POST", "/api/knowledge/insert", data)
    
    def query(self, query: str) -> Dict[str, Any]:
        """
        Query knowledge using natural language.
        
        This method uses the reliable basic query endpoint that returns
        structured facts without LLM processing to avoid timeouts.
        
        Args:
            query: Natural language query to search for relevant knowledge.
            
        Returns:
            Query results with relevant facts and metadata.
            
        Example:
            >>> facts = vrin.query("What is Python?")
            >>> print(facts)
            {'success': True, 'results': [{'facts': [['Python', 'is', 'programming language']], 'fact_count': 1}]}
        """
        if not query or not query.strip():
            raise VRINValidationError("Query cannot be empty")
        
        data = {"query": query.strip()}
        return self._make_request("POST", "/api/knowledge/query-basic", data)
    
    def query_advanced(self, query: str) -> Dict[str, Any]:
        """
        Advanced query with LLM processing (may timeout).
        
        This method uses the advanced query endpoint that includes
        embedding-based search and LLM answer generation. Note that
        this endpoint may timeout due to the complexity of operations.
        
        Args:
            query: Natural language query for advanced processing.
            
        Returns:
            Advanced query results with LLM-generated answers.
            
        Warning:
            This endpoint may timeout for complex queries.
        """
        if not query or not query.strip():
            raise VRINValidationError("Query cannot be empty")
        
        data = {"query": query.strip()}
        return self._make_request("POST", "/api/knowledge/query", data)
    
    def get_knowledge_graph(self) -> Dict[str, Any]:
        """
        Retrieve the knowledge graph for the current user.
        
        Returns:
            Knowledge graph with nodes and edges.
            
        Example:
            >>> graph = vrin.get_knowledge_graph()
            >>> print(f"Graph has {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
        """
        return self._make_request("GET", "/api/knowledge-graph")
    
    def create_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Create a new user account.
        
        Args:
            email: User's email address.
            password: User's password.
            
        Returns:
            User creation result with API key and user information.
            
        Example:
            >>> user = vrin.create_user("user@example.com", "password123")
            >>> print(f"API Key: {user['api_key']}")
        """
        if not email or not password:
            raise VRINValidationError("Email and password are required")
        
        data = {"email": email, "password": password}
        return self._make_request("POST", "/api/auth/signup", data)
    
    def get_facts(self, query: str) -> List[List[str]]:
        """
        Convenience method to get just the facts from a query.
        
        Args:
            query: Natural language query.
            
        Returns:
            List of facts as [subject, predicate, object] triples.
            
        Example:
            >>> facts = vrin.get_facts("What is Python?")
            >>> for fact in facts:
            ...     print(f"{fact[0]} {fact[1]} {fact[2]}")
        """
        response = self.query(query)
        if not response.get("success"):
            raise VRINError(f"Query failed: {response.get('error', 'Unknown error')}")
        
        facts = []
        for result in response.get("results", []):
            facts.extend(result.get("facts", []))
        
        return facts
    
    def insert_multiple(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Insert multiple pieces of knowledge at once.
        
        Args:
            texts: List of text strings to insert.
            
        Returns:
            List of insertion results for each text.
            
        Example:
            >>> texts = [
            ...     "Python is a programming language",
            ...     "React is a JavaScript library",
            ...     "Machine learning is a subset of AI"
            ... ]
            >>> results = vrin.insert_multiple(texts)
        """
        results = []
        for text in texts:
            try:
                result = self.insert(text)
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e), "text": text})
        
        return results
    
    def query_multiple(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Query multiple questions at once.
        
        Args:
            queries: List of query strings.
            
        Returns:
            List of query results for each question.
            
        Example:
            >>> queries = ["What is Python?", "What is React?", "What is machine learning?"]
            >>> results = vrin.query_multiple(queries)
        """
        results = []
        for query in queries:
            try:
                result = self.query(query)
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e), "query": query})
        
        return results 