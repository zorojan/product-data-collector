# 🔍 AI Product Spec Finder

A powerful web application that leverages Google's Gemini AI to find detailed product specifications through real-time web search and structured data extraction.

## ✨ Features

### 🎯 Core Functionality
- **Single Product Search**: Find specifications for individual products
- **Bulk Processing**: Process multiple products simultaneously (up to 50)
- **AI-Powered Search**: Uses Gemini AI with Google Search integration
- **Structured Data**: Clean, organized product information
- **Export Options**: Download results as JSON or CSV

### 🔍 Search Capabilities
- Product name search (e.g., "iPhone 15 Pro")
- Model number search (e.g., "WH-1000XM5")
- Article number search
- Brand + model combinations

### 📊 Data Extraction
- Brand and model information
- Product category classification
- Technical specifications
- Price range estimation
- Availability status
- Source attribution with grounding metadata

## 🚀 How It Works

1. **User Input**: Enter product queries in single or bulk mode
2. **AI Processing**: Gemini AI performs Google Search and analyzes results
3. **Data Extraction**: Structured information extracted using JSON schema
4. **Results Display**: Clean presentation with source attribution
5. **Export**: Download complete datasets for further analysis

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (for real searches)

### Quick Start

1. **Clone/Download** the repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   streamlit run app.py
   ```
4. **Access the app** at `http://localhost:8501`

### Configuration

#### Demo Mode (No API Key Required)
- Uses sample product database
- Perfect for testing and demonstrations
- Includes iPhone 15 Pro, Sony WH-1000XM5, MacBook Pro M3

#### Production Mode (API Key Required)
1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Enter the API key in the sidebar
3. Enable real-time web search capabilities

## 📱 Usage Examples

### Single Product Search
```
Input: "iPhone 15 Pro"
Output: Complete specifications, pricing, availability
```

### Bulk Processing
```json
[
  "iPhone 15 Pro",
  "Sony WH-1000XM5",
  "Samsung Galaxy S24",
  "MacBook Pro M3"
]
```

Or line-by-line:
```
iPhone 15 Pro
Sony WH-1000XM5
Samsung Galaxy S24
MacBook Pro M3
```

## 🏗️ Technical Architecture

### Core Components
- **app.py**: Main Streamlit interface
- **gemini_search.py**: Gemini AI integration
- **config.py**: Configuration and sample data
- **requirements.txt**: Python dependencies

### Data Flow
1. User input → Query processing
2. Query → Gemini AI with search tools
3. Web search → Result analysis
4. Data extraction → JSON structuring
5. Display → Export options

### AI Integration
- **Model**: Gemini 1.5 Flash
- **Tools**: Google Search retrieval
- **Prompt**: Structured JSON schema
- **Grounding**: Source attribution
- **Safety**: Content filtering

## 📊 Sample Output Structure

```json
{
  "brand": "Apple",
  "model": "iPhone 15 Pro",
  "category": "Smartphone",
  "specifications": {
    "display": "6.1-inch Super Retina XDR OLED",
    "processor": "A17 Pro chip",
    "storage": "128GB/256GB/512GB/1TB",
    "camera": "48MP Main, 12MP Ultra Wide, 12MP Telephoto"
  },
  "price_range": "$999 - $1,499",
  "availability": "Available",
  "sources": ["apple.com", "gsmarena.com", "techradar.com"]
}
```

## 🔧 Customization

### Adding New Sample Products
Edit `config.py` to add more sample products for demo mode.

### Modifying Search Prompts
Update `PRODUCT_SEARCH_PROMPT` in `config.py` to customize AI behavior.

### UI Customization
Modify the Streamlit interface in `app.py` for custom styling and layout.

## 🚀 Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy with automatic updates

## 🔒 Security & Privacy

- API keys are handled securely
- No data persistence - searches are stateless
- Source attribution maintains transparency
- Content filtering through Gemini safety features

## 📄 License

This project is open source. Please check the license file for details.

---

*Powered by Google Gemini AI | Real-time web search | Structured data extraction*
