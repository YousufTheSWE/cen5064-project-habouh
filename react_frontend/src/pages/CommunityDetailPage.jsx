import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { useAuth } from '../context/AuthContext'
import {
  deleteCommunity,
  getCommunity,
  transferCommunityOwnership,
  updateCommunity,
} from '../services/communityService'
import { getPosts, votePost } from '../services/postService'
import './CommunityDetailPage.css'

export default function CommunityDetailPage() {
  const { communityId } = useParams()
  const { user, accountId, authToken } = useAuth()
  const navigate = useNavigate()

  const [community, setCommunity] = useState(null)
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Editing state for community owner
  const [isEditing, setIsEditing] = useState(false)
  const [editName, setEditName] = useState('')
  const [editDesc, setEditDesc] = useState('')
  const [editPic, setEditPic] = useState('')

  // Transfer Ownership state
  const [showTransferModal, setShowTransferModal] = useState(false)
  const [transferTarget, setTransferTarget] = useState('')
  const [transferError, setTransferError] = useState('')
  const [transferSubmitting, setTransferSubmitting] = useState(false)

  useEffect(() => {
    Promise.all([getCommunity(communityId), getPosts(communityId, authToken)])
      .then(([commData, postsData]) => {
        setCommunity(commData)
        setEditName(commData.name)
        setEditDesc(commData.description)
        setEditPic(commData.picture)
        setPosts(postsData)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [communityId, authToken])

  const handleUpdate = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const updated = await updateCommunity(authToken, communityId, {
        name: editName,
        description: editDesc,
        picture: editPic,
      })
      setCommunity(updated)
      setIsEditing(false)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this community?')) return
    setError('')
    try {
      await deleteCommunity(authToken, communityId)
      navigate('/communities')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleTransferOwnership = async (e) => {
    e.preventDefault()
    if (!transferTarget.trim()) return
    setTransferError('')
    setTransferSubmitting(true)
    try {
      const updated = await transferCommunityOwnership(authToken, communityId, transferTarget.trim())
      setCommunity(updated)
      setShowTransferModal(false)
      setTransferTarget('')
    } catch (err) {
      setTransferError(err.message)
    } finally {
      setTransferSubmitting(false)
    }
  }

  const handleVote = async (e, post, direction) => {
    e.stopPropagation()
    if (!authToken) {
      navigate('/signin')
      return
    }
    const targetDirection = post.user_vote === direction ? 0 : direction
    try {
      const res = await votePost(authToken, post.id, targetDirection)
      setPosts((prevPosts) =>
        prevPosts.map((p) =>
          p.id === post.id
            ? { ...p, upvotes: res.upvotes, downvotes: res.downvotes, user_vote: res.user_vote }
            : p,
        ),
      )
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <div className="community-detail-page"><p className="empty-state">Loading community...</p></div>
  if (!community) return <div className="community-detail-page"><p className="empty-state">{error || 'Community not found'}</p></div>

  const isOwner = Number(accountId) === Number(community.owner_id)

  return (
    <div className="community-detail-page">
      <div style={{ marginBottom: '1.5rem', textAlign: 'left' }}>
        <button
          type="button"
          className="btn-secondary"
          onClick={() => navigate('/communities')}
        >
          ← Back to Communities
        </button>
      </div>

      {error && <p className="auth-error">{error}</p>}

      <section className="community-banner">
        {community.picture && (
          <div className="community-banner-cover">
            <img
              src={community.picture}
              alt={community.name}
              className="community-banner-img"
              onError={(e) => { e.currentTarget.style.display = 'none' }}
            />
          </div>
        )}
        <div className="community-banner-content">
          {isEditing ? (
            <form onSubmit={handleUpdate} className="form-body">
              <input
                className="form-input"
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
              <textarea
                className="form-textarea"
                value={editDesc}
                onChange={(e) => setEditDesc(e.target.value)}
                required
              />
              <input
                className="form-input"
                type="url"
                value={editPic}
                onChange={(e) => setEditPic(e.target.value)}
                required
              />
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button type="submit" className="btn-primary">Save</button>
                <button type="button" className="btn-secondary" onClick={() => setIsEditing(false)}>Cancel</button>
              </div>
            </form>
          ) : (
            <>
              <div className="community-banner-header">
                <div>
                  <h1 className="community-banner-title">{community.name}</h1>
                  <p className="community-banner-desc">{community.description}</p>
                  <span className="community-banner-owner">
                    Created by @{community.owner_username || `user_${community.owner_id}`}
                  </span>
                </div>
                {isOwner && (
                  <div className="community-banner-actions">
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => setIsEditing(true)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => {
                        setTransferError('')
                        setShowTransferModal(true)
                      }}
                    >
                      Transfer Ownership
                    </button>
                    <button
                      type="button"
                      className="btn-danger"
                      onClick={handleDelete}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </section>

      {/* Transfer Ownership Confirmation Modal */}
      {showTransferModal && (
        <div className="modal-overlay" onClick={() => !transferSubmitting && setShowTransferModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Transfer Ownership</h2>
            <p className="modal-desc">
              Are you sure you want to transfer ownership of <strong>{community.name}</strong>?
              This action cannot be undone. You will lose owner controls over this community.
            </p>
            {transferError && <p className="auth-error">{transferError}</p>}
            <form onSubmit={handleTransferOwnership}>
              <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                <label className="form-label" htmlFor="transfer-target">
                  Recipient Username or User ID
                </label>
                <input
                  id="transfer-target"
                  className="form-input"
                  type="text"
                  placeholder="e.g. johndoe or 123456789"
                  value={transferTarget}
                  onChange={(e) => setTransferTarget(e.target.value)}
                  disabled={transferSubmitting}
                  required
                />
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowTransferModal(false)}
                  disabled={transferSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={transferSubmitting || !transferTarget.trim()}
                >
                  {transferSubmitting ? 'Transferring...' : 'Confirm Transfer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <section className="posts-section">
        <div className="posts-section-header">
          <h2>Community Posts ({posts.length})</h2>
          {user && (
            <button
              type="button"
              className="btn-primary"
              onClick={() => navigate(`/communities/${communityId}/new-post`)}
            >
              + Create Post
            </button>
          )}
        </div>

        {posts.length === 0 ? (
          <div className="empty-state">
            <p>No posts in this community yet.</p>
            {user && (
              <button
                type="button"
                className="btn-primary"
                style={{ marginTop: '0.75rem' }}
                onClick={() => navigate(`/communities/${communityId}/new-post`)}
              >
                Create the First Post
              </button>
            )}
          </div>
        ) : (
          <div className="posts-list">
            {posts.map((post) => {
              const score = (post.upvotes || 0) - (post.downvotes || 0)
              return (
                <article
                  key={post.id}
                  className="post-item-card"
                  onClick={() => navigate(`/posts/${post.id}`)}
                >
                  <div className="vote-widget" onClick={(e) => e.stopPropagation()}>
                    <button
                      type="button"
                      aria-label="Upvote"
                      className={`vote-btn ${post.user_vote === 1 ? 'upvoted' : ''}`}
                      onClick={(e) => handleVote(e, post, 1)}
                    >
                      ▲
                    </button>
                    <span className="vote-score">{score}</span>
                    <button
                      type="button"
                      aria-label="Downvote"
                      className={`vote-btn ${post.user_vote === -1 ? 'downvoted' : ''}`}
                      onClick={(e) => handleVote(e, post, -1)}
                    >
                      ▼
                    </button>
                  </div>
                  <div className="post-item-content">
                    <h3 className="post-item-title">{post.name}</h3>
                    <p className="post-item-desc">{post.description}</p>
                    <div className="post-item-meta">
                      Posted by @{post.author_username || `user_${post.author_id}`}
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}
