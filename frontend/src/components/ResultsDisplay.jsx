import { useState } from 'react'
import './ResultsDisplay.css'

const ResultsDisplay = ({ results, onReset }) => {
  const [expandedSections, setExpandedSections] = useState({
    profile: false,
    recommendation: false,
    explanation: false,
    metrics: false,
  })

  // Support multiple drugs: normalize to a per-drug results array
  const perDrugResults = results.all_drugs_results && results.all_drugs_results.length > 0
    ? results.all_drugs_results
    : [{
        drug: results.drug,
        risk_assessment: results.risk_assessment,
        pharmacogenomic_profile: results.pharmacogenomic_profile,
        clinical_recommendation: results.clinical_recommendation,
        llm_generated_explanation: results.llm_generated_explanation,
        quality_metrics: results.quality_metrics,
      }]

  const [selectedDrugIndex, setSelectedDrugIndex] = useState(0)

  const activeResult = perDrugResults[selectedDrugIndex] || perDrugResults[0]

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const getRiskColor = (riskLabel) => {
    switch (riskLabel) {
      case 'Safe':
        return '#10b981'
      case 'Adjust Dosage':
        return '#f59e0b'
      case 'Toxic':
      case 'Ineffective':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'none':
        return '#10b981'
      case 'low':
        return '#84cc16'
      case 'moderate':
        return '#f59e0b'
      case 'high':
        return '#f97316'
      case 'critical':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  const downloadJSON = () => {
    const dataStr = JSON.stringify(results, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `pharmaguard_${results.patient_id}_${results.drug}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(results, null, 2))
    alert('JSON copied to clipboard!')
  }

  return (
    <div className="results-display">
        <div className="results-header">
          <h2>Analysis Results</h2>
          {perDrugResults.length > 1 && (
            <div className="drug-selector">
              {perDrugResults.map((drugResult, idx) => (
                <button
                  key={drugResult.drug}
                  type="button"
                  className={`drug-selector-button ${idx === selectedDrugIndex ? 'active' : ''}`}
                  onClick={() => setSelectedDrugIndex(idx)}
                >
                  {drugResult.drug}
                </button>
              ))}
            </div>
          )}
          <div className="results-actions">
          <button onClick={downloadJSON} className="action-button">
            Download JSON
          </button>
          <button onClick={copyToClipboard} className="action-button">
            Copy JSON
          </button>
          <button onClick={onReset} className="action-button secondary">
            New Analysis
          </button>
        </div>
      </div>

      <div className="results-content">
        {/* Patient Info */}
        <div className="result-card">
          <h3>Patient Information</h3>
            <div className="info-grid">
              <div>
                <span className="label">Patient ID:</span>
                <span className="value">{results.patient_id}</span>
              </div>
              <div>
                <span className="label">Drug:</span>
                <span className="value">{activeResult.drug}</span>
              </div>
              <div>
                <span className="label">Timestamp:</span>
                <span className="value">{new Date(results.timestamp).toLocaleString()}</span>
              </div>
            </div>
        </div>

        {/* Risk Assessment */}
        <div className="result-card risk-card">
          <h3>Risk Assessment</h3>
          <div className="risk-badge" style={{ backgroundColor: getRiskColor(activeResult.risk_assessment.risk_label) }}>
            {activeResult.risk_assessment.risk_label}
          </div>
          <div className="risk-details">
            <div className="risk-item">
              <span className="label">Confidence Score:</span>
              <span className="value">{(activeResult.risk_assessment.confidence_score * 100).toFixed(1)}%</span>
            </div>
            <div className="risk-item">
              <span className="label">Severity:</span>
              <span className="value severity-badge" style={{ backgroundColor: getSeverityColor(activeResult.risk_assessment.severity) }}>
                {activeResult.risk_assessment.severity.toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        {/* Pharmacogenomic Profile */}
        <div className="result-card">
          <div className="card-header" onClick={() => toggleSection('profile')}>
            <h3>Pharmacogenomic Profile</h3>
            <span className="toggle-icon">{expandedSections.profile ? '−' : '+'}</span>
          </div>
          {expandedSections.profile && (
            <div className="card-content">
              <div className="info-grid">
                <div>
                  <span className="label">Primary Gene:</span>
                  <span className="value">{activeResult.pharmacogenomic_profile.primary_gene}</span>
                </div>
                <div>
                  <span className="label">Diplotype:</span>
                  <span className="value">{activeResult.pharmacogenomic_profile.diplotype}</span>
                </div>
                <div>
                  <span className="label">Phenotype:</span>
                  <span className="value">{activeResult.pharmacogenomic_profile.phenotype}</span>
                </div>
              </div>
              {activeResult.pharmacogenomic_profile.detected_variants.length > 0 && (
                <div className="variants-list">
                  <h4>Detected Variants:</h4>
                  <ul>
                    {activeResult.pharmacogenomic_profile.detected_variants.map((variant, idx) => (
                      <li key={idx}>
                        <strong>{variant.rsid}</strong> - {variant.gene}
                        {variant.star_allele && ` (${variant.star_allele})`}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Clinical Recommendation */}
        <div className="result-card">
          <div className="card-header" onClick={() => toggleSection('recommendation')}>
            <h3>Clinical Recommendation</h3>
            <span className="toggle-icon">{expandedSections.recommendation ? '−' : '+'}</span>
          </div>
          {expandedSections.recommendation && (
            <div className="card-content">
              <p className="recommendation-action">{activeResult.clinical_recommendation.action}</p>
              {activeResult.clinical_recommendation.dosage_adjustment && (
                <div className="recommendation-item">
                  <strong>Dosage Adjustment:</strong>
                  <p>{activeResult.clinical_recommendation.dosage_adjustment}</p>
                </div>
              )}
              {activeResult.clinical_recommendation.monitoring && (
                <div className="recommendation-item">
                  <strong>Monitoring:</strong>
                  <p>{activeResult.clinical_recommendation.monitoring}</p>
                </div>
              )}
              {activeResult.clinical_recommendation.alternative_drugs && (
                <div className="recommendation-item">
                  <strong>Alternative Drugs:</strong>
                  <p>{activeResult.clinical_recommendation.alternative_drugs.join(', ')}</p>
                </div>
              )}
              {activeResult.clinical_recommendation.cpic_guideline && (
                <div className="recommendation-item">
                  <strong>CPIC Guideline:</strong>
                  <p>{activeResult.clinical_recommendation.cpic_guideline}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* LLM Explanation */}
        <div className="result-card">
          <div className="card-header" onClick={() => toggleSection('explanation')}>
            <h3>AI-Generated Explanation</h3>
            <span className="toggle-icon">{expandedSections.explanation ? '−' : '+'}</span>
          </div>
          {expandedSections.explanation && (
            <div className="card-content">
              <div className="explanation-section">
                <h4>Summary</h4>
                <p>{activeResult.llm_generated_explanation.summary}</p>
              </div>
              <div className="explanation-section">
                <h4>Biological Mechanism</h4>
                <p>{activeResult.llm_generated_explanation.mechanism}</p>
              </div>
              {activeResult.llm_generated_explanation.variant_citations.length > 0 && (
                <div className="explanation-section">
                  <h4>Cited Variants</h4>
                  <ul>
                    {activeResult.llm_generated_explanation.variant_citations.map((rsid, idx) => (
                      <li key={idx}>{rsid}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="explanation-section">
                <h4>Clinical Significance</h4>
                <p>{activeResult.llm_generated_explanation.clinical_significance}</p>
              </div>
            </div>
          )}
        </div>

        {/* Quality Metrics */}
        <div className="result-card">
          <div className="card-header" onClick={() => toggleSection('metrics')}>
            <h3>Quality Metrics</h3>
            <span className="toggle-icon">{expandedSections.metrics ? '−' : '+'}</span>
          </div>
          {expandedSections.metrics && (
            <div className="card-content">
              <div className="info-grid">
                <div>
                  <span className="label">VCF Parsing:</span>
                  <span className={`value ${activeResult.quality_metrics.vcf_parsing_success ? 'success' : 'error'}`}>
                    {activeResult.quality_metrics.vcf_parsing_success ? 'Success' : 'Failed'}
                  </span>
                </div>
                <div>
                  <span className="label">Total Variants:</span>
                  <span className="value">{activeResult.quality_metrics.variant_count}</span>
                </div>
                <div>
                  <span className="label">Target Gene Variants:</span>
                  <span className="value">{activeResult.quality_metrics.target_gene_variants}</span>
                </div>
              </div>
              {activeResult.quality_metrics.parsing_warnings.length > 0 && (
                <div className="warnings-list">
                  <h4>Warnings:</h4>
                  <ul>
                    {activeResult.quality_metrics.parsing_warnings.map((warning, idx) => (
                      <li key={idx}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ResultsDisplay
