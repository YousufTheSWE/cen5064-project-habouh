import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import { getCommunities } from '../services/communityService'
import './CommunitiesPage.css'

export default function CommunitiesPage() {
  const [communities, setCommunities] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    getCommunities()
      .then(setCommunities)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="communities-page">
      <header className="communities-header">
        <div className="communities-title-area">
          <h1>Communities</h1>
        </div>
        <div className="communities-nav-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate('/')}
          >
            Home
          </button>
          {user && (
            <button
              type="button"
              className="btn-primary"
              onClick={() => navigate('/communities/new')}
            >
              + Create Community
            </button>
          )}
        </div>
      </header>

      {error && <p className="auth-error">{error}</p>}
      {loading ? (
        <p className="empty-state">Loading communities...</p>
      ) : communities.length === 0 ? (
        <div className="empty-state">
          <h3>No communities created yet!</h3>
          <p>Be the first one to create a community for discussions.</p>
          {user ? (
            <button
              type="button"
              className="btn-primary"
              style={{ marginTop: '1rem' }}
              onClick={() => navigate('/communities/new')}
            >
              Create Community
            </button>
          ) : (
            <button
              type="button"
              className="btn-primary"
              style={{ marginTop: '1rem' }}
              onClick={() => navigate('/signin')}
            >
              Sign In to Create One
            </button>
          )}
        </div>
      ) : (
        <div className="communities-grid">
          {communities.map((c) => (
            <article
              key={c.id}
              className="community-card"
              onClick={() => navigate(`/communities/${c.id}`)}
            >
              <div className="community-card-img-wrap">
                {c.picture ? (
                  <img
                    src={c.picture}
                    alt={c.name}
                    className="community-card-img"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ) : (
                  <span className="community-card-placeholder">💬</span>
                )}
              </div>
              <div className="community-card-body">
                <h3 className="community-card-title">{c.name}</h3>
                <p className="community-card-desc">{c.description}</p>
                <div className="community-card-meta">
                  Created by @{c.owner_username || `user_${c.owner_id}`}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}
