"""Tests for VCF parser."""
import pytest
from backend.app.vcf_parser import parse_vcf_file, parse_info_field, parse_genotype


def test_parse_info_field():
    """Test INFO field parsing."""
    info_str = "GENE=CYP2D6;STAR=*4;RS=rs3892097"
    result = parse_info_field(info_str)
    assert result["GENE"] == "CYP2D6"
    assert result["STAR"] == "*4"
    assert result["RS"] == "rs3892097"


def test_parse_genotype():
    """Test genotype parsing."""
    format_str = "GT:DP:AD"
    sample_str = "0/1:50:25,25"
    result = parse_genotype(format_str, sample_str)
    assert result == "0/1"


def test_parse_vcf_file():
    """Test VCF file parsing."""
    vcf_content = """##fileformat=VCFv4.2
##INFO=<ID=GENE,Number=1,Type=String>
##INFO=<ID=STAR,Number=1,Type=String>
##INFO=<ID=RS,Number=1,Type=String>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
22	42522500	.	C	T	100	PASS	GENE=CYP2D6;STAR=*4;RS=rs3892097	GT:DP	0/1:50
10	94781859	.	G	A	100	PASS	GENE=CYP2C19;STAR=*2;RS=rs4244285	GT:DP	0/1:52
""".encode('utf-8')
    
    variants, warnings = parse_vcf_file(vcf_content)
    
    assert len(variants) == 2
    assert variants[0].gene == "CYP2D6"
    assert variants[0].rsid == "rs3892097"
    assert variants[0].star_allele == "*4"
    assert variants[1].gene == "CYP2C19"
    assert variants[1].rsid == "rs4244285"


def test_parse_vcf_file_empty():
    """Test parsing empty VCF file."""
    vcf_content = b""
    variants, warnings = parse_vcf_file(vcf_content)
    assert len(variants) == 0
    assert len(warnings) > 0
