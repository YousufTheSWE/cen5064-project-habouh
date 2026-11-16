import { createContext, useContext, useEffect, useState } from 'react'
import { createAccount, loginAccount, logoutAccount } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => localStorage.getItem('postclient_user') || null)
  const [accountId, setAccountId] = useState(() => {
    const saved = localStorage.getItem('postclient_account_id')
    return saved ? Number(saved) : null
  })
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('postclient_auth_token') || null)

  useEffect(() => {
    if (user) {
      localStorage.setItem('postclient_user', user)
    } else {
      localStorage.removeItem('postclient_user')
    }
  }, [user])

  useEffect(() => {
    if (accountId) {
      localStorage.setItem('postclient_account_id', String(accountId))
    } else {
      localStorage.removeItem('postclient_account_id')
    }
  }, [accountId])

  useEffect(() => {
    if (authToken) {
      localStorage.setItem('postclient_auth_token', authToken)
    } else {
      localStorage.removeItem('postclient_auth_token')
    }
  }, [authToken])

  const login = async (username, password) => {
    const data = await loginAccount(username, password)
    setUser(data.username)
    setAccountId(data.account_id)
    setAuthToken(data.auth_token)
    return data
  }

  const register = async (username, password) => {
    const data = await createAccount(username, password)
    setUser(data.username)
    setAccountId(data.account_id)
    setAuthToken(data.auth_token)
    return data
  }

  const updateUsernameInContext = (newUsername) => {
    setUser(newUsername)
    localStorage.setItem('postclient_user', newUsername)
  }

  const logout = () => {
    if (authToken) {
      logoutAccount(authToken)
    }
    setUser(null)
    setAccountId(null)
    setAuthToken(null)
    localStorage.removeItem('postclient_user')
    localStorage.removeItem('postclient_account_id')
    localStorage.removeItem('postclient_auth_token')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        accountId,
        authToken,
        login,
        register,
        updateUsernameInContext,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
