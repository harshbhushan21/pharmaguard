"""Phenotype determination from pharmacogenomic variants."""
from typing import List, Dict, Optional, Tuple
from .schemas import Variant, Phenotype
from .config import settings


# Star allele to phenotype mapping for each gene
# This is a simplified mapping - real implementations would use comprehensive databases
STAR_ALLELE_PHENOTYPES: Dict[str, Dict[str, Phenotype]] = {
    "CYP2D6": {
        "*1": Phenotype.NM,  # Normal function
        "*2": Phenotype.NM,  # Normal function
        "*3": Phenotype.PM,  # No function
        "*4": Phenotype.PM,  # No function
        "*5": Phenotype.PM,  # No function (deletion)
        "*6": Phenotype.PM,  # No function
        "*9": Phenotype.IM,  # Decreased function
        "*10": Phenotype.IM,  # Decreased function
        "*17": Phenotype.IM,  # Decreased function
        "*29": Phenotype.IM,  # Decreased function
        "*41": Phenotype.IM,  # Decreased function
        "*2xN": Phenotype.RM,  # Increased function (duplication)
        "*35x2": Phenotype.RM,  # Increased function
    },
    "CYP2C19": {
        "*1": Phenotype.NM,  # Normal function
        "*2": Phenotype.PM,  # No function
        "*3": Phenotype.PM,  # No function
        "*4": Phenotype.PM,  # No function
        "*5": Phenotype.PM,  # No function
        "*6": Phenotype.PM,  # No function
        "*7": Phenotype.PM,  # No function
        "*8": Phenotype.PM,  # No function
        "*17": Phenotype.RM,  # Increased function
    },
    "CYP2C9": {
        "*1": Phenotype.NM,  # Normal function
        "*2": Phenotype.IM,  # Decreased function
        "*3": Phenotype.IM,  # Decreased function
        "*5": Phenotype.IM,  # Decreased function
        "*6": Phenotype.IM,  # Decreased function
        "*11": Phenotype.IM,  # Decreased function
    },
    "SLCO1B1": {
        "*1": Phenotype.NM,  # Normal function
        "*5": Phenotype.IM,  # Decreased function
        "*15": Phenotype.IM,  # Decreased function
        "*17": Phenotype.IM,  # Decreased function
    },
    "TPMT": {
        "*1": Phenotype.NM,  # Normal function
        "*2": Phenotype.IM,  # Decreased function
        "*3A": Phenotype.IM,  # Decreased function
        "*3B": Phenotype.IM,  # Decreased function
        "*3C": Phenotype.IM,  # Decreased function
        "*4": Phenotype.PM,  # No function
    },
    "DPYD": {
        "*1": Phenotype.NM,  # Normal function
        "*2A": Phenotype.PM,  # No function
        "*13": Phenotype.IM,  # Decreased function
        "*9B": Phenotype.IM,  # Decreased function
    }
}


def determine_phenotype(gene: str, variants: List[Variant]) -> Tuple[str, Phenotype]:
    """
    Determine diplotype and phenotype from variants for a specific gene.
    
    Args:
        gene: Gene symbol
        variants: List of variants for this gene
        
    Returns:
        Tuple of (diplotype string, Phenotype enum)
    """
    if not variants:
        return "*1/*1", Phenotype.UNKNOWN
    
    # Extract star alleles from variants
    star_alleles = []
    for variant in variants:
        if variant.star_allele:
            star_alleles.append(variant.star_allele)
        else:
            # If no star allele annotation, try to infer from rsid
            inferred = infer_star_allele_from_rsid(gene, variant.rsid)
            if inferred:
                star_alleles.append(inferred)
    
    if not star_alleles:
        return "*1/*1", Phenotype.UNKNOWN
    
    # Determine diplotype (simplified - assumes two alleles)
    if len(star_alleles) >= 2:
        diplotype = f"{star_alleles[0]}/{star_alleles[1]}"
    elif len(star_alleles) == 1:
        diplotype = f"{star_alleles[0]}/*1"  # Assume heterozygous with wild-type
    else:
        diplotype = "*1/*1"
    
    # Determine phenotype from diplotype
    phenotype = get_phenotype_from_diplotype(gene, diplotype)
    
    return diplotype, phenotype


def get_phenotype_from_diplotype(gene: str, diplotype: str) -> Phenotype:
    """
    Get phenotype from diplotype using activity score or direct mapping.
    
    Args:
        gene: Gene symbol
        diplotype: Diplotype string (e.g., "*1/*2")
        
    Returns:
        Phenotype enum
    """
    if gene not in STAR_ALLELE_PHENOTYPES:
        return Phenotype.UNKNOWN
    
    gene_map = STAR_ALLELE_PHENOTYPES[gene]
    
    # Parse diplotype
    alleles = diplotype.split('/')
    if len(alleles) != 2:
        return Phenotype.UNKNOWN
    
    allele1, allele2 = alleles[0].strip(), alleles[1].strip()
    
    # Get phenotypes for each allele
    pheno1 = gene_map.get(allele1, Phenotype.UNKNOWN)
    pheno2 = gene_map.get(allele2, Phenotype.UNKNOWN)
    
    # Determine combined phenotype
    # Simplified logic: worst case scenario
    if pheno1 == Phenotype.PM or pheno2 == Phenotype.PM:
        return Phenotype.PM
    elif pheno1 == Phenotype.IM or pheno2 == Phenotype.IM:
        return Phenotype.IM
    elif pheno1 == Phenotype.RM or pheno2 == Phenotype.RM:
        # Check if both are RM for URM
        if pheno1 == Phenotype.RM and pheno2 == Phenotype.RM:
            return Phenotype.URM
        return Phenotype.RM
    elif pheno1 == Phenotype.NM and pheno2 == Phenotype.NM:
        return Phenotype.NM
    
    return Phenotype.UNKNOWN


def infer_star_allele_from_rsid(gene: str, rsid: str) -> Optional[str]:
    """
    Infer star allele from rsid (simplified mapping).
    
    Args:
        gene: Gene symbol
        rsid: dbSNP ID
        
    Returns:
        Star allele string or None
    """
    # This is a simplified mapping - real implementations would use comprehensive databases
    rsid_to_star: Dict[str, Dict[str, str]] = {
        "CYP2D6": {
            "rs1065852": "*10",  # Common decreased function variant
            "rs35742686": "*4",  # Common no function variant
            "rs3892097": "*4",   # Common no function variant
        },
        "CYP2C19": {
            "rs4244285": "*2",   # Common no function variant
            "rs4986893": "*3",   # Common no function variant
            "rs12248560": "*17", # Common increased function variant
        },
        "CYP2C9": {
            "rs1799853": "*2",   # Common decreased function variant
            "rs1057910": "*3",   # Common decreased function variant
        },
        "SLCO1B1": {
            "rs4149056": "*5",   # Common decreased function variant
        },
        "TPMT": {
            "rs1800462": "*3C",  # Common decreased function variant
            "rs1142345": "*3A",  # Common decreased function variant
        },
        "DPYD": {
            "rs3918290": "*2A",  # Common no function variant
            "rs55886062": "*13", # Common decreased function variant
        }
    }
    
    if gene in rsid_to_star and rsid in rsid_to_star[gene]:
        return rsid_to_star[gene][rsid]
    
    return None


def get_primary_gene_for_drug(drug: str) -> str:
    """
    Get the primary gene affecting metabolism for a drug.
    
    Args:
        drug: Drug name
        
    Returns:
        Primary gene symbol
    """
    drug_to_gene: Dict[str, str] = {
        "CODEINE": "CYP2D6",
        "WARFARIN": "CYP2C9",
        "CLOPIDOGREL": "CYP2C19",
        "SIMVASTATIN": "SLCO1B1",
        "AZATHIOPRINE": "TPMT",
        "FLUOROURACIL": "DPYD"
    }
    
    return drug_to_gene.get(drug.upper(), "UNKNOWN")
