const BACKEND_DOMAIN =
  import.meta.env.VITE_BACKEND_DOMAIN

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
