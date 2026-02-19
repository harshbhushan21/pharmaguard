"""LLM integration for generating clinical explanations."""
from typing import List, Dict
from openai import OpenAI
from .schemas import Variant, Phenotype, LLMExplanation
from .config import settings


def generate_explanation(
    drug: str,
    gene: str,
    phenotype: Phenotype,
    diplotype: str,
    variants: List[Variant],
    risk_label: str,
    clinical_recommendation: str
) -> LLMExplanation:
    """
    Generate LLM-powered clinical explanation.
    
    Args:
        drug: Drug name
        gene: Gene symbol
        phenotype: Patient phenotype
        diplotype: Diplotype string
        variants: List of detected variants
        risk_label: Risk assessment label
        clinical_recommendation: Clinical recommendation text
        
    Returns:
        LLMExplanation object
    """
    if not settings.openai_api_key:
        # Fallback explanation if API key not configured
        return LLMExplanation(
            summary=f"Patient has {phenotype.value} phenotype for {gene}, affecting {drug} metabolism.",
            mechanism=f"The {diplotype} diplotype results in {phenotype.value} phenotype, affecting {drug} metabolism.",
            variant_citations=[v.rsid for v in variants if v.rsid],
            clinical_significance=clinical_recommendation
        )
    
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Build variant information string
        variant_info = []
        for variant in variants:
            variant_str = f"- {variant.rsid}"
            if variant.star_allele:
                variant_str += f" (star allele: {variant.star_allele})"
            variant_info.append(variant_str)
        
        variant_text = "\n".join(variant_info) if variant_info else "No specific variants detected"
        
        # Construct prompt
        prompt = f"""You are a clinical pharmacogenomics expert. Generate a clear, evidence-based explanation for a pharmacogenomic risk assessment.

Patient Information:
- Drug: {drug}
- Gene: {gene}
- Diplotype: {diplotype}
- Phenotype: {phenotype.value}
- Risk Assessment: {risk_label}
- Clinical Recommendation: {clinical_recommendation}

Detected Variants:
{variant_text}

Please provide:
1. A concise summary (2-3 sentences) explaining the pharmacogenomic risk
2. A detailed explanation of the biological mechanism (how the genetic variants affect drug metabolism)
3. List all cited variant rsIDs
4. Clinical significance and implications

Format your response as JSON with these exact keys:
- "summary": string (concise summary)
- "mechanism": string (detailed mechanism explanation)
- "variant_citations": array of strings (rsIDs)
- "clinical_significance": string (clinical implications)

Be specific, cite variants by rsID, and explain the biological pathway clearly."""
        
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a clinical pharmacogenomics expert providing evidence-based explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        # Parse response
        content = response.choices[0].message.content
        
        # Try to extract JSON from response
        import json
        import re
        
        # Look for JSON in the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            explanation_data = json.loads(json_match.group())
            return LLMExplanation(
                summary=explanation_data.get("summary", ""),
                mechanism=explanation_data.get("mechanism", ""),
                variant_citations=explanation_data.get("variant_citations", []),
                clinical_significance=explanation_data.get("clinical_significance", "")
            )
        else:
            # Fallback: parse as text
            return LLMExplanation(
                summary=content[:200] + "..." if len(content) > 200 else content,
                mechanism=content,
                variant_citations=[v.rsid for v in variants if v.rsid],
                clinical_significance=clinical_recommendation
            )
    
    except Exception as e:
        # Fallback on error
        return LLMExplanation(
            summary=f"Patient has {phenotype.value} phenotype for {gene}, affecting {drug} metabolism. Risk assessment: {risk_label}.",
            mechanism=f"The {diplotype} diplotype results in {phenotype.value} phenotype. This affects the activity of {gene}, which is responsible for metabolizing {drug}.",
            variant_citations=[v.rsid for v in variants if v.rsid],
            clinical_significance=clinical_recommendation
        )
