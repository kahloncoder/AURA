import axios from 'axios';

const API_URL = 'http://localhost:5000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const roomsApi = {
  getRooms: async () => {
    const response = await api.get('/api/rooms');
    return response.data;
  },
  
  createCustomRoom: async (data: {
    agents: Array<{
      name: string;
      prompt: string;
      voice?: string;
    }>;
    duration_minutes: number;
  }) => {
    const response = await api.post('/api/custom-room', data);
    return response.data;
  },
};

// --- ADD THIS NEW OBJECT ---
// This adds the functions to get conversation history from the backend
export const conversationsApi = {
  getConversations: async () => {
    const response = await api.get('/api/conversations');
    return response.data;
  },
  getConversationById: async (id: string) => {
    const response = await api.get(`/api/conversations/${id}`);
    return response.data;
  },
};

export const authApi = {
  register: async (data: any) => {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  },
  login: async (data: any) => {
    const response = await api.post('/api/auth/login', data);
    return response.data; // This will include the token
  },
};