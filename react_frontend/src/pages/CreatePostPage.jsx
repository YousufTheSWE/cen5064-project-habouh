import { useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { useAuth } from '../context/AuthContext'
import { createPost } from '../services/postService'
import './CreateCommunityPage.css'
import './CreatePostPage.css'

export default function CreatePostPage() {
  const { communityId } = useParams()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
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
      const post = await createPost(authToken, {
        community_id: Number(communityId),
        name,
        description,
      })
      navigate(`/posts/${post.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="create-post-container">
      <div className="create-post-header">
        <h2>Create a Post</h2>
      </div>
      {error && <p className="auth-error">{error}</p>}
      <form onSubmit={handleSubmit} className="form-body">
        <div className="form-group">
          <label className="form-label" htmlFor="post-name">Title</label>
          <input
            id="post-name"
            className="form-input"
            type="text"
            placeholder="Give your post an interesting title..."
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="post-desc">Content</label>
          <textarea
            id="post-desc"
            className="form-textarea"
            style={{ minHeight: '140px' }}
            placeholder="Write your post content here..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
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
            {submitting ? 'Publishing...' : 'Publish Post'}
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate(`/communities/${communityId}`)}
          >
            Cancel
          </button>
        </div>
      </form>
    </main>
  )
}
