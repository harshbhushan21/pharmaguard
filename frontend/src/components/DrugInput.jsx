import { useState, useEffect } from 'react'
import { getSupportedDrugs } from '../services/api'
import './DrugInput.css'

const DrugInput = ({ value, onChange }) => {
  const [supportedDrugs, setSupportedDrugs] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  useEffect(() => {
    getSupportedDrugs().then(setSupportedDrugs)
  }, [])

  const handleInputChange = (e) => {
    onChange(e.target.value)
    setShowSuggestions(true)
  }

  const handleDrugSelect = (drug) => {
    if (value) {
      // Add to existing drugs if not already present
      const drugs = value.split(',').map(d => d.trim())
      if (!drugs.includes(drug)) {
        onChange([...drugs, drug].join(', '))
      }
    } else {
      onChange(drug)
    }
    setShowSuggestions(false)
  }

  const filteredDrugs = supportedDrugs.filter(drug =>
    drug.toLowerCase().includes(value.toLowerCase())
  )

  return (
    <div className="drug-input-container">
      <input
        type="text"
        placeholder="Enter drug name(s), e.g., CODEINE, WARFARIN"
        value={value}
        onChange={handleInputChange}
        onFocus={() => setShowSuggestions(true)}
        className="drug-input"
      />
      {showSuggestions && value && filteredDrugs.length > 0 && (
        <div className="drug-suggestions">
          {filteredDrugs.map((drug) => (
            <div
              key={drug}
              onClick={() => handleDrugSelect(drug)}
              className="drug-suggestion-item"
            >
              {drug}
            </div>
          ))}
        </div>
      )}
      <div className="supported-drugs-hint">
        <p>Supported drugs: {supportedDrugs.join(', ')}</p>
        <p className="hint-text">You can enter multiple drugs separated by commas</p>
      </div>
    </div>
  )
}

export default DrugInput
