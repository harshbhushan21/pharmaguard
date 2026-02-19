import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import './FileUpload.css'

const FileUpload = ({ onFileSelect, selectedFile }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      // Validate file extension
      if (!file.name.endsWith('.vcf')) {
        alert('Please upload a .vcf file')
        return
      }
      // Validate file size (5MB)
      const maxSize = 5 * 1024 * 1024
      if (file.size > maxSize) {
        alert('File size exceeds 5MB limit')
        return
      }
      onFileSelect(file)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/vcf': ['.vcf'],
      'text/plain': ['.vcf'],
    },
    multiple: false,
    maxSize: 5 * 1024 * 1024, // 5MB
  })

  return (
    <div className="file-upload-container">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${selectedFile ? 'has-file' : ''}`}
      >
        <input {...getInputProps()} />
        {selectedFile ? (
          <div className="file-selected">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
              <polyline points="13 2 13 9 20 9"></polyline>
            </svg>
            <p className="file-name">{selectedFile.name}</p>
            <p className="file-size">{(selectedFile.size / 1024).toFixed(2)} KB</p>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                onFileSelect(null)
              }}
              className="remove-file-button"
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="dropzone-content">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            {isDragActive ? (
              <p>Drop the VCF file here...</p>
            ) : (
              <>
                <p>Drag & drop a VCF file here, or click to select</p>
                <p className="file-hint">Maximum file size: 5MB</p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default FileUpload
