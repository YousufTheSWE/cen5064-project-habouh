const BACKEND_DOMAIN =
  import.meta.env.VITE_BACKEND_DOMAIN || 'http://127.0.0.1:8000'

export async function getCommunities() {
  const response = await fetch(`${BACKEND_DOMAIN}/communities`)
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load communities')
  }
  return data
}

export async function getCommunity(id, authToken = null) {
  const headers = {}
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`
  }
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${id}`, { headers })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load community')
  }
  return data
}

export async function createCommunity(authToken, { name, description, picture }) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ name, description, picture }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to create community')
  }
  return data.community
}

export async function updateCommunity(authToken, id, { name, description, picture }) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ name, description, picture }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to update community')
  }
  return data.community
}

export async function transferCommunityOwnership(authToken, id, target) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${id}/transfer_ownership`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ target }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to transfer ownership')
  }
  return data.community
}

export async function deleteCommunity(authToken, id) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to delete community')
  }
  return data
}

// Moderator Management
export async function getModerators(authToken, communityId) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${communityId}/moderators`, {
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load moderators')
  }
  return data
}

export async function addModerator(authToken, communityId, target) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${communityId}/moderators`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ target }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to add moderator')
  }
  return data.moderator
}

export async function removeModerator(authToken, communityId, targetAccountId) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${communityId}/moderators/${targetAccountId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to remove moderator')
  }
  return data
}

// Banned User Management
export async function getBannedUsers(authToken, communityId) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${communityId}/banned`, {
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load banned users')
  }
  return data
}

export async function banUser(authToken, communityId, target) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${communityId}/banned`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ target }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to ban user')
  }
  return data.banned
}

export async function unbanUser(authToken, communityId, targetAccountId) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${communityId}/banned/${targetAccountId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to unban user')
  }
  return data
}
