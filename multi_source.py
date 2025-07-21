"""
Multi-source data integration module.
Handles connections to Google/Gemini, Icecat, and GS1 APIs.
"""

import json
import requests
from typing import Dict, Any, Optional, List
import streamlit as st
from config import ICECAT_API_ENDPOINT, GS1_API_ENDPOINT

class IcecatSearcher:
    """Handles product specification search using Icecat API."""
    
    def __init__(self, api_key: Optional[str] = None, content_token: Optional[str] = None):
        self.api_key = api_key  # API Access Token
        self.content_token = content_token  # Content Access Token
        self.endpoint = ICECAT_API_ENDPOINT
    
    def search_product(self, query: str) -> Dict[str, Any]:
        """Search for product in Icecat database."""
        if not self.api_key:
            return self._demo_icecat_search(query)
        
        # Try multiple Icecat API approaches
        try:
            # Method 1: Try the standard Icecat Open Catalog API
            result = self._try_icecat_open_catalog(query)
            if result.get("brand") != "Error":
                return result
            
            # Method 2: Try the Icecat Live API
            result = self._try_icecat_live_api(query)
            if result.get("brand") != "Error":
                return result
            
            # If both methods fail, return demo data
            return self._demo_icecat_search(query)
            
        except Exception as e:
            return self._error_response(query, f"All Icecat methods failed: {str(e)}", "Icecat")
    
    def _try_icecat_open_catalog(self, query: str) -> Dict[str, Any]:
        """Try Icecat Open Catalog API."""
        try:
            # Icecat Open Catalog endpoint
            url = "https://live.icecat.biz/api/"
            params = {
                "UserName": self.api_key,
                "Language": "en",
                "Content": self.content_token or self.api_key,
                "search_text": query
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return self._parse_icecat_response(response, query)
            else:
                return self._error_response(query, f"Open Catalog API: {response.status_code}", "Icecat")
                
        except Exception as e:
            return self._error_response(query, f"Open Catalog error: {str(e)}", "Icecat")
    
    def _try_icecat_live_api(self, query: str) -> Dict[str, Any]:
        """Try Icecat Live API with different authentication."""
        try:
            # Alternative Icecat endpoint
            headers = {
                "Authorization": f"Basic {self.api_key}",
                "Content-Type": "application/json"
            }
            
            url = f"https://live.icecat.biz/api/v1/product/search"
            data = {
                "query": query,
                "limit": 1,
                "lang": "en"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return self._parse_icecat_response(response, query)
            else:
                return self._error_response(query, f"Live API: {response.status_code}", "Icecat")
                
        except Exception as e:
            return self._error_response(query, f"Live API error: {str(e)}", "Icecat")
    
    def _parse_icecat_response(self, response, query: str) -> Dict[str, Any]:
        """Parse Icecat API response (XML or JSON)."""
        try:
            # Try JSON first
            data = response.json()
            if "products" in data and data["products"]:
                product = data["products"][0]
                return self._format_icecat_data(product)
            else:
                return self._no_results_found(query, "Icecat")
                
        except:
            # Try XML parsing
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                product_elem = root.find(".//Product")
                if product_elem is not None:
                    return self._parse_icecat_xml(product_elem, query)
                else:
                    return self._no_results_found(query, "Icecat")
                    
            except Exception as e:
                return self._error_response(query, f"Failed to parse response: {str(e)}", "Icecat")
    
    def _parse_icecat_xml(self, product_elem, query: str) -> Dict[str, Any]:
        """Parse Icecat XML response."""
        try:
            # Extract basic product info from XML
            brand = product_elem.get("Supplier", "Unknown")
            model = product_elem.get("Name", query)
            category = product_elem.get("CategoryName", "Unknown")
            
            # Extract specifications from ProductFeature elements
            specs = {}
            for feature in product_elem.findall(".//ProductFeature"):
                feature_name = feature.get("CategoryFeature_Name", "")
                feature_value = feature.get("Presentation_Value", "")
                if feature_name and feature_value:
                    specs[feature_name.lower().replace(" ", "_")] = feature_value
            
            # Add basic product info
            specs["icecat_id"] = product_elem.get("ID", "")
            specs["product_url"] = product_elem.get("HighPic", "")
            
            return {
                "brand": brand,
                "model": model,
                "category": category,
                "specifications": specs,
                "price_range": "Contact supplier",
                "availability": "Check with retailer",
                "sources": ["icecat.biz"]
            }
            
        except Exception as e:
            return self._error_response(query, f"XML parsing error: {str(e)}", "Icecat")
    
    def _demo_icecat_search(self, query: str) -> Dict[str, Any]:
        """Demo Icecat search with sample data."""
        query_lower = query.lower()
        
        # Expanded sample Icecat-style data
        demo_products = {
            "dell_monitor": {
                "triggers": ['dell', 'p2422', 'monitor'],
                "data": {
                    "brand": "Dell",
                    "model": "P2422H",
                    "category": "LCD Monitor",
                    "specifications": {
                        "icecat_id": "123456789",
                        "screen_size": "24 inches",
                        "resolution": "1920 x 1080",
                        "panel_type": "IPS",
                        "response_time": "5 ms",
                        "refresh_rate": "60 Hz",
                        "connectivity": "HDMI, DisplayPort, VGA, USB",
                        "energy_rating": "Energy Star certified",
                        "vesa_mount": "100 x 100 mm"
                    },
                    "price_range": "$200 - $280",
                    "availability": "In Stock",
                    "sources": ["icecat.biz", "dell.com"]
                }
            },
            "gembird_ups": {
                "triggers": ['gembird', 'ups', '850'],
                "data": {
                    "brand": "Gembird",
                    "model": "UPS-PC-850AP",
                    "category": "UPS (Uninterruptible Power Supply)",
                    "specifications": {
                        "icecat_id": "987654321",
                        "power_capacity": "850 VA / 480 W",
                        "battery_type": "Sealed Lead Acid",
                        "backup_time": "10-15 minutes at full load",
                        "input_voltage": "230V AC ±25%",
                        "output_voltage": "230V AC ±10%",
                        "outlets": "4 x IEC 13A sockets",
                        "protection": "Surge, overload, short circuit",
                        "dimensions": "350 x 95 x 140 mm",
                        "weight": "4.5 kg"
                    },
                    "price_range": "$80 - $120",
                    "availability": "In Stock",
                    "sources": ["icecat.biz", "gembird.com"]
                }
            },
            "iphone": {
                "triggers": ['iphone', 'apple', '15', 'pro'],
                "data": {
                    "brand": "Apple",
                    "model": "iPhone 15 Pro",
                    "category": "Smartphone",
                    "specifications": {
                        "icecat_id": "456789123",
                        "display": "6.1-inch Super Retina XDR OLED",
                        "processor": "A17 Pro chip",
                        "storage": "128GB, 256GB, 512GB, 1TB",
                        "camera": "48MP main, 12MP ultra-wide, 12MP telephoto",
                        "battery": "Up to 23 hours video playback",
                        "connectivity": "5G, Wi-Fi 6E, Bluetooth 5.3",
                        "materials": "Titanium design"
                    },
                    "price_range": "$999 - $1,499",
                    "availability": "Available",
                    "sources": ["icecat.biz", "apple.com"]
                }
            }
        }
        
        # Check for matches
        for product_key, product_info in demo_products.items():
            if any(trigger in query_lower for trigger in product_info["triggers"]):
                return product_info["data"]
        
        return self._no_results_found(query, "Icecat Demo")
    
    def _format_icecat_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format Icecat API response to standard format."""
        return {
            "brand": data.get("brand", {}).get("name", "Unknown"),
            "model": data.get("name", "Unknown"),
            "category": data.get("category", {}).get("name", "Unknown"),
            "specifications": self._extract_icecat_specs(data),
            "price_range": "Contact supplier",
            "availability": "Check with retailer",
            "sources": ["icecat.biz"]
        }
    
    def _extract_icecat_specs(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Extract specifications from Icecat data."""
        specs = {}
        
        # Extract features
        features = data.get("features", [])
        for feature in features:
            if isinstance(feature, dict):
                name = feature.get("name", "")
                value = feature.get("value", "")
                if name and value:
                    specs[name.lower().replace(" ", "_")] = str(value)
        
        # Add basic info
        if data.get("short_desc"):
            specs["description"] = data["short_desc"]
        
        return specs
    
    def _no_results_found(self, query: str, source: str) -> Dict[str, Any]:
        """Standard no results response."""
        return {
            "brand": "Not Found",
            "model": query,
            "category": "Unknown",
            "specifications": {
                "status": f"No results found in {source}",
                "suggestion": "Try a different search term or check spelling"
            },
            "price_range": "N/A",
            "availability": "Unknown",
            "sources": [source.lower()]
        }
    
    def _error_response(self, query: str, error: str, source: str) -> Dict[str, Any]:
        """Standard error response."""
        return {
            "brand": "Error",
            "model": query,
            "category": "Error",
            "specifications": {
                "error": error,
                "source": source
            },
            "price_range": "N/A",
            "availability": "Error",
            "sources": [source.lower()]
        }


class GS1Searcher:
    """Handles product search using GS1 standards (demo implementation)."""
    
    def __init__(self):
        self.endpoint = GS1_API_ENDPOINT
    
    def search_product(self, query: str) -> Dict[str, Any]:
        """Search for product using GS1 standards."""
        # GS1 typically works with GTINs/barcodes
        # This is a demo implementation
        
        query_clean = query.replace("-", "").replace(" ", "")
        
        # Check if query looks like a GTIN/barcode
        if query_clean.isdigit() and len(query_clean) in [8, 12, 13, 14]:
            return self._demo_gs1_search(query_clean)
        else:
            return {
                "brand": "GS1 Search",
                "model": query,
                "category": "Product Identification",
                "specifications": {
                    "note": "GS1 search works best with GTIN/barcode numbers",
                    "gtin_format": "Enter 8, 12, 13, or 14 digit GTIN",
                    "example": "Try: 012345678905 or 1234567890123",
                    "status": "Invalid GTIN format"
                },
                "price_range": "N/A",
                "availability": "Unknown",
                "sources": ["gs1.org"]
            }
    
    def _demo_gs1_search(self, gtin: str) -> Dict[str, Any]:
        """Demo GS1 search with sample GTIN data."""
        # Sample GTINs for demo
        sample_gtins = {
            "012345678905": {
                "brand": "Sample Brand",
                "product_name": "Demo Product",
                "category": "Consumer Goods"
            },
            "1234567890123": {
                "brand": "Tech Corp",
                "product_name": "Electronic Device",
                "category": "Electronics"
            }
        }
        
        if gtin in sample_gtins:
            data = sample_gtins[gtin]
            return {
                "brand": data["brand"],
                "model": data["product_name"],
                "category": data["category"],
                "specifications": {
                    "gtin": gtin,
                    "gs1_verified": "Yes",
                    "product_type": data["category"],
                    "identification_standard": "GS1 GTIN"
                },
                "price_range": "Contact manufacturer",
                "availability": "Check with authorized retailers",
                "sources": ["gs1.org", "manufacturer"]
            }
        else:
            return {
                "brand": "Unknown",
                "model": f"GTIN: {gtin}",
                "category": "Product",
                "specifications": {
                    "gtin": gtin,
                    "status": "Valid GTIN format but not found in demo database",
                    "note": "This is a demo. Real GS1 integration would query the actual registry"
                },
                "price_range": "N/A",
                "availability": "Unknown",
                "sources": ["gs1.org"]
            }


class MultiSourceSearcher:
    """Orchestrates searches across multiple data sources."""
    
    def __init__(self, gemini_searcher=None, icecat_searcher=None, gs1_searcher=None):
        self.gemini_searcher = gemini_searcher
        self.icecat_searcher = icecat_searcher
        self.gs1_searcher = gs1_searcher
    
    def search_product(self, query: str, enabled_sources: List[str]) -> Dict[str, Any]:
        """Search across enabled sources and return best result."""
        results = {}
        errors = []
        
        # Search each enabled source
        if "google" in enabled_sources and self.gemini_searcher:
            try:
                # Use real API if available, otherwise demo
                results["google"] = self.gemini_searcher.search_product(query, use_demo_mode=None)
            except Exception as e:
                errors.append(f"Google search error: {str(e)}")
        
        if "icecat" in enabled_sources and self.icecat_searcher:
            try:
                results["icecat"] = self.icecat_searcher.search_product(query)
            except Exception as e:
                errors.append(f"Icecat search error: {str(e)}")
        
        if "gs1" in enabled_sources and self.gs1_searcher:
            try:
                results["gs1"] = self.gs1_searcher.search_product(query)
            except Exception as e:
                errors.append(f"GS1 search error: {str(e)}")
        
        # Combine results or return best one
        if results:
            return self._combine_results(results, query)
        else:
            return {
                "brand": "No Results",
                "model": query,
                "category": "Unknown",
                "specifications": {
                    "status": "No results from any enabled source",
                    "errors": errors if errors else ["No sources enabled"],
                    "enabled_sources": enabled_sources
                },
                "price_range": "N/A",
                "availability": "Unknown",
                "sources": enabled_sources
            }
    
    def _combine_results(self, results: Dict[str, Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Combine results from multiple sources."""
        # Priority: Icecat > Google > GS1 for detailed specs
        if "icecat" in results and results["icecat"].get("brand") != "Not Found":
            base_result = results["icecat"].copy()
            base_result["multi_source"] = True
        elif "google" in results and results["google"].get("brand") != "Unknown":
            base_result = results["google"].copy()
            base_result["multi_source"] = True
        elif "gs1" in results:
            base_result = results["gs1"].copy()
            base_result["multi_source"] = True
        else:
            # Return first available result
            base_result = list(results.values())[0].copy()
            base_result["multi_source"] = True
        
        # Add source information
        all_sources = []
        for source_name, result in results.items():
            all_sources.extend(result.get("sources", [source_name]))
        
        base_result["sources"] = list(set(all_sources))
        base_result["searched_sources"] = list(results.keys())
        
        # Add combined specifications
        combined_specs = base_result.get("specifications", {})
        combined_specs["search_results_count"] = len(results)
        combined_specs["sources_searched"] = ", ".join(results.keys())
        
        base_result["specifications"] = combined_specs
        
        return base_result
