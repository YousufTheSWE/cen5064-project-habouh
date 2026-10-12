import { createContext, useContext, useState } from 'react'
import { createAccount, loginAccount } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const login = async (username, password) => {
    const data = await loginAccount(username, password)
    setUser(data.username)
    return data
  }

  const register = async (username, password) => {
    const data = await createAccount(username, password)
    return data
  }

  const logout = () => setUser(null)

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
