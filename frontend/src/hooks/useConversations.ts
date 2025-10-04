import { useState, useEffect } from 'react';

export interface ConversationLog {
  room: string;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  conversation: Array<{
    timestamp: string;
    role: 'user' | 'assistant';
    content: string;
    agent?: string;
  }>;
}

export interface ConversationSummary {
  id: string;
  roomName: string;
  date: string;
  duration: string;
  messageCount: number;
  preview: string;
  fullLog: ConversationLog;
}

export const useConversations = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      
      // TODO: Replace with actual API call when MongoDB is enabled
      // const response = await fetch('http://localhost:5000/api/conversations');
      // const data = await response.json();
      
      // For now, load from localStorage as demo
      const savedLogs = localStorage.getItem('aura_conversations');
      
      if (savedLogs) {
        const logs: ConversationLog[] = JSON.parse(savedLogs);
        const summaries = logs.map((log, idx) => ({
          id: `conv_${idx}`,
          roomName: log.room,
          date: new Date(log.start_time).toLocaleDateString(),
          duration: formatDuration(log.duration_seconds),
          messageCount: log.conversation.length,
          preview: getConversationPreview(log),
          fullLog: log,
        }));
        setConversations(summaries);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getConversationPreview = (log: ConversationLog): string => {
    const firstUserMessage = log.conversation.find(m => m.role === 'user');
    return firstUserMessage?.content.substring(0, 100) || 'No messages';
  };

  const saveConversation = (log: ConversationLog) => {
    const savedLogs = localStorage.getItem('aura_conversations');
    const logs = savedLogs ? JSON.parse(savedLogs) : [];
    logs.push(log);
    localStorage.setItem('aura_conversations', JSON.stringify(logs));
    loadConversations();
  };

  const deleteConversation = (id: string) => {
    const updated = conversations.filter(c => c.id !== id);
    localStorage.setItem('aura_conversations', JSON.stringify(updated.map(c => c.fullLog)));
    setConversations(updated);
  };

  return {
    conversations,
    loading,
    loadConversations,
    saveConversation,
    deleteConversation,
  };
};
