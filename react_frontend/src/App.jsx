import { BrowserRouter, Route, Routes } from 'react-router'
import { AuthProvider } from './context/AuthContext'
import HomePage from './pages/HomePage'
import RegisterPage from './pages/RegisterPage'
import SignInPage from './pages/SignInPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
