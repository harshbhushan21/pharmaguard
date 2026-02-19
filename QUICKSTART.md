# Quick Start Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

## Quick Setup (5 minutes)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
uvicorn app.main:app --reload
```

### 2. Frontend Setup (New Terminal)
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 3. Test the Application
1. Open http://localhost:3000
2. Upload `sample_data/patient_001.vcf`
3. Enter drug: `CODEINE`
4. Click "Analyze Risk"

## Docker Quick Start
```bash
# Create .env file in root with OPENAI_API_KEY
docker-compose up --build
```

## Testing
```bash
cd backend
pytest tests/
```

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (should be 3.11+)
- Verify dependencies: `pip install -r requirements.txt`

**Frontend won't start:**
- Check Node version: `node --version` (should be 18+)
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

**API connection errors:**
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/config.py`
- Verify `VITE_API_URL` in `frontend/.env`

**VCF parsing errors:**
- Ensure VCF file follows v4.2 format
- Check that INFO fields contain GENE, STAR, RS tags
- Verify file size is under 5MB
