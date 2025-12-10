import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Trash2, Plus } from 'lucide-react';
import axios from 'axios';
import './App.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface Session {
  session_id: string;
  message_count: number;
  created_at: string;
  last_updated: string;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [showSidebar, setShowSidebar] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/sessions`);
      setSessions(response.data);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadSession = async (sid: string) => {
    try {
      const response = await axios.get(`${API_URL}/api/sessions/${sid}`);
      setMessages(response.data.messages);
      setSessionId(sid);
      setShowSidebar(false);
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const deleteSession = async (sid: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API_URL}/api/sessions/${sid}`);
      if (sid === sessionId) {
        setMessages([]);
        setSessionId(null);
      }
      loadSessions();
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const startNewSession = () => {
    setMessages([]);
    setSessionId(null);
    setShowSidebar(false);
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: input.trim(),
        session_id: sessionId,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setSessionId(response.data.session_id);
      loadSessions();
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <div className={`sidebar ${showSidebar ? 'show' : ''}`}>
        <div className="sidebar-header">
          <h2>Chat Sessions</h2>
          <button className="close-btn" onClick={() => setShowSidebar(false)}>
            ×
          </button>
        </div>
        <button className="new-chat-btn" onClick={startNewSession}>
          <Plus size={20} />
          New Chat
        </button>
        <div className="sessions-list">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              className={`session-item ${session.session_id === sessionId ? 'active' : ''}`}
              onClick={() => loadSession(session.session_id)}
            >
              <div className="session-info">
                <div className="session-title">
                  Session {session.session_id.slice(0, 8)}
                </div>
                <div className="session-meta">
                  {session.message_count} messages
                </div>
              </div>
              <button
                className="delete-session-btn"
                onClick={(e) => deleteSession(session.session_id, e)}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <button className="menu-btn" onClick={() => setShowSidebar(!showSidebar)}>
            ☰
          </button>
          <h1>Smart Assist</h1>
          <div className="header-subtitle">Financial Insights Agent</div>
        </div>

        {/* Messages */}
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <Bot size={64} className="welcome-icon" />
              <h2>Welcome to Smart Assist</h2>
              <p>
                I'm your financial insights assistant. I can help you analyze portfolios,
                calculate returns, assess risk, and answer questions about your financial data.
              </p>
              <div className="suggestions">
                <button onClick={() => setInput("What is my portfolio's total return?")}>
                  What is my portfolio's total return?
                </button>
                <button onClick={() => setInput("Show me my risk exposure by sector")}>
                  Show me my risk exposure by sector
                </button>
                <button onClick={() => setInput("Calculate Sharpe ratio for my holdings")}>
                  Calculate Sharpe ratio for my holdings
                </button>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <div className="message-icon">
                  {message.role === 'user' ? <User size={24} /> : <Bot size={24} />}
                </div>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  <div className="message-timestamp">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="message assistant">
              <div className="message-icon">
                <Bot size={24} />
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form className="input-form" onSubmit={sendMessage}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me about your portfolio, returns, risk, or market analysis..."
            disabled={loading}
          />
          <button type="submit" disabled={!input.trim() || loading}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
