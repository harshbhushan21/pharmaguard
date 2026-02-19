"""Tests for phenotype determination."""
import pytest
from backend.app.phenotype import (
    determine_phenotype,
    get_phenotype_from_diplotype,
    infer_star_allele_from_rsid,
    get_primary_gene_for_drug
)
from backend.app.schemas import Variant, Phenotype


def test_determine_phenotype():
    """Test phenotype determination."""
    variants = [
        Variant(rsid="rs3892097", gene="CYP2D6", star_allele="*4"),
        Variant(rsid="rs1065852", gene="CYP2D6", star_allele="*10")
    ]
    
    diplotype, phenotype = determine_phenotype("CYP2D6", variants)
    assert diplotype in ["*4/*10", "*10/*4"]
    assert phenotype in [Phenotype.PM, Phenotype.IM]


def test_get_phenotype_from_diplotype():
    """Test phenotype from diplotype."""
    phenotype = get_phenotype_from_diplotype("CYP2D6", "*4/*4")
    assert phenotype == Phenotype.PM


def test_infer_star_allele_from_rsid():
    """Test star allele inference from rsid."""
    result = infer_star_allele_from_rsid("CYP2D6", "rs1065852")
    assert result == "*10"


def test_get_primary_gene_for_drug():
    """Test primary gene lookup."""
    assert get_primary_gene_for_drug("CODEINE") == "CYP2D6"
    assert get_primary_gene_for_drug("WARFARIN") == "CYP2C9"
    assert get_primary_gene_for_drug("UNKNOWN") == "UNKNOWN"
