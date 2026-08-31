import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT Auth Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- Document Endpoints ---
export const fetchDocuments = async (params = {}) => {
  const res = await api.get('/api/documents', { params });
  return res.data;
};

export const fetchDocumentDetails = async (docId) => {
  const res = await api.get(`/api/documents/${docId}`);
  return res.data;
};

export const uploadDocumentFile = async (formData) => {
  const res = await api.post('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const deleteDocument = async (docId) => {
  const res = await api.delete(`/api/documents/${docId}`);
  return res.data;
};

// --- Specialized Extractor Endpoints ---
export const fetchExtractorData = async (docId, extractorType) => {
  // extractorType: 'text' | 'images' | 'graphs' | 'tables' | 'numericals' | 'equations'
  const res = await api.get(`/api/documents/${docId}/extractors/${extractorType}`);
  return res.data;
};

// --- Chat & RAG Assistant Endpoints ---
export const askChatQuestion = async (payload) => {
  const res = await api.post('/api/query', payload);
  return res.data;
};

export const askChatQuestionWithFile = async (formData) => {
  const res = await api.post('/api/query/with-file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const fetchChatSessions = async () => {
  const res = await api.get('/api/query/sessions');
  return res.data;
};

export const createChatSession = async (title, documentId = null) => {
  const res = await api.post('/api/query/sessions', { title, document_id: documentId });
  return res.data;
};

export const renameChatSession = async (sessionId, title) => {
  const res = await api.put(`/api/query/sessions/${sessionId}`, { title });
  return res.data;
};

export const fetchSessionMessages = async (sessionId) => {
  const res = await api.get(`/api/query/sessions/${sessionId}`);
  return res.data;
};

export const clearSession = async (sessionId) => {
  const res = await api.delete(`/api/query/sessions/${sessionId}`);
  return res.data;
};

export const deleteChatSession = clearSession;

export const fetchQueryHistory = async (limit = 30) => {
  const res = await api.get('/api/query/history', { params: { limit } });
  return res.data;
};

export const fetchSystemHealth = async () => {
  const res = await api.get('/api/system/health');
  return res.data;
};

export default api;
