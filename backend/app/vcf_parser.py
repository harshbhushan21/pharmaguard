"""VCF file parser for extracting pharmacogenomic variants."""
import io
from typing import List, Dict, Optional, Tuple
from .schemas import Variant
from .config import settings


def parse_vcf_file(vcf_content: bytes) -> Tuple[List[Variant], List[str]]:
    """
    Parse VCF file content and extract variants for target genes.
    
    Args:
        vcf_content: Raw VCF file content as bytes
        
    Returns:
        Tuple of (list of Variant objects, list of warning messages)
    """
    warnings = []
    variants = []
    
    try:
        # Decode VCF content
        vcf_text = vcf_content.decode('utf-8')
        lines = vcf_text.split('\n')
    except UnicodeDecodeError:
        warnings.append("Failed to decode VCF file as UTF-8")
        return [], warnings
    
    # Track header lines
    header_end = -1
    for i, line in enumerate(lines):
        if line.startswith('#CHROM'):
            header_end = i
            break
    
    if header_end == -1:
        warnings.append("VCF header not found")
        return [], warnings
    
    # Parse header to get column indices
    header_line = lines[header_end]
    header_cols = header_line.strip().split('\t')
    
    try:
        chrom_idx = header_cols.index('#CHROM')
        pos_idx = header_cols.index('POS')
        ref_idx = header_cols.index('REF')
        alt_idx = header_cols.index('ALT')
        qual_idx = header_cols.index('QUAL')
        info_idx = header_cols.index('INFO')
        format_idx = header_cols.index('FORMAT')
        sample_idx = format_idx + 1 if len(header_cols) > format_idx + 1 else None
    except ValueError as e:
        warnings.append(f"Missing required VCF column: {e}")
        return [], warnings
    
    # Parse variant lines
    for line_num, line in enumerate(lines[header_end + 1:], start=header_end + 2):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            cols = line.split('\t')
            if len(cols) < len(header_cols):
                warnings.append(f"Line {line_num}: Insufficient columns")
                continue
            
            chromosome = cols[chrom_idx]
            position = int(cols[pos_idx]) if cols[pos_idx] != '.' else None
            ref_allele = cols[ref_idx]
            alt_allele = cols[alt_idx].split(',')[0]  # Take first ALT allele
            quality = float(cols[qual_idx]) if cols[qual_idx] != '.' else None
            
            # Parse INFO field
            info_str = cols[info_idx]
            info_dict = parse_info_field(info_str)
            
            # Extract genotype if available
            genotype = None
            if sample_idx and len(cols) > sample_idx:
                format_str = cols[format_idx]
                sample_str = cols[sample_idx]
                genotype = parse_genotype(format_str, sample_str)
            
            # Extract gene, star allele, and rsid from INFO
            gene = info_dict.get('GENE', '')
            star_allele = info_dict.get('STAR', None)
            rsid = info_dict.get('RS', '')
            
            # Filter for target genes
            if gene and gene.upper() in [g.upper() for g in settings.target_genes]:
                variant = Variant(
                    rsid=rsid if rsid else f"chr{chromosome}:{position}",
                    gene=gene.upper(),
                    star_allele=star_allele,
                    chromosome=chromosome,
                    position=position,
                    ref_allele=ref_allele,
                    alt_allele=alt_allele,
                    quality=quality,
                    genotype=genotype
                )
                variants.append(variant)
        
        except (ValueError, IndexError) as e:
            warnings.append(f"Line {line_num}: Parsing error - {e}")
            continue
    
    return variants, warnings


def parse_info_field(info_str: str) -> Dict[str, str]:
    """
    Parse VCF INFO field into dictionary.
    
    Args:
        info_str: INFO field string (e.g., "GENE=CYP2D6;STAR=*1;RS=rs123")
        
    Returns:
        Dictionary of INFO key-value pairs
    """
    info_dict = {}
    if not info_str or info_str == '.':
        return info_dict
    
    for item in info_str.split(';'):
        if '=' in item:
            key, value = item.split('=', 1)
            info_dict[key] = value
        else:
            info_dict[item] = True
    
    return info_dict


def parse_genotype(format_str: str, sample_str: str) -> Optional[str]:
    """
    Parse genotype from FORMAT and SAMPLE fields.
    
    Args:
        format_str: FORMAT field (e.g., "GT:DP:AD")
        sample_str: SAMPLE field (e.g., "0/1:50:25,25")
        
    Returns:
        Genotype string (e.g., "0/1") or None
    """
    try:
        format_fields = format_str.split(':')
        sample_fields = sample_str.split(':')
        
        if 'GT' in format_fields:
            gt_idx = format_fields.index('GT')
            if gt_idx < len(sample_fields):
                return sample_fields[gt_idx]
    except (ValueError, IndexError):
        pass
    
    return None
