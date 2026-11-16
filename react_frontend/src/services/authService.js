const BACKEND_DOMAIN =
  import.meta.env.VITE_BACKEND_DOMAIN || 'http://127.0.0.1:8000'

export async function checkUsernameAvailable(username, authToken = null) {
  const headers = {}
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`
  }
  const response = await fetch(
    `${BACKEND_DOMAIN}/check_username?username=${encodeURIComponent(username)}`,
    { headers },
  )
  if (!response.ok) return false
  const data = await response.json()
  return data.available
}

export async function createAccount(username, password) {
  const response = await fetch(`${BACKEND_DOMAIN}/create_account`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await response.json()
  if (!response.ok) {
    const errorMsg =
      data.error ||
      (Array.isArray(data.detail) ? data.detail[0]?.msg : data.detail) ||
      'Failed to create account'
    throw new Error(errorMsg)
  }
  return data
}

export async function loginAccount(username, password) {
  const response = await fetch(`${BACKEND_DOMAIN}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await response.json()
  if (!response.ok) {
    const errorMsg =
      data.error ||
      (Array.isArray(data.detail) ? data.detail[0]?.msg : data.detail) ||
      'Failed to sign in'
    throw new Error(errorMsg)
  }
  return data
}

export async function updateUsername(authToken, username) {
  const response = await fetch(`${BACKEND_DOMAIN}/me/username`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ username }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to update username')
  }
  return data.username
}

export async function updatePassword(authToken, currentPassword, newPassword) {
  const response = await fetch(`${BACKEND_DOMAIN}/me/password`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to update password')
  }
  return data
}

export async function logoutAccount(authToken) {
  if (!authToken) return
  await fetch(`${BACKEND_DOMAIN}/logout`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  }).catch(() => {})
}
