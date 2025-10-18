#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Database setup
echo "🗄️ Setting up database..."
echo "Database URL: ${DATABASE_URL:0:30}..." # Show first 30 chars only

# Check if database is accessible
python -c "
from app.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Create tables if they don't exist
echo "📋 Creating database tables..."
python -c "
from app.database import engine, Base
from app.models.law_models import LawSection, LegalCase, CaseCitation, CaseSectionAssociation, CaseSimilarity, LawAmendment, SearchQuery
from app.models.chat_models import ChatConversation, ChatMessage

# Import all models to ensure they're registered
print('Creating tables...')
Base.metadata.create_all(bind=engine)
print('✅ Tables created successfully!')
"

# Download ML models (sentence-transformers cache)
echo "🤖 Downloading ML models..."
python -c "
from sentence_transformers import SentenceTransformer
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print('✅ ML model downloaded successfully!')
except Exception as e:
    print(f'⚠️ ML model download failed (will retry at runtime): {e}')
"

echo "✅ Build completed successfully!"
