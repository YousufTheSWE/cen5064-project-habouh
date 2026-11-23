import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { useAuth } from '../context/AuthContext'
import {
  addModerator,
  banUser,
  deleteCommunity,
  getBannedUsers,
  getCommunity,
  getModerators,
  removeModerator,
  transferCommunityOwnership,
  unbanUser,
  updateCommunity,
} from '../services/communityService'
import { getPosts, votePost } from '../services/postService'
import {
  approveReport,
  deleteReportedItem,
  getReports,
  reportPost,
} from '../services/reportService'
import './CommunityDetailPage.css'

export default function CommunityDetailPage() {
  const { communityId } = useParams()
  const { user, accountId, authToken } = useAuth()
  const navigate = useNavigate()

  const [community, setCommunity] = useState(null)
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [feedbackMsg, setFeedbackMsg] = useState('')

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

  // Tabs: 'posts' | 'reports' | 'moderation'
  const [activeTab, setActiveTab] = useState('posts')

  // Reports state
  const [reports, setReports] = useState([])
  const [reportsLoading, setReportsLoading] = useState(false)

  // Moderation & Bans state
  const [moderators, setModerators] = useState([])
  const [bannedUsers, setBannedUsers] = useState([])
  const [modTarget, setModTarget] = useState('')
  const [banTarget, setBanTarget] = useState('')
  const [modSubmitting, setModSubmitting] = useState(false)

  useEffect(() => {
    Promise.all([getCommunity(communityId, authToken), getPosts(communityId, authToken)])
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

  const isOwner = community ? (Number(accountId) === Number(community.owner_id) || community.is_owner) : false
  const isModerator = community ? (community.is_moderator || isOwner) : false
  const isBanned = community ? community.is_banned : false

  // Load reports or moderation data when tabs change or on initial load for mods
  useEffect(() => {
    if (!authToken || !isModerator) return

    if (activeTab === 'reports') {
      setReportsLoading(true)
      getReports(authToken, communityId)
        .then((data) => setReports(data))
        .catch((err) => setError(err.message))
        .finally(() => setReportsLoading(false))
    } else if (activeTab === 'moderation') {
      Promise.all([
        getModerators(authToken, communityId),
        getBannedUsers(authToken, communityId),
      ])
        .then(([mods, banned]) => {
          setModerators(mods)
          setBannedUsers(banned)
        })
        .catch((err) => setError(err.message))
    }
  }, [activeTab, authToken, communityId, isModerator])

  // Also fetch report count badge in background for moderators
  useEffect(() => {
    if (authToken && isModerator && activeTab === 'posts') {
      getReports(authToken, communityId)
        .then((data) => setReports(data))
        .catch(() => {})
    }
  }, [authToken, communityId, isModerator, activeTab])

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

  const handleReportPost = async (e, post) => {
    e.stopPropagation()
    if (!authToken) {
      navigate('/signin')
      return
    }
    setError('')
    setFeedbackMsg('')
    try {
      await reportPost(authToken, post.id)
      setFeedbackMsg(`Post "${post.name}" reported to moderators.`)
      // Refresh reports
      if (isModerator) {
        getReports(authToken, communityId).then(setReports).catch(() => {})
      }
    } catch (err) {
      setError(err.message)
    }
  }

  const handleApproveReport = async (report) => {
    setError('')
    setFeedbackMsg('')
    try {
      await approveReport(authToken, communityId, report.target_type, report.target_id)
      setReports((prev) =>
        prev.filter(
          (r) => !(r.target_type === report.target_type && r.target_id === report.target_id),
        ),
      )
      if (report.target_type === 'post') {
        setPosts((prev) =>
          prev.map((p) => (p.id === report.target_id ? { ...p, is_approved: 1 } : p)),
        )
      }
      setFeedbackMsg(`${report.target_type === 'post' ? 'Post' : 'Comment'} approved and removed from report log.`)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteReported = async (report) => {
    if (!window.confirm(`Delete this reported ${report.target_type}?`)) return
    setError('')
    setFeedbackMsg('')
    try {
      await deleteReportedItem(authToken, communityId, report.target_type, report.target_id)
      setReports((prev) =>
        prev.filter(
          (r) => !(r.target_type === report.target_type && r.target_id === report.target_id),
        ),
      )
      if (report.target_type === 'post') {
        setPosts((prev) => prev.filter((p) => p.id !== report.target_id))
      }
      setFeedbackMsg(`Reported ${report.target_type} deleted.`)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleBanAuthorFromReport = async (report) => {
    if (!window.confirm(`Ban user @${report.author_username} from this community?`)) return
    setError('')
    setFeedbackMsg('')
    try {
      await banUser(authToken, communityId, String(report.author_id))
      setFeedbackMsg(`User @${report.author_username} has been banned from this community.`)
      if (activeTab === 'moderation') {
        getBannedUsers(authToken, communityId).then(setBannedUsers).catch(() => {})
      }
    } catch (err) {
      setError(err.message)
    }
  }

  const handleAddModerator = async (e) => {
    e.preventDefault()
    if (!modTarget.trim()) return
    setError('')
    setFeedbackMsg('')
    setModSubmitting(true)
    try {
      const added = await addModerator(authToken, communityId, modTarget.trim())
      setModerators([...moderators, added])
      setModTarget('')
      setFeedbackMsg(`Added @${added.username} as a moderator.`)
    } catch (err) {
      setError(err.message)
    } finally {
      setModSubmitting(false)
    }
  }

  const handleRemoveModerator = async (targetAccountId) => {
    if (!window.confirm('Remove this user from moderators?')) return
    setError('')
    setFeedbackMsg('')
    try {
      await removeModerator(authToken, communityId, targetAccountId)
      setModerators(moderators.filter((m) => m.account_id !== targetAccountId))
      setFeedbackMsg('Moderator removed.')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleBanUserManual = async (e) => {
    e.preventDefault()
    if (!banTarget.trim()) return
    setError('')
    setFeedbackMsg('')
    setModSubmitting(true)
    try {
      const banned = await banUser(authToken, communityId, banTarget.trim())
      setBannedUsers([...bannedUsers, banned])
      setBanTarget('')
      setFeedbackMsg(`Banned @${banned.username} from this community.`)
    } catch (err) {
      setError(err.message)
    } finally {
      setModSubmitting(false)
    }
  }

  const handleUnbanUser = async (targetAccountId) => {
    if (!window.confirm('Unban this user?')) return
    setError('')
    setFeedbackMsg('')
    try {
      await unbanUser(authToken, communityId, targetAccountId)
      setBannedUsers(bannedUsers.filter((b) => b.account_id !== targetAccountId))
      setFeedbackMsg('User unbanned.')
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <div className="community-detail-page"><p className="empty-state">Loading community...</p></div>
  if (!community) return <div className="community-detail-page"><p className="empty-state">{error || 'Community not found'}</p></div>

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

      {isBanned && (
        <div className="banned-banner">
          ⚠️ You have been banned from this community by a moderator. You cannot create or edit posts/comments, or submit reports.
        </div>
      )}

      {error && <p className="auth-error">{error}</p>}
      {feedbackMsg && <div className="success-banner">{feedbackMsg}</div>}

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

      {/* Navigation tabs for moderators & owners */}
      {isModerator && (
        <div className="comm-nav-tabs">
          <button
            type="button"
            className={`comm-tab-btn ${activeTab === 'posts' ? 'active' : ''}`}
            onClick={() => setActiveTab('posts')}
          >
            Posts ({posts.length})
          </button>
          <button
            type="button"
            className={`comm-tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            Report Log
            {reports.length > 0 && <span className="tab-badge">{reports.length}</span>}
          </button>
          <button
            type="button"
            className={`comm-tab-btn ${activeTab === 'moderation' ? 'active' : ''}`}
            onClick={() => setActiveTab('moderation')}
          >
            Moderation & Bans
          </button>
        </div>
      )}

      {/* TAB 1: Posts Section */}
      {activeTab === 'posts' && (
        <section className="posts-section">
          <div className="posts-section-header">
            <h2>Community Posts ({posts.length})</h2>
            {user && !isBanned && (
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
              {user && !isBanned && (
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
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <h3 className="post-item-title">{post.name}</h3>
                        {post.is_approved ? (
                          isModerator && <span className="approved-pill">✓ Approved</span>
                        ) : (
                          user && !isBanned && (
                            <button
                              type="button"
                              className="btn-report"
                              onClick={(e) => handleReportPost(e, post)}
                            >
                              🚩 Report
                            </button>
                          )
                        )}
                      </div>
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
      )}

      {/* TAB 2: Report Log */}
      {activeTab === 'reports' && isModerator && (
        <section className="reports-section">
          <h2 style={{ textAlign: 'left', marginBottom: '1.5rem', color: 'var(--text-h)' }}>
            Report Log ({reports.length})
          </h2>
          {reportsLoading ? (
            <p className="empty-state">Loading report log...</p>
          ) : reports.length === 0 ? (
            <p className="empty-state">No active reports. All posts and comments are in good standing.</p>
          ) : (
            <div className="reports-list">
              {reports.map((report) => (
                <div key={`${report.target_type}-${report.target_id}`} className="report-item-card">
                  <div className="report-item-header">
                    <span className="report-type-badge">{report.target_type}</span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text)' }}>
                      Author: <strong>@{report.author_username}</strong>
                    </span>
                  </div>

                  {report.title && <h3 className="report-item-title">{report.title}</h3>}
                  <div className="report-item-content">{report.content}</div>

                  <div className="report-reporters-section">
                    <strong>Reported by {report.report_count} user(s):</strong>
                    <div>
                      {report.reporters.map((rep) => (
                        <span key={rep.id} className="reporter-chip">
                          @{rep.username}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="report-item-actions">
                    <button
                      type="button"
                      className="btn-primary"
                      onClick={() => handleApproveReport(report)}
                    >
                      ✓ Approve {report.target_type}
                    </button>
                    <button
                      type="button"
                      className="btn-danger"
                      onClick={() => handleDeleteReported(report)}
                    >
                      Delete {report.target_type}
                    </button>
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => handleBanAuthorFromReport(report)}
                    >
                      Ban Author (@{report.author_username})
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* TAB 3: Moderation & Bans Panel */}
      {activeTab === 'moderation' && isModerator && (
        <section className="moderation-section">
          <div className="mod-panel-grid">
            {/* Owner Section: Moderators */}
            {isOwner && (
              <div className="mod-card">
                <h3>Designate Moderators</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text)', marginBottom: '1rem' }}>
                  Moderators can view the report log, approve/delete reported content, and ban users.
                </p>

                {moderators.length === 0 ? (
                  <p style={{ fontSize: '0.9rem', color: 'var(--text)', fontStyle: 'italic' }}>
                    No designated moderators yet.
                  </p>
                ) : (
                  <ul className="mod-list">
                    {moderators.map((mod) => (
                      <li key={mod.account_id} className="mod-list-item">
                        <span>@{mod.username}</span>
                        <button
                          type="button"
                          className="btn-danger btn-small"
                          onClick={() => handleRemoveModerator(mod.account_id)}
                        >
                          Remove
                        </button>
                      </li>
                    ))}
                  </ul>
                )}

                <form onSubmit={handleAddModerator} className="mod-add-form">
                  <input
                    className="form-input"
                    type="text"
                    placeholder="Username or User ID"
                    value={modTarget}
                    onChange={(e) => setModTarget(e.target.value)}
                    disabled={modSubmitting}
                    required
                  />
                  <button
                    type="submit"
                    className="btn-primary"
                    disabled={modSubmitting || !modTarget.trim()}
                  >
                    Add Mod
                  </button>
                </form>
              </div>
            )}

            {/* Banned Users Section */}
            <div className="mod-card">
              <h3>Banned Users</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text)', marginBottom: '1rem' }}>
                Banned users cannot create posts, leave comments, or submit reports.
              </p>

              {bannedUsers.length === 0 ? (
                <p style={{ fontSize: '0.9rem', color: 'var(--text)', fontStyle: 'italic' }}>
                  No banned users in this community.
                </p>
              ) : (
                <ul className="mod-list">
                  {bannedUsers.map((b) => (
                    <li key={b.account_id} className="mod-list-item">
                      <div>
                        <strong>@{b.username}</strong>
                        {b.banned_by_username && (
                          <span style={{ fontSize: '0.75rem', color: 'var(--text)', display: 'block' }}>
                            banned by @{b.banned_by_username}
                          </span>
                        )}
                      </div>
                      <button
                        type="button"
                        className="btn-secondary btn-small"
                        onClick={() => handleUnbanUser(b.account_id)}
                      >
                        Unban
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              <form onSubmit={handleBanUserManual} className="mod-add-form">
                <input
                  className="form-input"
                  type="text"
                  placeholder="Username or User ID"
                  value={banTarget}
                  onChange={(e) => setBanTarget(e.target.value)}
                  disabled={modSubmitting}
                  required
                />
                <button
                  type="submit"
                  className="btn-danger"
                  disabled={modSubmitting || !banTarget.trim()}
                >
                  Ban User
                </button>
              </form>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
