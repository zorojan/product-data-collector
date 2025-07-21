# 🔑 API Keys Setup Guide

## Quick Start
Your API keys have been configured and should work automatically! 

## Configuration Files

### api_keys.py
This file contains your actual API keys:
- ✅ Gemini API Key: Configured
- ✅ Icecat API Access Token: Configured  
- ✅ Icecat Content Access Token: Configured

### Security Notes
- ✅ This file is in .gitignore (won't be committed to git)
- ⚠️ Keep this file secure and never share publicly
- 🔄 You can rotate keys anytime by updating the file

## API Sources

### 🤖 Google Gemini AI
- **Website**: https://aistudio.google.com/app/apikey
- **Your Key**: AIzaSyAscnWh6-p0v-v2Uoktbd2cjFhaAE_hQmQ
- **Usage**: Real-time web search and AI-powered analysis

### 🗄️ Icecat Product Database
- **Website**: https://icecat.biz/
- **API Access Token**: f2a8304b-5820-41ae-8e8f-a2555351c1b5
- **Content Access Token**: 21395317-bace-48c6-8195-54944a6f8fd0
- **Usage**: Global product specifications database

## How to Use

1. **Open the application** - API keys will load automatically
2. **Select data sources** in the sidebar:
   - ✅ Google Search (via Gemini) - for web search
   - ✅ Icecat Product Database - for detailed specs
   - ✅ GS1 Global Registry - for GTIN/barcode lookup

3. **Search for products** - the app will use all selected sources

## Troubleshooting

### If keys don't load automatically:
1. Make sure `api_keys.py` is in the same folder as `app.py`
2. Check that the file contains the correct variable names
3. Restart the Streamlit application

### If you get API errors:
1. Verify your keys are still valid on the provider websites
2. Check your API quotas and limits
3. Make sure your internet connection is stable

### Manual Key Entry:
If automatic loading fails, you can always enter keys manually in the sidebar.

## Production Deployment

For production environments:
1. Use environment variables instead of files
2. Use secrets management services
3. Implement key rotation policies
4. Monitor API usage and costs

## Support

- **Gemini API**: https://ai.google.dev/docs
- **Icecat API**: https://icecat.biz/en/menu/API
- **Application Issues**: Check the Streamlit logs
