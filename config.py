# Configuration for AI Product Spec Finder

# API Endpoints
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
ICECAT_API_ENDPOINT = "https://live.icecat.biz/api"
GS1_API_ENDPOINT = "https://api.gs1.org/v1"

# Data source configuration
DATA_SOURCES = {
    "google": {
        "name": "Google Search (via Gemini)",
        "description": "Real-time web search using Gemini AI",
        "requires_api_key": True,
        "api_key_field": "gemini_api_key"
    },
    "icecat": {
        "name": "Icecat Product Database",
        "description": "Global product catalog with detailed specifications",
        "requires_api_key": True,
        "api_key_field": "icecat_api_key"
    },
    "gs1": {
        "name": "GS1 Global Registry",
        "description": "Global standards for product identification",
        "requires_api_key": False,
        "api_key_field": None
    }
}

# Product search prompt template
PRODUCT_SEARCH_PROMPT = """
You are an AI assistant that helps find detailed product specifications by searching the web.

Search for the following product: "{query}"

Please provide a structured JSON response with the following format:
{{
    "brand": "Brand name",
    "model": "Model name/number",
    "category": "Product category",
    "specifications": {{
        "spec1": "value1",
        "spec2": "value2",
        // Add all relevant technical specifications
    }},
    "price_range": "Price range if available",
    "availability": "Availability status",
    "sources": ["source1.com", "source2.com"]
}}

Use your web search capabilities to find accurate, up-to-date information from official websites, retailers, and trusted tech review sites.
Focus on technical specifications, features, and key product details.
"""

# Sample product database for demo purposes
SAMPLE_PRODUCTS = {
    "iphone 15 pro": {
        "brand": "Apple",
        "model": "iPhone 15 Pro",
        "category": "Smartphone",
        "specifications": {
            "display": "6.1-inch Super Retina XDR OLED, 2556×1179 resolution",
            "processor": "A17 Pro chip with 6-core CPU",
            "storage": "128GB, 256GB, 512GB, 1TB options",
            "camera": "48MP Main, 12MP Ultra Wide, 12MP Telephoto (3x zoom)",
            "battery": "Up to 23 hours video playback",
            "os": "iOS 17",
            "connectivity": "5G, Wi-Fi 6E, Bluetooth 5.3",
            "materials": "Titanium design with Ceramic Shield front",
            "water_resistance": "IP68 (up to 6 meters for 30 minutes)"
        },
        "price_range": "$999 - $1,499",
        "availability": "Available",
        "sources": ["apple.com", "gsmarena.com", "techradar.com", "theverge.com"]
    },
    "sony wh-1000xm5": {
        "brand": "Sony",
        "model": "WH-1000XM5",
        "category": "Wireless Noise-Canceling Headphones",
        "specifications": {
            "driver": "30mm dynamic drivers",
            "frequency_response": "4Hz - 40kHz",
            "battery_life": "30 hours with ANC, 40 hours without ANC",
            "charging": "USB-C, Quick charge: 3 min = 3 hours playback",
            "weight": "250g",
            "connectivity": "Bluetooth 5.2, NFC, 3.5mm jack",
            "noise_canceling": "Industry-leading ANC with V1 processor",
            "microphones": "8 microphones for call clarity",
            "codec_support": "LDAC, SBC, AAC"
        },
        "price_range": "$399 - $429",
        "availability": "Available",
        "sources": ["sony.com", "rtings.com", "whatifi.com", "headphonesty.com"]
    },
    "macbook pro m3": {
        "brand": "Apple",
        "model": "MacBook Pro M3",
        "category": "Laptop",
        "specifications": {
            "processor": "Apple M3 chip with 8-core CPU and 10-core GPU",
            "memory": "8GB, 16GB, or 24GB unified memory",
            "storage": "512GB, 1TB, 2TB SSD options",
            "display": "14-inch or 16-inch Liquid Retina XDR display",
            "battery": "Up to 22 hours video playback",
            "ports": "3x Thunderbolt 4, HDMI, SDXC, MagSafe 3",
            "os": "macOS Sonoma",
            "weight": "3.4 lbs (14-inch), 4.7 lbs (16-inch)"
        },
        "price_range": "$1,599 - $2,499",
        "availability": "Available",
        "sources": ["apple.com", "macrumors.com", "9to5mac.com"]
    },
    "dell p2422h": {
        "brand": "Dell",
        "model": "P2422H",
        "category": "Professional Monitor",
        "specifications": {
            "screen_size": "24-inch (23.8-inch viewable)",
            "resolution": "1920 x 1080 Full HD",
            "panel_type": "IPS technology",
            "refresh_rate": "60Hz",
            "response_time": "8ms (normal); 5ms (fast)",
            "brightness": "250 cd/m² (typical)",
            "contrast_ratio": "1000:1 (typical)",
            "color_gamut": "99% sRGB",
            "connectivity": "HDMI 1.4, DisplayPort 1.2, VGA, USB 3.2 hub",
            "adjustability": "Height, tilt, swivel, pivot",
            "vesa_mount": "100mm x 100mm",
            "power_consumption": "18W (typical)"
        },
        "price_range": "$200 - $280",
        "availability": "Available",
        "sources": ["dell.com", "displayspecifications.com", "rtings.com"]
    },
    "samsung galaxy s24": {
        "brand": "Samsung",
        "model": "Galaxy S24",
        "category": "Smartphone",
        "specifications": {
            "display": "6.2-inch Dynamic AMOLED 2X, 2340×1080",
            "processor": "Snapdragon 8 Gen 3 / Exynos 2400",
            "storage": "128GB, 256GB, 512GB",
            "camera": "50MP main, 12MP ultrawide, 10MP telephoto",
            "battery": "4000mAh with 25W fast charging",
            "os": "Android 14 with One UI 6.1",
            "connectivity": "5G, Wi-Fi 6E, Bluetooth 5.3",
            "materials": "Aluminum frame with Gorilla Glass Victus 2",
            "water_resistance": "IP68"
        },
        "price_range": "$799 - $999",
        "availability": "Available",
        "sources": ["samsung.com", "gsmarena.com", "androidcentral.com"]
    },
    "tesla model 3": {
        "brand": "Tesla",
        "model": "Model 3",
        "category": "Electric Vehicle",
        "specifications": {
            "drivetrain": "Rear-wheel drive / All-wheel drive",
            "range": "272-358 miles EPA estimated",
            "acceleration": "0-60 mph in 4.2-5.8 seconds",
            "top_speed": "125-162 mph",
            "charging": "Supercharger V3 compatible, up to 250kW",
            "interior": "15-inch touchscreen, premium audio",
            "autopilot": "Standard Autopilot included",
            "seating": "5 adults",
            "cargo": "15 cu ft rear, 2.8 cu ft front trunk"
        },
        "price_range": "$38,990 - $54,990",
        "availability": "Available",
        "sources": ["tesla.com", "edmunds.com", "motortrend.com"]
    },
    "airpods pro": {
        "brand": "Apple",
        "model": "AirPods Pro (2nd generation)",
        "category": "Wireless Earbuds",
        "specifications": {
            "chip": "Apple H2 chip",
            "noise_cancellation": "Active Noise Cancellation",
            "battery_life": "6 hours listening, 30 hours with case",
            "charging": "MagSafe, Lightning, Qi wireless",
            "audio": "Adaptive Audio, Personalized Spatial Audio",
            "controls": "Touch control, Siri voice control",
            "water_resistance": "IPX4 (earbuds and case)",
            "case": "MagSafe Charging Case included"
        },
        "price_range": "$249 - $279",
        "availability": "Available",
        "sources": ["apple.com", "soundguys.com", "whatifi.com"]
    }
}
