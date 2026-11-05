/**
 * Chat Service - API Layer connecting to FastAPI backend
 */

/**
 * Format bytes into readable string (KB, MB, etc.)
 */
export function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

const BACKEND_URL = 'http://localhost:8000';

/**
 * Send a chat message with optional document attachments to FastAPI.
 * 
 * @param {Object} params
 * @param {string} params.text - The prompt or query from the user.
 * @param {Array<File>} params.files - Any attached files/documents.
 * @returns {Promise<Object>} The AI assistant response.
 */
export async function sendMessageToAI({ text, files = [] }) {
  const formData = new FormData();
  formData.append('query', text || '');

  if (files && files.length > 0) {
    files.forEach((file) => {
      formData.append('files', file);
    });
  }

  const response = await fetch(`${BACKEND_URL}/api/chat`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorMessage = `Server error (${response.status})`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : JSON.stringify(errorData.detail);
      }
    } catch (_) {
      // Keep default error message if response is not JSON
    }
    throw new Error(errorMessage);
  }

  const data = await response.json();

  return {
    id: Date.now().toString(),
    text: data.response || data.answer || 'No response returned from server.',
    filesProcessed: data.files_processed || [],
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  };
}
