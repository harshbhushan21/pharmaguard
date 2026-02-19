"""Pydantic schemas for request/response models."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLabel(str, Enum):
    """Risk assessment labels."""
    SAFE = "Safe"
    ADJUST_DOSAGE = "Adjust Dosage"
    TOXIC = "Toxic"
    INEFFECTIVE = "Ineffective"
    UNKNOWN = "Unknown"


class Severity(str, Enum):
    """Severity levels."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class Phenotype(str, Enum):
    """Phenotype classifications."""
    PM = "PM"  # Poor Metabolizer
    IM = "IM"  # Intermediate Metabolizer
    NM = "NM"  # Normal Metabolizer
    RM = "RM"  # Rapid Metabolizer
    URM = "URM"  # Ultrarapid Metabolizer
    UNKNOWN = "Unknown"


class Variant(BaseModel):
    """Variant information model."""
    rsid: str = Field(..., description="dbSNP ID")
    gene: str = Field(..., description="Gene symbol")
    star_allele: Optional[str] = Field(None, description="Star allele designation")
    chromosome: Optional[str] = None
    position: Optional[int] = None
    ref_allele: Optional[str] = None
    alt_allele: Optional[str] = None
    quality: Optional[float] = None
    genotype: Optional[str] = None


class PharmacogenomicProfile(BaseModel):
    """Pharmacogenomic profile model."""
    primary_gene: str = Field(..., description="Primary gene affecting drug metabolism")
    diplotype: str = Field(..., description="Diplotype designation (e.g., *1/*2)")
    phenotype: Phenotype = Field(..., description="Phenotype classification")
    detected_variants: List[Variant] = Field(default_factory=list, description="List of detected variants")


class RiskAssessment(BaseModel):
    """Risk assessment model."""
    risk_label: RiskLabel = Field(..., description="Risk classification")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    severity: Severity = Field(..., description="Severity level")


class ClinicalRecommendation(BaseModel):
    """Clinical recommendation model."""
    action: str = Field(..., description="Recommended action")
    dosage_adjustment: Optional[str] = Field(None, description="Dosage adjustment guidance")
    monitoring: Optional[str] = Field(None, description="Monitoring requirements")
    alternative_drugs: Optional[List[str]] = Field(None, description="Alternative drug options")
    cpic_guideline: Optional[str] = Field(None, description="CPIC guideline reference")


class LLMExplanation(BaseModel):
    """LLM-generated explanation model."""
    summary: str = Field(..., description="Summary of the pharmacogenomic risk")
    mechanism: str = Field(..., description="Biological mechanism explanation")
    variant_citations: List[str] = Field(default_factory=list, description="Cited variant rsIDs")
    clinical_significance: str = Field(..., description="Clinical significance")


class QualityMetrics(BaseModel):
    """Quality metrics model."""
    vcf_parsing_success: bool = Field(..., description="Whether VCF parsing succeeded")
    variant_count: int = Field(..., ge=0, description="Total number of variants detected")
    target_gene_variants: int = Field(..., ge=0, description="Variants in target genes")
    missing_annotations: List[str] = Field(default_factory=list, description="Missing annotation fields")
    parsing_warnings: List[str] = Field(default_factory=list, description="Parsing warnings")


class AnalysisRequest(BaseModel):
    """Analysis request model."""
    drugs: str = Field(..., description="Comma-separated drug names")
    patient_id: Optional[str] = Field(None, description="Optional patient identifier")


class AnalysisResponse(BaseModel):
    """Complete analysis response model matching the required JSON schema."""
    patient_id: str = Field(..., description="Patient identifier")
    drug: str = Field(..., description="Drug name")
    timestamp: str = Field(..., description="ISO8601 timestamp")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment")
    pharmacogenomic_profile: PharmacogenomicProfile = Field(..., description="Pharmacogenomic profile")
    clinical_recommendation: ClinicalRecommendation = Field(..., description="Clinical recommendation")
    llm_generated_explanation: LLMExplanation = Field(..., description="LLM-generated explanation")
    quality_metrics: QualityMetrics = Field(..., description="Quality metrics")
