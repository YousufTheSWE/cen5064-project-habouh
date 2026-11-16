const BACKEND_DOMAIN =
  import.meta.env.VITE_BACKEND_DOMAIN || 'http://127.0.0.1:8000'

export async function getPosts(communityId = null, authToken = null) {
  const url = communityId
    ? `${BACKEND_DOMAIN}/posts?community_id=${communityId}`
    : `${BACKEND_DOMAIN}/posts`
  const headers = {}
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`
  }
  const response = await fetch(url, { headers })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load posts')
  }
  return data
}

export async function getPost(id, authToken = null) {
  const headers = {}
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`
  }
  const response = await fetch(`${BACKEND_DOMAIN}/posts/${id}`, { headers })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load post')
  }
  return data
}

export async function createPost(authToken, { community_id, name, description }) {
  const response = await fetch(`${BACKEND_DOMAIN}/posts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ community_id, name, description }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to create post')
  }
  return data.post
}

export async function updatePost(authToken, id, { name, description }) {
  const response = await fetch(`${BACKEND_DOMAIN}/posts/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ name, description }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to update post')
  }
  return data.post
}

export async function votePost(authToken, id, direction) {
  const response = await fetch(`${BACKEND_DOMAIN}/posts/${id}/vote`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ direction }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to vote on post')
  }
  return data
}

export async function deletePost(authToken, id) {
  const response = await fetch(`${BACKEND_DOMAIN}/posts/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to delete post')
  }
  return data
}
