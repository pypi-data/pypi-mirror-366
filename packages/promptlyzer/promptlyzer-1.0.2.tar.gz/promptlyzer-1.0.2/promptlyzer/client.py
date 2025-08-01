"""
Promptlyzer Client Library

A comprehensive Python client for interacting with the Promptlyzer API.
Provides prompt management, caching, and multi-provider LLM inference capabilities.

Author: Promptlyzer Team
License: MIT
"""

import os
import json
import requests
import time
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from .exceptions import (
    PromptlyzerError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    ServerError,
    RateLimitError
)
from .inference import InferenceManager
from .simple_collector import SimpleDatasetCollector


class PromptlyzerClient:
    """
    Main client for interacting with the Promptlyzer API.
    
    This client provides:
    - API key and JWT authentication support
    - Prompt management with caching
    - Multi-provider LLM inference
    - Connection pooling for better performance
    - Comprehensive error handling
    
    Example:
        >>> client = PromptlyzerClient(api_key="pk_live_...")
        >>> prompt = client.get_prompt("project-id", "greeting")
        >>> print(prompt['content'])
    """
    
    def __init__(
        self,
        api_url: str = None,
        api_key: str = None,
        environment: str = "dev",
        cache_ttl_minutes: int = 5,
        max_pool_connections: int = 10
    ):
        """
        Initialize a new PromptlyzerClient.
        
        Args:
            api_url: The URL of the Promptlyzer API.
            api_key: API key for authentication (required).
            environment: The prompt environment to use (dev, staging, prod).
            cache_ttl_minutes: Cache time-to-live in minutes. Defaults to 5 minutes.
            max_pool_connections: Maximum number of connections in the pool. Defaults to 10.
        """
        self.api_url = api_url or os.environ.get("PROMPTLYZER_API_URL", "https://api.promptlyzer.com")
        self.api_key = api_key or os.environ.get("PROMPTLYZER_API_KEY")
        self.environment = environment
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.max_pool_connections = max_pool_connections
        
        # Initialize cache
        self._cache = {}
        
        # Initialize session for connection pooling
        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=self.max_pool_connections, 
                                              pool_maxsize=self.max_pool_connections)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)
        
        # Async session (initialized on demand)
        self._async_session = None
        
        # Validate API key is provided
        if not self.api_key:
            raise AuthenticationError("API key is required. Set PROMPTLYZER_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize inference manager
        self.inference = InferenceManager(promptlyzer_client=self)
    
    def __del__(self):
        """Cleanup resources on deletion."""
        if hasattr(self, '_session') and self._session:
            self._session.close()
    
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests.
        
        Returns:
            Dict[str, str]: The headers with API key authentication.
        """
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
    
    def _get_cache_key(self, *args) -> str:
        """
        Generate a cache key from the arguments.
        
        Args:
            *args: Arguments to include in the cache key.
            
        Returns:
            str: The cache key.
        """
        return ":".join(str(arg) for arg in args)
    
    def _get_from_cache(self, cache_key: str) -> Tuple[bool, Any]:
        """
        Try to get a value from the cache.
        
        Args:
            cache_key: The cache key.
            
        Returns:
            Tuple[bool, Any]: A tuple of (is_cached, value).
                If is_cached is False, value will be None.
        """
        if cache_key not in self._cache:
            return False, None
            
        cached_item = self._cache[cache_key]
        if datetime.now() - cached_item["timestamp"] > self.cache_ttl:
            # Cache expired
            return False, None
            
        return True, cached_item["value"]
    
    def _add_to_cache(self, cache_key: str, value: Any) -> None:
        """
        Add a value to the cache.
        
        Args:
            cache_key: The cache key.
            value: The value to cache.
        """
        self._cache[cache_key] = {
            "value": value,
            "timestamp": datetime.now()
        }
    
    def list_prompts(self, project_id: str, environment: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        List all prompts in a project, returning only their latest versions.
        
        Args:
            project_id: The ID of the project.
            environment: The environment to filter by. Defaults to client's environment.
            use_cache: Whether to use cached results if available. Defaults to True.
            
        Returns:
            Dict[str, Any]: An object containing prompts and total count.
        """
        env = environment or self.environment
        cache_key = self._get_cache_key("list_prompts", project_id, env)
        
        # Try to get from cache if use_cache is True
        if use_cache:
            is_cached, cached_value = self._get_from_cache(cache_key)
            if is_cached:
                return cached_value
        
        # Fixed URL - not using version parameter
        url = f"{self.api_url}/projects/{project_id}/prompts?env={env}"
        headers = self.get_headers()
        
        response = self._make_request("GET", url, headers=headers)
        
        # Cache the results
        self._add_to_cache(cache_key, response)
        
        return response
    
    def get_prompt(self, project_id: str, prompt_name: str, environment: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get a specific prompt by name, returning only the latest version with content directly accessible.
        
        Args:
            project_id: The ID of the project.
            prompt_name: The name of the prompt.
            environment: The environment to get the prompt from. Defaults to client's environment.
            use_cache: Whether to use cached results if available. Defaults to True.
            
        Returns:
            Dict[str, Any]: A simplified prompt object with content directly accessible.
        """
        env = environment or self.environment
        cache_key = self._get_cache_key("get_prompt", project_id, prompt_name, env)
        
        # Try to get from cache if use_cache is True
        if use_cache:
            is_cached, cached_value = self._get_from_cache(cache_key)
            if is_cached:
                return cached_value
        
        # Fixed URL - not using version parameter
        url = f"{self.api_url}/projects/{project_id}/prompts/{prompt_name}?env={env}"
        headers = self.get_headers()
        
        response = self._make_request("GET", url, headers=headers)
        
        # Simplify the response structure to make content directly accessible
        simplified_response = {
            "name": response.get("name"),
            "project_id": project_id,
            "environment": env,
            "version": response.get("current_version"),
            "content": response.get("version", {}).get("content", "")
        }
        
        # Cache the simplified results
        self._add_to_cache(cache_key, simplified_response)
        
        return simplified_response
    
    def get_prompt_content(self, project_id: str, prompt_name: str, environment: Optional[str] = None, use_cache: bool = True) -> str:
        """
        Get only the content of a prompt.
        
        Args:
            project_id: The ID of the project.
            prompt_name: The name of the prompt.
            environment: The environment to get the prompt from. Defaults to client's environment.
            use_cache: Whether to use cached results if available. Defaults to True.
            
        Returns:
            str: The prompt content text.
        """
        prompt_data = self.get_prompt(project_id, prompt_name, environment, use_cache)
        return prompt_data.get("content", "")
    
    def clear_cache(self) -> None:
        """
        Clear the entire cache.
        """
        self._cache = {}
    
    def clear_prompt_cache(self, project_id: str, prompt_name: str = None, environment: Optional[str] = None) -> None:
        """
        Clear cache for a specific prompt or all prompts in a project.
        
        Args:
            project_id: The ID of the project.
            prompt_name: The name of the prompt. If None, clear all prompts in the project.
            environment: The environment to clear. If None, clear client's environment.
        """
        env = environment or self.environment
        
        if prompt_name:
            # Clear specific prompt cache
            get_key = self._get_cache_key("get_prompt", project_id, prompt_name, env)
            if get_key in self._cache:
                del self._cache[get_key]
        else:
            # Clear all prompts in the project
            list_key = self._get_cache_key("list_prompts", project_id, env)
            if list_key in self._cache:
                del self._cache[list_key]
            
            # Also clear specific prompt caches for this project
            keys_to_delete = []
            for key in self._cache:
                if project_id in key and env in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._cache[key]
    
    def _make_request(self, method: str, url: str, headers: Dict[str, str] = None, json_data: Dict[str, Any] = None) -> Any:
        """
        Make a request to the Promptlyzer API using connection pooling.
        
        Args:
            method: The HTTP method to use.
            url: The URL to request.
            headers: The headers to include.
            json_data: The JSON data to send.
            
        Returns:
            Any: The parsed JSON response.
            
        Raises:
            Various PromptlyzerError subclasses depending on the error.
        """
        try:
            response = self._session.request(method, url, headers=headers, json=json_data)
            response.raise_for_status()
            return response.json()
        
        except requests.HTTPError as e:
            return self._handle_request_error(e, e.response)
    
    def _handle_request_error(self, error: requests.HTTPError, response: requests.Response) -> None:
        """
        Handle HTTP errors from the API.
        
        Args:
            error: The HTTPError exception.
            response: The response object.
            
        Raises:
            AuthenticationError: For 401 status codes.
            ResourceNotFoundError: For 404 status codes.
            ValidationError: For 400 and 422 status codes.
            RateLimitError: For 429 status codes.
            ServerError: For 500+ status codes.
            PromptlyzerError: For all other error codes.
        """
        status_code = response.status_code
        
        try:
            error_data = response.json()
            detail = error_data.get("detail", "Unknown error")
        except (ValueError, KeyError):
            detail = response.text or "Unknown error"
        
        if status_code == 401:
            raise AuthenticationError(detail, status_code, response)
        elif status_code == 404:
            raise ResourceNotFoundError(detail, status_code, response)
        elif status_code in (400, 422):
            raise ValidationError(detail, status_code, response)
        elif status_code == 429:
            raise RateLimitError(detail, status_code, response)
        elif status_code >= 500:
            raise ServerError(detail, status_code, response)
        else:
            raise PromptlyzerError(detail, status_code, response)
    
    def configure_inference_provider(self, provider: str, api_key: str, base_url: Optional[str] = None) -> None:
        """
        Configure an inference provider with API key.
        
        Args:
            provider: Provider name (openai, anthropic, together)
            api_key: API key for the provider
            base_url: Optional base URL for the provider
        """
        self.inference.add_provider(provider, api_key, base_url)
    
    def get_inference_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get inference metrics summary from API.
        
        Args:
            days: Number of days to look back (default: 7)
            
        Returns:
            Dict containing metrics summary
        """
        try:
            url = f"{self.api_url}/llm-gateway/metrics/summary?days={days}"
            headers = self.get_headers()
            response = self._make_request("GET", url, headers=headers)
            return response.get("summary", {})
        except Exception:
            # Fallback to local metrics if API fails
            return self.inference.get_metrics_summary()
    
    async def submit_inference_metrics(self) -> None:
        """Submit collected inference metrics to the API."""
        await self.inference.submit_metrics_to_api()