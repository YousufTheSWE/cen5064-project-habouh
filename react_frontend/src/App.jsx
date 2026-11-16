import { BrowserRouter, Route, Routes } from 'react-router'
import { AuthProvider } from './context/AuthContext'
import CommunitiesPage from './pages/CommunitiesPage'
import CommunityDetailPage from './pages/CommunityDetailPage'
import CreateCommunityPage from './pages/CreateCommunityPage'
import CreatePostPage from './pages/CreatePostPage'
import HomePage from './pages/HomePage'
import PostDetailPage from './pages/PostDetailPage'
import RegisterPage from './pages/RegisterPage'
import SettingsPage from './pages/SettingsPage'
import SignInPage from './pages/SignInPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/communities" element={<CommunitiesPage />} />
          <Route path="/communities/new" element={<CreateCommunityPage />} />
          <Route path="/communities/:communityId" element={<CommunityDetailPage />} />
          <Route path="/communities/:communityId/new-post" element={<CreatePostPage />} />
          <Route path="/posts/:postId" element={<PostDetailPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
