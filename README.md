# PharmaGuard

**AI-Powered Pharmacogenomic Risk Assessment Platform**

PharmaGuard is a web application that analyzes patient genetic data (VCF files) and drug names to predict personalized pharmacogenomic risks and provide clinically actionable recommendations with LLM-generated explanations.


## Live Demo

- **Live Application**: [https://pharmaguard-two.vercel.app/]
- **LinkedIn Video**: [Video Link - To be added]

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [Team](#team)

## Features

- **VCF File Parsing**: Parses authentic VCF files (Variant Call Format v4.2) to extract pharmacogenomic variants
- **Variant Detection**: Identifies variants across 6 critical genes:
  - CYP2D6 (Codeine metabolism)
  - CYP2C19 (Clopidogrel metabolism)
  - CYP2C9 (Warfarin metabolism)
  - SLCO1B1 (Simvastatin transport)
  - TPMT (Azathioprine metabolism)
  - DPYD (Fluorouracil metabolism)
- **Risk Assessment**: Predicts drug-specific risks:
  - Safe
  - Adjust Dosage
  - Toxic
  - Ineffective
  - Unknown
- **Clinical Recommendations**: Provides CPIC guideline-aligned dosing recommendations
- **AI Explanations**: Generates detailed clinical explanations using LLM with variant citations and biological mechanisms
- **Modern UI**: Clean, responsive web interface with drag-and-drop file upload

## Architecture

```
┌─────────────────┐
│   React Frontend │
│   (Vite + React) │
└────────┬─────────┘
         │ HTTP/REST
         │
┌────────▼─────────┐
│  FastAPI Backend  │
│   (Python 3.11)   │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ VCF   │ │ OpenAI│
│Parser │ │  API  │
└───────┘ └───────┘
```

### Data Flow

1. User uploads VCF file and enters drug name(s)
2. Frontend sends file and drug data to backend API
3. Backend parses VCF file to extract variants
4. Variants are mapped to star alleles and phenotypes
5. Drug risk is assessed based on CPIC guidelines
6. LLM generates clinical explanation
7. Results are returned as structured JSON
8. Frontend displays results with color-coded risk levels

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11** - Programming language
- **Pydantic** - Data validation
- **OpenAI API** - LLM for generating explanations
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **React Dropzone** - File upload component

### Deployment
- **Vercel** - Frontend hosting
- **Render** - Backend hosting

## Installation

### Prerequisites

- Python 3.11, 3.12, or 3.13 (Python 3.13 requires Pydantic 2.8.0+)
- Node.js 18+
- OpenAI API key (for LLM explanations)

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pharmaguard
```

2. Navigate to backend directory:
```bash
cd backend
```

3. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create `.env` file:
```bash
cp .env.example .env
```

6. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

7. Run the backend:
```bash
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Edit `.env` if backend is running on different port:
```
VITE_API_URL=http://localhost:8000
```

5. Run the frontend:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`


## Usage

### Web Interface

1. Open the application in your browser
2. Upload a VCF file (drag-and-drop or click to select)
3. Enter drug name(s) (comma-separated for multiple drugs)
4. Optionally enter a patient ID
5. Click "Analyze Risk"
6. View results with:
   - Risk assessment (color-coded)
   - Pharmacogenomic profile
   - Clinical recommendations
   - AI-generated explanation
   - Quality metrics
7. Download or copy JSON results

### Supported Drugs

- CODEINE
- WARFARIN
- CLOPIDOGREL
- SIMVASTATIN
- AZATHIOPRINE
- FLUOROURACIL

### Sample VCF Files

Sample VCF files are available in the `sample_data/` directory:
- `patient_001.vcf` - Sample patient with multiple variants
- `patient_002.vcf` - Sample patient with normal metabolizer variants

## API Documentation

### Endpoints

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "PharmaGuard API"
}
```

#### `GET /api/drugs`
Get list of supported drugs.

**Response:**
```json
{
  "drugs": ["CODEINE", "WARFARIN", "CLOPIDOGREL", "SIMVASTATIN", "AZATHIOPRINE", "FLUOROURACIL"]
}
```

#### `POST /api/analyze`
Main analysis endpoint.

**Request:**
- `vcf_file` (file): VCF file (multipart/form-data)
- `drugs` (string): Comma-separated drug names
- `patient_id` (string, optional): Patient identifier

**Response:**
```json
{
  "patient_id": "PATIENT_XXX",
  "drug": "DRUG_NAME",
  "timestamp": "ISO8601_timestamp",
  "risk_assessment": {
    "risk_label": "Safe|Adjust Dosage|Toxic|Ineffective|Unknown",
    "confidence_score": 0.0,
    "severity": "none|low|moderate|high|critical"
  },
  "pharmacogenomic_profile": {
    "primary_gene": "GENE_SYMBOL",
    "diplotype": "*X/*Y",
    "phenotype": "PM|IM|NM|RM|URM|Unknown",
    "detected_variants": [
      {
        "rsid": "rsXXXX",
        "gene": "GENE",
        "star_allele": "*X",
        ...
      }
    ]
  },
  "clinical_recommendation": {
    "action": "...",
    "dosage_adjustment": "...",
    "monitoring": "...",
    "alternative_drugs": [...],
    "cpic_guideline": "..."
  },
  "llm_generated_explanation": {
    "summary": "...",
    "mechanism": "...",
    "variant_citations": [...],
    "clinical_significance": "..."
  },
  "quality_metrics": {
    "vcf_parsing_success": true,
    "variant_count": 0,
    "target_gene_variants": 0,
    "missing_annotations": [],
    "parsing_warnings": []
  }
}
```

## Deployment

### Backend Deployment (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `OPENAI_API_KEY`
   - `CORS_ORIGINS` (your frontend URL)
6. Deploy

### Frontend Deployment (Vercel)

1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to frontend directory: `cd frontend`
3. Run: `vercel`
4. Configure environment variables:
   - `VITE_API_URL` (your backend URL)
5. Deploy


## Project Structure

```
pharmaguard-1/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── schemas.py           # Pydantic models
│   │   ├── vcf_parser.py        # VCF file parser
│   │   ├── phenotype.py         # Phenotype determination
│   │   ├── drug_rules.py        # Drug risk assessment
│   │   └── llm.py               # LLM integration
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── DrugInput.jsx
│   │   │   ├── ResultsDisplay.jsx
│   │   │   └── ErrorDisplay.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── .env.example
├── sample_data/
│   ├── patient_001.vcf
│   └── patient_002.vcf
├── tests/
│   ├── test_vcf_parser.py
│   ├── test_phenotype.py
│   ├── test_drug_rules.py
│   └── test_api.py
├── docker-compose.yml
├── vercel.json
├── render.yaml
├── netlify.toml
└── README.md
```

## Team

- Natasha Agarwal
- Disha Kurkuri
- Disha R Rao
- Harsh Bhushan



**Note**: This application is for educational and research purposes. Clinical decisions should always be made in consultation with qualified healthcare professionals.
