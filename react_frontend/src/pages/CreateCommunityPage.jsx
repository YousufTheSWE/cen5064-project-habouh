import { useState } from 'react'
import { useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import { createCommunity } from '../services/communityService'
import './CreateCommunityPage.css'

export default function CreateCommunityPage() {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [picture, setPicture] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const { authToken } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!authToken) {
      navigate('/signin')
      return
    }
    setError('')
    setSubmitting(true)
    try {
      const community = await createCommunity(authToken, { name, description, picture })
      navigate(`/communities/${community.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="form-container">
      <div className="form-header">
        <h2>Create a Community</h2>
      </div>
      {error && <p className="auth-error">{error}</p>}
      <form onSubmit={handleSubmit} className="form-body">
        <div className="form-group">
          <label className="form-label" htmlFor="comm-name">Community Name</label>
          <input
            id="comm-name"
            className="form-input"
            type="text"
            placeholder="e.g. Technology, Gaming, Cooking"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="comm-desc">Description</label>
          <textarea
            id="comm-desc"
            className="form-textarea"
            placeholder="What is this community about?"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="comm-pic">Picture URL</label>
          <input
            id="comm-pic"
            className="form-input"
            type="url"
            placeholder="https://example.com/image.png"
            value={picture}
            onChange={(e) => setPicture(e.target.value)}
            required
          />
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn-primary"
            style={{ flex: 1 }}
            disabled={submitting}
          >
            {submitting ? 'Creating...' : 'Create Community'}
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate('/communities')}
          >
            Cancel
          </button>
        </div>
      </form>
    </main>
  )
}
