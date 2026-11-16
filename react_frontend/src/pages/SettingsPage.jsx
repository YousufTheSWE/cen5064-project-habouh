import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import {
  checkUsernameAvailable,
  updatePassword,
  updateUsername,
} from '../services/authService'
import './SettingsPage.css'

export default function SettingsPage() {
  const { user, authToken, updateUsernameInContext } = useAuth()
  const navigate = useNavigate()

  // Username form state
  const [newUsername, setNewUsername] = useState(user || '')
  const [usernameStatus, setUsernameStatus] = useState(null)
  const [usernameError, setUsernameError] = useState('')
  const [usernameSuccess, setUsernameSuccess] = useState('')
  const [updatingUsername, setUpdatingUsername] = useState(false)

  // Password form state
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const [updatingPassword, setUpdatingPassword] = useState(false)

  useEffect(() => {
    if (!authToken) {
      navigate('/signin')
    }
  }, [authToken, navigate])

  // Live availability check for username update
  useEffect(() => {
    const trimmed = newUsername.trim()
    if (!trimmed || trimmed === user) {
      setUsernameStatus(null)
      return
    }
    setUsernameStatus('checking')
    const timer = setTimeout(async () => {
      try {
        const available = await checkUsernameAvailable(trimmed, authToken)
        setUsernameStatus(available ? 'available' : 'taken')
      } catch {
        setUsernameStatus(null)
      }
    }, 400)

    return () => clearTimeout(timer)
  }, [newUsername, user, authToken])

  const handleUsernameSubmit = async (e) => {
    e.preventDefault()
    if (newUsername === user) return
    if (usernameStatus === 'taken') {
      setUsernameError('Username is already taken')
      return
    }
    setUsernameError('')
    setUsernameSuccess('')
    setUpdatingUsername(true)
    try {
      const updated = await updateUsername(authToken, newUsername.trim())
      updateUsernameInContext(updated)
      setUsernameSuccess('Username updated successfully!')
      setUsernameStatus(null)
    } catch (err) {
      setUsernameError(err.message)
    } finally {
      setUpdatingUsername(false)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    setPasswordError('')
    setPasswordSuccess('')

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match')
      return
    }
    if (newPassword.length < 8) {
      setPasswordError('Password must be at least 8 characters')
      return
    }

    setUpdatingPassword(true)
    try {
      await updatePassword(authToken, currentPassword, newPassword)
      setPasswordSuccess('Password updated successfully!')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      setPasswordError(err.message)
    } finally {
      setUpdatingPassword(false)
    }
  }

  return (
    <div className="settings-container">
      <header className="settings-header">
        <h1>Account Settings</h1>
        <button
          type="button"
          className="btn-secondary"
          onClick={() => navigate('/communities')}
        >
          ← Back
        </button>
      </header>

      {/* Update Username Section */}
      <section className="settings-section">
        <h2>Change Username</h2>
        {usernameError && <p className="auth-error">{usernameError}</p>}
        {usernameSuccess && <p className="settings-success">{usernameSuccess}</p>}
        <form onSubmit={handleUsernameSubmit} className="form-body">
          <div className="form-group">
            <label className="form-label" htmlFor="settings-user">New Username</label>
            <input
              id="settings-user"
              className="form-input"
              type="text"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              required
            />
            {usernameStatus === 'checking' && (
              <span className="username-status status-checking">Checking availability...</span>
            )}
            {usernameStatus === 'available' && (
              <span className="username-status status-available">✓ Username is available</span>
            )}
            {usernameStatus === 'taken' && (
              <span className="username-status status-taken">✗ Username is already taken</span>
            )}
          </div>
          <button
            type="submit"
            className="btn-primary"
            style={{ alignSelf: 'flex-start' }}
            disabled={updatingUsername || usernameStatus === 'taken' || newUsername === user}
          >
            {updatingUsername ? 'Saving...' : 'Update Username'}
          </button>
        </form>
      </section>

      {/* Update Password Section */}
      <section className="settings-section">
        <h2>Change Password</h2>
        {passwordError && <p className="auth-error">{passwordError}</p>}
        {passwordSuccess && <p className="settings-success">{passwordSuccess}</p>}
        <form onSubmit={handlePasswordSubmit} className="form-body">
          <div className="form-group">
            <label className="form-label" htmlFor="curr-pass">Current Password</label>
            <input
              id="curr-pass"
              className="form-input"
              type="password"
              placeholder="Enter current password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="new-pass">New Password</label>
            <input
              id="new-pass"
              className="form-input"
              type="password"
              placeholder="Minimum 8 characters"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="conf-pass">Confirm New Password</label>
            <input
              id="conf-pass"
              className="form-input"
              type="password"
              placeholder="Re-enter new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ alignSelf: 'flex-start' }}
            disabled={updatingPassword}
          >
            {updatingPassword ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </section>
    </div>
  )
}
