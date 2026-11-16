const BACKEND_DOMAIN =
  import.meta.env.VITE_BACKEND_DOMAIN || 'http://127.0.0.1:8000'

export async function getComments(postId, authToken = null) {
  const headers = {}
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`
  }
  const response = await fetch(`${BACKEND_DOMAIN}/comments?post_id=${postId}`, {
    headers,
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load comments')
  }
  return data
}

export async function getComment(id, authToken = null) {
  const headers = {}
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`
  }
  const response = await fetch(`${BACKEND_DOMAIN}/comments/${id}`, { headers })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load comment')
  }
  return data
}

export async function createComment(authToken, { post_id, description }) {
  const response = await fetch(`${BACKEND_DOMAIN}/comments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ post_id, description }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to create comment')
  }
  return data.comment
}

export async function updateComment(authToken, id, { description }) {
  const response = await fetch(`${BACKEND_DOMAIN}/comments/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ description }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to update comment')
  }
  return data.comment
}

export async function voteComment(authToken, id, direction) {
  const response = await fetch(`${BACKEND_DOMAIN}/comments/${id}/vote`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ direction }),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to vote on comment')
  }
  return data
}

export async function deleteComment(authToken, id) {
  const response = await fetch(`${BACKEND_DOMAIN}/comments/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to delete comment')
  }
  return data
}
