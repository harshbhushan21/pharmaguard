"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_supported_drugs():
    """Test supported drugs endpoint."""
    response = client.get("/api/drugs")
    assert response.status_code == 200
    assert "drugs" in response.json()
    assert "CODEINE" in response.json()["drugs"]


def test_analyze_endpoint_missing_file():
    """Test analyze endpoint without file."""
    response = client.post("/api/analyze", data={"drugs": "CODEINE"})
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_invalid_file():
    """Test analyze endpoint with invalid file."""
    response = client.post(
        "/api/analyze",
        files={"vcf_file": ("test.txt", b"not a vcf file", "text/plain")},
        data={"drugs": "CODEINE"}
    )
    assert response.status_code == 400


def test_analyze_endpoint_invalid_drug():
    """Test analyze endpoint with invalid drug."""
    vcf_content = b"""##fileformat=VCFv4.2
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
22	42522500	.	C	T	100	PASS	GENE=CYP2D6;STAR=*4;RS=rs3892097	GT:DP	0/1:50
"""
    response = client.post(
        "/api/analyze",
        files={"vcf_file": ("test.vcf", vcf_content, "text/vcf")},
        data={"drugs": "INVALID_DRUG"}
    )
    assert response.status_code == 400
