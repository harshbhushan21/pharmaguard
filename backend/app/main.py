"""FastAPI main application."""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import io

from .config import settings
from .schemas import (
    AnalysisRequest,
    AnalysisResponse,
    Variant,
    PharmacogenomicProfile,
    RiskAssessment,
    ClinicalRecommendation,
    LLMExplanation,
    QualityMetrics,
    Phenotype,
    DrugAnalysisResult,
)
from .vcf_parser import parse_vcf_file
from .phenotype import determine_phenotype, get_primary_gene_for_drug
from .drug_rules import assess_drug_risk
from .llm import generate_explanation

app = FastAPI(
    title="PharmaGuard API",
    description="AI-powered pharmacogenomic risk assessment API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PharmaGuard API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "drugs": "/api/drugs",
            "analyze": "/api/analyze"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "PharmaGuard API"}


@app.get("/api/drugs")
async def get_supported_drugs():
    """Get list of supported drugs."""
    return {"drugs": settings.supported_drugs}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_pharmacogenomics(
    vcf_file: UploadFile = File(..., description="VCF file upload"),
    drugs: str = Form(..., description="Comma-separated drug names"),
    patient_id: Optional[str] = Form(None, description="Optional patient ID")
):
    """
    Main analysis endpoint for pharmacogenomic risk assessment.
    
    Accepts VCF file and drug name(s), returns comprehensive risk assessment.
    """
    try:
        # Validate file
        if not vcf_file.filename.endswith('.vcf'):
            raise HTTPException(status_code=400, detail="File must be a .vcf file")
        
        # Read file content
        file_content = await vcf_file.read()
        
        # Check file size (5MB limit)
        max_size = settings.max_file_size_mb * 1024 * 1024
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {settings.max_file_size_mb}MB limit"
            )
        
        # Parse drugs
        drug_list = [d.strip().upper() for d in drugs.split(',') if d.strip()]
        if not drug_list:
            raise HTTPException(status_code=400, detail="At least one drug must be provided")

        # Validate drugs
        invalid_drugs = [d for d in drug_list if d not in settings.supported_drugs]
        if invalid_drugs:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported drugs: {', '.join(invalid_drugs)}. Supported: {', '.join(settings.supported_drugs)}"
            )
        
        # Parse VCF file once (shared across drugs)
        variants, warnings = parse_vcf_file(file_content)
        
        # If no variants were parsed, treat this as an invalid VCF and
        # return a clear client error instead of proceeding with analysis.
        if not variants:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No pharmacogenomic variants could be parsed from the VCF file. "
                    "Please ensure the file is a valid VCF with the required annotations."
                ),
            )

        # Build per-drug results
        per_drug_results = []
        for drug in drug_list:
            primary_gene = get_primary_gene_for_drug(drug)

            # Filter variants for primary gene
            gene_variants = [v for v in variants if v.gene == primary_gene]

            # Determine phenotype
            diplotype, phenotype = determine_phenotype(primary_gene, gene_variants)

            # Assess drug risk
            risk_assessment, clinical_recommendation = assess_drug_risk(drug, phenotype, primary_gene)

            # Generate LLM explanation
            llm_explanation = generate_explanation(
                drug=drug,
                gene=primary_gene,
                phenotype=phenotype,
                diplotype=diplotype,
                variants=gene_variants,
                risk_label=risk_assessment.risk_label.value,
                clinical_recommendation=clinical_recommendation.action,
            )

            # Create pharmacogenomic profile
            profile = PharmacogenomicProfile(
                primary_gene=primary_gene,
                diplotype=diplotype,
                phenotype=phenotype,
                detected_variants=gene_variants,
            )

            # Quality metrics (per drug)
            quality_metrics = QualityMetrics(
                vcf_parsing_success=len(warnings) == 0,
                variant_count=len(variants),
                target_gene_variants=len(gene_variants),
                missing_annotations=[],
                parsing_warnings=warnings,
            )

            per_drug_results.append(
                DrugAnalysisResult(
                    drug=drug,
                    risk_assessment=RiskAssessment(**risk_assessment.model_dump()),
                    pharmacogenomic_profile=PharmacogenomicProfile(**profile.model_dump()),
                    clinical_recommendation=ClinicalRecommendation(**clinical_recommendation.model_dump()),
                    llm_generated_explanation=LLMExplanation(**llm_explanation.model_dump()),
                    quality_metrics=QualityMetrics(**quality_metrics.model_dump()),
                )
            )

        # Use the first drug's result for backward-compatible top-level fields
        primary_result = per_drug_results[0]
        primary_drug = primary_result.drug
        
        # Generate patient ID if not provided
        if not patient_id:
            patient_id = f"PATIENT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create response
        response = AnalysisResponse(
            patient_id=patient_id,
            drug=primary_drug,
            timestamp=datetime.now().isoformat(),
            risk_assessment=primary_result.risk_assessment,
            pharmacogenomic_profile=primary_result.pharmacogenomic_profile,
            clinical_recommendation=primary_result.clinical_recommendation,
            llm_generated_explanation=primary_result.llm_generated_explanation,
            quality_metrics=primary_result.quality_metrics,
            all_drugs_results=per_drug_results if len(per_drug_results) > 1 else None,
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
