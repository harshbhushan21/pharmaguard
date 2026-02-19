import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // 60 seconds for file upload and analysis
})

export const analyzePharmacogenomics = async (vcfFile, drugs, patientId = null) => {
  const formData = new FormData()
  formData.append('vcf_file', vcfFile)
  formData.append('drugs', drugs)
  if (patientId) {
    formData.append('patient_id', patientId)
  }

  try {
    const response = await api.post('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.detail || 'Analysis failed')
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check your connection.')
    } else {
      // Error setting up request
      throw new Error(error.message || 'An error occurred')
    }
  }
}

export const getSupportedDrugs = async () => {
  try {
    const response = await api.get('/api/drugs')
    return response.data.drugs
  } catch (error) {
    console.error('Error fetching supported drugs:', error)
    return []
  }
}

export default api
