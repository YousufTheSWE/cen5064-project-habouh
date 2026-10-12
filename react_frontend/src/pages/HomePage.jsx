import { useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import './HomePage.css'

export default function HomePage() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  return (
    <main className="home-container">
      {user ? (
        <>
          <h2>Welcome, {user}!</h2>
          <button type="button" onClick={logout} className="signout-btn">
            Sign out
          </button>
        </>
      ) : (
        <>
          <h2>You are not signed in</h2>
          <div className="home-button-group">
            <button
              type="button"
              onClick={() => navigate('/signin')}
              className="home-btn"
            >
              Sign in
            </button>
            <button
              type="button"
              onClick={() => navigate('/register')}
              className="home-btn"
            >
              Registor
            </button>
          </div>
        </>
      )}
    </main>
  )
}
