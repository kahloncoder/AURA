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