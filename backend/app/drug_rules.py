"""Drug risk assessment engine based on CPIC guidelines."""
from typing import Dict, Tuple
from .schemas import RiskLabel, Severity, Phenotype, ClinicalRecommendation, RiskAssessment
from .phenotype import get_primary_gene_for_drug


def assess_drug_risk(drug: str, phenotype: Phenotype, gene: str) -> Tuple[RiskAssessment, ClinicalRecommendation]:
    """
    Assess drug risk based on phenotype and CPIC guidelines.
    
    Args:
        drug: Drug name
        phenotype: Patient phenotype
        gene: Gene symbol
        
    Returns:
        Tuple of (RiskAssessment, ClinicalRecommendation)
    """
    drug_upper = drug.upper()
    
    # CPIC guideline implementations
    if drug_upper == "CODEINE":
        return assess_codeine_risk(phenotype)
    elif drug_upper == "WARFARIN":
        return assess_warfarin_risk(phenotype)
    elif drug_upper == "CLOPIDOGREL":
        return assess_clopidogrel_risk(phenotype)
    elif drug_upper == "SIMVASTATIN":
        return assess_simvastatin_risk(phenotype)
    elif drug_upper == "AZATHIOPRINE":
        return assess_azathioprine_risk(phenotype)
    elif drug_upper == "FLUOROURACIL":
        return assess_fluorouracil_risk(phenotype)
    else:
        return (
            RiskAssessment(
                risk_label=RiskLabel.UNKNOWN,
                confidence_score=0.0,
                severity=Severity.NONE
            ),
            ClinicalRecommendation(
                action="Drug not supported for pharmacogenomic analysis",
                cpic_guideline="N/A"
            )
        )


def assess_codeine_risk(phenotype: Phenotype) -> Tuple[RiskAssessment, ClinicalRecommendation]:
    """Assess CODEINE risk based on CYP2D6 phenotype."""
    if phenotype == Phenotype.PM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.INEFFECTIVE,
                confidence_score=0.95,
                severity=Severity.HIGH
            ),
            ClinicalRecommendation(
                action="Avoid codeine - poor conversion to active metabolite",
                dosage_adjustment="Consider alternative analgesic (e.g., morphine, oxycodone)",
                monitoring="Monitor for inadequate pain relief",
                alternative_drugs=["MORPHINE", "OXYCODONE", "HYDROMORPHONE"],
                cpic_guideline="CPIC Guideline for Codeine and CYP2D6"
            )
        )
    elif phenotype == Phenotype.IM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.ADJUST_DOSAGE,
                confidence_score=0.85,
                severity=Severity.MODERATE
            ),
            ClinicalRecommendation(
                action="Reduced efficacy expected",
                dosage_adjustment="Consider alternative analgesic or increased monitoring",
                monitoring="Monitor for inadequate pain relief",
                cpic_guideline="CPIC Guideline for Codeine and CYP2D6"
            )
        )
    elif phenotype == Phenotype.URM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.TOXIC,
                confidence_score=0.95,
                severity=Severity.CRITICAL
            ),
            ClinicalRecommendation(
                action="Increased risk of toxicity - avoid codeine",
                dosage_adjustment="Avoid codeine due to rapid conversion to morphine",
                monitoring="Monitor for respiratory depression and excessive sedation",
                alternative_drugs=["MORPHINE", "OXYCODONE"],
                cpic_guideline="CPIC Guideline for Codeine and CYP2D6"
            )
        )
    elif phenotype == Phenotype.RM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.ADJUST_DOSAGE,
                confidence_score=0.80,
                severity=Severity.MODERATE
            ),
            ClinicalRecommendation(
                action="Increased conversion to active metabolite",
                dosage_adjustment="Consider lower starting dose or alternative",
                monitoring="Monitor for signs of toxicity",
                cpic_guideline="CPIC Guideline for Codeine and CYP2D6"
            )
        )
    else:  # NM or Unknown
        return (
            RiskAssessment(
                risk_label=RiskLabel.SAFE,
                confidence_score=0.90 if phenotype == Phenotype.NM else 0.50,
                severity=Severity.NONE
            ),
            ClinicalRecommendation(
                action="Standard dosing recommended",
                cpic_guideline="CPIC Guideline for Codeine and CYP2D6"
            )
        )


def assess_warfarin_risk(phenotype: Phenotype) -> Tuple[RiskAssessment, ClinicalRecommendation]:
    """Assess WARFARIN risk based on CYP2C9 phenotype."""
    if phenotype == Phenotype.PM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.TOXIC,
                confidence_score=0.90,
                severity=Severity.HIGH
            ),
            ClinicalRecommendation(
                action="Increased bleeding risk - reduce starting dose",
                dosage_adjustment="Reduce starting dose by 30-50%",
                monitoring="Frequent INR monitoring required",
                cpic_guideline="CPIC Guideline for Warfarin and CYP2C9"
            )
        )
    elif phenotype == Phenotype.IM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.ADJUST_DOSAGE,
                confidence_score=0.85,
                severity=Severity.MODERATE
            ),
            ClinicalRecommendation(
                action="Reduced clearance - lower maintenance dose",
                dosage_adjustment="Reduce starting dose by 20-30%",
                monitoring="Frequent INR monitoring required",
                cpic_guideline="CPIC Guideline for Warfarin and CYP2C9"
            )
        )
    else:  # NM or Unknown
        return (
            RiskAssessment(
                risk_label=RiskLabel.SAFE,
                confidence_score=0.90 if phenotype == Phenotype.NM else 0.50,
                severity=Severity.NONE
            ),
            ClinicalRecommendation(
                action="Standard dosing recommended",
                monitoring="Standard INR monitoring",
                cpic_guideline="CPIC Guideline for Warfarin and CYP2C9"
            )
        )


def assess_clopidogrel_risk(phenotype: Phenotype) -> Tuple[RiskAssessment, ClinicalRecommendation]:
    """Assess CLOPIDOGREL risk based on CYP2C19 phenotype."""
    if phenotype == Phenotype.PM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.INEFFECTIVE,
                confidence_score=0.95,
                severity=Severity.HIGH
            ),
            ClinicalRecommendation(
                action="Reduced antiplatelet effect - consider alternative",
                dosage_adjustment="Consider alternative antiplatelet agent",
                monitoring="Monitor for cardiovascular events",
                alternative_drugs=["PRASUGREL", "TICAGRELOR"],
                cpic_guideline="CPIC Guideline for Clopidogrel and CYP2C19"
            )
        )
    elif phenotype == Phenotype.IM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.ADJUST_DOSAGE,
                confidence_score=0.85,
                severity=Severity.MODERATE
            ),
            ClinicalRecommendation(
                action="Reduced antiplatelet effect",
                dosage_adjustment="Consider higher dose or alternative agent",
                monitoring="Monitor for cardiovascular events",
                cpic_guideline="CPIC Guideline for Clopidogrel and CYP2C19"
            )
        )
    elif phenotype == Phenotype.RM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.SAFE,
                confidence_score=0.90,
                severity=Severity.NONE
            ),
            ClinicalRecommendation(
                action="Enhanced antiplatelet effect",
                cpic_guideline="CPIC Guideline for Clopidogrel and CYP2C19"
            )
        )
    else:  # NM or Unknown
        return (
            RiskAssessment(
                risk_label=RiskLabel.SAFE,
                confidence_score=0.90 if phenotype == Phenotype.NM else 0.50,
                severity=Severity.NONE
            ),
            ClinicalRecommendation(
                action="Standard dosing recommended",
                cpic_guideline="CPIC Guideline for Clopidogrel and CYP2C19"
            )
        )


def assess_simvastatin_risk(phenotype: Phenotype) -> Tuple[RiskAssessment, ClinicalRecommendation]:
    """Assess SIMVASTATIN risk based on SLCO1B1 phenotype."""
    if phenotype == Phenotype.PM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.TOXIC,
                confidence_score=0.90,
                severity=Severity.HIGH
            ),
            ClinicalRecommendation(
                action="Increased myopathy risk - reduce dose or avoid",
                dosage_adjustment="Reduce dose by 50% or use alternative statin",
                monitoring="Monitor for muscle symptoms and CK levels",
                alternative_drugs=["PRAVASTATIN", "ROSUVASTATIN"],
                cpic_guideline="CPIC Guideline for Simvastatin and SLCO1B1"
            )
        )
    elif phenotype == Phenotype.IM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.ADJUST_DOSAGE,
                confidence_score=0.85,
                severity=Severity.MODERATE
            ),
            ClinicalRecommendation(
                action="Increased myopathy risk",
                dosage_adjustment="Consider lower dose or alternative statin",
                monitoring="Monitor for muscle symptoms",
                cpic_guideline="CPIC Guideline for Simvastatin and SLCO1B1"
            )
        )
    else:  # NM or Unknown
        return (
            RiskAssessment(
                risk_label=RiskLabel.SAFE,
                confidence_score=0.90 if phenotype == Phenotype.NM else 0.50,
                severity=Severity.NONE
            ),
            ClinicalRecommendation(
                action="Standard dosing recommended",
                cpic_guideline="CPIC Guideline for Simvastatin and SLCO1B1"
            )
        )


def assess_azathioprine_risk(phenotype: Phenotype) -> Tuple[RiskAssessment, ClinicalRecommendation]:
    """Assess AZATHIOPRINE risk based on TPMT phenotype."""
    if phenotype == Phenotype.PM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.TOXIC,
                confidence_score=0.95,
                severity=Severity.CRITICAL
            ),
            ClinicalRecommendation(
                action="Severe myelosuppression risk - avoid azathioprine",
                dosage_adjustment="Avoid azathioprine - use alternative immunosuppressant",
                monitoring="If used, frequent CBC monitoring required",
                alternative_drugs=["MERCAPTOPURINE", "MYCOPHENOLATE"],
                cpic_guideline="CPIC Guideline for Azathioprine and TPMT"
            )
        )
    elif phenotype == Phenotype.IM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.ADJUST_DOSAGE,
                confidence_score=0.90,
                severity=Severity.HIGH
            ),
            ClinicalRecommendation(
                action="Increased myelosuppression risk - reduce dose",
                dosage_adjustment="Reduce dose by 30-50%",
                monitoring="Frequent CBC monitoring required",
                cpic_guideline="CPIC Guideline for Azathioprine and TPMT"
            )
        )
    else:  # NM or Unknown
        return (
            RiskAssessment(
                risk_label=RiskLabel.SAFE,
                confidence_score=0.90 if phenotype == Phenotype.NM else 0.50,
                severity=Severity.NONE
            ),
            ClinicalRecommendation(
                action="Standard dosing recommended",
                monitoring="Standard CBC monitoring",
                cpic_guideline="CPIC Guideline for Azathioprine and TPMT"
            )
        )


def assess_fluorouracil_risk(phenotype: Phenotype) -> Tuple[RiskAssessment, ClinicalRecommendation]:
    """Assess FLUOROURACIL risk based on DPYD phenotype."""
    if phenotype == Phenotype.PM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.TOXIC,
                confidence_score=0.95,
                severity=Severity.CRITICAL
            ),
            ClinicalRecommendation(
                action="Severe toxicity risk - avoid fluorouracil",
                dosage_adjustment="Avoid fluorouracil - use alternative chemotherapy",
                monitoring="If used, intensive monitoring required",
                alternative_drugs=["CAPECITABINE", "Alternative chemotherapy regimens"],
                cpic_guideline="CPIC Guideline for Fluorouracil and DPYD"
            )
        )
    elif phenotype == Phenotype.IM:
        return (
            RiskAssessment(
                risk_label=RiskLabel.ADJUST_DOSAGE,
                confidence_score=0.90,
                severity=Severity.HIGH
            ),
            ClinicalRecommendation(
                action="Increased toxicity risk - reduce dose",
                dosage_adjustment="Reduce starting dose by 50%",
                monitoring="Frequent monitoring for toxicity",
                cpic_guideline="CPIC Guideline for Fluorouracil and DPYD"
            )
        )
    else:  # NM or Unknown
        return (
            RiskAssessment(
                risk_label=RiskLabel.SAFE,
                confidence_score=0.90 if phenotype == Phenotype.NM else 0.50,
                severity=Severity.NONE
            ),
            ClinicalRecommendation(
                action="Standard dosing recommended",
                monitoring="Standard toxicity monitoring",
                cpic_guideline="CPIC Guideline for Fluorouracil and DPYD"
            )
        )
