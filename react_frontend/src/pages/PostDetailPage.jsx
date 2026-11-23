import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { useAuth } from '../context/AuthContext'
import {
  createComment,
  deleteComment,
  getComments,
  updateComment,
  voteComment,
} from '../services/commentService'
import { getCommunity } from '../services/communityService'
import { deletePost, getPost, updatePost, votePost } from '../services/postService'
import { reportComment, reportPost } from '../services/reportService'
import './PostDetailPage.css'

export default function PostDetailPage() {
  const { postId } = useParams()
  const { user, accountId, authToken } = useAuth()
  const navigate = useNavigate()

  const [post, setPost] = useState(null)
  const [community, setCommunity] = useState(null)
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [feedbackMsg, setFeedbackMsg] = useState('')

  // Edit Post state
  const [isEditingPost, setIsEditingPost] = useState(false)
  const [editPostName, setEditPostName] = useState('')
  const [editPostDesc, setEditPostDesc] = useState('')

  // New Comment state
  const [newCommentText, setNewCommentText] = useState('')
  const [commentSubmitting, setCommentSubmitting] = useState(false)

  // Edit Comment state
  const [editingCommentId, setEditingCommentId] = useState(null)
  const [editCommentText, setEditCommentText] = useState('')

  useEffect(() => {
    Promise.all([getPost(postId, authToken), getComments(postId, authToken)])
      .then(([postData, commentsData]) => {
        setPost(postData)
        setEditPostName(postData.name)
        setEditPostDesc(postData.description)
        setComments(commentsData)
        return getCommunity(postData.community_id, authToken)
      })
      .then((commData) => {
        if (commData) setCommunity(commData)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [postId, authToken])

  const isBanned = community ? community.is_banned : false
  const isModerator = community ? community.is_moderator || community.is_owner : false
  const isPostAuthor = Number(accountId) === Number(post?.author_id)
  const postScore = (post?.upvotes || 0) - (post?.downvotes || 0)

  const handleUpdatePost = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const updated = await updatePost(authToken, postId, {
        name: editPostName,
        description: editPostDesc,
      })
      setPost((prev) => ({ ...prev, ...updated, is_approved: 0 }))
      setIsEditingPost(false)
      setFeedbackMsg('Post updated successfully.')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeletePost = async () => {
    if (!window.confirm('Are you sure you want to delete this post?')) return
    setError('')
    try {
      await deletePost(authToken, postId)
      navigate(`/communities/${post.community_id}`)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleVotePost = async (direction) => {
    if (!authToken) {
      navigate('/signin')
      return
    }
    const targetDirection = post.user_vote === direction ? 0 : direction
    try {
      const res = await votePost(authToken, postId, targetDirection)
      setPost((prev) => ({
        ...prev,
        upvotes: res.upvotes,
        downvotes: res.downvotes,
        user_vote: res.user_vote,
      }))
    } catch (err) {
      setError(err.message)
    }
  }

  const handleReportPost = async () => {
    if (!authToken) {
      navigate('/signin')
      return
    }
    setError('')
    setFeedbackMsg('')
    try {
      await reportPost(authToken, postId)
      setFeedbackMsg('Post reported to community moderators.')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleCreateComment = async (e) => {
    e.preventDefault()
    if (!authToken) {
      navigate('/signin')
      return
    }
    setError('')
    setCommentSubmitting(true)
    try {
      const created = await createComment(authToken, {
        post_id: Number(postId),
        description: newCommentText,
      })
      setComments([...comments, created])
      setNewCommentText('')
    } catch (err) {
      setError(err.message)
    } finally {
      setCommentSubmitting(false)
    }
  }

  const handleVoteComment = async (comment, direction) => {
    if (!authToken) {
      navigate('/signin')
      return
    }
    const targetDirection = comment.user_vote === direction ? 0 : direction
    try {
      const res = await voteComment(authToken, comment.id, targetDirection)
      setComments((prevComments) =>
        prevComments.map((c) =>
          c.id === comment.id
            ? { ...c, upvotes: res.upvotes, downvotes: res.downvotes, user_vote: res.user_vote }
            : c,
        ),
      )
    } catch (err) {
      setError(err.message)
    }
  }

  const handleReportComment = async (comment) => {
    if (!authToken) {
      navigate('/signin')
      return
    }
    setError('')
    setFeedbackMsg('')
    try {
      await reportComment(authToken, comment.id)
      setFeedbackMsg('Comment reported to community moderators.')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleUpdateComment = async (commentId) => {
    setError('')
    try {
      const updated = await updateComment(authToken, commentId, {
        description: editCommentText,
      })
      setComments(comments.map((c) => (c.id === commentId ? { ...c, ...updated, is_approved: 0 } : c)))
      setEditingCommentId(null)
      setFeedbackMsg('Comment updated successfully.')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Delete this comment?')) return
    setError('')
    try {
      await deleteComment(authToken, commentId)
      setComments(comments.filter((c) => c.id !== commentId))
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <div className="post-detail-page"><p className="empty-state">Loading post...</p></div>
  if (!post) return <div className="post-detail-page"><p className="empty-state">{error || 'Post not found'}</p></div>

  return (
    <div className="post-detail-page">
      <div style={{ marginBottom: '1.5rem', textAlign: 'left' }}>
        <button
          type="button"
          className="btn-secondary"
          onClick={() => navigate(`/communities/${post.community_id}`)}
        >
          ← Back to Community
        </button>
      </div>

      {isBanned && (
        <div className="banned-banner">
          ⚠️ You are banned from this community. You cannot comment, edit, or submit reports.
        </div>
      )}

      {error && <p className="auth-error">{error}</p>}
      {feedbackMsg && <div className="success-banner">{feedbackMsg}</div>}

      <article className="post-main-card">
        {isEditingPost ? (
          <form onSubmit={handleUpdatePost} className="form-body">
            <input
              className="form-input"
              type="text"
              value={editPostName}
              onChange={(e) => setEditPostName(e.target.value)}
              required
            />
            <textarea
              className="form-textarea"
              style={{ minHeight: '120px' }}
              value={editPostDesc}
              onChange={(e) => setEditPostDesc(e.target.value)}
              required
            />
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button type="submit" className="btn-primary">Save Changes</button>
              <button type="button" className="btn-secondary" onClick={() => setIsEditingPost(false)}>Cancel</button>
            </div>
          </form>
        ) : (
          <div className="post-main-layout">
            <div className="vote-widget">
              <button
                type="button"
                aria-label="Upvote"
                className={`vote-btn ${post.user_vote === 1 ? 'upvoted' : ''}`}
                onClick={() => handleVotePost(1)}
              >
                ▲
              </button>
              <span className="vote-score">{postScore}</span>
              <button
                type="button"
                aria-label="Downvote"
                className={`vote-btn ${post.user_vote === -1 ? 'downvoted' : ''}`}
                onClick={() => handleVotePost(-1)}
              >
                ▼
              </button>
            </div>
            <div className="post-main-content">
              <div className="post-header-top">
                <h1 className="post-detail-title">{post.name}</h1>
                <div className="post-actions">
                  {post.is_approved ? (
                    isModerator && <span className="approved-pill">✓ Approved</span>
                  ) : (
                    user && !isBanned && (
                      <button
                        type="button"
                        className="btn-report"
                        onClick={handleReportPost}
                      >
                        🚩 Report
                      </button>
                    )
                  )}
                  {isPostAuthor && (
                    <>
                      {!isBanned && (
                        <button
                          type="button"
                          className="btn-secondary btn-small"
                          onClick={() => setIsEditingPost(true)}
                        >
                          Edit
                        </button>
                      )}
                      <button
                        type="button"
                        className="btn-danger btn-small"
                        onClick={handleDeletePost}
                      >
                        Delete
                      </button>
                    </>
                  )}
                </div>
              </div>
              <div className="post-detail-meta">
                Posted by @{post.author_username || `user_${post.author_id}`}
              </div>
              <div className="post-detail-body">
                {post.description}
              </div>
            </div>
          </div>
        )}
      </article>

      <section className="comments-section">
        <h2 className="comments-header">Comments ({comments.length})</h2>

        {user && !isBanned ? (
          <form onSubmit={handleCreateComment} className="comment-form-card">
            <textarea
              className="form-textarea"
              placeholder="Write a comment..."
              rows={3}
              value={newCommentText}
              onChange={(e) => setNewCommentText(e.target.value)}
              required
            />
            <div style={{ textAlign: 'right', marginTop: '0.75rem' }}>
              <button
                type="submit"
                className="btn-primary"
                disabled={commentSubmitting}
              >
                {commentSubmitting ? 'Posting...' : 'Post Comment'}
              </button>
            </div>
          </form>
        ) : isBanned ? (
          <div className="comment-form-card" style={{ textAlign: 'center' }}>
            <p style={{ margin: 0, color: '#ef4444' }}>You cannot comment because you are banned in this community.</p>
          </div>
        ) : (
          <div className="comment-form-card" style={{ textAlign: 'center' }}>
            <p style={{ margin: '0 0 0.75rem' }}>Sign in to leave a comment.</p>
            <button
              type="button"
              className="btn-secondary btn-small"
              onClick={() => navigate('/signin')}
            >
              Sign In
            </button>
          </div>
        )}

        {comments.length === 0 ? (
          <p className="empty-state">No comments yet. Start the conversation!</p>
        ) : (
          <div className="comments-list">
            {comments.map((comment) => {
              const isCommentAuthor = Number(accountId) === Number(comment.author_id)
              const commentScore = (comment.upvotes || 0) - (comment.downvotes || 0)
              return (
                <div key={comment.id} className="comment-card">
                  <div className="comment-main-layout">
                    <div className="vote-widget">
                      <button
                        type="button"
                        aria-label="Upvote"
                        className={`vote-btn ${comment.user_vote === 1 ? 'upvoted' : ''}`}
                        onClick={() => handleVoteComment(comment, 1)}
                      >
                        ▲
                      </button>
                      <span className="vote-score">{commentScore}</span>
                      <button
                        type="button"
                        aria-label="Downvote"
                        className={`vote-btn ${comment.user_vote === -1 ? 'downvoted' : ''}`}
                        onClick={() => handleVoteComment(comment, -1)}
                      >
                        ▼
                      </button>
                    </div>
                    <div className="comment-main-content">
                      <div className="comment-card-header">
                        <span style={{ fontWeight: 600, color: 'var(--accent)' }}>
                          @{comment.author_username || `user_${comment.author_id}`}
                        </span>
                        <div className="comment-actions">
                          {comment.is_approved ? (
                            isModerator && <span className="approved-pill">✓ Approved</span>
                          ) : (
                            user && !isBanned && (
                              <button
                                type="button"
                                className="btn-report"
                                onClick={() => handleReportComment(comment)}
                              >
                                🚩 Report
                              </button>
                            )
                          )}
                          {isCommentAuthor && editingCommentId !== comment.id && (
                            <>
                              {!isBanned && (
                                <button
                                  type="button"
                                  className="btn-secondary btn-small"
                                  onClick={() => {
                                    setEditingCommentId(comment.id)
                                    setEditCommentText(comment.description)
                                  }}
                                >
                                  Edit
                                </button>
                              )}
                              <button
                                type="button"
                                className="btn-danger btn-small"
                                onClick={() => handleDeleteComment(comment.id)}
                              >
                                Delete
                              </button>
                            </>
                          )}
                        </div>
                      </div>

                      {editingCommentId === comment.id ? (
                        <div style={{ marginTop: '0.5rem' }}>
                          <textarea
                            className="form-textarea"
                            value={editCommentText}
                            onChange={(e) => setEditCommentText(e.target.value)}
                            required
                          />
                          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                            <button
                              type="button"
                              className="btn-primary btn-small"
                              onClick={() => handleUpdateComment(comment.id)}
                            >
                              Save
                            </button>
                            <button
                              type="button"
                              className="btn-secondary btn-small"
                              onClick={() => setEditingCommentId(null)}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <p className="comment-card-desc">{comment.description}</p>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}

