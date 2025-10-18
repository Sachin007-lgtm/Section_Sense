# Criminal Law Knowledge Base - BDA Lab Project

A comprehensive **AI-powered legal search and analytics system** that leverages **Big Data techniques** and **NLP** to help legal professionals quickly find relevant criminal law sections, analyze precedents, and get intelligent recommendations.

## 🎯 Key Features

### **AI-Powered Search Engine**
- **Vector Similarity Search**: Uses sentence transformers to convert legal queries into embeddings
- **Semantic Matching**: Finds relevant law sections using cosine similarity instead of just keyword matching
- **Smart Categorization**: Automatically classifies laws by crime type, severity, and punishment
- **Query Understanding**: Handles natural language queries like "procedure when magistrate cannot decide a case"

### **Comprehensive Data Pipeline**
- **Web Scraping**: Automated extraction from 1,056+ legal sections across multiple Indian law acts
- **Data Enrichment**: Automatic keyword extraction, crime type classification, and severity assessment
- **Multi-Act Support**: Bharatiya Nyaya Sanhita (2023), Bharatiya Nagarik Suraksha Sanhita (2023), Indian Evidence Act (1872)
- **Real-time Processing**: Background data processing and continuous updates

### **Advanced Analytics**
- **Search Analytics**: Track search patterns, popular queries, and user behavior
- **Legal Insights**: Statistical analysis of crime types, punishment trends, and law categories
- **Performance Metrics**: Query execution times, similarity scores, and relevance tracking

## 🏗️ Technical Architecture

```
Criminal Law Knowledge Base
├── Backend/ (FastAPI + AI Engine)
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/              # SQLAlchemy database models
│   │   │   └── law_models.py    # Legal sections, cases, search queries
│   │   ├── services/            # Business logic
│   │   │   ├── search_service.py      # Vector similarity search
│   │   │   └── sqlite_search_service.py # Database search
│   │   ├── schemas.py           # Pydantic request/response models
│   │   └── database.py          # Database configuration
│   ├── data/
│   │   ├── ipc_scraper.py       # Web scraping engine
│   │   ├── all_sections_enriched.json  # 1,056 legal sections dataset
│   │   └── all_sections_enriched.csv   # Same data in CSV format
│   └── criminal_law_kb.db       # SQLite database
├── Frontend/ (Streamlit Dashboard)
│   └── [UI Components]
└── INTEGRATION_README.md        # Project integration guide
```

## 🔧 Technology Stack

### **Backend Infrastructure**
- **API Framework**: FastAPI (async, OpenAPI documentation)
- **Database**: SQLAlchemy ORM + SQLite/PostgreSQL
- **AI/ML Stack**: 
  - SentenceTransformers (`all-MiniLM-L6-v2`) for embeddings
  - scikit-learn for cosine similarity computation
  - NumPy for vector operations

### **Data Processing**
- **Web Scraping**: BeautifulSoup4 + Requests
- **Data Analysis**: Pandas + NumPy
- **Text Processing**: Regular expressions, keyword extraction
- **Output Formats**: JSON, CSV for analytics

### **Development Tools**
- **Environment**: Conda virtual environment
- **Documentation**: Auto-generated OpenAPI docs
- **Logging**: Python logging with structured output

## 🚀 Quick Start Guide

### **1. Environment Setup**
```bash
# Navigate to Backend directory
cd "C:\Users\sachi\Desktop\BDA lab\Backend"

# Activate conda environment (if not already active)
conda activate ./mvenv

# Install all dependencies
pip install -r requirements.txt
```

### **2. Data Preparation**
```bash
# Run the web scraper to get latest legal sections
python data/ipc_scraper.py

# Load scraped data into database
python load_data.py
```

### **3. Start the Backend Server**
```bash
# Option 1: Using uvicorn (RECOMMENDED)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python module
python -m uvicorn app.main:app --reload

# Option 3: Development mode with auto-reload
uvicorn app.main:app --reload
```

### **4. Access the System**
- **🔗 API Endpoints**: http://localhost:8000
- **📚 Interactive API Docs**: http://localhost:8000/docs
- **📖 Alternative Docs**: http://localhost:8000/redoc
- **💻 Frontend Dashboard**: http://localhost:8501 (if running Streamlit)

### **5. Verify the Setup**
```bash
# Check if server is running
curl "http://localhost:8000/api/v1/health"

# Or visit in browser
# http://localhost:8000/docs
```

## 🔍 API Usage Examples

### **Search for Legal Sections**
```bash
# Search using natural language query
curl -X POST "http://localhost:8000/api/v1/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "procedure when magistrate cannot decide a case",
       "search_type": "section_search",
       "max_results": 10
     }'

# Search with filters
curl "http://localhost:8000/api/v1/search/sections?query=murder&category=Offences Against Human Body&max_results=5"
```

### **Get Search Suggestions**
```bash
curl "http://localhost:8000/api/v1/suggestions?query=theft"
```

### **Health Check**
```bash
curl "http://localhost:8000/api/v1/health"
```

## 📊 Dataset Information

### **Legal Sections Database**
- **Total Records**: 1,056+ legal sections
- **Coverage**: 
  - Bharatiya Nyaya Sanhita, 2023 (530+ sections)
  - Bharatiya Nagarik Suraksha Sanhita, 2023
  - Indian Evidence Act, 1872
- **Data Fields**: Section number, title, description, category, crime type, severity, punishment, keywords
- **Update Frequency**: On-demand via web scraper

### **Enriched Metadata**
- **Crime Types**: Physical harm, Property harm, Document fraud, etc.
- **Severity Levels**: Heinous, Serious, Moderate, Unknown
- **Categories**: 10+ predefined legal categories
- **Keywords**: Auto-extracted for better search matching

## 🧠 AI/ML Implementation Details

### **Vector Search Engine**
```python
# How the semantic search works:
1. Query Processing: "procedure when magistrate cannot decide a case"
2. Embedding Generation: SentenceTransformer.encode(query) → 384-dim vector
3. Section Embedding: Pre-computed vectors for all 1,056 sections
4. Similarity Calculation: cosine_similarity(query_vector, section_vectors)
5. Ranking: Sort by similarity score (0.0 to 1.0)
6. Filtering: Return results above threshold (>0.3)
```

### **Model Performance**
- **Model**: `all-MiniLM-L6-v2` (22MB, optimized for speed)
- **Vector Dimensions**: 384
- **Search Speed**: <100ms for 1,000+ sections
- **Accuracy**: Semantic understanding vs keyword matching

### **Data Enrichment Pipeline**
```python
# Automatic classification examples:
"murder" → Crime Type: "Offences Against Human Body", Severity: "Heinous"
"theft" → Crime Type: "Offences Against Property", Severity: "Moderate"  
"forgery" → Crime Type: "Document/identity fraud", Severity: "Moderate"
```

## 🧪 Testing & Validation

### **Manual Testing Available**
- **API Documentation**: Visit http://localhost:8000/docs for interactive testing
- **Health Check**: http://localhost:8000/api/v1/health
- **Sample Search**: Use the interactive API docs to test search functionality

### **Performance Metrics**
- Search execution time tracking
- Similarity score distribution analysis
- Query pattern analytics
- Database query optimization

## 🔮 Future Enhancements

### **Planned Features**
- **Case Law Integration**: Supreme Court and High Court judgments
- **Multi-language Support**: Hindi, regional languages
- **Advanced Analytics**: Legal trend analysis, case outcome prediction
- **Document Upload**: PDF analysis and similar case finding
- **Real-time Updates**: Live legal database synchronization

## ⚖️ Legal Disclaimer

This system is designed for **educational and research purposes** in the field of **Big Data Analytics** and **Legal Technology**. For actual legal use, ensure:

- ✅ **Accuracy Verification**: All legal references must be independently verified
- ✅ **Current Information**: Laws may have been amended since data collection
- ✅ **Professional Consultation**: Consult qualified legal professionals for actual cases
- ✅ **Compliance**: Ensure compliance with data usage and legal practice regulations

**Note**: This is a **proof-of-concept** demonstrating AI applications in legal document processing and search.

## 👥 Contributing

### **How to Contribute**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### **Areas for Contribution**
- Additional legal act scrapers
- Improved NLP models for legal text
- Performance optimizations
- UI/UX improvements
- Test coverage expansion

## 📜 License & Credits

**License**: MIT License - see LICENSE file for details

**Academic Project**: Big Data Analytics Lab  
**Domain**: Legal Technology & AI Applications  
**Institution**: [Your Institution Name]

**Data Sources**: 
- India Code (indiacode.nic.in) - Public domain legal documents
- Government of India legal databases

---

## 📞 Support & Contact

For questions about this **BDA Lab project**:
- 📧 **Technical Issues**: Create an issue in the repository
- 📚 **Documentation**: Check `/docs` folder for detailed guides
- 🔍 **API Reference**: Visit http://localhost:8000/docs when server is running

**Project Status**: ✅ **Production Ready** for educational and research purposes
