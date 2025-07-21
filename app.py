import streamlit as st
import json
import pandas as pd
import time
import re
from typing import List, Dict, Any
from io import StringIO
from gemini_search import GeminiProductSearcher, validate_api_key, format_specifications
from multi_source import IcecatSearcher, GS1Searcher, MultiSourceSearcher
from config import DATA_SOURCES

# Try to load API keys from file (if available)
try:
    from api_keys import GEMINI_API_KEY, ICECAT_API_ACCESS_TOKEN, ICECAT_CONTENT_ACCESS_TOKEN
    DEFAULT_GEMINI_KEY = GEMINI_API_KEY
    DEFAULT_ICECAT_KEY = ICECAT_API_ACCESS_TOKEN
except ImportError:
    DEFAULT_GEMINI_KEY = ""
    DEFAULT_ICECAT_KEY = ""

# Configure page
st.set_page_config(
    page_title="AI Product Spec Finder",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.product-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #1f77b4;
}
.spec-item {
    background-color: #ffffff;
    padding: 10px;
    margin: 5px 0;
    border-radius: 5px;
    border: 1px solid #e0e0e0;
}
.stProgress .st-bo {
    background-color: #1f77b4;
}
</style>
""", unsafe_allow_html=True)

def search_with_multi_sources(query: str, searchers: Dict[str, Any], enabled_sources: List[str]) -> Dict[str, Any]:
    """
    Search for product specifications using multiple sources.
    """
    multi_searcher = MultiSourceSearcher(
        gemini_searcher=searchers.get("google"),
        icecat_searcher=searchers.get("icecat"),
        gs1_searcher=searchers.get("gs1")
    )
    
    # Debug info
    if "google" in enabled_sources and searchers.get("google"):
        gemini_searcher = searchers.get("google")
        has_api_key = bool(gemini_searcher.api_key)
        st.sidebar.write(f"🔍 Gemini searcher has API key: {has_api_key}")
        if has_api_key:
            st.sidebar.success("🚀 Real-time Google search will be used!")
    
    return multi_searcher.search_product(query, enabled_sources)

def process_bulk_input(bulk_text: str) -> List[str]:
    """Process bulk input text and extract product queries."""
    try:
        # Try to parse as JSON array
        queries = json.loads(bulk_text)
        if isinstance(queries, list):
            return [str(q) for q in queries]
    except json.JSONDecodeError:
        pass
    
    # Fall back to line-by-line parsing
    lines = bulk_text.strip().split('\n')
    return [line.strip() for line in lines if line.strip()]

def display_product_card(product_data: Dict[str, Any], query: str):
    """Display a product information card."""
    # Check if this is a multi-source result
    is_multi_source = product_data.get('multi_source', False)
    searched_sources = product_data.get('searched_sources', [])
    
    st.markdown(f"""
    <div class="product-card">
        <h3>🔍 Search Query: {query}</h3>
        <h2>{product_data.get('brand', 'Unknown')} {product_data.get('model', 'Unknown')}</h2>
        <p><strong>Category:</strong> {product_data.get('category', 'N/A')}</p>
        <p><strong>Price Range:</strong> {product_data.get('price_range', 'N/A')}</p>
        <p><strong>Availability:</strong> {product_data.get('availability', 'N/A')}</p>
        {f'<p><strong>Sources Searched:</strong> {", ".join(searched_sources)}</p>' if is_multi_source else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Display specifications
    specs = product_data.get('specifications', {})
    if specs:
        st.subheader("📋 Specifications")
        cols = st.columns(2)
        for i, (key, value) in enumerate(specs.items()):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="spec-item">
                    <strong>{key.replace('_', ' ').title()}:</strong><br>{value}
                </div>
                """, unsafe_allow_html=True)
    
    # Display sources
    sources = product_data.get('sources', [])
    if sources:
        st.subheader("🌐 Data Sources")
        for source in sources:
            st.markdown(f"• {source}")
        
        # Show multi-source indicator
        if is_multi_source:
            st.info("ℹ️ This result was compiled from multiple data sources for comprehensive information.")

# Main App
st.title("🔍 AI Product Spec Finder")
st.markdown("Find detailed product specifications using AI-powered web search")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Keys section
    st.subheader("🔑 API Keys")
    
    # Show if keys are auto-loaded
    if DEFAULT_GEMINI_KEY:
        st.success("✅ Gemini API key loaded from file")
        gemini_api_key = st.text_input("Gemini API Key (auto-loaded)", 
                                      value=DEFAULT_GEMINI_KEY, 
                                      type="password",
                                      help="Gemini API key loaded from api_keys.py")
    else:
        gemini_api_key = st.text_input("Gemini API Key", type="password", 
                                      help="Enter your Google Gemini API key for real searches")
    
    if DEFAULT_ICECAT_KEY:
        st.success("✅ Icecat API key loaded from file") 
        icecat_api_key = st.text_input("Icecat API Key (auto-loaded)",
                                      value=DEFAULT_ICECAT_KEY,
                                      type="password",
                                      help="Icecat API key loaded from api_keys.py")
    else:
        icecat_api_key = st.text_input("Icecat API Key", type="password",
                                      help="Enter your Icecat API key for product database access")
    
    # Data Sources section
    st.subheader("📊 Data Sources")
    st.markdown("Select which sources to search:")
    
    # Source checkboxes
    source_google = st.checkbox("🔍 Google Search (via Gemini)", value=True,
                               help="Real-time web search using Gemini AI")
    source_icecat = st.checkbox("🗄️ Icecat Product Database", value=False,
                               help="Global product catalog with detailed specifications")
    source_gs1 = st.checkbox("🏷️ GS1 Global Registry", value=False,
                            help="Global standards for product identification (works with GTINs)")
    
    # Initialize searchers based on available API keys
    searchers = {}
    enabled_sources = []
    
    # Google/Gemini searcher
    if source_google:
        enabled_sources.append("google")
        use_real_gemini = gemini_api_key and validate_api_key(gemini_api_key)
        searchers["google"] = GeminiProductSearcher(gemini_api_key if use_real_gemini else None)
        
        if gemini_api_key and not use_real_gemini:
            st.warning("⚠️ Invalid Gemini API key format")
        elif use_real_gemini:
            st.success("✅ Gemini API configured - REAL SEARCH MODE")
            st.info("🌐 Will search Google in real-time using Gemini AI")
            
            # Test API button
            if st.button("🧪 Test Gemini API"):
                with st.spinner("Testing API connection..."):
                    try:
                        test_searcher = GeminiProductSearcher(gemini_api_key)
                        test_result = test_searcher.search_product("iPhone 15", use_demo_mode=False)
                        if test_result.get("brand") != "Unknown":
                            st.success("✅ API test successful! Real data received.")
                        else:
                            st.warning("⚠️ API responded but no data found.")
                    except Exception as e:
                        st.error(f"❌ API test failed: {str(e)}")
        else:
            st.info("🧪 Google search in demo mode - limited to sample products")
    
    # Icecat searcher
    if source_icecat:
        enabled_sources.append("icecat")
        # Pass both API tokens to Icecat searcher
        try:
            from api_keys import ICECAT_CONTENT_ACCESS_TOKEN
            content_token = ICECAT_CONTENT_ACCESS_TOKEN
        except ImportError:
            content_token = None
            
        searchers["icecat"] = IcecatSearcher(
            api_key=icecat_api_key if icecat_api_key else None,
            content_token=content_token
        )
        
        if icecat_api_key:
            st.success("✅ Icecat API configured")
            
            # Test Icecat API button
            if st.button("🧪 Test Icecat API"):
                with st.spinner("Testing Icecat API connection..."):
                    try:
                        test_searcher = IcecatSearcher(icecat_api_key, DEFAULT_ICECAT_KEY)
                        test_result = test_searcher.search_product("Dell P2422H")
                        if test_result.get("brand") not in ["Error", "Not Found"]:
                            st.success("✅ Icecat API test successful!")
                            st.json(test_result)
                        else:
                            st.warning("⚠️ Icecat API responded but returned error/no data")
                            st.json(test_result)
                    except Exception as e:
                        st.error(f"❌ Icecat API test failed: {str(e)}")
        else:
            st.info("🧪 Icecat in demo mode")
    
    # GS1 searcher
    if source_gs1:
        enabled_sources.append("gs1")
        searchers["gs1"] = GS1Searcher()
        st.info("ℹ️ GS1 search enabled (works with GTIN codes)")
    
    # Show enabled sources
    if enabled_sources:
        st.success(f"🚀 Active sources: {', '.join(enabled_sources)}")
    else:
        st.warning("⚠️ No sources selected")
    
    st.markdown("---")
    st.markdown("""
    ### 🚀 How It Works
    1. **Single Query**: Enter one product name
    2. **Bulk Processing**: Enter multiple products (JSON array or line-by-line)
    3. **AI Search**: Uses Gemini AI with Google Search
    4. **Export**: Download results as JSON/CSV
    """)
    
    st.markdown("### 📋 Demo Products")
    st.markdown("""
    Try these in demo mode:
    - **iPhone 15 Pro** - Apple smartphone
    - **Sony WH-1000XM5** - Wireless headphones  
    - **MacBook Pro M3** - Apple laptop
    - **Dell P2422H** - Professional monitor
    - **Samsung Galaxy S24** - Android smartphone
    - **Tesla Model 3** - Electric vehicle
    - **AirPods Pro** - Wireless earbuds
    """)
    
    # Quick search buttons
    st.markdown("### 🚀 Quick Search")
    if st.button("🖥️ Dell P2422H"):
        st.session_state.quick_search = "Dell P2422H"
    if st.button("📱 iPhone 15 Pro"):
        st.session_state.quick_search = "iPhone 15 Pro"
    if st.button("🎧 Sony WH-1000XM5"):
        st.session_state.quick_search = "Sony WH-1000XM5"
    
    if st.button("ℹ️ About"):
        st.info("""
        This app uses Google's Gemini AI to search for product specifications 
        in real-time. It provides structured data extraction from web sources.
        """)
    
    # API usage info
    st.markdown("### 🔑 API Status")
    api_status = []
    if "google" in enabled_sources:
        api_status.append("Google Search")
    if "icecat" in enabled_sources:
        api_status.append("Icecat Database")
    if "gs1" in enabled_sources:
        api_status.append("GS1 Registry")
    
    if api_status:
        st.success(f"✅ {', '.join(api_status)} enabled")
    else:
        st.warning("⚠️ No data sources enabled")

# Main interface tabs
tab1, tab2 = st.tabs(["🔍 Single Query", "📊 Bulk Processing"])

with tab1:
    st.header("Single Product Search")
    
    # Check for quick search from sidebar
    default_query = ""
    if 'quick_search' in st.session_state:
        default_query = st.session_state.quick_search
        del st.session_state.quick_search
    
    col1, col2 = st.columns([3, 1])
    with col1:
        single_query = st.text_input(
            "Enter product name, model, or article number:",
            value=default_query,
            placeholder="e.g., Dell P2422H, iPhone 15 Pro, Sony WH-1000XM5"
        )
    with col2:
        search_button = st.button("🔍 Search", type="primary")
    
    # Auto-search if there's a default query
    if default_query and not search_button:
        search_button = True
    
    if search_button and single_query:
        if not enabled_sources:
            st.error("⚠️ Please select at least one data source in the sidebar settings.")
        else:
            with st.spinner("🤖 AI is searching for product specifications..."):
                try:
                    product_data = search_with_multi_sources(single_query, searchers, enabled_sources)
                    display_product_card(product_data, single_query)
                    
                    # Store in session state for export
                    if 'search_results' not in st.session_state:
                        st.session_state.search_results = []
                    st.session_state.search_results.append({
                        'query': single_query,
                        'data': product_data
                    })
                    
                except Exception as e:
                    st.error(f"Error during search: {str(e)}")

with tab2:
    st.header("Bulk Product Processing")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        bulk_input = st.text_area(
            "Enter products (JSON array or one per line):",
            height=200,
            placeholder='["iPhone 15 Pro", "Dell P2422H", "Sony WH-1000XM5"]\n\nOR:\n\niPhone 15 Pro\nDell P2422H\nSony WH-1000XM5\nSamsung Galaxy S24'
        )
    
    with col2:
        st.markdown("### Options")
        max_products = st.number_input("Max products to process", 1, 50, 10)
        process_button = st.button("🚀 Process Bulk", type="primary")
        
        if st.button("📋 Load Sample"):
            sample_data = '["iPhone 15 Pro", "Sony WH-1000XM5", "Dell P2422H", "Samsung Galaxy S24", "MacBook Pro M3", "Tesla Model 3", "AirPods Pro"]'
            st.session_state.bulk_sample = sample_data
    
    # Use sample data if loaded
    if 'bulk_sample' in st.session_state:
        bulk_input = st.session_state.bulk_sample
        del st.session_state.bulk_sample
    
    if process_button and bulk_input:
        if not enabled_sources:
            st.error("⚠️ Please select at least one data source in the sidebar settings.")
        else:
            try:
                queries = process_bulk_input(bulk_input)
                queries = queries[:max_products]  # Limit to max_products
                
                if not queries:
                    st.warning("No valid queries found in input.")
                else:
                    st.info(f"Processing {len(queries)} products using sources: {', '.join(enabled_sources)}")
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    results_container = st.empty()
                    
                    bulk_results = []
                    
                    for i, query in enumerate(queries):
                        status_text.text(f"Processing: {query}")
                        progress_bar.progress((i + 1) / len(queries))
                        
                        try:
                            product_data = search_with_multi_sources(query, searchers, enabled_sources)
                            bulk_results.append({
                                'query': query,
                                'brand': product_data.get('brand', ''),
                                'model': product_data.get('model', ''),
                                'category': product_data.get('category', ''),
                                'price_range': product_data.get('price_range', ''),
                                'availability': product_data.get('availability', ''),
                                'specifications': json.dumps(product_data.get('specifications', {})),
                                'sources': ', '.join(product_data.get('sources', []))
                            })
                        except Exception as e:
                            st.error(f"Error processing {query}: {str(e)}")
                            bulk_results.append({
                                'query': query,
                                'brand': 'Error',
                                'model': 'Error',
                                'category': 'Error',
                                'price_range': 'Error',
                                'availability': 'Error',
                                'specifications': 'Error',
                                'sources': 'Error'
                            })
                    
                    status_text.text("✅ Processing complete!")
                    
                    # Display results table
                    if bulk_results:
                        df = pd.DataFrame(bulk_results)
                        st.subheader("📊 Results")
                        st.dataframe(df, use_container_width=True)
                        
                        # Export options
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            csv = df.to_csv(index=False)
                            st.download_button(
                                "📥 Download CSV",
                                csv,
                                "product_specs.csv",
                                "text/csv"
                            )
                        
                        with col2:
                            json_data = df.to_json(orient='records', indent=2)
                            st.download_button(
                                "📥 Download JSON",
                                json_data,
                                "product_specs.json",
                                "application/json"
                            )
                        
                        with col3:
                            st.metric("Products Processed", len(bulk_results))
            
            except Exception as e:
                st.error(f"Error processing bulk input: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 Powered by Google Gemini AI | �️ Icecat Product Database | 🏷️ GS1 Standards | 🔍 Multi-source data extraction</p>
    <p><em>Configure your API keys and select data sources in the sidebar for full functionality.</em></p>
</div>
""", unsafe_allow_html=True)
