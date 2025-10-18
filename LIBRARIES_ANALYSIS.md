# 📦 Libraries & Environment Analysis

## 🐍 Python Environment

### Environment Type
- **Type**: **Conda Environment** (Anaconda3)
- **Python Version**: 3.12.7 (packaged by Anaconda, Inc.)
- **Virtual Environment Folder**: `mvenv/` (Python venv wrapper)
- **Base Location**: `C:\Users\sachi\anaconda3`

### How It's Set Up
You're using **Anaconda Python** as the base, but created a **virtual environment** (venv) named `mvenv/` for project isolation.

---

## 📚 Backend Libraries Used

### Web Framework & API
```python
fastapi==0.119.0          # Modern async web framework (~50 MB)
uvicorn[standard]==0.37.0 # ASGI server (~10 MB)
python-multipart==0.0.20  # File upload support (~1 MB)
```

### Database & ORM
```python
sqlalchemy==2.0.44        # Database ORM (~5 MB)
psycopg2-binary==2.9.11   # PostgreSQL driver (~5 MB)
```

### 🚨 HEAVY ML/AI Libraries (Storage Intensive)

#### PyTorch ⚠️ **~800 MB - 2.5 GB**
```python
torch==2.8.0              # Deep learning framework
```
- **Version**: 2.8.0+cpu (CPU-only version)
- **Size**: ~800 MB - 1.5 GB (CPU version)
- **GPU Version**: Would be ~2-3 GB
- **Used By**: `sentence-transformers`, `transformers`
- **Location**: `C:\Users\sachi\AppData\Roaming\Python\Python312\site-packages\torch`

#### Transformers ⚠️ **~400 MB**
```python
transformers==4.57.0      # Hugging Face transformers
sentence-transformers==5.1.1  # Sentence embeddings
huggingface-hub==0.35.3   # Model download/cache
```
- **Models Downloaded**: `all-MiniLM-L6-v2` (~80-100 MB)
- **Cache Location**: `~/.cache/huggingface/` or `sentence_transformers_cache/`

### Data Science Libraries
```python
pandas==2.3.3             # Data manipulation (~50 MB)
numpy==2.3.3              # Numerical computing (~20 MB)
scikit-learn==1.7.2       # Machine learning (~40 MB)
scipy==1.16.2             # Scientific computing (~60 MB)
```

### Other Libraries
```python
beautifulsoup4==4.14.2    # Web scraping (~1 MB)
requests==2.32.3          # HTTP library (~500 KB)
python-dotenv==1.1.1      # Environment variables (~50 KB)
streamlit==1.28.1         # Dashboard (unused) (~30 MB)
plotly==5.17.0            # Plotting (unused) (~50 MB)
elasticsearch==8.11.0     # Search engine (unused) (~5 MB)
groq==0.32.0              # AI API client (~2 MB)
pydantic==2.12.1          # Data validation (~5 MB)
```

---

## 🎨 Frontend Libraries

### Core Framework
```json
"react": "^18.3.1"           // ~2 MB
"react-dom": "^18.3.1"       // ~2 MB
"react-router-dom": "^6.30.1" // ~500 KB
"typescript": "^5.8.3"        // ~50 MB (dev)
```

### Build Tools
```json
"vite": "^5.4.19"            // ~20 MB (dev)
"@vitejs/plugin-react-swc": "^3.11.0"
```

### UI Libraries (Radix UI + shadcn/ui)
```json
"@radix-ui/*": "Multiple packages"  // ~10-15 MB total
"tailwindcss": "^3.4.17"     // ~5 MB (dev)
"lucide-react": "^0.462.0"   // ~3 MB (icons)
```

### State Management & Forms
```json
"@tanstack/react-query": "^5.83.0"  // ~500 KB
"react-hook-form": "^7.61.1"        // ~200 KB
"zod": "^3.25.76"                   // ~200 KB
```

---

## 💾 Total Storage Usage

### Backend Dependencies
| Category | Size | Critical? |
|----------|------|-----------|
| **PyTorch** | ~800 MB - 1.5 GB | ⚠️ **HEAVY** |
| **Transformers** | ~400 MB | ⚠️ **HEAVY** |
| **ML Models Cache** | ~100-200 MB | ⚠️ **HEAVY** |
| **Pandas + NumPy + SciPy** | ~130 MB | Medium |
| **FastAPI + Uvicorn** | ~60 MB | Light |
| **SQLAlchemy + psycopg2** | ~10 MB | Light |
| **Other Libraries** | ~100 MB | Light |
| **Unused (Streamlit, Plotly, Elasticsearch)** | ~85 MB | ❌ **WASTE** |

**Total Backend**: ~1.5 - 2.5 GB

### Frontend Dependencies
- **node_modules/**: ~300-500 MB
- **Build output (dist/)**: ~5-10 MB

---

## ⚠️ Heavy Storage Libraries - YES!

### You ARE Using Heavy Libraries:

1. **PyTorch (torch==2.8.0)**: 
   - ✅ **800 MB - 1.5 GB** (CPU version)
   - Used for: Sentence transformers ML model
   - **Impact**: Slow Render builds, high memory usage

2. **Transformers (transformers==4.57.0)**:
   - ✅ **~400 MB**
   - Used for: NLP models from Hugging Face
   - **Impact**: Longer deployment times

3. **Sentence Transformers**:
   - ✅ **~100 MB** (plus model cache)
   - Downloads model: `all-MiniLM-L6-v2` (~80 MB)
   - **Impact**: First deployment downloads models

### Where They're Used:
```python
# Backend/app/services/universal_search_service.py
from sentence_transformers import SentenceTransformer

def __init__(self):
    self.model = SentenceTransformer('all-MiniLM-L6-v2')
    # Uses PyTorch under the hood
```

---

## 🚨 Deployment Impact

### Render Free Tier Considerations:

1. **Build Time**: 
   - PyTorch + Transformers = **+5-7 minutes** to build time
   - Model downloads = **+2-3 minutes**
   - **Total first build**: 10-15 minutes

2. **Disk Space**:
   - Free tier has limited ephemeral storage
   - PyTorch alone: ~1.5 GB
   - Should fit but leaves less room

3. **Memory Usage**:
   - Free tier: 512 MB RAM
   - PyTorch + Model loaded: ~300-400 MB
   - **TIGHT but should work**

4. **Cold Start**:
   - Loading PyTorch + model takes 10-20 seconds
   - **First request after spin-down will be SLOW**

---

## ❌ Unused Libraries (Should Remove)

These are in `requirements.txt` but **NOT USED**:

```python
streamlit==1.28.1         # ❌ NOT USED (~30 MB)
plotly==5.17.0            # ❌ NOT USED (~50 MB)
elasticsearch==8.11.0     # ❌ NOT USED (~5 MB)
```

**Savings**: ~85 MB if removed

---

## ✅ Optimization Recommendations

### Option 1: Keep Current Setup (Recommended)
- ✅ Semantic search works (high quality)
- ⚠️ Slow first load after spin-down
- ⚠️ Longer build times
- ✅ Good user experience after warm-up

### Option 2: Remove Heavy ML Libraries
**If you want lighter deployment:**

1. Remove from `requirements.txt`:
   ```
   torch==2.8.0
   transformers==4.57.0
   sentence-transformers==5.1.1
   scipy==1.16.2
   streamlit==1.28.1
   plotly==5.17.0
   elasticsearch==8.11.0
   ```

2. Update search service to use **simple text matching** (no ML)

**Trade-offs**:
- ✅ **Much faster** builds (~2-3 min vs 10-15 min)
- ✅ **Lower memory** usage (~100 MB vs 400 MB)
- ✅ **Faster cold starts** (5 sec vs 20 sec)
- ❌ **Lower quality** search results
- ❌ No semantic understanding

### Option 3: Hybrid Approach
- Use ML libraries in **local development**
- Use **simple search** in production (Render)
- Add feature flag to switch between modes

---

## 📊 Summary

| Aspect | Status |
|--------|--------|
| **Environment** | ✅ Conda (Anaconda3) + venv |
| **Python Version** | ✅ 3.12.7 |
| **Heavy Libraries** | ⚠️ **YES** - PyTorch (~1.5 GB) |
| **Total Backend Size** | ⚠️ **1.5 - 2.5 GB** |
| **Render Compatible** | ✅ **YES** (but slow builds) |
| **Memory Fit** | ⚠️ **TIGHT** (should work) |
| **Unused Bloat** | ❌ ~85 MB (streamlit, plotly, elasticsearch) |

---

## 🎯 Current State: **DEPLOYMENT READY**

Your project **WILL deploy** to Render with current libraries, but:
- ⚠️ **Expect 10-15 minute first build**
- ⚠️ **Cold starts will be 20-30 seconds**
- ⚠️ **Memory usage near free tier limit**

**Recommendation**: Deploy as-is first, optimize later if needed.

---

**Analysis Date**: October 19, 2025
**Environment**: Conda (Anaconda3) + Python 3.12.7
**Heavy Libraries**: PyTorch 2.8.0, Transformers 4.57.0
**Deployment Impact**: Medium (slower builds, higher memory)
