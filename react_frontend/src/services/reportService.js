const BACKEND_DOMAIN =
  import.meta.env.VITE_BACKEND_DOMAIN || 'http://127.0.0.1:8000'

export async function reportPost(authToken, postId) {
  const response = await fetch(`${BACKEND_DOMAIN}/posts/${postId}/report`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to report post')
  }
  return data
}

export async function reportComment(authToken, commentId) {
  const response = await fetch(`${BACKEND_DOMAIN}/comments/${commentId}/report`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to report comment')
  }
  return data
}

export async function getReports(authToken, communityId) {
  const response = await fetch(`${BACKEND_DOMAIN}/communities/${communityId}/reports`, {
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to load report log')
  }
  return data
}

export async function approveReport(authToken, communityId, targetType, targetId) {
  const response = await fetch(
    `${BACKEND_DOMAIN}/communities/${communityId}/reports/${targetType}/${targetId}/approve`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    },
  )
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to approve item')
  }
  return data
}

export async function deleteReportedItem(authToken, communityId, targetType, targetId) {
  const response = await fetch(
    `${BACKEND_DOMAIN}/communities/${communityId}/reports/${targetType}/${targetId}`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    },
  )
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Failed to delete reported item')
  }
  return data
}
