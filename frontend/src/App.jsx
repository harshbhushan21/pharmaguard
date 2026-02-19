import { useState } from 'react'
import FileUpload from './components/FileUpload'
import DrugInput from './components/DrugInput'
import ResultsDisplay from './components/ResultsDisplay'
import ErrorDisplay from './components/ErrorDisplay'
import { analyzePharmacogenomics } from './services/api'
import './styles/App.css'

function App() {
  const [vcfFile, setVcfFile] = useState(null)
  const [drugs, setDrugs] = useState('')
  const [patientId, setPatientId] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileSelect = (file) => {
    setVcfFile(file)
    setError(null)
  }

  const handleDrugsChange = (value) => {
    setDrugs(value)
    setError(null)
  }

  const handleAnalyze = async () => {
    if (!vcfFile) {
      setError('Please select a VCF file')
      return
    }

    if (!drugs.trim()) {
      setError('Please enter at least one drug name')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const result = await analyzePharmacogenomics(vcfFile, drugs, patientId)
      setResults(result)
    } catch (err) {
      setError(err.message || 'An error occurred during analysis')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setVcfFile(null)
    setDrugs('')
    setPatientId('')
    setResults(null)
    setError(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>PharmaGuard</h1>
        <p>AI-Powered Pharmacogenomic Risk Assessment</p>
      </header>

      <main className="app-main">
        {!results ? (
          <div className="input-section">
            <div className="input-card">
              <h2>1. Upload VCF File</h2>
              <FileUpload onFileSelect={handleFileSelect} selectedFile={vcfFile} />
            </div>

            <div className="input-card">
              <h2>2. Enter Drug Name(s)</h2>
              <DrugInput value={drugs} onChange={handleDrugsChange} />
            </div>

            <div className="input-card">
              <h2>3. Patient ID (Optional)</h2>
              <input
                type="text"
                placeholder="Enter patient ID (optional)"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                className="patient-id-input"
              />
            </div>

            <button
              onClick={handleAnalyze}
              disabled={loading || !vcfFile || !drugs.trim()}
              className="analyze-button"
            >
              {loading ? 'Analyzing...' : 'Analyze Risk'}
            </button>

            {error && <ErrorDisplay error={error} />}
          </div>
        ) : (
          <div className="results-section">
            <ResultsDisplay results={results} onReset={handleReset} />
          </div>
        )}
      </main>
    </div>
  )
}

export default App
