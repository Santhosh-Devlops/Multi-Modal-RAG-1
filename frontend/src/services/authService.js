import apiClient from './apiService';

export const register = async (email, password, fullName) => {
  const res = await apiClient.post('/api/auth/register', {
    email,
    password,
    full_name: fullName,
  });
  return res.data;
};

export const login = async (email, password) => {
  const res = await apiClient.post('/api/auth/login', { email, password });
  return res.data;
};

export const getCurrentUser = async () => {
  const res = await apiClient.get('/api/auth/me');
  return res.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

