"""Tests for drug risk assessment."""
import pytest
from backend.app.drug_rules import assess_drug_risk
from backend.app.schemas import Phenotype, RiskLabel, Severity


def test_assess_codeine_pm():
    """Test CODEINE risk assessment for PM phenotype."""
    risk, rec = assess_drug_risk("CODEINE", Phenotype.PM, "CYP2D6")
    assert risk.risk_label == RiskLabel.INEFFECTIVE
    assert risk.severity == Severity.HIGH


def test_assess_codeine_urm():
    """Test CODEINE risk assessment for URM phenotype."""
    risk, rec = assess_drug_risk("CODEINE", Phenotype.URM, "CYP2D6")
    assert risk.risk_label == RiskLabel.TOXIC
    assert risk.severity == Severity.CRITICAL


def test_assess_warfarin_im():
    """Test WARFARIN risk assessment for IM phenotype."""
    risk, rec = assess_drug_risk("WARFARIN", Phenotype.IM, "CYP2C9")
    assert risk.risk_label == RiskLabel.ADJUST_DOSAGE
    assert risk.severity == Severity.MODERATE


def test_assess_clopidogrel_pm():
    """Test CLOPIDOGREL risk assessment for PM phenotype."""
    risk, rec = assess_drug_risk("CLOPIDOGREL", Phenotype.PM, "CYP2C19")
    assert risk.risk_label == RiskLabel.INEFFECTIVE
    assert "alternative" in rec.action.lower()


def test_assess_azathioprine_pm():
    """Test AZATHIOPRINE risk assessment for PM phenotype."""
    risk, rec = assess_drug_risk("AZATHIOPRINE", Phenotype.PM, "TPMT")
    assert risk.risk_label == RiskLabel.TOXIC
    assert risk.severity == Severity.CRITICAL


def test_assess_fluorouracil_pm():
    """Test FLUOROURACIL risk assessment for PM phenotype."""
    risk, rec = assess_drug_risk("FLUOROURACIL", Phenotype.PM, "DPYD")
    assert risk.risk_label == RiskLabel.TOXIC
    assert risk.severity == Severity.CRITICAL
