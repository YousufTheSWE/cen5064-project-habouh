import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import { checkUsernameAvailable } from '../services/authService'
import './RegisterPage.css'

export default function RegisterPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [usernameStatus, setUsernameStatus] = useState(null) // null | 'checking' | 'available' | 'taken'
  const [submitting, setSubmitting] = useState(false)

  const { register } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const trimmed = username.trim()
    if (!trimmed) {
      setUsernameStatus(null)
      return
    }
    setUsernameStatus('checking')
    const timer = setTimeout(async () => {
      try {
        const available = await checkUsernameAvailable(trimmed)
        setUsernameStatus(available ? 'available' : 'taken')
      } catch {
        setUsernameStatus(null)
      }
    }, 400)

    return () => clearTimeout(timer)
  }, [username])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (usernameStatus === 'taken') {
      setError('Username is already taken')
      return
    }
    setError('')
    setSubmitting(true)
    try {
      await register(username, password)
      navigate('/communities')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-container">
      <h2>Registor</h2>
      {error && <p className="auth-error">{error}</p>}
      <form onSubmit={handleSubmit} className="auth-form">
        <div style={{ textAlign: 'left' }}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="auth-input"
          />
          {usernameStatus === 'checking' && (
            <span style={{ fontSize: '0.8rem', color: 'var(--text)', display: 'block', marginTop: '4px' }}>
              Checking availability...
            </span>
          )}
          {usernameStatus === 'available' && (
            <span style={{ fontSize: '0.8rem', color: '#10b981', display: 'block', marginTop: '4px' }}>
              ✓ Username is available
            </span>
          )}
          {usernameStatus === 'taken' && (
            <span style={{ fontSize: '0.8rem', color: '#ef4444', display: 'block', marginTop: '4px' }}>
              ✗ Username is already taken
            </span>
          )}
        </div>

        <input
          type="password"
          placeholder="Password (minimum 8 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="auth-input"
        />
        <button
          type="submit"
          className="auth-submit-btn"
          disabled={submitting || usernameStatus === 'taken'}
        >
          {submitting ? 'Registering...' : 'Registor'}
        </button>
      </form>
      <div className="auth-link-container">
        <Link to="/signin" className="auth-link">
          sign in instead
        </Link>
      </div>
    </main>
  )
}
