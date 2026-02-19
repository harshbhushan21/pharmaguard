import './ErrorDisplay.css'

const ErrorDisplay = ({ error }) => {
  if (!error) return null

  return (
    <div className="error-display">
      <div className="error-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <div className="error-content">
        <h3>Error</h3>
        <p>{error}</p>
      </div>
    </div>
  )
}

export default ErrorDisplay
