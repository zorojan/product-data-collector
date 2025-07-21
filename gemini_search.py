"""
Gemini AI integration module for product specification search.
This module handles the interaction with Google's Gemini API.
"""

import json
import requests
from typing import Dict, Any, Optional
import streamlit as st
from config import GEMINI_API_ENDPOINT, PRODUCT_SEARCH_PROMPT, SAMPLE_PRODUCTS

class GeminiProductSearcher:
    """Handles product specification search using Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.endpoint = GEMINI_API_ENDPOINT
    
    def search_product(self, query: str, use_demo_mode: bool = None) -> Dict[str, Any]:
        """
        Search for product specifications.
        
        Args:
            query: Product name/model to search for
            use_demo_mode: If True, uses sample data. If None, auto-detect based on API key
            
        Returns:
            Dictionary containing product specifications
        """
        # Auto-detect mode based on API key availability
        if use_demo_mode is None:
            use_demo_mode = not bool(self.api_key)
        
        if use_demo_mode or not self.api_key:
            return self._demo_search(query)
        else:
            return self._real_api_search(query)
    
    def _demo_search(self, query: str) -> Dict[str, Any]:
        """Demo mode using sample data with improved matching."""
        query_lower = query.lower().strip()
        
        # Remove common words that don't help with matching
        query_cleaned = query_lower.replace("monitor", "").replace("laptop", "").replace("phone", "").strip()
        
        # Check for exact matches first
        for key, product in SAMPLE_PRODUCTS.items():
            if key == query_lower or key in query_lower:
                return product
        
        # Check for partial matches with product model/brand
        for key, product in SAMPLE_PRODUCTS.items():
            product_brand = product.get('brand', '').lower()
            product_model = product.get('model', '').lower()
            
            # Check if query contains brand and model parts
            if product_brand in query_lower or product_model in query_lower:
                return product
            
            # Check individual words
            key_words = key.split()
            query_words = query_cleaned.split()
            
            # If any significant word matches
            for query_word in query_words:
                if len(query_word) > 2:  # Skip very short words
                    for key_word in key_words:
                        if query_word in key_word or key_word in query_word:
                            return product
        
        # Special cases for common product searches
        if any(term in query_lower for term in ['dell', 'p2422', '2422']):
            if 'dell p2422h' in SAMPLE_PRODUCTS:
                return SAMPLE_PRODUCTS['dell p2422h']
        
        if any(term in query_lower for term in ['galaxy', 's24', 'samsung']):
            if 'samsung galaxy s24' in SAMPLE_PRODUCTS:
                return SAMPLE_PRODUCTS['samsung galaxy s24']
        
        if any(term in query_lower for term in ['tesla', 'model 3', 'model3']):
            if 'tesla model 3' in SAMPLE_PRODUCTS:
                return SAMPLE_PRODUCTS['tesla model 3']
        
        if any(term in query_lower for term in ['airpods', 'pro', 'earbuds']):
            if 'airpods pro' in SAMPLE_PRODUCTS:
                return SAMPLE_PRODUCTS['airpods pro']
        
        # If still no match, show available products
        available_products = list(SAMPLE_PRODUCTS.keys())
        return {
            "brand": "Unknown",
            "model": query,
            "category": "Product",
            "specifications": {
                "status": "Product not found in demo database",
                "suggestion": f"Try one of these available products: {', '.join(available_products)}",
                "search_tip": "Demo mode supports: iPhone 15 Pro, Sony WH-1000XM5, MacBook Pro M3, Dell P2422H, Samsung Galaxy S24, Tesla Model 3, AirPods Pro",
                "note": "This is demo mode. Connect your Gemini API key for real searches."
            },
            "price_range": "N/A",
            "availability": "Unknown",
            "sources": ["demo-mode"]
        }
    
    def _real_api_search(self, query: str) -> Dict[str, Any]:
        """Real API search using Gemini."""
        if not self.api_key:
            raise ValueError("API key is required for real searches")
        
        prompt = PRODUCT_SEARCH_PROMPT.format(query=query)
        
        headers = {
            "Content-Type": "application/json",
        }
        
        # Add API key to URL
        api_url = f"{self.endpoint}?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048,
            },
            "tools": [{
                "googleSearchRetrieval": {
                    "dynamicRetrievalConfig": {
                        "mode": "MODE_DYNAMIC",
                        "dynamicThreshold": 0.7
                    }
                }
            }]
        }
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the generated content
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Try to parse as JSON
                    try:
                        product_data = json.loads(content)
                        
                        # Add grounding metadata if available
                        if "groundingMetadata" in result["candidates"][0]:
                            grounding = result["candidates"][0]["groundingMetadata"]
                            if "searchEntryPoints" in grounding:
                                sources = []
                                for entry in grounding["searchEntryPoints"]:
                                    if "renderedContent" in entry:
                                        sources.append(entry["renderedContent"])
                                product_data["sources"] = sources
                        
                        return product_data
                    
                    except json.JSONDecodeError:
                        # If not valid JSON, return raw content
                        return {
                            "brand": "Unknown",
                            "model": query,
                            "category": "Product",
                            "specifications": {"raw_response": content},
                            "price_range": "N/A",
                            "availability": "Unknown",
                            "sources": ["gemini-api"]
                        }
                
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"API error: {str(e)}")
    
    def bulk_search(self, queries: list, use_demo_mode: bool = True, 
                   progress_callback=None) -> list:
        """
        Perform bulk product searches.
        
        Args:
            queries: List of product queries
            use_demo_mode: Whether to use demo mode
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of product data dictionaries
        """
        results = []
        
        for i, query in enumerate(queries):
            try:
                if progress_callback:
                    progress_callback(i + 1, len(queries), query)
                
                result = self.search_product(query, use_demo_mode)
                results.append({
                    "query": query,
                    "success": True,
                    "data": result
                })
                
            except Exception as e:
                results.append({
                    "query": query,
                    "success": False,
                    "error": str(e),
                    "data": {
                        "brand": "Error",
                        "model": query,
                        "category": "Error",
                        "specifications": {"error": str(e)},
                        "price_range": "N/A",
                        "availability": "Error",
                        "sources": ["error"]
                    }
                })
        
        return results

# Utility functions
def validate_api_key(api_key: str) -> bool:
    """Validate Gemini API key format."""
    if not api_key:
        return False
    
    # Basic validation - Gemini API keys typically start with certain patterns
    if len(api_key) < 20:
        return False
    
    return True

def format_specifications(specs: Dict[str, Any]) -> str:
    """Format specifications dictionary for display."""
    if not specs:
        return "No specifications available"
    
    formatted = []
    for key, value in specs.items():
        formatted_key = key.replace('_', ' ').title()
        formatted.append(f"{formatted_key}: {value}")
    
    return "\n".join(formatted)
